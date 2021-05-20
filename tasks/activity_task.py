from BiliClient import asyncbili
from .push_message_task import webhook
import asyncio, logging, json

activity_task_lock = asyncio.Lock()
activity_task_path = {}
async def activity_task(biliapi: asyncbili,
                        task_config: dict
                        ) -> None:
    activity_list = []
    if 'path' in task_config:
        if task_config["path"] in activity_task_path:
            activity_list.extend(activity_task_path[task_config["path"]])
        else:
            try:
                with open(task_config["path"], 'r', encoding='utf-8') as fp:
                    activity_task_path[task_config["path"]] = json.load(fp)
            except Exception as e:
                logging.warning(f'{biliapi.name}: 读取活动列表异常,原因为({str(e)})')
                webhook.addMsg('msg_simple', f'{biliapi.name}:读取活动列表异常\n')
            else:
                activity_list.extend(activity_task_path[task_config["path"]])
    if 'activities' in task_config:
        activity_list.extend(task_config["activities"])
    for x in activity_list:
        for y in range(2, 5):
            try:
                await biliapi.activityAddTimes(x["sid"], y) #执行增加抽奖次数操作,一般是分享转发
            except Exception as e:
                logging.warning(f'{biliapi.name}: 增加({x["name"]})活动抽奖次数异常,原因为({str(e)})')

        try:
            ret = await biliapi.activityMyTimes(x["sid"])
            if ret["code"] == 0:
                times = ret["data"]["times"]
            else:
                logging.info(f'{biliapi.name}: 获取({x["name"]})活动抽奖次数错误，消息为({ret["message"]})')
                continue
        except Exception as e:
            logging.warning(f'{biliapi.name}: 获取({x["name"]})活动抽奖次数异常，原因为({str(e)})，跳过参与活动')
            continue

        for ii in range(times):
            try:
                async with activity_task_lock:
                    ret = await biliapi.activityDo(x["sid"], 1)
                    if ret["code"]:
                        logging.info(f'{biliapi.name}: 参与({x["name"]})活动第({ii + 1}/{times})次，结果为({ret["message"]})')
                    else:
                        logging.info(f'{biliapi.name}: 参与({x["name"]})活动第({ii + 1}/{times})次，结果为({ret["data"][0]["gift_name"]})')
                        if not ret["data"][0]["gift_name"] == '未中奖0':
                            webhook.addMsg('msg_simple', f'{biliapi.name}:参与({x["name"]})活动获得({ret["data"][0]["gift_name"]})\n')
                    await asyncio.sleep(6) #抽奖延时
            except Exception as e:
                logging.warning(f'{biliapi.name}: 参与({x["name"]})活动异常，原因为({str(e)})')