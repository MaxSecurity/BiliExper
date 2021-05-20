from BiliClient import asyncbili
from .push_message_task import webhook
import logging

async def manga_sign_task(biliapi: asyncbili) -> None:
    try:
        ret = await biliapi.mangaClockIn()
        if(ret["code"] == 0):
            logging.info(f'{biliapi.name}: 漫画签到成功')
        elif ret["msg"] == 'clockin clockin is duplicate':
            logging.info(f'{biliapi.name}: 漫画今天已经签到过了')
        else:
            logging.warning(f'{biliapi.name}: 漫画签到失败，信息为({ret["msg"]})')
            webhook.addMsg('msg_simple', f'{biliapi.name}:漫画签到失败\n')
    except Exception as e: 
        logging.warning(f'{biliapi.name}: 漫画签到异常,原因为：{str(e)}')
        webhook.addMsg('msg_simple', f'{biliapi.name}:漫画签到失败\n')