from aiohttp import ClientSession, ClientTimeout
import asyncio, logging
from io import StringIO
class WebHook:
    '''消息推送'''
    def __init__(self):
        self._is_set = False

    def set(self, webhook: dict):
        if 'http_header' in webhook:
            self._default_header: dict = webhook["http_header"]
        else:
            self._default_header = {"User-Agent":"Mozilla/5.0"}
        if 'variable' in webhook:
            self._default_variable: dict = webhook["variable"]
        else:
            self._default_variable = {"title":"B站经验脚本消息推送"}

        self._hooks = [x for x in webhook["hooks"] if not 'enable' in x or x["enable"]]
        self._is_set = True

    def __len__(self):
        return len(self._hooks)

    def addMsgStream(self, name: str, io: StringIO = None):
        if self._is_set:
            if io:
                self._default_variable[name] = io
            else:
                self._default_variable[name] = StringIO()

    def addMsg(self, name: str, msg: str):
        if self._is_set and name in self._default_variable and self._default_variable[name]:
            self._default_variable[name].write(msg)

    async def send(self):
        if self._is_set and len(self):
            try:
                timeout = ClientTimeout(total=30, connect=15, sock_connect=30, sock_read=25)
                async with ClientSession(timeout=timeout) as s:
                    await asyncio.wait([self._send(ii, s) for ii in range(len(self))])
            except Exception as e: 
                logging.warning(f'推送消息异常，原因为{str(e)}')
        else:
            logging.info('未定义消息推送')

    async def _send(self, n: int, session: ClientSession):
        hook = self._hooks[n]
        params = hook["params"]
        headers = {}
        if 'http_header' in hook:
            headers = hook["http_header"]
            for x in self._default_header:
                if not x in headers:
                    headers[x] = self._default_header[x]
        else:
            headers = self._default_header
        
        if 'variable' in hook:
            variable = hook["variable"]
            for x in self._default_variable:
                if not x in variable:
                    variable[x] = self._default_header[x]
        else:
            variable = self._default_variable

        url = hook["url"]
        for v in variable:
            var = '{'+v+'}'
            if not v.startswith('msg_'):
                url = url.replace(var, variable[v])
            for p in params:
                if v.startswith('msg_'):
                    if 'msg_separ' in hook:
                        params[p] = params[p].replace(var, variable[v].getvalue().replace('\n', hook["msg_separ"]))
                    else:
                        params[p] = params[p].replace(var, variable[v].getvalue())
                else:
                    params[p] = params[p].replace(var, variable[v])
        result = None
        try:
            if hook["method"] == 0:
                async with session.get(url, params=params, headers=headers, verify_ssl=False) as r:
                    result = await r.text()
            elif hook["method"] == 1:
                async with session.post(url, data=params, headers=headers, verify_ssl=False) as r:
                    result = await r.text()
            elif hook["method"] == 3:
                async with session.post(url, json=params, headers=headers, verify_ssl=False) as r:
                    result = await r.text()
        except Exception as e: 
            logging.warning(f'推送消息({hook["name"]})异常，原因为{str(e)}')
        if result:
            logging.info(f'推送消息({hook["name"]}),结果:{result}')

webhook = WebHook()