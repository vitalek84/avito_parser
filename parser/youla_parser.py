import logging
import logging.handlers
import random

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import time
import phone_recognizer as recognizer
import pytesseract
import re
import random
import string
import json

import urllib
import requests
import psycopg2
from bs4 import BeautifulSoup
import config

# from google.cloud import translate
from google.api_core.exceptions import Forbidden

import monitoring

USES_COUNT = 10

logger = logging.getLogger(__name__)

# translate_client = translate.Client()
# from google.cloud import translate_v3beta1 as translate
# translate_client = translate.TranslationServiceClient()


def parseItemPages(urls):
    proxy = get_proxy()

    options = Options()
    options.add_argument("--headless")

    profile = webdriver.FirefoxProfile()
    driver = webdriver.Firefox(
        firefox_options=options, firefox_profile=profile, proxy=proxy
    )

    try:
        parsed = []
        for url, pub_date in urls:
            i = parseItemPage(driver, url, pub_date)
            if i:
                parsed.append(i)
        return parsed
    finally:
        driver.quit()


def parseItemPage(driver, url, pub_date):
    auth = None
    try:
        auth = get_page_with_auth(driver, url)
        if not auth:
            return None
        item_name = parse_name(driver)
        if not item_name:
            return None

        item_cost = parse_cost(driver, url)
        if item_cost is None:
            return None

        item_description = parse_description(driver, url)
        if item_description is None:
            return None

        item_description = yandex_translate(item_description, url)

        item_address = parse_address(driver, url)

        item_image_urls = [
            el.get_attribute("src") for el in driver.find_elements(By.XPATH, "//div[@data-test-component='ProductGallery']//img[@width]")
        ]
        item_image_urls = list(set(item_image_urls))

        item_category = [
            el.text for el in driver.find_elements(By.XPATH, "//ul[@data-test-component='Breadcrumbs']/li[position()>1]")
        ]

        username = parse_username(driver)
        if username is None:
            return None        

        userphone = parse_userphone(driver)
        if userphone is None:
            return None        

        decrement_auth_use(auth['id'])

        return {
            'pub_date': pub_date,
            'phone': userphone,
            'name': username,
            'title': item_name,
            'comment': item_description,
            'price': item_cost,
            'location': item_address,
            'images': item_image_urls,
            'category': item_category,
            'url': url
        }
    except:
        monitoring.exception()
        logger.exception("Page {} parsing failed".format(url))
        driver.save_screenshot('exception.png')
        if auth:
            decrement_auth_use(auth['id']) 


def reset_auth_use():
    conf = config.getConfig()
    if conf.get('RESET_AUTH_USE', False):
        db_auth = psycopg2.connect(conf["AUTH_DB"])
        with db_auth.cursor() as cursor: 
            cursor.execute("UPDATE json_auth SET uses = 0")
            db_auth.commit()


def get_free_auth():
    conf = config.getConfig()
    db_auth = psycopg2.connect(conf["AUTH_DB"])
    with db_auth.cursor() as cursor:
        cursor.execute(
            """WITH cte AS (
                SELECT id          
                FROM   json_auth
                WHERE  status = 1 and uses < {USES_COUNT}
                ORDER by uses desc
                LIMIT  1                  
                )
            UPDATE json_auth s
            SET uses = uses + 1 
            FROM cte
            WHERE s.id = cte.id
            RETURNING s.id, row""".format(
                USES_COUNT=USES_COUNT
                )
           )
        db_auth.commit()
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "auth": row[1]
            }
    return None


def random_name():
    name = "Мария"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Host": "farium.ru",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36"
    }
    r = requests.get(
        "http://farium.ru/random/generate?time=1564343667076&arg1={}&arg2=18&type=name".format(
            random.randint(0, 1)), headers=headers)
    if r.status_code == 200:
        name = r.json().get("content", "Серега")
    name = name.replace("\r", "")
    name = name.replace("\n", "")
    return name


def registrate(number, driver, state_url):
    wait = WebDriverWait(driver, 30)
    login_url = "https://youla.ru/"
    xpath_enter = "//section[1]/div[1]/div[1]/div[3]/a[1]"
    xpath_by_phone = "button.auth_group_button"
    xpath_input_phone = "//form[@class='auth_group__form']/div[1]/div[1]/div[2]/input[1]"
    xpath_input_phone_button = "//form[@class='auth_group__form']/div[3]/button[1]"
    name = random_name()
    last_name = random.choice(string.ascii_uppercase)
    driver.get(login_url)
    enter = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_enter)))
    enter.click()
    by_phone = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, xpath_by_phone)))
    by_phone.click()
    input_phone = wait.until(EC.presence_of_element_located((By.XPATH, xpath_input_phone)))
    if number.startswith("7") or number.startswith("8"):
        number = number[1:]
    elif number.startswith("+7"):
        number = number[2:]
    input_phone.send_keys(number)
    time.sleep(2)
    input_phone_button = driver.find_element(
        By.XPATH, xpath_input_phone_button)
    input_phone_button.click()
    code = confirmation_code(state_url, timeout=5, retry=5)
    if not code:
        logger.error(
            "Confirmation code not present."
        ) 
        return None

    input_code = driver.find_element(By.NAME, "code")
    input_code.send_keys(code)
    time.sleep(3)
    input_code_button = driver.find_element(
        By.XPATH, "//button[@data-test-action='CodeConfirmClick']")
    input_code_button.click()
    time.sleep(3)

    reg_name_input = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//form[@class='auth_group__form']/div[1]/div[2]/div[1]/input[1]")))
    reg_name_input.send_keys(name)
    reg_last_name_input = driver.find_element(
        By.XPATH, "//form[@class='auth_group__form']/div[1]/div[2]/div[2]/input[1]")
    reg_last_name_input.send_keys(last_name)
    reg_button_enter = driver.find_element(
        By.XPATH, "//form[@class='auth_group__form']/button[1]")
    reg_button_enter.click()

    auth = driver.get_cookies()
    if not [x for x in auth or [] if x["name"] == 'youla_auth_refresh']:
        time.sleep(5)
        driver.get(login_url)
        auth = driver.get_cookies()

    return auth


def confirmation_code(state_url, timeout, retry):
    conf = config.getConfig()
    while retry:        
        r = requests.get(
            state_url, 
            headers={"Authorization": "Bearer {}".format(conf["PHONE_TOKEN"])})
        if r.status_code == 200:
            sms = r.json().get("sms")
            if sms:
                code = sms[0].get("code")
                if code:
                    return code
            else:
               logger.debug(
                    "Confirmation code not present in body at ['sms'][0]['code']. Body: {}".format(
                    r.text)
                ) 
        else:
            logger.debug(
                "Confirmation code not fetched. Status: {}, Body: {}".format(
                r.status_code, r.text)
            )   

        retry = retry - 1
        time.sleep(timeout)
    
    logger.error(
        "Confirmation code not fetched. {}".format(
        state_url)
    ) 
    return None


def create_new_auth(driver):
    auth = None
    get_num = "https://5sim.net/v1/user/buy/activation/russia/any/youla"
    get_state = "https://5sim.net/v1/user/check/{id_code}"
    conf = config.getConfig()
    r = requests.get(get_num, 
        headers={"Authorization": "Bearer {}".format(conf["PHONE_TOKEN"])}
    )
    if r.status_code == 200:
        body = r.json()
        id_code = body.get("id")
        number = body.get("phone")
        if id_code and number:
            state_url = get_state.format(id_code=id_code)
            auth = registrate(number, driver, state_url)
            if not auth:
                logger.error(
                    "Authentication failed. Phone: {}, id: {}".format(
                    number, id_code)
                )
            else:
                logger.debug(
                    "Authentication success. Phone: {}, id: {}".format(
                    number, id_code)
                )
        else:
            logger.error(
                "Registration phone or task id not avaliable. Phone: {}, id: {}".format(
                number, id_code)
            )
    else:
        logger.error(
            "Auth code not fetched. Status: {}, Body: {}".format(
            r.status_code, r.text)
        )
    return auth


def get_page_with_auth(driver, url):
    conf = config.getConfig()
    db_auth = psycopg2.connect(conf["AUTH_DB"])
    auth = get_free_auth()
    if not auth:
        auth = create_new_auth(driver)
        if auth and [x for x in auth or [] if x["name"] == 'youla_auth_refresh']:
            with db_auth.cursor() as cursor:
                row = json.dumps(auth)
                cursor.execute(
                    "insert into json_auth (row, uses) values (%s, 0) RETURNING id, row", (row, )
                )
                db_auth.commit()
                auth =  get_free_auth()
        else:
            logger.error(
                "Parser can\'t get auth, url:{}".format(url))
            return None
    driver.get(url)
    for a in auth['auth']:
        driver.add_cookie(a)
    driver.get(url)
    try:
        s = driver.find_element(By.XPATH, "//section[1]/div[1]/div[1]/div[3]/a[1]/span[1]")
        if s.text == 'Войти':
            logger.error("Auth token expired {}".format(auth['id']))
            with db_auth.cursor() as cursor:
                cursor.execute(
                    "update json_auth set status = 0 where id = %s", (auth['id'],)
                 )
                db_auth.commit()
                return None
        return auth
    except NoSuchElementException:
        return auth
    except Exception:
        logger.exception("Authentication failed")
        return None


def parseCategoryPage(args, end_date):
    page = 1
    urls = []
    serpId = ""

    while True:
        logger.info("Parse links from main page {}/{} to date {}".format(page, args.pages, end_date))

        url = page_url(args, page, serpId)
        logger.info("Fetching page {}".format(url))

        data = request_category(url)
        if page == 1:
            serpId = data["serpId"]

        if is_empty_page(data):
            break

        page_urls = [i for i in parse_url_date(data) if i[1] > end_date]

        urls += page_urls
        if not page_urls:
            logger.info("There is nothing to import from {}".format(url))
            break

        page += 1
        if args.pages and page > args.pages:
            logger.info("Maximum page limit reached {}".format(page))
            break

    return urls


def request_category(url):
    retries = 3
    while retries:
        proxy = get_proxy()
        auth = ""
        if proxy.socksUsername and proxy.socksPassword:
            auth = "{}:{}@".format(proxy.socksUsername, proxy.socksPassword)
        try:
            return requests.get(url, proxies={
                'http': 'https://{}{}'.format(auth, proxy.http_proxy),
                'https': 'https://{}{}'.format(auth, proxy.ssl_proxy)
            }, timeout=10).json()
        except (requests.ConnectTimeout, requests.ReadTimeout, requests.Timeout) as e:
            logger.error(
                "Connection timeout to url [{}] over proxy {}".format(
                    url, proxy.http_proxy))
            monitoring.timeout(proxy.http_proxy)
        except (requests.ConnectionError, requests.HTTPError) as e:
            logger.error(
                "Connection error to url [{}] over proxy {}".format(
                    url, proxy.http_proxy))
            monitoring.connection_error(proxy.http_proxy)
        except Exception as e:
            logger.exception("Cant get category")
            monitoring.exception()
        retries -= 1
    monitoring.exception()
    raise RuntimeError("Cant get working proxy")


def page_url(args, page, serpId):
    return "https://youla.ru/web-api/products?attributes[sort_field]=date_published&cId=%s&city=%s&page=%d&serpId=%s" % (args.category, args.city, page, serpId)


def is_empty_page(data):
    try:
        if "error" in data:
            return True
    except Exception:
        return False


def parse_url_date(data):
    soup = BeautifulSoup(data["html"], 'html.parser')

    urls = []
    for el in soup.find_all("li"):
        url = el.a['href']
        date_unparsed = el.figcaption.find_all('div', {"class": "product_item__date"})[0].span.text

        date = parseYoulaDate(date_unparsed)
        if date is None:
            logger.error("Date parsing fail {}".format(date_unparsed))
            monitoring.other()
            continue

        urls.append((
            "https://youla.ru"+url,
            date
        ))
    return urls


def yandex_translate(row, url):
    res = None
    try:
        en_text = yandex_cust_translate(row)
        if en_text:
            res = yandex_cust_translate(en_text, lang="en-ru")
    except Exception:
        logger.exception(
            "Translate body failed, url {}".format(url))
    return res


def yandex_cust_translate(row, lang="ru-en"):
    conf = config.getConfig()
    res = None
    url = "https://translate.yandex.net/api/v1.5/tr.json/translate"
    url = '?'.join([
        url, urllib.parse.urlencode(
            {
                "key": conf["TRANSLATE_TOKEN"],
                "text": row,
                "lang": lang
            })])
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data and data.get("code", None) == 200 and data.get("text", None):
            res = data["text"][0]
        else:
            logger.error(
                "Bad format answer, data: {}, row: {}".format(
                    data, row))
    else:
        logger.error(
            "can\'t get translate data, row: {}".format(
                row))
    return res

            
def decrement_auth_use(auth_id):
    conf = config.getConfig()
    db_auth = psycopg2.connect(conf["AUTH_DB"])
    with db_auth.cursor() as cursor:
        cursor.execute(
            "update json_auth set uses = uses - 1 where id = %s", (auth_id,)
        )
        db_auth.commit()


def parse_name(driver):
    xpath = "//section[1]/div[1]/div[1]/div[1]/div[1]/h2[1]"
    try:
        node = driver.find_element(By.XPATH, xpath)
        return node.text
    except NoSuchElementException:
        logger.error("Unable to find adv name by xpath {}".format(xpath))
        monitoring.missing_node(xpath)
    except:
        monitoring.exception()
        logger.exception("Unable to find adv name")
    return None

def parse_username(driver):
    xpath = "//a[@data-test-component='UserNameClick']"
    try:
        node = driver.find_element(By.XPATH, xpath)
        return node.text.split("(")[0]
    except NoSuchElementException:
        logger.error("Unable to find username by xpath {}".format(xpath))
        monitoring.missing_node(xpath)
    except:
        monitoring.exception()
        logger.exception("Unable to find username")
    return None


def parse_userphone(driver):
    xpath = "//button[@data-test-action='PhoneNumberClick']"
    try:
        node = driver.find_element(By.XPATH, xpath)
        node.click()
        time.sleep(1)
        xpath = "//div[@data-test-component='ProductPhoneNumberModal']/div/div/a[starts-with(@href, 'tel:')]"
        node = driver.find_element(By.XPATH, xpath)
        return node.text
    except NoSuchElementException:
        logger.error("Unable to find user phone by xpath {}".format(xpath))
        monitoring.missing_node(xpath)
    except:
        monitoring.exception()
        logger.exception("Unable to find user phone")
    return None


def parse_cost(driver, url):
    xpath = "//div[@data-test-component='ProductSidebar']/div/h3/span[@data-test-component='Price']"
    try:
        cost_text = driver.find_element(By.XPATH, xpath).text.split(" ")[0]
        cost_text = cost_text.replace("\u205f", "")
        if cost_text.lower() == "бесплатно":
            return 0
        return int(cost_text)
    except NoSuchElementException:
        logger.error("Unable to find price by xpath {}".format(xpath))
        monitoring.missing_node(xpath)
        return 0
    except Exception:
        logger.exception("Failed to parse cost at {}".format(url))
        monitoring.other()
        return None


def parse_description(driver, url):
    xpath = "//dl[@data-test-component='DescriptionList']/dd"
    try:
        return driver.find_element(By.XPATH, xpath).text
    except NoSuchElementException:
        logger.error("Unable to find description by xpath {}".format(xpath))
        monitoring.missing_node(xpath)
        return ""
    except Exception:
        logger.exception("Failed to parse description at {}".format(url))
        monitoring.other()
        return None


def parse_address(driver, url):
    xpath = "//li[@data-test-component='ProductMap']/dd/div/div/span"
    try:
        node = driver.find_elements(By.XPATH, xpath)
        if len(node) == 0:
            monitoring.missing_node(xpath)
            logger.error("Unable to find address by xpath {}".format(xpath))
            return None
        return [node[0].text]
    except NoSuchElementException:
        monitoring.missing_node(xpath)
        logger.error("Unable to find address by xpath {}".format(xpath))
        return None
    except Exception:
        logger.exception("Failed to parse address")
        monitoring.other()
        return None


def parseYoulaDate(date_text):
    date_text = date_text.strip().replace("\xa0", " ")
    splitted = date_text.split(" ")
    # Сегодня
    try:
        if splitted[0] == "сегодня":
            time = parseTime(splitted[2])
            return datetime.today().replace(hour=time[0], minute=time[1], second=0, microsecond=0)
        # Вчера
        elif splitted[0] == "вчера":
            time = parseTime(splitted[2])
            return datetime.today().replace(hour=time[0], minute=time[1], second=0, microsecond=0) - timedelta(days=1)
        # Число Месяц
        else:
            day = int(splitted[0].strip())
            month = parseMonth(splitted[1])
            if month == None:
                logger.error("Date month not found {}, {}".format(date_text, splitted))
                return None

            return datetime.today().replace(month=month, day=day, hour=0, minute=0, second=0, microsecond=0)
    except:
        logger.exception("Parse date error {}, {}".format(date_text, splitted))
        monitoring.other()
    return None


def parseTime(time_text):
    pattern = re.compile(r"^(([01]?\d|2[0-3]):([0-5]\d)|24:00)$")
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
        'ноября',
        'декабря'
    ]
    month_text = month_text.strip()
    for k, month_pattern in enumerate(months):
        if month_text == month_pattern:
            return k + 1
    return None


def get_proxy():
    conf = config.getConfig()
    if conf.get('PROXY_LIST', None):
        return get_proxy_obj(
            random.choice(conf['PROXY_LIST']))

    retries = 3
    while retries:
        try:
            response = requests.get(conf["PROXY_MANAGER"])
            try:
                data = response.json()
                return get_proxy_obj(data)
            except:
                monitoring.exception()
                logger.exception("Cant parse proxy response {}".format(response.text))
        except:
            logger.exception("Cant get proxy")
        retries -= 1
    monitoring.exception()
    raise RuntimeError("Proxy not found")

def get_proxy_obj(data):
    if data.get('username', None) is None:
        logger.info("Using proxy: {}:{}".format(data['host'], data['port']))
    else:
        logger.info("Using secure proxy: {}:{}".format(data['host'], data['port']))
    host_port = "{}:{}".format(data['host'], data['port'])
    proxy = Proxy()
    proxy.proxy_type = ProxyType.MANUAL
    proxy.http_proxy = host_port
    proxy.socks_proxy = host_port
    proxy.ssl_proxy = host_port
    proxy.socksUsername = data.get('username', None)
    proxy.socksPassword = data.get('password', None)
    return proxy 