from BiliClient import asyncbili
from .push_message_task import webhook
import logging

async def watch_task(biliapi: asyncbili) -> None:
    try:
        ret = await biliapi.getRegions(27, 15)
    except Exception as e:
        logging.warning(f'{biliapi.name}: 获取B站分区视频信息异常，原因为{str(e)}，跳过模拟视频观看')
        webhook.addMsg('msg_simple', f'{biliapi.name}:模拟视频观看失败\n')
        return

    if ret["code"]:
        logging.warning(f'{biliapi.name}: 获取B站分区视频信息异常，原因为{ids["message"]}，跳过视频观看')
        webhook.addMsg('msg_simple', f'{biliapi.name}:模拟视频观看失败\n')
        return
    ids = ret["data"]["archives"]

    try:
        ret = await biliapi.report(ids[5]["aid"], ids[5]["cid"], 300)
        if ret["code"] == 0:
            logging.info(f'{biliapi.name}: 成功模拟观看av号为{ids[5]["aid"]}的视频')
        else:
            logging.warning(f'{biliapi.name}: 模拟观看av号为{ids[5]["aid"]}的视频投币失败，原因为：{ret["message"]}')
            webhook.addMsg('msg_simple', f'{biliapi.name}:模拟视频观看失败\n')
    except Exception as e: 
        logging.warning(f'{biliapi.name}: 模拟视频观看异常，原因为{str(e)}')
        webhook.addMsg('msg_simple', f'{biliapi.name}:模拟视频观看失败\n')