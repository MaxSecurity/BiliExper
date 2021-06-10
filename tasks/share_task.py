from BiliClient import asyncbili
from .push_message_task import webhook
import logging

async def share_task(biliapi: asyncbili) -> None:
    try:
        ret = await biliapi.getRegions(27, 15)
    except Exception as e:
        logging.warning(f'{biliapi.name}: 获取B站分区视频信息异常，原因为{str(e)}，跳过视频分享')
        webhook.addMsg('msg_simple', f'{biliapi.name}:视频分享失败\n')
        return

    if ret["code"]:
        logging.warning(f'{biliapi.name}: 获取B站分区视频信息异常，原因为{ret["message"]}，跳过视频分享')
        webhook.addMsg('msg_simple', f'{biliapi.name}:视频分享失败\n')
        return
    ids = ret["data"]["archives"]

    try:
        ret = await biliapi.share(ids[5]["aid"])
        if ret["code"] == 0:
            logging.info(f'{biliapi.name}: 成功分享av号为{ids[5]["aid"]}的视频')
        else:
            logging.warning(f'{biliapi.name}: 分享av号为{ids[5]["aid"]}的视频失败，原因为：{ret["message"]}')
            webhook.addMsg('msg_simple', f'{biliapi.name}:视频分享失败\n')
    except Exception as e: 
        logging.warning(f'{biliapi.name}: 分享视频异常，原因为{str(e)}')
        webhook.addMsg('msg_simple', f'{biliapi.name}:视频分享失败\n')