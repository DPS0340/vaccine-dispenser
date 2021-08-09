from typing import Callable, Tuple
import inspect
vaccine_candidates = [
    {"name": "아무거나", "code": "ANY"},
    {"name": "화이자", "code": "VEN00013"},
    {"name": "모더나", "code": "VEN00014"},
    {"name": "아스트라제네카", "code": "VEN00015"},
    {"name": "얀센", "code": "VEN00016"},
    {"name": "(미사용)", "code": "VEN00017"},
    {"name": "(미사용)", "code": "VEN00018"},
    {"name": "(미사용)", "code": "VEN00019"},
    {"name": "(미사용)", "code": "VEN00020"},
]


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
    UA = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
    }


cookies_map = {}
temp_cookies_map = {}


def make_queue(send_func: Callable) -> Tuple[Callable, Callable]:
    queue = []

    def add_message(text: str):
        nonlocal queue
        queue.append(text)

    async def release_messages():
        nonlocal queue
        is_coroutine = inspect.iscoroutinefunction(send_func)
        while queue:
            text = queue.pop(0)
            if is_coroutine:
                await send_func(text)
            else:
                send_func(text)
    return (add_message, release_messages)


def get_ip_address():
    import requests
    return requests.get('https://checkip.amazonaws.com').text.strip()


ip_address = get_ip_address()
webserver_port = 8088

testing = False
