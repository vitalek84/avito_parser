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


logger = logging.getLogger(__name__)


def parseCategoryPage(args, end_date):
    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Firefox(firefox_options=options)

    try:
        page = 1
        urls = []

        while True:
            logger.info("Parse links from main page {}/{} to date {}".format(page, args.pages, end_date))

            url = page_url(args, page)
            logger.info("Fetching page {}".format(url))
            driver.get(url)

            if is_empty_page(driver, url):
                break

            page_urls = [i for i in parse_url_date(driver) if i[1] > end_date]
            urls += page_urls
            if not page_urls:
                logging.info("There is nothing to import from {}".format(url))
                break

            page += 1
            if args.pages and page > args.pages:
                logging.info("Maximum page limit reached {}".format(page))
                break

        return urls
    finally:
        driver.quit()


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
    for el in driver.find_elements(By.XPATH, "//div[contains(@class,'item_table_extended')]"):
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


def parseItemPages(urls):
    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Firefox(firefox_options=options)

    try:
        parsed = []
        for url, pub_date in urls:
            i = parseItemPage(driver, url, pub_date)
            if i:
                parsed.append(i)
        return parsed
    finally:
        driver.close()


def parseItemPage(driver, url, pub_date):
    try:
        driver.get(url)

        item_name = driver.find_element(By.CLASS_NAME, "title-info-title-text").text
        item_cost = parse_cost(driver, url)
        if item_cost is None:
            return None

        item_description = parse_description(driver, url)
        if item_description is None:
            return None

        item_address = parse_address(driver, url)
        if item_address is None:
            return None

        item_image_urls = [
            el.get_attribute("src") for el in driver.find_elements(By.XPATH, "//div[contains(@class, 'gallery-imgs-container')]/div/div/img")
        ]

        item_category = [
            el.text for el in driver.find_elements(By.XPATH, "//div[contains(@class, 'breadcrumbs')]/a[position()>1]")
        ]

        user_name = driver.find_element(By.XPATH, "//div[@class='seller-info-name']").text

        phone_button = driver.find_element(By.XPATH, "//div[contains(@class,'item-phone-number')]")
        phone_button.click()
        time.sleep(1)
        user_phone = recognizer.base64_image_to_text(
            driver.find_element(By.XPATH, "//div[contains(@class,'item-phone')]/img").get_attribute("src")
        )

        return {
            'pub_date': pub_date,
            'phone': user_phone,
            'name': user_name,
            'title': item_name,
            'comment': item_description,
            'price': item_cost,
            'location': item_address,
            'images': item_image_urls,
            'category': item_category,
            'url': url
        }
    except:
        logger.exception("Page {} parsing failed".format(url))


def parse_cost(driver, url):
    try:
        return int(driver.find_element(By.CLASS_NAME, "js-item-price").get_attribute("content"))
    except NoSuchElementException as e:
        logger.info("Adv at page {} has no price".format(url))
        return 0
    except Exception as e:
        logger.exception("Failed to parse cost at {}".format(url))
        return None


def parse_description(driver, url):
    try:
        try:
            return driver.find_element(By.CLASS_NAME, "item-description-html").text
        except NoSuchElementException:
            return driver.find_element(By.CLASS_NAME, "item-description-text").text
    except NoSuchElementException:
        logger.info("Adv at page {} has no description".format(url))
        return ""
    except Exception as e:
        logger.exception("Failed to parse description at {}".format(url))
        return None


def parse_address(driver, url):
    try:
        a1 = driver.find_element(By.XPATH, "//div[@class='item-map-location']/span[@itemprop='name']").text
        return [a1] + driver.find_element(
            By.XPATH,
            "//div[@class='item-map-location']/span[@class='item-map-address']/span"
        ).text.split(", ")
    except NoSuchElementException as e:
        logger.info("Adv at page {} has no address".format(url))
        return None
    except Exception as e:
        logger.exception("Failed to parse address")
        return None


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
