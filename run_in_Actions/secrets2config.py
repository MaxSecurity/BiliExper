# -*- coding: utf-8 -*-
# 用Secrets生成配置文件config.json

import json5, os, re, traceback
from collections import OrderedDict

ADVCONFIG: str = os.environ.get('ADVCONFIG', None)

if ADVCONFIG:
    print("已配置ADVCONFIG，用于覆盖config.json文件")
    with open('./config/config.json','w',encoding='utf-8') as fp:
        fp.write(ADVCONFIG)

BILICONFIG: str = os.environ.get('BILICONFIG', None)
PUSH_MESSAGE: str = os.environ.get('PUSH_MESSAGE', None)

if not (BILICONFIG or ADVCONFIG):
    print("secrets(BILICONFIG)和secrets(ADVCONFIG)至少填写一个，不提供账号cookie没办法登录")
    exit(-1)

try:
    with open('./config/config.json','r',encoding='utf-8') as fp:
        configData: dict = json5.load(fp, object_pairs_hook=OrderedDict)
except:
    print(f'配置文件加载失败，原因为({traceback.format_exc()})')
    print(f'此错误是由于配置文件不符合json5(json)格式导致的，如果您不了解json规范，建议您恢复config/config.json文件，删除advconfig(如果配置过)，仅使用biliconfig和push_message(可选)两个secrets')
    exit(-1)

if BILICONFIG:
    print("发现biliconfig，开始映射cookie")
    SESSDATA, bili_jct, DedeUserID = False, False, False
    users = []
    cookieDatas = {}
    for ii, x in enumerate(BILICONFIG.split("\n")):
        cookie = x.strip().replace(",", "%2C").replace("%2A", "*")
        if re.match("[a-z0-9]{8}%2C[0-9a-z]{10}%2C[a-z0-9]{5}.[a-z0-9]{2}", cookie):
            cookieDatas["SESSDATA"] = cookie
            SESSDATA = True
            print(f'biliconfig第{ii+1}行解析为SESSDATA')
        elif re.match("[a-z0-9]{31}", cookie):
            cookieDatas["bili_jct"] = cookie
            bili_jct = True
            print(f'biliconfig第{ii+1}行解析为bili_jct')
        elif re.match("^[0-9]{5,}$", cookie):
            cookieDatas["DedeUserID"] = cookie
            DedeUserID = True
            print(f'biliconfig第{ii+1}行解析为DedeUserID')
        else:
            print(f'biliconfig第{ii+1}行不能解析为cookie，跳过本行')
        if SESSDATA and bili_jct and DedeUserID:
            users.append({"cookieDatas": cookieDatas.copy(), "tasks": {}})
            SESSDATA, bili_jct, DedeUserID = False, False, False
            print(f'biliconfig成功添加1个账号')
    if len(users) == 0:
        print("虽然配置了BILICONFIG，但并没有发现有效账户cookie")
        exit(-1)
    else:
        configData["users"] = users

if PUSH_MESSAGE:
    print("发现push_message，开始映射到webhook消息推送")
    ADVCONFIG: str = os.environ.get('ADVCONFIG', None)
    if os.environ.get('SIMPLIFIED', '0') == '1':
        msg_type = 'msg_simple'
    else:
        msg_type = 'msg_raw'

    configData["webhook"] = {
        "http_header": {"User-Agent":"Mozilla/5.0"},
        "variable": {
            msg_type: None,
            "title": "B站经验脚本消息推送"
            }
        }
    i = 0
    webhooks = []
    for ii, x in enumerate(PUSH_MESSAGE.split("\n")):
        value = x.strip()
        if x.startswith("SCT"):
            i += 1
            webhooks.append({
                "name": f"server酱Turbo版消息推送{i}",
                "msg_separ": "\n\n",
                "method": 1,
                "url": f"https://sctapi.ftqq.com/{value}.send",
                "params": {
                    "text": "{title}",
                    "desp": f"{{{msg_type}}}" 
                }
            })
            print(f"push_message第{ii+1}行解析为server酱Turbo版消息推送")
        elif x.startswith("SCU"):
            i += 1
            webhooks.append({
                "name": f"server酱消息推送{i}",
                "msg_separ": "\n\n",
                "method": 1,
                "url": f"https://sc.ftqq.com/{value}.send",
                "params": {
                    "text": "{title}",
                    "desp": f"{{{msg_type}}}" 
                }
            })
            print(f"push_message第{ii+1}行解析为server酱消息推送")
        elif re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", value):
            i += 1
            webhooks.append({
                "name": f"邮箱消息推送{i}",
                "msg_separ": r"<br>",
                "method": 1,
                "url": "https://email.berfen.com/api",
                "params": {
                    "to": value,              # 收件人
                    "title": "{title}",       # 邮件标题
                    "text": f"{{{msg_type}}}" # 邮件内容
                }
            })
            print(f"push_message第{ii+1}行解析为邮箱消息推送")
        elif re.match("^[0-9a-z]{32}$", value):
            i += 1
            webhooks.append({
                "name": f"酷推个人QQ消息推送{i}",
                "method": 3,
                "url": f"https://push.xuthus.cc/send/{value}",
                "params": {
                    "c": f"{{{msg_type}}}"
                }
            })
            print(f"push_message第{ii+1}行解析为酷Q消息推送")
        else:
            ma = re.match("^([0-9]{7,11}:[0-9 a-z A-Z -_]*),(.*)$", value)
            if ma:
                i += 1
                ma = ma.groups()
                webhooks.append({
                    "name": f"telegram_bot消息推送{i}",
                    "method": 1,
                    "url": f"https://api.telegram.org/bot{ma[0]}/sendMessage",
                    "params": {
                        "chat_id": ma[1],
                        "text": f"{{{msg_type}}}" 
                    }
                })
                print(f"push_message第{ii+1}行解析为telegram_bot消息推送")
    configData["webhook"]["hooks"] = webhooks

with open('./config/config.json','w',encoding='utf-8') as fp:
    json5.dump(configData, fp, ensure_ascii=False)
