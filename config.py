import json
import logging
import sys

from rfc5424logging import Rfc5424SysLogHandler

CONFIG = {}


def loadConfig(path):
    global CONFIG
    file = open(path)
    data = json.load(file)
    CONFIG = data
    print("Config loaded: {}".format(CONFIG))
    required_fields = [
        "PARSE",
        "PYTHON_COMMAND",
        "TESSERACT_COMMAND",
        "WEB_HOST",
        "WEB_PORT",
        "API",
        "USER_ID",
        "TRANSLATE_TOKEN",
        "PHONE_TOKEN",
        "AUTH_DB"
    ]
    for field in required_fields:
        if not field in CONFIG:
            raise Exception("Can't load {} in config {} file.".format(field, path))


def getConfig():
    return CONFIG


def initLogger():
    conf = getConfig()
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    if conf.get('SYSLOG', None):
        address = (conf['SYSLOG']['host'], conf['SYSLOG']['port'])
        logging.info('Connecting to syslog {}'.format(address))
        root_logger = logging.getLogger()
        syslog_handler = Rfc5424SysLogHandler(address=address)
        root_logger.addHandler(syslog_handler)