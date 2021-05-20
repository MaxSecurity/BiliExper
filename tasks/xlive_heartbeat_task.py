from BiliClient import asyncbili
from .push_message_task import webhook
import logging, uuid
from asyncio import TimeoutError, sleep, wait, ensure_future
from concurrent.futures import CancelledError
from async_timeout import timeout
from typing import Awaitable, AsyncGenerator, Tuple, Union, List, Iterator

async def xlive_heartbeat_task(biliapi: asyncbili,
                               task_config: dict
                               ) -> Awaitable:
    timeout = task_config.get("timeout", task_config.get("time", 30)) * 60
    send_msg = task_config.get("send_msg", "")
    medal_room = task_config.get("medal_room", True)
    rooms_id = set(task_config.get("room_id", []))
    live_status = task_config.get("live_status", [0, 1])
    tasks = []
    rooms = await get_rooms(biliapi)
    if send_msg:
        tasks.append(send_msg_task(biliapi, rooms, send_msg))

    if medal_room:
        rooms_id |= set(rooms)

    tasks.extend([heartbeat_task(biliapi, x, timeout, live_status) for x in rooms_id])

    if tasks:
        await wait(map(ensure_future, tasks))

async def get_rooms(biliapi: asyncbili) -> Awaitable[List[int]]:
    '''获取所有勋章房间'''
    result = []
    page = 1
    while True:
        try:
            ret = await biliapi.xliveFansMedal(page, 50)
        except Exception as e:
            logging.warning(f'{biliapi.name}: 获取有勋章的直播间异常，原因为{str(e)}')
            break
        else:
            if ret["code"] == 0:
                if not ret["data"]["fansMedalList"]:
                    break
                for medal in ret["data"]["fansMedalList"]:
                    if 'roomid' in medal:
                        result.append(medal["roomid"])
            else:
                logging.warning(f'{biliapi.name}: 获取有勋章的直播间失败，信息为{ret["message"]}')
                break
            page += 1

    return result

async def send_msg_task(biliapi: asyncbili,
                        rooms: List[int],
                        msg: str
                        ) -> Awaitable:
    su = 0
    for roomid in rooms:
        id = roomid
        retry = 2
        while retry:
            await sleep(3)
            try:
                ret = await biliapi.xliveRoomInit(id)
            except Exception as e:
                logging.warning(f'{biliapi.name}: 获取房间{id}的真实id异常，原因为{str(e)}')
            else:
                if ret["code"] == 0:
                    id = ret["data"]["room_id"]
                else:
                    logging.warning(f'{biliapi.name}: 获取房间{id}的真实id失败，信息为{ret["message"]}')

            try:
                ret = await biliapi.xliveMsgSend(id, msg)
            except Exception as e:
                logging.warning(f'{biliapi.name}: 直播在房间{id}发送信息异常，原因为{str(e)}，重试')
                retry -= 1
            else:
                if ret["code"] == 0:
                    if ret["message"] == '':
                        logging.info(f'{biliapi.name}: 直播在房间{id}发送信息成功')
                        su += 1
                        break
                    else:
                        logging.warning(f'{biliapi.name}: 直播在房间{id}发送信息，消息为{ret["message"]}，重试')
                        retry -= 1
                else:
                    logging.warning(f'{biliapi.name}: 直播在房间{id}发送信息失败，消息为{ret["message"]}，跳过')
                    break
    webhook.addMsg('msg_simple', f'{biliapi.name}:直播成功在{su}个房间发送消息\n')

async def heartbeat_task(biliapi: asyncbili,
                         room_id: int,
                         max_time: Union[int, float],
                         live_status: Iterator[int]
                         ) -> Awaitable:
    try:
        ret = await biliapi.xliveGetRoomInfo(room_id)
    except Exception as e:
        logging.warning(f'{biliapi.name}: 直播请求房间{room_id}信息异常，原因为{str(e)}，跳过直播心跳')
        webhook.addMsg('msg_simple', f'{biliapi.name}:直播心跳失败\n')
        return
    else:
        if ret["code"] != 0:
            logging.info(f'{biliapi.name}: 直播请求房间{room_id}信息失败，信息为：{ret["message"]}，跳过直播心跳')
            webhook.addMsg('msg_simple', f'{biliapi.name}:直播间{room_id}心跳失败\n')
            return
        if not ret["data"]["room_info"]["live_status"] in live_status:
            return
        parent_area_id = ret["data"]["room_info"]["parent_area_id"]
        area_id = ret["data"]["room_info"]["area_id"]
        room_id = ret["data"]["room_info"]["room_id"] #为了防止上面的id是短id，这里确保得到的是长id
    del ret

    retry = 2
    ii = 0
    try:
        async with timeout(max_time):
            async for code, data in xliveHeartBeatLoop(biliapi, 
                                                       parent_area_id, 
                                                       area_id, 
                                                       room_id): #每一次迭代发送一次心跳
                if code != 0:
                    if retry and code != -400:
                        logging.warning(f'{biliapi.name}: 直播{room_id}心跳错误，原因为{data}，重新进入房间')
                        retry -= 1
                        continue
                    else:
                        logging.warning(f'{biliapi.name}: 直播{room_id}心跳错误，原因为{data}，退出心跳')
                        break
                ii += 1
                logging.info(f'{biliapi.name}: 成功在id为{room_id}的直播间发送第{ii}次心跳')
                await sleep(data) #等待下一次迭代

    except TimeoutError:
        logging.info(f'{biliapi.name}: 直播{room_id}心跳超时{max_time}s退出')
    except CancelledError:
        logging.warning(f'{biliapi.name}: 直播{room_id}心跳任务被强制取消')
    except Exception as e:
        logging.warning(f'{biliapi.name}: 直播{room_id}心跳异常，异常为{str(e)}，退出直播心跳')
        webhook.addMsg('msg_simple', f'{biliapi.name}:直播{room_id}心跳发生异常\n')

async def xliveHeartBeatLoop(biliapi: asyncbili, 
                             parent_area_id: int, 
                             area_id: int, 
                             room_id: int
                             ) -> AsyncGenerator[Tuple[int, Union[int, str]], None]:
    '''心跳循环'''
    _uuid = str(uuid.uuid4())
    while True:
        num = 0
        ret = await biliapi.xliveHeartBeatE(parent_area_id,
                                            area_id,
                                            room_id,
                                            num,
                                            _uuid)
        if ret["code"] == 0:
            ets = ret["data"]["timestamp"]
            benchmark = ret["data"]["secret_key"]
            interval = ret["data"]["heartbeat_interval"]
            secret_rule = ret["data"]["secret_rule"]
            num += 1
            yield 0, interval
        else:
            yield ret["code"], ret["message"]
            continue

        while True:
            num += 1
            ret = await biliapi.xliveHeartBeatX(parent_area_id,
                                                area_id,
                                                room_id,
                                                num,
                                                _uuid,
                                                ets,
                                                benchmark,
                                                interval,
                                                secret_rule
                                                )
            if ret["code"] == 0:
                ets = ret["data"]["timestamp"]
                benchmark = ret["data"]["secret_key"]
                interval = ret["data"]["heartbeat_interval"]
                secret_rule = ret["data"]["secret_rule"]
                num += 1
                yield 0, interval
            else:
                yield ret["code"], ret["message"]
                break