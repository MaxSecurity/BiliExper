from BiliClient import asyncbili
from .push_message_task import webhook
import logging, time

async def manga_vip_reward_task(biliapi: asyncbili,
                                task_config: dict
                                ) -> None:
    taday = time.localtime(time.time() + 28800 + time.timezone).tm_mday
    if not taday in task_config["days"]:
        return
    try:
        ret = await biliapi.mangaGetVipReward()
        if(ret["code"] == 0):
            logging.info(f'{biliapi.name}: 大会员成功领取{ret["data"]["amount"]}张漫读劵')
        else:
            logging.warning(f'{biliapi.name}: 大会员领取漫读劵失败,信息为：{ret["msg"]}')
            webhook.addMsg('msg_simple', f'{biliapi.name}:领取漫读劵失败\n')
    except Exception as e: 
        logging.warning(f'{biliapi.name}: 大会员领取漫读劵异常,原因为：{str(e)}')
        webhook.addMsg('msg_simple', f'{biliapi.name}:领取漫读劵失败\n')