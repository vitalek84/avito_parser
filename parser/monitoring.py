import os
import logging
import time
import config
import requests


logger = logging.getLogger(__name__)


def timeout(ip):
    send("proxy_timeout", 1, tags={'ip': ip})


def connection_error(ip):
    send("proxy_connection_error", 1, tags={'ip': ip})


def missing_node(xpath):
    send("selenium_missing_node", 1, tags={'path': xpath})


def other():
    send("other", 1)


def exception():
    send("exception", 1)


def parsed(count):
    send("parsed", count)


def send(key, value, tags=None):
    try:
        if tags is None:
            tags = {}
        conf = config.getConfig()
        influxdb_api = conf.get('INFLUXDB_API', None)
        if influxdb_api:
            hostname = os.uname()[1]
            tags['hostname'] = hostname
            data = "{},{} value={} {}".format(
                key, 
                ",".join(["{}={}".format(k, v) for k, v in tags.items()]),
                value,
                str(int(time.time() * 1000000000))
            )
            requests.post(influxdb_api, data)
    except:
        logger.exception('Unable to send metrics')
