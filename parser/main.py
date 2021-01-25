import asyncio
import logging
import logging.handlers
import math
from multiprocessing import Pool

import os
import sys
import functools
import json
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.realpath(os.path.join(__file__, ".."))))

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from datetime import datetime, timedelta
import json
import os

import config
import youla_parser as service_parser
import argparse
import aiohttp
from PIL import Image
import dateutil.parser

import monitoring

def default_json(obj):
    if isinstance(obj, datetime):
        return str(obj)
    return str(obj)


json_dumps = functools.partial(json.dumps, default=default_json)


logger = logging.getLogger('parser_main')

parser = argparse.ArgumentParser()
parser.add_argument(
    "city", help="City name. https://www.avito.ru/>tulskaya_oblast<", type=str)
parser.add_argument(
    "location_id", help="Location id", type=int)
parser.add_argument(
    "category", help="Category name. https://www.avito.ru/tulskaya_oblast/>avtomobili<", type=str)
parser.add_argument(
    "category_id", help="Category id", type=int)
parser.add_argument(
    "-c", "--config", help="Path to config", type=str, default="default.json")
parser.add_argument(
    "--pages", help="Maximum pages to parse. Default = 100", default=100, type=int)
parser.add_argument(
    "--date",
    help="Parsing end date (ISO 8601. 2018-08-15T15:38:41.887005). Default - one hour ago now",
    default=(datetime.now() - timedelta(minutes=60)).isoformat(), type=str)
parser.add_argument(
    "--workers",
    help="Workers count. Default 1", default=1, type=int)
parser.add_argument(
    "--test", action='store_true', help="Test application", default=False)

args = parser.parse_args()

end_date = dateutil.parser.parse(args.date)

CHUNK_SIZE = 10
WORKERS = args.workers


async def main(loop):
    token = await authenticate()
    if not token:
        return

    logger.info("main started")
    logger.info("Collect pages started")

    urls = service_parser.parseCategoryPage(args, end_date)
    logger.info("Links collected {}".format(len(urls)))

    if urls:
        logger.info("Found advs to import {}".format(len(urls)))
        chunk_limit = math.ceil(len(urls) / args.workers)
        chunks = [[i, urls[i * chunk_limit:(i + 1) * chunk_limit]] for i in range(args.workers)]

        service_parser.reset_auth_use()
        pool = Pool(args.workers)
        try:
            data = pool.map(page_parser, chunks)
        except:
            pool.close()
            return None

        started_at = datetime.now().timestamp() 
        launchs_id = None

        with get_conn() as conn:
            with conn as cursor: 
                cursor.execute(
                    "INSERT INTO launchs(region, category, to_date, started_at, done_at) VALUES(?, ?, ?, ?, ?)",
                    (args.city, args.category, 0, started_at, datetime.now().timestamp())
                )
                res = cursor.execute('SELECT last_insert_rowid()')
                row = res.fetchone()
                launchs_id = row[0]
                conn.commit()

        for idx, chunk in enumerate(data):
            try:
                if chunk:
                    chunk = sorted(chunk, key=lambda i: i['pub_date'])
                    await import_chunk(idx, chunk, token, launchs_id)
                    monitoring.parsed(len(chunk))
                    logger.info("Imported anns chunk {} with {} items".format(idx, len(chunk)))
                else:
                    logger.info("Import chunk {} is empty".format(idx))
            except:
                logger.exception("Import failed {}".format(idx))
                break
    else:
        logger.info("Nothing to import")


def page_parser(chunk):
    idx, urls = chunk
    logger.info("Page {} parser started".format(idx))

    try:
        parsed = service_parser.parseItemPages(urls)
        return parsed
    except:
        logger.exception("Page parsing failed. {}".format(urls))


async def authenticate():
    conf = config.getConfig()
    async with aiohttp.ClientSession() as session:
        data = {
            "login": "admin@stok.relabs.ru",
            "pwd": "EuTYSCL",
            "type": "backoffice"
        }
        async with session.post("{}/auth/login".format(conf["API"]), data=data) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data['data']['sid']
            logger.error("Private API authentication failed. {}".format(await resp.read()))
            return None


async def import_chunk(chunk_idx, chunk, token, launchs_id):
    for idx, item in enumerate(chunk):
        if await import_item(idx, chunk_idx, item, token):
            with get_conn() as conn:
                with conn as cursor: 
                    cursor.execute(
                        "UPDATE launchs SET to_date = ?, done_at = ? WHERE id = ? AND to_date < ?",
                        (
                            item['pub_date'].timestamp(), 
                            datetime.now().timestamp(), 
                            launchs_id, 
                            item['pub_date'].timestamp()
                        )
                    )
                    conn.commit() 


async def import_item(idx, chunk_idx, item, token):
    try:
        images = await download_images(idx, chunk_idx, item['images'])
        ann = await import_ann(item, token)
        if ann:
            await import_images(ann, images, token)
            return ann
    except Exception:
        logger.exception("Import failed")
    return None


async def import_ann(item, token):
    conf = config.getConfig()
    async with aiohttp.ClientSession() as session:
        comment = \
            item["comment"].strip().replace(
                "<br>", "\n"
            ).replace(
                "<br/>", "\n"
            )
        json = {
            "category_id": args.category_id,
            "address_id": args.location_id,
            "user_id": conf['USER_ID'],
            "price": item["price"] * 100,
            "title": item["title"],
            "comment": "{}\n{}\n{}".format(item["name"].strip(), item["phone"].strip(), comment),
            "state": "published",
            "pub_time": item["pub_date"].isoformat()
        }

        async with session.post("{}/api/v1/private/anns?_sid={}".format(conf["API"], token), json=json) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data["item"]
            logger.error("Ann not saved. {}".format(await resp.json()))
            return None


async def import_images(ann, images, token):
    conf = config.getConfig()
    result = []
    async with aiohttp.ClientSession() as session:
        for pos, image_path in enumerate(images):
            with open(image_path, 'rb') as image_fd:
                data = {
                    "user_id": str(conf['USER_ID']),
                    "link_type": "ann",
                    "link_id": str(ann["id"]),
                    "image": image_fd,
                    "en": "true",
                    "pos": str(pos + 1)
                }
                async with session.post("{}/api/v1/private/images?_sid={}".format(conf["API"], token), data=data) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        result.append(data)
                    else:
                        logger.error("Ann image not saved. {}".format(await resp.json()))
            os.unlink(image_path)
    return result


async def download_images(idx, chunk_idx, images):
    ret = []
    async with aiohttp.ClientSession() as session:
        for image_idx, image in enumerate(images):
            async with session.get(image) as resp:
                _, ext = os.path.basename(image).split(".", maxsplit=1)
                if resp.status == 200:
                    image_data = await resp.read()
                    path = os.path.join('/tmp', "{}_{}_{}.{}".format(chunk_idx, idx, image_idx, ext))
                    with open(path, "wb+") as fd:
                        fd.write(image_data)
                    im = Image.open(path)
                    w, h = im.size
                    im.crop((0, 0, w, h - 40)).save(path)
                    ret.append(path)
    return ret


def get_conn():
    return sqlite3.connect("state.db")


if __name__ == "__main__":
    config.loadConfig(args.config)
    config.initLogger()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))

