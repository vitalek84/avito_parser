# -*- coding: utf-8 -*-
import csv
import json
import logging
import sys
import argparse
import os

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


def file_reader(current_path, file_obj):
    text = file_obj.read()
    try:
        data = [
            [r["phone"], r["name"], r["url"]] for r in json.loads(text)]
        csv_writer(
            data,
            os.path.join(current_path + "/" + "data.csv")
        )
    except Exception as e:
        logger.error("csv phone creator error {}".format(e))
        raise e


def csv_writer(data, path):
    with open(path, "a", newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for line in data:
            writer.writerow(line)


def main(folder_name):
    current_path = os.path.dirname(
        os.path.realpath(os.path.join(__file__)))
    data_path = current_path + '/' + folder_name
    try:
        files = os.listdir(data_path)
    except Exception as e:
        logger.error("Bad path directory, e: {}".format(e))
    if not files:
        logger.error("csv phone creator, No files!")
        exit()
    logger.info('files: {}'.format(len(files)))
    for f in files:
        with open(os.path.join(data_path + "/" + f), "r") as f_obj:
            file_reader(data_path, f_obj)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-data_folder_name", help="Path to json files folder", type=str)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    logger.info('{}'.format(args.data_folder_name))
    main(args.data_folder_name)
