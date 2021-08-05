# original code from https://github.com/DPS0340/CleanerBot/blob/master/src/server.py

from aiohttp import web
from multidict import MultiDict
from constants import webserver_port, cookies_map, temp_cookies_map
from discord.ext import commands, tasks
import aiohttp
from log import logger
from constants import Headers
from http.cookies import SimpleCookie

header = Headers.UA

app = web.Application()
routes = web.RouteTableDef()
class Webserver(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.webserver_port = webserver_port
        self.sessions = {}
        app.router.add_routes([
            web.get('', self.kakao_proxy),
            web.post('', self.kakao_proxy),
            web.get('/{url:.*}', self.kakao_proxy),
            web.post('/{url:.*}', self.kakao_proxy)])
        self.web_server.start()

    async def kakao_proxy(self, request: web.Request):
        url = request.path_qs
        headers = request.headers.copy()

        logger.info(f'Headers: {headers}')
        logger.info(f'URL: {url}')

        remote_url = f"https://accounts.kakao.com{url}"

        request_header = {**header, 'Referer': remote_url}
        
        if self.sessions.get(request.remote):
            session = self.sessions[request.remote]
        else:
            session = aiohttp.ClientSession(headers=request_header)
            self.sessions[request.remote] = session
            
        http_method = session.post if request.method == 'POST' else session.get

        if request.method == 'POST':
            data = await request.post()
            req = await http_method(remote_url, data=data, ssl=False)
        else:
            req = await http_method(remote_url, ssl=False)
        body = await req.read()
        text = body.decode('utf-8')
        headers = MultiDict(req.headers.copy())
        new_headers = MultiDict()

        for (k, v) in headers.items():
            if k != 'Set-Cookie':
                continue
            new_headers.add(k, v)
        
        headers = new_headers

        req_cookies = SimpleCookie()
        for cookie in list(headers.values()):
            # 여러개의 쿠키 키-밸류 쌍에 일반화 필요
            # 더 좋은 방법이 있을지...?
            cookie = cookie.split(";")[0]
            req_cookies.load(cookie)
            if temp_cookies_map.get(request.remote) is None:
                temp_cookies_map[request.remote] = {}
            temp_cookies_map[request.remote] = {**temp_cookies_map[request.remote], **dict(req_cookies.copy())}
        
        if 'weblogin/sso_initialize' in url:
            cookies_map[request.remote] = temp_cookies_map[request.remote]
            del temp_cookies_map[request.remote]

        response = web.Response(text=text, status=req.status, headers=headers, content_type=req.content_type)
        return response

    @tasks.loop()
    async def web_server(self):
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host='0.0.0.0', port=self.webserver_port)
        await site.start()
        

    @web_server.before_loop
    async def web_server_before_loop(self):
        await self.bot.wait_until_ready()