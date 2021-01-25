# -*- coding: utf-8 -*-
import logging
import logging.handlers
import sys
import argparse
import asyncio
from datetime import datetime, timedelta
import subprocess
import signal

import functools

import config
import os
import shutil
from aiohttp import web
import json
import sqlite3
import dateutil.parser


ROOT_FOLDER = dir_path = os.path.dirname(os.path.realpath(__file__))
args = None


logger = logging.getLogger(__name__)


def default_json(obj):
    if isinstance(obj, datetime):
        return str(obj)
    return str(obj)


json_dumps = functools.partial(json.dumps, default=default_json)


async def getStatus(req):
    limit = 10
    try:
        limit = int(req.query.get('limit', 10))
    except:
        limit = 10

    with get_conn() as conn:
        result = conn.execute("SELECT id, region, category, to_date, started_at, done_at FROM launchs ORDER BY id DESC LIMIT ?", [limit])
        data = [{
            "id": i[0],
            "region": i[1],
            "category": i[2],
            "to_date": datetime.fromtimestamp(i[3]),
            "started_at": datetime.fromtimestamp(i[4]) if i[4] else 0,
            "done_at": datetime.fromtimestamp(i[5]) if i[5] else 0
        } for i in result.fetchall()]
        return web.json_response(data=data, dumps=json_dumps)


async def start(loop, conf):
    await schedule(loop)


async def schedule(loop):
    time_dt = (get_next_schedule_datetime() - datetime.now()).seconds
    loop.call_later(time_dt, lambda: asyncio.ensure_future(parse(loop), loop=loop))
    logger.info("Scheduled after {}".format(time_dt))


def get_next_schedule_datetime():
    now = datetime.now() + timedelta(hours=1, seconds=1)
    return now.replace(minute=0, second=0, microsecond=0)


async def parse(loop):
    conf = config.getConfig()
    for region, location_id, categories in conf["PARSE"]:
        for category, category_id in categories:
            start_time = datetime.now()
            logger.info("region={}, category={}, started={}".format(region, category, start_time))

            parser_args = [
                conf["PYTHON_COMMAND"],
                os.path.join(ROOT_FOLDER, "parser", "main.py"),
                region,
                str(location_id),
                category,
                str(category_id),
                "--config",
                args.config,
                "--workers",
                "2",
                "--date",
                last_import_time(region, category).isoformat(),
                "--pages",
                str(args.pages)
            ]
            if args.test:
                parser_args.append("--test")

            env = dict(os.environ)

            ret = await loop.run_in_executor(None, start_parser, parser_args, env)
            if ret != 0:
               logger.error("Parser subprocess failed. {}".format(ret)) 
    await schedule(loop)


def start_parser(args, env):
    logger.info("Calling parser {}".format(args))
    proc = subprocess.Popen(args, env=env)
    try:
        proc.wait()
        return proc.returncode
    except KeyboardInterrupt:
        proc.send_signal(signal.SIGINT)
        proc.wait()
        os._exit(1)
    except:
        proc.send_signal(signal.SIGINT)
        proc.wait()
        return proc.returncode


def last_import_time(region, category):
    with get_conn() as conn:
        res = conn.execute(
            "SELECT to_date FROM launchs WHERE region=? AND category=? AND to_date != 0 ORDER BY id DESC LIMIT 1",
            [region, category]
        )
        data = res.fetchone()
        if data is None or (data[0] - datetime.now().timestamp()) > 2 * 3600:
            return get_prev_hour()

        return datetime.fromtimestamp(data[0])


def get_prev_hour():
    now = datetime.now() - timedelta(hours=1)
    return now.replace(minute=0, second=0, microsecond=0)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Path to config", type=str, default="default.json")
    parser.add_argument("--init", action='store_true', help="Init application", default=False)
    parser.add_argument("--pages",
                        help="Maximum pages to look for. Default 100", default=100, type=int)
    parser.add_argument("--test", action='store_true', help="Test application", default=False)
    return parser.parse_args()


def init():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS launchs(
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                region VARCHAR(255), 
                category VARCHAR(255),
                to_date FLOAT,
                started_at FLOAT,
                done_at FLOAT
                )""")


def get_conn():
    return sqlite3.connect("state.db")


if __name__ == "__main__":
    args = parse_args()
    config.loadConfig(args.config)
    config.initLogger()
    conf = config.getConfig()

    try:
        if args.init:
            init()
        elif args.test:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(
                parse(loop)
            )
        else:
            loop = asyncio.get_event_loop()
            asyncio.ensure_future(start(loop, conf), loop=loop)
            app = web.Application()
            app.router.add_get('/', getStatus)
            web.run_app(app, host=conf['WEB_HOST'], port=conf['WEB_PORT'])
            loop.close()
    except:
        pass