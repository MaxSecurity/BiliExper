from BiliClient import asyncbili
from .push_message_task import webhook
import logging, json

uid_map = {
    17561219: "直播小喇叭"
    }

async def msg_notify_task(biliapi: asyncbili,
                          task_config: dict
                          ):
    '''获取主站@和私信消息'''
    try:
        ret = await biliapi.msgFeedUnread()
    except Exception as e: 
        logging.warning(f'{biliapi.name}: 未读@消息数量获取异常，原因为({str(e)})')
        webhook.addMsg('msg_simple', f'{biliapi.name}:获取未读@消息失败\n')
    else:
        if ret["code"] == 0:
            msg_at_num = ret["data"]["at"]
            if msg_at_num > 0: #有人at
                webhook.addMsg('msg_simple', f'{biliapi.name}:有未读@消息{msg_at_num}条\n')
                try:
                    ret = await biliapi.msgFeedAt()
                except Exception as e: 
                    logging.warning(f'{biliapi.name}: 未读@消息获取异常，原因为({str(e)})')
                else:
                    if ret["code"] == 0:
                        for ii, item in enumerate(ret["data"]["items"]):
                            if ii >= msg_at_num:
                                break
                            try:
                                logging.info(f'{biliapi.name}: 收到({item["user"]["nickname"]})的@消息({item["item"]["source_content"]})')
                            except: 
                                ...
                    else:
                        logging.warning(f'{biliapi.name}: 未读@消息获取失败，信息为{ret["message"]}')
        else:
            logging.warning(f'{biliapi.name}: 未读@消息数量获取失败，信息为{ret["message"]}')
            webhook.addMsg('msg_simple', f'{biliapi.name}:获取未读@消息数量失败\n')

    try:
        ret = await biliapi.getSessions()
    except Exception as e: 
        logging.warning(f'{biliapi.name}: 未读私信消息获取异常，原因为({str(e)})')
        webhook.addMsg('msg_simple', f'{biliapi.name}:获取私信消息失败\n')
    else:
        if ret["code"] == 0:
            if 'session_list' in ret["data"]:
                for item in ret["data"]["session_list"]:
                    if item["unread_count"] == 0:
                        break
                    show_name = uid_map.get(item["last_msg"]["sender_uid"], item["last_msg"]["sender_uid"])
                    content = item["last_msg"]["content"]
                    find = None
                    for word in task_config["black_keywords"]:
                        if word in content:
                            find = word
                            break
                    if not find:
                        logging.info(f'{biliapi.name}: 收到({show_name})的私信消息{item["unread_count"]}条，最后一条消息为({content})')
                        webhook.addMsg('msg_simple', f'{biliapi.name}:收到({show_name})的私信消息{item["unread_count"]}条\n')
                    else:
                        logging.info(f'{biliapi.name}: 收到({show_name})的私信消息{item["unread_count"]}条，被关键字“{find}”过滤')
                    try:
                        ret = await biliapi.sessionUpdateAck(item["talker_id"], item["max_seqno"])
                    except Exception as e: 
                        logging.warning(f'{biliapi.name}: 设置{item["talker_id"]}消息为已读异常，原因为({str(e)})')
                    else:
                        if ret["code"] == 0:
                            logging.info(f'{biliapi.name}: 成功设置{item["talker_id"]}消息为已读')
                        else:
                            logging.warning(f'{biliapi.name}: 设置{item["talker_id"]}消息为已读失败，信息为{ret["msg"]}')
        else:
            logging.warning(f'{biliapi.name}: 未读私信消息获取失败，信息为{ret["msg"]}')
            webhook.addMsg('msg_simple', f'{biliapi.name}:获取私信消息失败\n')