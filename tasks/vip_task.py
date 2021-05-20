from BiliClient import asyncbili
from .push_message_task import webhook
from typing import Coroutine, Awaitable
from datetime import datetime, timedelta
from calendar import monthrange
import logging

async def vip_task(biliapi: asyncbili,
                   task_config: dict
                   ) -> Coroutine[None, None, None]:
    now = datetime.utcnow() + timedelta(hours=8)
    month_len = monthrange(now.year, now.month)[1]
    receive_day = task_config.get("receiveDay", 1)
    receive_day = receive_day if receive_day > 0 else month_len + receive_day
    chargeDay = task_config.get("chargeDay", 1)
    chargeDay = chargeDay if chargeDay > 0 else month_len + chargeDay

    if now.day == receive_day:
        await receivePrivilege(biliapi)

    if now.day == chargeDay:
        await bpCharge(biliapi, task_config["BpCharge"])

pivilege = ('大会员B币券', '大会员优惠券')
async def receivePrivilege(biliapi: asyncbili) -> Coroutine[None, None, None]:
    '''领取大会员权益'''
    try:
        ret = await biliapi.vipPrivilegeList()
    except Exception as e:
        logging.warning(f'{biliapi.name}: 获取大会员权益列表异常，原因为({repr(e)})')
        webhook.addMsg('msg_simple', f'{biliapi.name}:领取大会员权益失败\n')
        return

    if ret["code"] != 0:
        logging.warning(f'{biliapi.name}: 获取大会员权益列表失败，信息为({ret["message"]})')
        webhook.addMsg('msg_simple', f'{biliapi.name}:领取大会员权益失败\n')
        return

    for x in ret["data"]["list"]:
        if x["state"] == 0:
            try:
                ret = await biliapi.vipPrivilegeReceive(x["type"])
            except Exception as e:
                logging.warning(f'{biliapi.name}: 领取{pivilege[x["type"] - 1]}异常，原因为({str(e)})')
                webhook.addMsg('msg_simple', f'{biliapi.name}:领取{pivilege[x["type"] - 1]}失败\n')
            else:
                if ret["code"] == 0:
                    logging.info(f'{biliapi.name}: 成功领取{pivilege[x["type"] - 1]}')
                else:
                    logging.warning(f'{biliapi.name}: 领取{pivilege[x["type"] - 1]}失败，信息为({ret["message"]})')
                    webhook.addMsg('msg_simple', f'{biliapi.name}:领取{pivilege[x["type"] - 1]}失败\n')

async def receivePrivilege(biliapi: asyncbili) -> Coroutine[None, None, None]:
    '''领取大会员权益'''
    try:
        ret = await biliapi.vipPrivilegeList()
    except Exception as e:
        logging.warning(f'{biliapi.name}: 获取大会员权益列表异常，原因为({repr(e)})')
        webhook.addMsg('msg_simple', f'{biliapi.name}:领取大会员权益失败\n')
        return

    if ret["code"] != 0:
        logging.warning(f'{biliapi.name}: 获取大会员权益列表失败，信息为({ret["message"]})')
        webhook.addMsg('msg_simple', f'{biliapi.name}:领取大会员权益失败\n')
        return

    for x in ret["data"]["list"]:
        if x["state"] == 0:
            try:
                ret = await biliapi.vipPrivilegeReceive(x["type"])
            except Exception as e:
                logging.warning(f'{biliapi.name}: 领取{pivilege[x["type"] - 1]}异常，原因为({str(e)})')
                webhook.addMsg('msg_simple', f'{biliapi.name}:领取{pivilege[x["type"] - 1]}失败\n')
            else:
                if ret["code"] == 0:
                    logging.info(f'{biliapi.name}: 成功领取{pivilege[x["type"] - 1]}')
                else:
                    logging.warning(f'{biliapi.name}: 领取{pivilege[x["type"] - 1]}失败，信息为({ret["message"]})')
                    webhook.addMsg('msg_simple', f'{biliapi.name}:领取{pivilege[x["type"] - 1]}失败\n')

async def bpCharge(biliapi: asyncbili,
                   chargeConfig: dict
                   ) -> Coroutine[None, None, None]:
    '''B币劵消费'''
    try:
        ret = await biliapi.getUserWallet()
    except Exception as e:
        logging.warning(f'{biliapi.name}: 获取B币劵数量异常，原因为{repr(e)}，跳过消费')
        webhook.addMsg('msg_simple', f'{biliapi.name}:花费B币劵失败\n')
        return

    if ret["code"] != 0:
        logging.warning(f'{biliapi.name}: 获取B币劵数量失败，信息为{ret["message"]}，跳过消费')
        return

    cbp = ret["data"]["couponBalance"]
    for x in chargeConfig:
        if cbp < 1:
            break
        if task_config["BpCharge"][x] < 1:
            continue
        pay = cbp if task_config["BpCharge"][x] > cbp else task_config["BpCharge"][x]

        if x == 'charge':
            try:
                ret = await biliapi.elecPayBcoin(biliapi.uid, pay)
            except Exception as e:
                logging.warning(f'{biliapi.name}: B币劵充电异常，原因为{repr(e)}')
            else:
                if ret["data"]["order_no"]: #order_no是订单号，如果是空字符串就兑换失败了
                    cbp -= pay
                    logging.info(f'{biliapi.name}: 成功花费{pay}张B币劵给自己充电')
                else:
                    logging.warning(f'{biliapi.name}: B币劵充电失败，信息为{ret["message"]}')

        elif x == 'Bp2Gold':
            try:
                ret = await biliapi.xliveBp2Gold(pay)
            except Exception as e:
                logging.warning(f'{biliapi.name}: B币劵兑换金瓜子异常，原因为{repr(e)}')
            else:
                if ret["code"] == 0:
                    cbp -= pay
                    logging.info(f'{biliapi.name}: 成功花费{pay}张B币劵兑换金瓜子')
                else:
                    logging.warning(f'{biliapi.name}: B币劵兑换金瓜子失败，信息为{ret["message"]}')

        elif x == 'Bp2Coupons':
            try:
                ret = await biliapi.mangaPayBCoin(pay)
            except Exception as e:
                logging.warning(f'{biliapi.name}: B币劵兑换漫读劵异常，原因为{repr(e)}')
            else:
                if ret["code"] == 0:
                    cbp -= pay
                    logging.info(f'{biliapi.name}: 成功花费{pay}张B币劵兑换漫读劵')
                else:
                    logging.warning(f'{biliapi.name}: B币劵兑换漫读劵失败，信息为{ret["message"]}')
