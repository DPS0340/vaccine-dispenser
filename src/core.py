import asyncio
from typing import Callable, Tuple
from log import logger as logging
import aiohttp
import json
import os
import sys
import unicodedata
import urllib3
import time
from pyppeteer import launch, page as page_module, network_manager
from constants import Headers, cookies_map, make_queue, webserver_port, testing
from mock import MockResponse, mock_check_user_info_loaded, mock_find_vaccine, mock_try_reservation
from utils import async_wrapper
from constants import search_time

urllib3.disable_warnings()


async def login_request(id, pw):
    browser = await launch(headless=True, options={'args': ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']})
    page = await browser.newPage()
    url = 'https://accounts.kakao.com/login?continue=https%3A%2F%2Fvaccine-map.kakao.com%2Fmap2%3Fv%3D1'

    await page.goto(url)

    id_selector = '#id_email_2'
    pw_selector = '#id_password_3'

    await page.waitForSelector(id_selector)
    await page.waitForSelector(pw_selector)

    id_input = await page.querySelector(id_selector)
    pw_input = await page.querySelector(pw_selector)

    await id_input.click()
    await id_input.type(id)
    await pw_input.click()
    await pw_input.type(pw)

    stay_signed_in_button = await page.querySelector('#staySignedIn')
    await stay_signed_in_button.click()

    login_button = await page.querySelector('button.btn_g.btn_confirm.submit')

    await login_button.click()
    await asyncio.sleep(2)
    await page.waitForSelector('body')

    is_captcha = False

    captcha_selector = '.wrap_captcha'

    try:
        captcha_selector = await page.querySelector(captcha_selector)
        if captcha_selector is not None:
            is_captcha = True
    except:
        is_captcha = True

    if is_captcha:
        return None, None, None

    lookup_button_selector = 'button.btn.btn_yellow'

    try:
        lookup_button = await page.querySelector(lookup_button_selector)
        if lookup_button is None:
            raise Exception
        await lookup_button.click()
        logging.info("found lookup button")
    except Exception as err:
        logging.info("not found lookup button")
        pass

    cookies = await page.cookies()
    return cookies, browser, page


async def find_position(message, page: page_module.Page, address: str, zoom_level: int):
    finder_selector = '.btn_util.btn_search'

    await page.waitForSelector(finder_selector)
    finder = await page.querySelector(finder_selector)
    await finder.click()

    search_form_selector = '#searchKeyword'
    await page.waitForSelector(search_form_selector)
    search_form = await page.querySelector(search_form_selector)
    await search_form.click()

    await search_form.type(address)
    await page.keyboard.press('Enter')

    result_link_selector = '.link_search'
    try:
        await page.waitForSelector(result_link_selector, timeout=1000)
    except:
        await message.channel.send("????????? ?????? ???????????????!")
        return None, None, None, None

    result_link = await page.querySelector(result_link_selector)

    await result_link.click()

    await asyncio.sleep(1)

    map_selector = '#map'

    map = await page.querySelector(map_selector)

    top_x, top_y, bottom_x, bottom_y = None, None, None, None
    find_count = 0

    deltaY = 200
    if zoom_level >= 0:
        deltaY *= -1
        zoom_level = min(zoom_level, 2)
    zoom_level = abs(zoom_level)

    def wait_for_request():
        while find_count < zoom_level:
            continue

    async def intercept_network_request(request: network_manager.Request):
        await request.continue_()
        if 'left_count_by_coords' not in request.url:
            return
        nonlocal find_count, top_x, top_y, bottom_x, bottom_y
        find_count += 1
        data: dict = json.loads(request.postData)
        bottomRight = data.get('bottomRight')
        topLeft = data.get('topLeft')
        top_x, top_y = topLeft.get('x'), topLeft.get('y')
        bottom_x, bottom_y = bottomRight.get('x'), bottomRight.get('y')
        if find_count < zoom_level:
            # Simple Recursion
            nonlocal map, page
            await map.click({'button': 'middle'})
            await page.mouse.wheel({'deltaY': deltaY})

    await page.setRequestInterception(True)
    page.on('request', lambda request: asyncio.ensure_future(
        intercept_network_request(request)))

    await map.click({'button': 'middle'})
    await page.mouse.wheel({'deltaY': deltaY})

    await async_wrapper(wait_for_request)

    return top_x, top_y, bottom_x, bottom_y


async def login_proxy_request(bot, message):
    url = 'https://github.com/DPS0340/vaccine-dispenser/releases/'
    await message.channel.send("????????? ???????????? ??????, hosts ?????? ????????? ???????????????. ?????? DNS??? ????????? ????????? ?????? ????????? ???????????? ????????????.")
    await message.channel.send(f"{url} ?????? ?????? ????????? ?????? ????????? ???????????? ??????????????????!")
    await message.channel.send("???????????? ????????????, ???????????? IP??? ????????? ?????????.")

    try:
        new_message = await bot.wait_for('message', check=lambda m: m.author == message.author and m.channel == message.channel, timeout=300.0)
        ip = new_message.content
    except asyncio.TimeoutError:
        await message.channel.send("?????? ??????!")
        logging.info("Timeout")
        return

    url = f'http://vaccinebot.kakao.com:{webserver_port}/login?continue=https%3A%2F%2Fvaccine-map.kakao.com%2Fmap2%3Fv%3D1'
    timeout = 180.0

    await message.channel.send(f"{url} ??? ?????????????????? ????????? ???????????? ???????????????! **??? ????????? ????????? ??????????????????.**\n{int(timeout)}??? ?????? ????????? ???????????? ???????????????.")

    started_time = time.time()

    def wait_for_cookies():
        while cookies_map.get(ip) is None:
            current_time = time.time()
            if current_time - started_time >= timeout:
                return None
            continue
        cookies = cookies_map[ip]
        del cookies_map[ip]
        return cookies

    cookies = await async_wrapper(wait_for_cookies)

    if not cookies:
        await message.channel.send("???????????? ????????? ???????????????. ?????? ?????? ???????????? ??????????????????.")
        return None

    await message.channel.send("????????? ??????!")

    return cookies


async def check_user_info_loaded(message, cookies):
    user_info_api = 'https://vaccine.kakao.com/api/v1/user'
    async with aiohttp.ClientSession(headers=Headers.headers_vacc, cookies=cookies) as session:
        user_info_response = await session.get(user_info_api, ssl=False)
    user_info_json = json.loads(await user_info_response.read())
    logging.info(user_info_json)
    if user_info_json.get('error'):
        await message.channel.send("????????? ????????? ??????????????? ?????????????????????.")
        await message.channel.send("???????????? ?????? ????????? ?????? ??????????????? ???????????? -> ?????? ?????? ?????? ?????? -> ???????????? ?????? -> ?????? ?????? ?????? -> ???????????? ??? ????????? ???????????????.")
        await close(message)
        return False
    else:
        await message.channel.send("????????? ?????? ?????????...")
        user_info = user_info_json.get("user")
        for key in user_info:
            value = user_info[key]
            if key != 'status':
                continue
            if key == 'status' and value == "NORMAL":
                await message.channel.send("????????? ????????? ??????????????? ??????????????????.")
                return True
            elif key == 'status' and value == "UNKNOWN":
                await message.channel.send("????????? ??? ??? ?????? ??????????????????. 1339 ?????? ???????????? ??????????????????.")
                await close(message)
                return False
            else:
                await message.channel.send("?????? ????????? ?????????????????? ????????? ????????? ??????????????????.")
                await close(message, success=None)
                return False
        await message.channel.send("????????? ?????? ????????? ?????????????????????.")
        return False


def fill_str_with_space(input_s, max_size=40, fill_char=" "):
    """
    - ????????? ??? ????????? 2????????? ????????????, ????????? 1????????? ?????????.
    - ?????? ??????(max_size)??? 40??????, input_s??? ?????? ????????? ????????? ?????????
    ?????? ????????? fill_char??? ?????????.
    """
    length = 0
    for c in input_s:
        if unicodedata.east_asian_width(c) in ["F", "W"]:
            length += 2
        else:
            length += 1
    return input_s + fill_char * (max_size - length)


# Something is wrong here
def is_in_range(coord_type, coord, user_min_x=-180.0, user_max_y=90.0):
    korea_coordinate = {  # Republic of Korea coordinate
        "min_x": 124.5,
        "max_x": 132.0,
        "min_y": 33.0,
        "max_y": 38.9
    }
    try:
        if coord_type == "x":
            return max(korea_coordinate["min_x"], user_min_x) <= float(coord) <= korea_coordinate["max_x"]
        elif coord_type == "y":
            return korea_coordinate["min_y"] <= float(coord) <= min(korea_coordinate["max_y"], user_max_y)
        else:
            return False
    except ValueError:
        # float ?????? ??? ?????? ??????
        return False


def clear():
    if 'win' in sys.platform.lower():
        os.system('cls')
    else:
        os.system('clear')


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


async def close(message, success=False, add_message=None):
    sender = add_message if add_message else message.channel.send
    success_message = "???????????? ?????? ??????!! \n ????????????????????? ???????????????."
    error_message = "????????? ?????? ???????????? ????????? ?????????????????????."

    message = success_message if success else error_message

    if add_message:
        sender(message)
    else:
        await sender(message)


def pretty_print(json_object):
    for org in json_object["organizations"]:
        if org.get('status') == "CLOSED" or org.get('status') == "EXHAUSTED" or org.get('status') == "UNAVAILABLE":
            continue
        return(
            f"????????????: {org.get('leftCounts')}\t??????: {org.get('status')}\t?????????: {org.get('orgName')}\t??????: {org.get('address')}")


async def try_reservation(message, cookies, organization_code, vaccine_type, mq: Tuple[Callable, Callable], lq: Tuple[Callable, Callable], retry=False):
    reservation_url = 'https://vaccine.kakao.com/api/v2/reservation'
    if retry:
        reservation_url = 'https://vaccine.kakao.com/api/v2/reservation/retry'
    data = {"from": "List", "vaccineCode": vaccine_type,
            "orgCode": organization_code, "distance": None}

    add_message, release_messages = mq
    add_log, release_logs = lq

    if testing:
        response_text = await mock_try_reservation(reservation_url, data=json.dumps(data), ssl=False)
        response_json = json.loads(response_text)
    else:
        async with aiohttp.ClientSession(headers=Headers.headers_vacc, cookies=cookies) as session:
            response = await session.post(reservation_url, data=json.dumps(data), ssl=False)
        response_json = json.loads(await response.read())

    add_log(response_json)
    value = response_json.get('code', '')
    if value == "NO_VACANCY":
        add_message("???????????? ?????? ????????? ????????? ?????????????????????.")
        return False
    elif value == "TIMEOUT":
        add_message("TIMEOUT, ????????? ??????????????????.")
        return await try_reservation(message, cookies, organization_code, vaccine_type, mq, lq, retry=True)
    elif value == "SUCCESS":
        add_message("?????????????????? ??????!!!")
        organization_code_success = response_json.get("organization")
        add_message(
            f"????????????: {organization_code_success.get('orgName')}\n????????????: {organization_code_success.get('phoneNumber')}\n??????: {organization_code_success.get('address')}")
        await close(message, success=True, add_message=add_message)
        return True
    else:
        add_message("ERROR. ?????? ???????????? ??????, ????????? ????????? ?????? ?????? 1339??? ????????? ???????????? ??????????????????.")
        add_message(await response.read())
        await close(message, add_message=add_message)
        return False

# ===================================== def ===================================== #

# pylint: disable=too-many-locals,too-many-statements,too-many-branches


async def find_vaccine(message, cookies, vaccine_type, top_x, top_y, bottom_x, bottom_y, only_left, mq: Tuple[Callable, Callable], lq: Tuple[Callable, Callable]):
    url = 'https://vaccine-map.kakao.com/api/v3/vaccine/left_count_by_coords'
    data = {"bottomRight": {"x": bottom_x, "y": bottom_y}, "topLeft": {
        "x": top_x, "y": top_y}, "onlyLeft": only_left, "order": "count"}

    done = False
    founds = []

    add_message, release_messages = mq
    add_log, release_logs = lq

    await message.channel.send(f"????????? {search_time}??? ????????? ?????? ????????????..")

    while not done:
        try:
            await asyncio.sleep(search_time)
            if testing:
                response = MockResponse()
            else:
                async with aiohttp.ClientSession(headers=Headers.headers_map) as session:
                    response = await session.post(url, data=json.dumps(
                        data), ssl=False, timeout=5)
            text = await response.read()
            json_data = json.loads(text)

            organizations = json_data.get("organizations", [])

            if organizations != [] or response.status != 200:
                logging.info(response.status)
                logging.info(json_data)

            founds = [x for x in organizations if x.get('leftCounts') != 0]
            if founds:
                done = True
                break
        except asyncio.exceptions.TimeoutError as err:
            logging.info(f"timeout err: {err}", exc_info=True)
            continue
        except Exception as err:
            logging.critical(err, exc_info=True)
            await message.channel.send("?????? ??????!")
            await message.channel.send(err)
            await close(message)

    async def prepare_reservation(found):
        if found is None:
            return False
        add_message(
            f"{found.get('orgName')} ?????? ????????? {found.get('leftCounts')}??? ??????????????????.")
        add_message(f"????????? : {found.get('address')} ?????????.")
        organization_code = found.get('orgCode')

        # ?????? ?????? ???????????? ??????
        vaccine_found_code = None

        check_organization_url = f'https://vaccine.kakao.com/api/v3/org/org_code/{organization_code}'
        async with aiohttp.ClientSession(headers=Headers.headers_vacc, cookies=cookies) as session:
            check_organization_response = await session.get(check_organization_url, data=json.dumps(
                data), headers=Headers.headers_vacc, ssl=False, timeout=5)
        text = await check_organization_response.read()
        logging.info(text)
        check_organization_data = json.loads(text).get("lefts")
        for x in check_organization_data:
            if x.get('leftCount', 0) != 0 and x.get('vaccineCode') == vaccine_type:
                found = x
                add_message(
                    f"{x.get('vaccineName')} ????????? {x.get('leftCount')}??? ??????????????????.")
                vaccine_found_code = x.get('vaccineCode')
                break
            else:
                add_message(f"{x.get('vaccineName')} ????????? ????????????.")

        if vaccine_found_code:
            result = await try_reservation(message, cookies, organization_code, vaccine_found_code, mq, lq)
            return result
        else:
            return False

    queue = [prepare_reservation(found) for found in founds]
    results = await asyncio.gather(*queue)
    await asyncio.gather(release_messages(), release_logs())
    succeed_result = [result for result in results if result == True]
    is_success = len(succeed_result) > 0
    return is_success


async def reservation(bot, message, vaccine_type, id, pw, **kwargs):
    cookies, browser, page = await login_request(id, pw)
    if cookies:
        cookies = {x['name']: x['value'] for x in cookies}
    else:
        cookies = await login_proxy_request(bot, message)
        if not cookies:
            return
    if kwargs.get('address') is not None:
        address, zoom_level, only_left = kwargs.values()
        top_x, top_y, bottom_x, bottom_y = await find_position(message, page, address, zoom_level)
    else:
        top_x, top_y, bottom_x, bottom_y, only_left = kwargs.values()

    await browser.close()
    del browser

    if None in [top_x, top_y, bottom_x, bottom_y]:
        return

    if testing:
        user_available = await mock_check_user_info_loaded(message, cookies)
    else:
        user_available = await check_user_info_loaded(message, cookies)
    if not user_available:
        return
    find_result = False
    mq = make_queue(message.channel.send)
    lq = make_queue(logging.info)
    while not find_result:
        find_result = await find_vaccine(message, cookies, vaccine_type, top_x, top_y, bottom_x, bottom_y, only_left, mq, lq)
