from BiliClient import asyncbili
from .push_message_task import webhook
import logging

async def xliveSign_task(biliapi: asyncbili) -> None:
    try:
        ret = await biliapi.xliveSign()
        if ret["code"] == 0:
            logging.info(f'{biliapi.name}: 直播签到成功，信息:{ret["data"]["text"]}，特别信息:{ret["data"]["specialText"]}，本月已签到{ret["data"]["hadSignDays"]}天')
        else:
            logging.info(f'{biliapi.name}: 直播签到失败，信息为：{ret["message"]}')
            webhook.addMsg('msg_simple', f'{biliapi.name}:直播签到失败\n')
    except Exception as e:
        logging.warning(f'{biliapi.name}: 直播签到异常，原因为{str(e)}')
        webhook.addMsg('msg_simple', f'{biliapi.name}:直播签到失败\n')