# -*- coding: utf-8 -*-
import requests, re
from BiliClient import Dynamic
try:
    from json5 import load
except:
    from json import load

num = 2  #单次发布图片数量，不能超过9

with open('config/config.json','r',encoding='utf-8') as fp:
    configData = load(fp)

dynamic = Dynamic(configData["users"][0]["cookieDatas"]) #登录
content = dynamic.Content()

content.add('随机二次元图片')

session = requests.sessions.Session()
for _ in range(num):
    content.picFile(session.get('https://www.dmoe.cc/random.php').content)

dynamic.submit()