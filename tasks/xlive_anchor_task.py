from BiliClient import asyncbili
import logging, time
from asyncio import TimeoutError, sleep
from aiohttp.client_exceptions import ServerDisconnectedError
from concurrent.futures import CancelledError
from async_timeout import timeout
from typing import AsyncGenerator, Awaitable, Dict, Any, List, Union, Tuple

async def xlive_anchor_task(biliapi: asyncbili,
                            task_config: Dict[str, Any]
                            ) -> Awaitable:
    '''天选时刻任务'''
    Timeout = task_config.get("timeout", 850)
    delay = task_config.get("delay", 0)
    follow_group = task_config.get("follow_group", None)
    unfollow = task_config.get("unfollow", True)
    clean_group_interval = task_config.get("clean_group_interval", 0)
    run_once = task_config.get("run_once", False)
    if follow_group:
        tagid = await getRelationTagByName(biliapi, follow_group)
        if tagid == -1:
            logging.warning(f'{biliapi.name}: 天选时刻指定关注分组不可用，退出任务')
            return
        if clean_group_interval != 0 and time.localtime(time.time() + 28800 + time.timezone).tm_mday % clean_group_interval == 0:
            await cleanGroup(biliapi, tagid)

    save_map = {}
    is_followed = True
    try:
        async with timeout(Timeout):
            while True:
                for area in task_config["search_areas"]:
                    async for room in xliveRoomGenerator(biliapi, area["paid"], area["aid"], area["sort"], area["ps"]):
                        if '2' in room["pendant_info"] and room["pendant_info"]["2"]["pendent_id"] == 504: #判断房间是否有天选时刻
                            if delay:
                                await sleep(delay)

                            ok, anchor = await getAnchorInfo(biliapi, room["roomid"]) #获取天选信息
                            if not ok or not anchor:
                                continue

                            if anchor["status"] != 1: #排除重复参加
                                continue

                            if anchor["id"] in save_map: #排除重复参加
                                continue

                            if not isJoinAnchor(anchor, task_config): #过滤条件
                                save_map[anchor["id"]] = None
                                continue

                            if not anchor["require_type"] == 1:
                                is_followed = True
                            elif unfollow or follow_group:  #需要取关或者需要加入用户组，提前判断是否已经关注
                                is_followed = await isUserFollowed(biliapi, room["uid"])

                            if follow_group and not is_followed:      #需要加入用户组但没有被关注，执行加入用户组
                                await relationAddUser(biliapi, room["uid"], tagid)

                            await anchorJoin(biliapi, anchor, room, is_followed or not unfollow, save_map) #参加天选时刻

                if run_once:
                    break
                await sleep(task_config["search_interval"])
                await cleanMapWithUnfollow(biliapi, save_map)
    
    except TimeoutError:
        logging.info(f'{biliapi.name}: 天选时刻抽奖任务超时({Timeout}秒)')
    except CancelledError:
        logging.warning(f'{biliapi.name}: 天选时刻抽奖任务被强制取消')
    except Exception as e:
        logging.warning(f'{biliapi.name}: 天选时刻抽奖任务异常，异常为({str(e)})')

    await cleanMapWithUnfollow(biliapi, save_map, True)

def isJoinAnchor(anchor: Dict[str, Any], 
                 condition: Dict[str, Any]
                 ) -> bool:
    if not anchor:
        return False
    if anchor["gift_price"] > condition["price_limit"]:
        return False
    if not [anchor["require_type"], anchor["require_value"]] in condition["anchor_type"]:
        return False
    if anchor["room_id"] in condition["room_filter"]:
        return False
    for gf in condition["gift_filter"]:
        if gf in anchor["award_name"]:
            return False
    for dm in condition["danmu_filter"]:
        if dm in anchor["danmu"]:
            return False
    return True

async def isUserFollowed(biliapi: asyncbili, 
                   uid: int
                   ) -> Awaitable[bool]:
    '''判断是否关注用户'''
    try:
        ret = await biliapi.getRelationByUid(uid)
    except CancelledError as e:
        raise e
    except Exception as e:
        logging.warning(f'{biliapi.name}: 天选判断与用户{uid}的关注状态失败，原因为({str(e)})，默认未关注')
        return False
    else:
        if ret["code"] == 0:
            return ret["data"]["attribute"] == 2
        else:
            logging.warning(f'{biliapi.name}: 天选判断与用户{uid}的关注状态失败，原因为({ret["message"]})，默认未关注')
            return False

async def anchorJoin(biliapi: asyncbili, 
                     anchor: dict,
                     room: dict,
                     is_followed: bool,
                     save_map: dict
                     ) -> Awaitable:
    '''参加天选时刻'''
    try:
        ret = await biliapi.xliveAnchorJoin(anchor["id"], anchor["gift_id"], anchor["gift_num"])
    except CancelledError as e:
        raise e
    except Exception as e:
        logging.warning(f'{biliapi.name}: 参与直播间{room["roomid"]}的天选时刻{anchor["id"]}异常，原因为({str(e)})')
    else:
        if ret["code"] == 0:
            save_map[anchor["id"]] = (room["roomid"], room["uid"], anchor["current_time"]+anchor["time"],not is_followed)
            logging.info(f'{biliapi.name}: 参与直播间{room["roomid"]}的天选时刻{anchor["id"]}({anchor["award_name"]})成功')

async def cleanMapWithUnfollow(biliapi: asyncbili, 
                        save_map: dict,
                        clean_all: bool = False
                        ) -> Awaitable:
    now_time = int(time.time())
    for k in list(save_map.keys()):
        if save_map[k]:
            if clean_all or now_time > save_map[k][2]:
                if save_map[k][3]:
                    await biliapi.followUser(save_map[k][1], 0)
                    logging.info(f'{biliapi.name}: 取关主播{save_map[k][1]}')
                del save_map[k]

async def getAnchorInfo(biliapi: asyncbili, 
                        room_id: int
                        ) -> Awaitable[Tuple[bool, Dict]]:
    '''获取房间天选时刻信息'''
    try:
        ret = await biliapi.getLotteryInfoWeb(room_id)
    except CancelledError as e:
        raise e
    except Exception as e:
        logging.warning(f'{biliapi.name}: 天选时刻抽奖任务获取直播间{room_id}抽奖信息异常，原因为({str(e)})')
        return False, None
    if ret["code"] != 0:
        logging.warning(f'{biliapi.name}: 天选时刻抽奖任务获取直播间{room["roomid"]}抽奖信息失败，信息为({ret["message"]})')
        return False, None
    return bool(ret["data"]["anchor"]), ret["data"]["anchor"]

async def xliveRoomGenerator(biliapi: asyncbili,
                             pAreaId: int,
                             AreaId: int,
                             sort: str,
                             page_num: int
                             ) -> AsyncGenerator:
    page = 0
    has_more = True
    while has_more:
        page += 1
        try:
            ret = await biliapi.xliveSecondGetList(pAreaId, AreaId, sort, page)
        except CancelledError as e:
            raise e
        except ServerDisconnectedError:
            logging.warning(f'{biliapi.name}: 获取直播间列表异常,原因为(服务器强制断开连接)')
            return
        except Exception as e:
            logging.warning(f'{biliapi.name}: 获取直播间列表异常,原因为({str(e)})')
            return
        else:
            if ret["code"] != 0:
                logging.warning(f'{biliapi.name}: 获取直播间列表失败,信息为({ret["message"]})')
                return

        for item in ret["data"]["list"]:
            yield item

        if page >= page_num:
            return

        has_more = ret["data"]["has_more"] == 1

async def getRelationTagByName(biliapi: asyncbili,
                               name: str,
                               auto_create: bool = True
                               ) -> Awaitable[int]:
    tagid = -1
    try:
        ret = await biliapi.getRelationTags()
    except CancelledError as e:
        raise e
    except Exception as e:
        logging.warning(f'{biliapi.name}: 天选获取用户分组失败,原因为({str(e)})')
    else:
        if ret["code"] != 0:
            logging.warning(f'{biliapi.name}: 天选获取用户分组失败,信息为({ret["message"]})')
        else:
            for tag in ret["data"]:
                if tag["name"] == name:
                    tagid = tag["tagid"]

    if tagid != -1 or not auto_create:
        return tagid

    try:
        ret = await biliapi.createRelationTag(name)
    except CancelledError as e:
        raise e
    except Exception as e:
        logging.warning(f'{biliapi.name}: 天选创建用户分组异常,原因为({str(e)})')
    else:
        if ret["code"] != 0:
            logging.warning(f'{biliapi.name}: 天选创建用户分组失败,信息为({ret["message"]})')
        else:
            return ret["data"]["tagid"]
    
    return tagid

async def relationAddUser(biliapi: asyncbili,
                          uid: int,
                          tagid: int
                          ) -> Awaitable[int]:
    await biliapi.followUser(uid, 1)
    await sleep(1)
    try:
        ret = await biliapi.relationTagsAddUser(uid, tagid)
    except CancelledError as e:
        raise e
    except Exception as e:
        logging.warning(f'{biliapi.name}: 天选将主播{uid}加入分组异常,原因为({str(e)})')
    else:
        if ret["code"] != 0:
            logging.warning(f'{biliapi.name}: 天选将主播{uid}加入分组失败,信息为({ret["message"]})')

async def cleanGroup(biliapi: asyncbili,
                     tagid: int
                     ) -> Awaitable:
    has = True
    while has:
        try:
            ret = await biliapi.getRelationTag(tagid)
        except CancelledError as e:
            raise e
        except Exception as e:
            logging.warning(f'{biliapi.name}: 天选获取分组用户异常,原因为({str(e)})')
            break
        else:
            if ret["code"] != 0:
                logging.warning(f'{biliapi.name}: 天选获取分组用户失败,信息为({ret["message"]})')
                break
        has = len(ret["data"]) == 50

        for x in ret["data"]:
            await biliapi.followUser(x["mid"], 0)
