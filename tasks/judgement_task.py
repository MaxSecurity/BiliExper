from BiliClient import asyncbili
from .push_message_task import webhook
import logging
from asyncio import TimeoutError, sleep
from concurrent.futures import CancelledError
from async_timeout import timeout
from typing import Awaitable, Tuple

voteInfo = ("未投票", "封禁", "否认", "弃权", "删除")

async def judgement_task(biliapi: asyncbili, 
                         task_config: dict
                         ) -> Awaitable:
    '''风纪委员会投票任务'''
    try:
        ret = await biliapi.juryInfo()
    except Exception as e:
        logging.warning(f'{biliapi.name}: 获取风纪委员信息异常，原因为{str(e)}，跳过投票')
        webhook.addMsg('msg_simple', f'{biliapi.name}:风纪委投票失败\n')
        return
    if ret["code"] == 25005:
        logging.warning(f'{biliapi.name}: 风纪委员投票失败，请去https://www.bilibili.com/judgement/apply 申请成为风纪委员')
        webhook.addMsg('msg_simple', f'{biliapi.name}:不是风纪委\n')
        return
    elif ret["code"] != 0:
        logging.warning(f'{biliapi.name}: 风纪委员投票失败，信息为：{ret["msg"]}')
        webhook.addMsg('msg_simple', f'{biliapi.name}:风纪委投票失败\n')
        return
    if ret["data"]["status"] != 1:
        logging.warning(f'{biliapi.name}: 风纪委员投票失败，风纪委员资格失效')
        webhook.addMsg('msg_simple', f'{biliapi.name}:风纪委资格失效\n')
        return

    logging.info(f'{biliapi.name}: 拥有风纪委员身份，开始获取案件投票，当前裁决正确率为：{ret["data"]["rightRadio"]}%')
    webhook.addMsg('msg_simple', f'{biliapi.name}:风纪委当前裁决正确率为：{ret["data"]["rightRadio"]}%\n')

    baiduNLPConfig = task_config.get("baiduNLP", None)
    params = task_config.get("params", {})
    vote_num = task_config.get("vote_num", 20)
    check_interval = task_config.get("check_interval", 420)
    Timeout = task_config.get("timeout", 850)
    run_once = task_config.get("run_once", False)

    over = False
    su = 0
    try:
        async with timeout(Timeout):
            while True:
                while True:
                    try:
                        ret = await biliapi.juryCaseObtain()
                    except CancelledError as e:
                        raise e
                    except Exception as e:
                        logging.warning(f'{biliapi.name}: 获取风纪委员案件异常，原因为{str(e)}，跳过本次投票')
                        break
                    if ret["code"] == 25008:
                        logging.info(f'{biliapi.name}: 风纪委员没有新案件了')
                        break
                    elif ret["code"] == 25014:
                        over = True
                        logging.info(f'{biliapi.name}: 风纪委员案件已审满')
                        break
                    elif ret["code"] != 0:
                        logging.warning(f'{biliapi.name}: 获取风纪委员案件失败，信息为：{ret["message"]}')
                        break
                    cid = ret["data"]["id"]
                    params = task_config.get("params", {})
                    default = True
                    try:
                        ret = await biliapi.juryCase(cid)
                    except CancelledError as e:
                        raise e
                    except Exception as e:
                        logging.warning(f'{biliapi.name}: 获取风纪委员案件他人投票结果异常，原因为{str(e)}，使用默认投票参数')
                    else:
                        if ret["code"] == 0:
                            vote = [(4, ret["data"]["voteDelete"]), (2, ret["data"]["voteBreak"]), (1, ret["data"]["voteRule"])]
                            vote.sort(key=lambda x: x[1], reverse=True)
                            params = params.copy()
                            params["vode"] = vote[0][0]
                            default = False
                        else:
                            logging.warning(f'{biliapi.name}: 获取风纪委员案件他人投票结果异常，原因为{ret["message"]}，使用默认投票参数')

                    try:
                        ret = await biliapi.juryVote(cid, **params) #将参数params展开后传参
                    except CancelledError as e:
                        raise e
                    except Exception as e:
                        logging.warning(f'{biliapi.name}: 风纪委员投票id为{cid}的案件异常，原因为{str(e)}')
                    else:
                        if ret["code"] == 0:
                            su += 1
                            if default:
                                logging.info(f'{biliapi.name}: 风纪委员成功为id为{cid}的案件投({voteInfo[params["vote"]]})票')
                            else:
                                logging.info(f'{biliapi.name}: 风纪委员成功为id为{cid}的案件投({voteInfo[params["vote"]]})票，当前案件投票数({voteInfo[vote[0][0]]}{vote[0][1]}票),({voteInfo[vote[1][0]]}{vote[1][1]}票),({voteInfo[vote[2][0]]}{vote[2][1]}票)')
                        else:   
                            logging.warning(f'{biliapi.name}: 风纪委员投票id为{cid}的案件失败，信息为：{ret["message"]}')

                if over or run_once or su >= vote_num:
                    logging.info(f'{biliapi.name}: 风纪委员投票成功完成{su}次后退出')
                    break
                else:
                    logging.info(f'{biliapi.name}: 风纪委员投票等待{check_interval}s后继续获取案件')
                    await sleep(check_interval)

    except TimeoutError:
        logging.info(f'{biliapi.name}: 风纪委员投票任务超时({Timeout}秒)退出')
    except CancelledError:
        logging.warning(f'{biliapi.name}: 风纪委员投票任务被强制取消')

    webhook.addMsg('msg_simple', f'{biliapi.name}:风纪委投票成功{su}次\n')