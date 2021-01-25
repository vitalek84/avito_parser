import asyncio
import logging
import logging.handlers
import math
from multiprocessing import Pool

import os
import sys
import functools
import json

sys.path.insert(0, os.path.dirname(os.path.realpath(os.path.join(__file__, ".."))))

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from datetime import datetime, timedelta
import json
import os

import config
import avito_phone_parser as service_parser
import argparse
import aiohttp
from PIL import Image
import dateutil.parser


def default_json(obj):
    if isinstance(obj, datetime):
        return str(obj)
    return str(obj)



json_dumps = functools.partial(json.dumps, default=default_json)


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(
    logging.handlers.RotatingFileHandler('parser.log', 'a', 10 * 1024 * 1024, 5)
)

parser = argparse.ArgumentParser()
parser.add_argument("city", help="City name. https://www.avito.ru/>tulskaya_oblast<", type=str)
parser.add_argument("category", help="Category name. https://www.avito.ru/tulskaya_oblast/>avtomobili<", type=str)
parser.add_argument("-c", "--config", help="Path to config", type=str, default="default.json")
parser.add_argument("--pages", help="Maximum pages to parse. Default = 100", default=100, type=int)
parser.add_argument("--path",
                    help="Path to reports folder. Default $city_$category", type=str)
parser.add_argument("--workers",
                    help="Workers count. Default 1", default=1, type=int)
parser.add_argument("--test", action='store_true', help="Test application", default=False)
parser.add_argument("--chunk_size", help="Set data chunk size", default=10, type=int)
parser.add_argument("--link_tmp", help="Path to temp links file", default="links.tmp", type=str)

args = parser.parse_args()


folder = str(args.city) + "-" + str(args.category)

if args.path:
    folder = args.path

if not os.path.exists(folder):
    os.makedirs(folder)
if os.path.exists(args.link_tmp):
    os.unlink(args.link_tmp)

CHUNK_SIZE = args.chunk_size
WORKERS = args.workers


async def main(loop):

    logger.info("main started")
    logger.info("parseCategoryPage started; Chunk size: {}".format(CHUNK_SIZE))

    links_file = open(args.link_tmp, "w+")
    urls_count = service_parser.parseCategoryPage(args, links_file)
    logger.info("Links collected {}".format(urls_count))
    tesseract_cmd = config.getConfig()['TESSERACT_COMMAND']
    links_file.seek(0,0)
    if urls_count > 0:
        total_picked = 0
        logger.info("Found advs to import {}".format(urls_count))
        chunk_limit = min(CHUNK_SIZE, math.ceil(urls_count / args.workers))
        total_chunks = 0
        while True:
            urls = pickUrls(links_file, chunk_limit*args.workers)
            if len(urls) == 0:
                break
            total_picked += len(urls)
            logger.info("Import {}/{}".format(total_picked, urls_count))
            chunk_cur_limit = min(CHUNK_SIZE, math.ceil(len(urls) / args.workers))
            chunks = [[total_chunks+i, tesseract_cmd, urls[i * chunk_cur_limit:(i + 1) * chunk_cur_limit]] for i in range(args.workers)]
            total_chunks += len(chunks)
            pool = Pool(args.workers)
            data = pool.map(page_parser, chunks)
    else:
        logger.info("Nothing to import")

    links_file.close()


def pickUrls(file, count):
    urls = []
    for i in range(0, count):
        url = pickUrl(file)
        if url == None:
            return urls
        urls.append(url)
    return urls


def pickUrl(file):
    url = file.readline()
    if not url:
        return None
    return url

def page_parser(chunk):
    idx, tesseract_cmd, urls = chunk
    logger.info("Page {} parser started".format(idx))

    try:
        parsed = service_parser.parseItemPages(urls, tesseract_cmd)
        flush_data_to_file(parsed, idx)
        return parsed
    except:
        logger.exception("Page parsing failed. {}".format(urls))


def flush_data_to_file(data, chunk):
    path = "%s/%06d.json" % (folder, chunk)
    with open(path, "w+") as fd:
        fd.write(json_dumps(data))

if __name__ == "__main__":
    config.loadConfig(args.config)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))

