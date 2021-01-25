import logging

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime, timedelta
import time
import phone_recognizer as recognizer
import pytesseract
import re
import requests


logger = logging.getLogger(__name__)


def parseCategoryPage(args, f):    
    count = 0
    page = 1
    urls = []
    retry = 3

    while True:
        proxy = get_proxy()

        options = Options()
        options.add_argument("--headless")
        
        profile = webdriver.FirefoxProfile()
        driver = webdriver.Firefox(
            firefox_options=options, firefox_profile=profile, proxy=proxy
        )

        logger.info("Parse links from main page {}/{}".format(page, args.pages))

        url = page_url(args, page)
        logger.info("Fetching page {}".format(url))
        try:
            driver.get(url)
            retry = 3
            if is_empty_page(driver, url):
                break

            page_urls = [i for i in parse_url_date(driver)]
            count += len(page_urls)
            for url in page_urls:
                f.write(url[0] + "\n")
            if not page_urls:
                logging.info("There is nothing to import from {}".format(url))
                break

            page += 1
            if args.pages and page > args.pages:
                logging.info("Maximum page limit reached {}".format(page))
                break
            driver.close()
        except:
            if retry != 0:
                retry -= 1
                continue   
            raise      

    return count


def page_url(args, page):
    return "https://www.avito.ru/%s/%s?p=%d&s=104" % (args.city, args.category, page)


def is_empty_page(driver, url):
    try:
        if driver.find_element(By.CLASS_NAME, "nulus__header") == "По вашему запросу ничего не найдено":
            logger.info("Can't get page {}. Probably last page received".format(url))
            return True
    except Exception as e:
        return False


def parse_url_date(driver):
    urls = []
    for el in driver.find_elements(By.XPATH, "//div[contains(@class,'js-item-extended')]"):
        try:
            el.find_element(By.CLASS_NAME, "vas-applied_bottom")
            continue
        except Exception as e:
            pass

        url_el = el.find_element(By.TAG_NAME, "a")
        date_el = el.find_element(By.CLASS_NAME, "js-item-date")
        date = parseAvitoDate(date_el.get_attribute("data-absolute-date"))

        if date is None:
            logger.error("Date parsing fail {}".format(date_el.get_attribute("data-absolute-date")))
            continue

        urls.append((
            url_el.get_attribute("href"),
            date
        ))
    return urls


def parseItemPages(urls, tesseract_cmd):
    proxy = get_proxy()

    options = Options()
    options.add_argument("--headless")
    
    profile = webdriver.FirefoxProfile()
    driver = webdriver.Firefox(
        firefox_options=options, firefox_profile=profile, proxy=proxy
    )

    try:
        parsed = []
        for url in urls:
            i = parseItemPage(driver, url, tesseract_cmd)
            if i:
                parsed.append(i)
        return parsed
    finally:
        driver.close()


def parseItemPage(driver, url, tesseract_cmd):
    try:
        driver.get(url)

        user_name = driver.find_element(By.XPATH, "//div[contains(@class,'seller-info-name')]").text

        phone_button = driver.find_element(By.XPATH, "//div[contains(@class,'item-phone-number')]")
        phone_button.click()
        time.sleep(1)
        user_phone = recognizer.base64_image_to_text(
            driver.find_element(By.XPATH, "//div[contains(@class,'item-phone')]/img").get_attribute("src"),
            tesseract_cmd
        )

        return {
            'phone': user_phone,
            'name': user_name,
            'url': url
        }
    except:
        logger.exception("Page {} parsing failed".format(url))


def parseAvitoDate(date_text):
    date_text = date_text.strip().replace("\xa0", " ")
    splitted = date_text.split(" ")
    # Сегодня
    try:
        if splitted[0] == "Сегодня":
            time = parseTime(splitted[1])
            return datetime.today().replace(hour=time[0], minute=time[1], second=0, microsecond=0)
        # Вчера
        elif splitted[0] == "Вчера":
            time = parseTime(splitted[1])
            return datetime.today().replace(hour=time[0], minute=time[1], second=0, microsecond=0) - timedelta(days=1)
        # Число Месяц
        else:
            time = parseTime(splitted[2])
            day = int(splitted[0].strip())
            month = parseMonth(splitted[1])
            if month == None:
                logger.error("Date month not found {}, {}".format(date_text, splitted))
                return None

            return datetime.today().replace(month=month, day=day, hour=time[0], minute=time[1], second=0, microsecond=0)
    except:
        logger.exception("Parse date error {}, {}".format(date_text, splitted))
    return None


def parseTime(time_text):
    pattern = re.compile(r"^(([01]\d|2[0-3]):([0-5]\d)|24:00)$")
    t = pattern.match(time_text.strip())
    return int(t.group(2)), int(t.group(3))


def parseMonth(month_text):
    months = [
        'января',
        'февраля',
        'марта',
        'апреля',
        'мая',
        'июня',
        'июля',
        'августа',
        'сентября',
        'октября',
        'декабря'
    ]
    month_text = month_text.strip()
    for k, month_pattern in enumerate(months):
        if month_text == month_pattern:
            return k + 1
    return None

def get_proxy():
    retries = 3
    while retries:
        try:
            response = requests.get('http://10.77.105.240/')
            try:
                data = response.json()
                logger.info("Using proxy: {}:{}".format(data['host'], data['port']))
                host_port = "{}:{}".format(data['host'], data['port'])
                proxy = Proxy()
                proxy.proxy_type = ProxyType.MANUAL
                proxy.http_proxy = host_port
                proxy.socks_proxy = host_port
                proxy.ssl_proxy = host_port
                proxy.socksUsername = data.get('username', None)
                proxy.socksPassword = data.get('password', None)
                return proxy
            except:
                logger.exception("Cant parse proxy response {}".format(response.text))
                retries -= 1
        except:
            logger.exception("Cant get proxy")
            retries -= 1
    raise RuntimeError("Proxy not found")