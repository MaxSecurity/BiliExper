# -*- coding: utf-8 -*-
from BiliClient import VideoUploaderWeb as VideoUploader
import time
try:
    from json5 import load
except:
    from json import load
from pytube import YouTube

with open('config/config.json','r',encoding='utf-8') as fp:
    configData = load(fp)

url = input("请粘贴youtube视频完整链接后按回车：")
title = input("请输入B站发布标题(直接回车默认为视频标题)：")
tags = (input("请输入B站视频标签(必填,多个用英文逗号隔开)：")).split(',')
tid = input("请输入B站视频分区编号(直接回车默认为生活->其他分区)：")
if not tid:
    tid = 174

print("开始解析youtube视频")
video = YouTube(url)
for x in video.streams:
    print(x)
itag = input("请输入要下载的itag(直接回车默认为22)：")
if itag:
    filename = video.streams.get_by_itag(int(itag)).download()
else:
    filename = video.streams.get_by_itag(22).download()

bilivideo = VideoUploader(configData["users"][0]["cookieDatas"]) #创建B站视频发布任务
print(f'开始将{filename}上传至B站，请耐心等待')
vd = bilivideo.uploadFileOneThread(filename) #上传视频
if not vd:
    print("上传失败")
    exit(0)

print(f'上传完成,即将发布，请等待最多30s')
vd["title"] = title
bilivideo.add(vd)  #添加视频
#bilivideo.setTitle(title)
bilivideo.setCopyright(2)
#bilivideo.setDesc(f'转载于：{url}') #添加简介
bilivideo.setSource(url) #添加转载地址说明
if tid:
    bilivideo.setTid(int(tid)) #设置视频分区,默认为 生活，其他分区

bilivideo.setTag(list(tags)) #设置视频标签,数组,好像最多9个

i = 15
while(i):
    time.sleep(10) #B站需要足够的时间来生成封面
    pics = bilivideo.recovers(vd) #获取视频截图，刚上传的视频可能获取不到
    if len(pics):
        bilivideo.setCover(pics[0]) #设置视频封面
        break
    i -= 1

ret = bilivideo.submit() #提交视频发布
print(ret)
print("结束")
