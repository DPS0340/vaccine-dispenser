import asyncio
from log import logger as logging
import aiohttp
import json
import os
import sys
import time
import unicodedata
import urllib3
import platform
from pyppeteer import launch

search_time = 0.5  # 잔여백신을 해당 시간마다 한번씩 검색합니다. 단위: 초
urllib3.disable_warnings()

async def login_request(id, pw):
    os_type = platform.system()
    if os_type == "Linux":
        browser = await launch(executablePath='/usr/bin/google-chrome-stable', headless=True, options={'args': ['--no-sandbox']})
    else:
        browser = await launch(headless=True)
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
    await page.waitForSelector('body')

    lookup_button_selector = 'button.btn.btn_yellow'

    await page.waitForSelector(lookup_button_selector)
    lookup_button = await page.querySelector(lookup_button_selector)
    await lookup_button.click()

    cookies = await page.cookies()
    return cookies

async def check_user_info_loaded(message, cookies):
    user_info_api = 'https://vaccine.kakao.com/api/v1/user'
    async with aiohttp.ClientSession(headers=Headers.headers_vacc, cookies=cookies) as session:
        user_info_response = await session.get(user_info_api, ssl=False)
    user_info_json = json.loads(await user_info_response.read())
    logging.info(user_info_json)
    if user_info_json.get('error'):
        await message.channel.send("사용자 정보를 불러오는데 실패하였습니다.")
        await close(message)
        return False
    else:
        await message.channel.send("사용자 정보 파싱중...")
        user_info = user_info_json.get("user")
        for key in user_info:
            value = user_info[key]
            if key != 'status':
                continue
            if key == 'status' and value == "NORMAL":
                await message.channel.send("사용자 정보를 불러오는데 성공했습니다.")
                return True
            elif key == 'status' and value == "UNKNOWN":
                await message.channel.send("상태를 알 수 없는 사용자입니다. 1339 또는 보건소에 문의해주세요.")
                await close(message)
                return False
            else:
                await message.channel.send("이미 접종이 완료되었거나 예약이 완료된 사용자입니다.")
                await close(message, success=None)
                return False
        await message.channel.send("사용자 정보 파싱에 실패하였습니다.")
        return False


def fill_str_with_space(input_s, max_size=40, fill_char=" "):
    """
    - 길이가 긴 문자는 2칸으로 체크하고, 짧으면 1칸으로 체크함.
    - 최대 길이(max_size)는 40이며, input_s의 실제 길이가 이보다 짧으면
    남은 문자를 fill_char로 채운다.
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
        # float 이외 값 입력 방지
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


async def close(message, success=False):
    if success is True:
        await message.channel.send("잔여백신 예약 성공!! \n 카카오톡지갑을 확인하세요.")
    else:
        await message.channel.send("오류와 함께 잔여백신 예약이 종료되었습니다.")


def pretty_print(json_object):
    for org in json_object["organizations"]:
        if org.get('status') == "CLOSED" or org.get('status') == "EXHAUSTED" or org.get('status') == "UNAVAILABLE":
            continue
        return(
            f"잔여갯수: {org.get('leftCounts')}\t상태: {org.get('status')}\t기관명: {org.get('orgName')}\t주소: {org.get('address')}")


class Headers:
    headers_map = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=utf-8",
        "Origin": "https://vaccine-map.kakao.com",
        "Accept-Language": "en-us",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 KAKAOTALK 9.4.2",
        "Referer": "https://vaccine-map.kakao.com/",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "Keep-Alive",
        "Keep-Alive": "timeout=5, max=1000"
    }
    headers_vacc = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=utf-8",
        "Origin": "https://vaccine.kakao.com",
        "Accept-Language": "en-us",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 KAKAOTALK 9.4.2",
        "Referer": "https://vaccine.kakao.com/",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "Keep-Alive",
        "Keep-Alive": "timeout=5, max=1000"
    }


async def try_reservation(message, cookies, organization_code, vaccine_type, retry=False):
    reservation_url = 'https://vaccine.kakao.com/api/v1/reservation'
    if retry:
        reservation_url = 'https://vaccine.kakao.com/api/v1/reservation/retry'
    data = {"from": "Map", "vaccineCode": vaccine_type,
            "orgCode": organization_code, "distance": None}
    async with aiohttp.ClientSession(headers=Headers.headers_vacc, cookies=cookies) as session:
        response = await session.post(reservation_url, data=json.dumps(data), ssl=False)
    response_json = json.loads(await response.read())
    logging.info(response_json)
    for key in response_json:
        value = response_json[key]
        if key != 'code':
            continue
        if key == 'code' and value == "NO_VACANCY":
            await message.channel.send("잔여백신 접종 신청이 선착순 마감되었습니다.")
            time.sleep(0.08)
        elif key == 'code' and value == "TIMEOUT":
            await message.channel.send("TIMEOUT, 예약을 재시도합니다.")
            try_reservation(organization_code, vaccine_type, retry=True)
        elif key == 'code' and value == "SUCCESS":
            await message.channel.send("백신접종신청 성공!!!")
            organization_code_success = response_json.get("organization")
            await message.channel.send(
                f"병원이름: {organization_code_success.get('orgName')}\t" +
                f"전화번호: {organization_code_success.get('phoneNumber')}\t" +
                f"주소: {organization_code_success.get('address')}")
            await close(message, success=True)
            return True
        else:
            await message.channel.send("ERROR. 아래 메시지를 보고, 예약이 신청된 병원 또는 1339에 예약이 되었는지 확인해보세요.")
            await message.channel.send(await response.read())
            await close(message)
            return False

# ===================================== def ===================================== #

# pylint: disable=too-many-locals,too-many-statements,too-many-branches
async def find_vaccine(message, cookies, vaccine_type, top_x, top_y, bottom_x, bottom_y):
    url = 'https://vaccine-map.kakao.com/api/v2/vaccine/left_count_by_coords'
    data = {"bottomRight": {"x": bottom_x, "y": bottom_y}, "onlyLeft": False, "order": "latitude",
            "topLeft": {"x": top_x, "y": top_y}}
    done = False
    found = None

    while not done:
        try:
            time.sleep(search_time)
            async with aiohttp.ClientSession(headers=Headers.headers_map) as session:
                response = await session.post(url, data=json.dumps(
                    data), ssl=False, timeout=5)
                logging.info(response.status)

            text = await response.read()
            json_data = json.loads(text)
            logging.info(json_data)

            for x in json_data.get("organizations"):
                if x.get('status') == "AVAILABLE" or x.get('leftCounts') != 0:
                    found = x
                    done = True
                    break
        except asyncio.exceptions.TimeoutError as err:
            logging.info(f"timeout err: {err}", exc_info=True)
            continue
        except Exception as err:
            logging.critical(err, exc_info=True)
            await message.channel.send("오류 발생!")
            await message.channel.send(err)
            await close(message)

    if found is None:
        return False
    await message.channel.send(f"{found.get('orgName')} 에서 백신을 {found.get('leftCounts')}개 발견했습니다.")
    await message.channel.send(f"주소는 : {found.get('address')} 입니다.")
    organization_code = found.get('orgCode')

    # 실제 백신 남은수량 확인
    vaccine_found_code = None

    if vaccine_type == "ANY":  # ANY 백신 선택
        check_organization_url = f'https://vaccine.kakao.com/api/v2/org/org_code/{organization_code}'
        async with aiohttp.ClientSession(headers=Headers.headers_vacc, cookies=cookies) as session:
            check_organization_response = await session.get(check_organization_url, data=json.dumps(
                    data), headers=Headers.headers_vacc, ssl=False, timeout=5)
        text = await check_organization_response.read()
        check_organization_data = json.loads(text).get("lefts")
        for x in check_organization_data:
            if x.get('leftCount') != 0:
                found = x
                await message.channel.send(f"{x.get('vaccineName')} 백신을 {x.get('leftCount')}개 발견했습니다.")
                vaccine_found_code = x.get('vaccineCode')
                break
            else:
                await message.channel.send(f"{x.get('vaccineName')} 백신이 없습니다.")

    else:
        vaccine_found_code = vaccine_type
        await message.channel.send(f"{vaccine_found_code} 으로 예약을 시도합니다.")

    if vaccine_found_code and try_reservation(cookies, organization_code, vaccine_found_code):
        return True
    else:
        return False

async def reservation(message, vaccine_type, id, pw, top_x, top_y, bottom_x, bottom_y):
    cookies = await login_request(id, pw)
    cookies = {x['name']: x['value'] for x in cookies}
    user_available = await check_user_info_loaded(message, cookies)
    if not user_available:
        return
    find_result = False
    while not find_result:
        find_result = await find_vaccine(message, cookies, vaccine_type, top_x, top_y, bottom_x, bottom_y)
