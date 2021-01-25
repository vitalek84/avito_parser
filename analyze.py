# -*- coding: utf-8 -*-

import asyncio
import argparse
import aiohttp
import datetime
from dateutil.parser import parse as date_parse
import math


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("servers", metavar='N', help="Server urls", nargs='+', type=str)
    parser.add_argument("-l", "--limit", help="Data limit", type=int, default=10)
    parser.add_argument("-v", "--verbose", help="Show verbose", action='store_true', default=False)
    return parser.parse_args()


async def stats(args):
    for server in args.servers:
        print("Server {}".format(server))
        data = await get_status(server, args.limit)
        if data is None:
            return

        grouped = await group_data(data)

        await show_summary(grouped, args)
        await show_duration(grouped, args)


async def show_summary(grouped, args):
    print("Regions {}".format(len(grouped)))
    categories = []
    for i in grouped.values():
        categories += i.keys()
    categories = set(categories)
    print("Categories {}".format(len(categories)))


async def show_duration(grouped, args):
    avg_duration = {}
    max_duration = {}
    min_duration = {}
    for region, categories in grouped.items():
        avg_duration[region] = {}
        max_duration[region] = {}
        min_duration[region] = {}

        for category, l in categories.items():
            avg_duration[region][category] = datetime.timedelta(seconds=sum([i['duration'].seconds for i in l]) / len(l))
            max_duration[region][category] = datetime.timedelta(seconds=max([i['duration'].seconds for i in l]))
            min_duration[region][category] = datetime.timedelta(seconds=min([i['duration'].seconds for i in l]))

        avg_duration[region]['_'] = datetime.timedelta(
            seconds=sum([i.seconds for i in avg_duration[region].values()])
        )
        max_duration[region]['_'] = datetime.timedelta(
            seconds=sum([i.seconds for i in max_duration[region].values()])
        )
        min_duration[region]['_'] = datetime.timedelta(
            seconds=sum([i.seconds for i in min_duration[region].values()])
        )

    for region in sorted(avg_duration):
        print("{} ({} / {} / {})".format(
            region, min_duration[region]['_'], avg_duration[region]['_'], max_duration[region]['_'])
        )
        categories = avg_duration[region]
        for category in reversed(sorted(categories, key=lambda key: categories[key])):
            if category == '_':
                continue

            print("\t{} ({} / {} / {})".format(
                category, min_duration[region][category], avg_duration[region][category], max_duration[region][category])
            )
            if args.verbose:
                for i in grouped[region][category]:
                    print("\t\tAt {started_at} - {duration}".format(**i))


async def group_data(data):
    grouped = {}
    for i in data:
        if i['done_at'] == 0:
            continue

        region, category = i['region'], i['category']
        if region not in grouped:
            grouped[region] = {}
        if category not in grouped[region]:
            grouped[region][category] = []

        i['started_at'] = date_parse(i["started_at"])
        i['done_at'] = date_parse(i["done_at"])
        i['duration'] = i["done_at"] - i["started_at"]
        grouped[region][category].append(i)
    return grouped


async def get_status(url, limit=10):
    async with aiohttp.ClientSession() as session:
        async with session.get("{}/?limit={}".format(url, limit)) as resp:
            if resp.status == 200:
                return await resp.json()
            print("Response code is {}".format(resp.status))
            return None

if __name__ == "__main__":
    args = parse_args()

    asyncio.get_event_loop().run_until_complete(stats(args))