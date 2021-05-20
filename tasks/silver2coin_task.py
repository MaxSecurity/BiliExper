from BiliClient import asyncbili
from .push_message_task import webhook
import logging

async def silver2coin_task(biliapi: asyncbili) -> None:
   try:
       ret = await biliapi.xliveGetStatus()
       if ret["code"] != 0:
           logging.warning(f'{biliapi.name}: 获取瓜子信息失败，信息为({ret["msg"]})，跳过兑换硬币')
           webhook.addMsg('msg_simple', f'{biliapi.name}:瓜子转硬币失败\n')
           return
   except Exception as e: 
       logging.warning(f'{biliapi.name}: 获取瓜子信息异常，原因为{str(e)}，跳过兑换硬币')
       webhook.addMsg('msg_simple', f'{biliapi.name}:瓜子转硬币失败\n')
       return

   if ret["data"]["silver_2_coin_left"] == 0:
       logging.warning(f'{biliapi.name}: 今日银瓜子兑换硬币额度已经用完')
       return

   try:
       ret = await biliapi.silver2coin()
       if ret["code"] != 0:
           logging.warning(f'{biliapi.name}: 银瓜子兑换硬币失败，信息为({ret["msg"]})')
           webhook.addMsg('msg_simple', f'{biliapi.name}:瓜子转硬币失败\n')
       else:
           logging.info(f'{biliapi.name}: 成功将银瓜子兑换为1个硬币')
   except Exception as e: 
       logging.warning(f'{biliapi.name}: 银瓜子兑换硬币异常，原因为{str(e)}，跳过兑换硬币')
       webhook.addMsg('msg_simple', f'{biliapi.name}:瓜子转硬币失败\n')