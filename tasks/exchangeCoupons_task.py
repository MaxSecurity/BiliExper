from BiliClient import asyncbili
from .push_message_task import webhook
import logging

async def exchangeCoupons_task(biliapi: asyncbili, 
                         task_config: dict
                         ):
    '''积分兑换福利劵'''
    num = task_config["num"] #兑换福利劵数量
    try:
        now_point = (await biliapi.mangaGetPoint())["data"]["point"]
        buy_num = int(now_point) // 100
        if buy_num < num:
            num = buy_num
        if num == 0:
            print(f'{biliapi.name}: 积分兑换福利券失败，积分不足')
            webhook.addMsg('msg_simple', f'{biliapi.name}:兑换福利券失败\n')
            return
        data = await biliapi.mangaShopExchange(195, 100, num)
        if data["code"] != 0:
            if data["code"] == 9:
                logging.info(f'{biliapi.name}: 积分兑换福利券失败，手速太慢，库存不够了')
            else:
                logging.info(f'{biliapi.name}: 积分兑换福利券失败')
            webhook.addMsg('msg_simple', f'{biliapi.name}:兑换福利券失败\n')
        else:
            logging.info(f'{biliapi.name}: 成功兑换{num}张福利劵')
    except Exception as e: 
        logging.warning(f'{biliapi.name}: 积分兑换福利券异常,原因为：{str(e)}')
        webhook.addMsg('msg_simple', f'{biliapi.name}:兑换福利券异常\n')