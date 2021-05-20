# -*- coding: utf-8 -*-
#from BiliClient import VideoUploaderWeb as VideoUploader    # 模拟网页端上传，支持多线程但不能分P
from BiliClient import VideoUploaderApp  as VideoUploader, bili    # 模拟APP端上传，支持分P但没有多线程
from getopt import getopt
import os, sys, re, time
from json import dump
try:
    from json5 import load
except:
    from json import load

for path in ('./user.json', './config/user.json', '/etc/BiliExp/user.json', None):
    if path and os.path.exists(path):
        break
if not path:
    raise FileNotFoundError('未找到账户配置文件')

def main(*args, **kwargs):
    with open(path,'r',encoding='utf-8-sig') as fp:
        userData = load(fp)

    biliapi = bili()
    video_uploader = VideoUploader(biliapi)
    isLogin = False
    if userData["access_token"] and \
        biliapi.login_by_access_token(userData["access_token"], userData["refresh_token"]):
        ...
    elif userData["username"] and \
        userData["password"] and \
        biliapi.login_by_password(userData["username"], userData["password"]):
        userData["access_token"] = biliapi.access_token
        userData["refresh_token"] = biliapi.refresh_token
        with open(path,'w',encoding='utf-8') as fp:
            dump(userData, fp, ensure_ascii=False, indent=4)
    else:
        print("账户登录失败")
        exit(6)

    if not kwargs["path"]:
        raise ValueError('未提供视频文件路径')
    if kwargs["cover"] and not os.path.exists(kwargs["cover"]):
        raise FileNotFoundError(kwargs["cover"])

    if kwargs["tid"]:
        video_uploader.setTid(kwargs["tid"])
    if kwargs["title"]:
        video_uploader.setTitle(kwargs["title"])
    if kwargs["desc"]:
        video_uploader.setDesc(kwargs["title"])
    if kwargs["nonOriginal"]:
        video_uploader.setCopyright(2)
    else:
        video_uploader.setCopyright(1)
    if kwargs["source"]:
        video_uploader.setSource(kwargs["source"])
    if kwargs["dtime"]:
        video_uploader.setDtime(kwargs["dtime"])

    print('正在上传中.....')
    for v in kwargs["path"]:
        fname, fename = os.path.split(v)
        video_info = video_uploader.uploadFileOneThread(v)
        video_uploader.add(video_info)
        print(f'上传"{fename}"成功')

    if kwargs["cover"]:
        video_uploader.setCover(kwargs["cover"])

    if kwargs["tags"]:
        video_uploader.setTag(kwargs["tags"])
    else:
        video_uploader.setTag(video_uploader.getTags()[0:1])

    result = video_uploader.submit()
    if result["code"] == 0:
        print(f'提交成功，av{result["data"]["aid"]}，{result["data"]["bvid"]}')
    else:
        print(f'提交失败,原因为{result["message"]}')

if __name__=="__main__":
    kwargs = {
        "path": [],
        "title": None,
        "desc": None,
        "cover": None,
        "tid": 174,
        "tags": None,
        "nonOriginal": False,
        "source": None,
        "dtime": 0
        }
    opts, args = getopt(sys.argv[1:], "hVnSv:t:d:c:i:T:s:D:", ["help", "version", "nonOriginal", "singleThread", "videopath=", "title=", "desc=", "cover=", "tid=", "tags=", "source=", "DelayTime="])
    for opt, arg in opts:
        if opt in ('-h','--help'):
            print('VideoUploader -v <视频文件路径> -t <视频标题> -d <视频简介> -c <视频封面图片路径> -t <视频标签> -n -s <非原创时视频来源网址>')
            print(' -v --videopath     视频文件路径')
            print(' -t --title         视频标题，不指定默认为视频文件名')
            print(' -d --desc          视频简介，不指定默认为空')
            print(' -c --cover         视频封面图片路径，不提供默认用官方提供的第一张图片')
            print(' -i --tid           分区id，默认为174，即生活,其他分区')
            print(' -T --tags          视频标签，多个标签用半角逗号隔开，带空格必须打引号，不提供默认用官方推荐的前两个标签')
            print(' -n --nonOriginal   勾选转载，不指定本项默认为原创')
            print(' -s --source        -n参数存在时指定转载源视频网址')
            print(' -D --DelayTime     发布时间戳,10位整数,官方的延迟发布,时间戳距离现在必须大于4小时')
            print(' -V --version       显示版本信息')
            print(' -h --help          显示帮助信息')
            print('以上参数中只有-v --videopath为必选参数，其他均为可选参数')
            exit()
        elif opt in ('-V','--version'):
            print('B站视频上传器 videoDownloader v1.2.1')
            exit()
        elif opt in ('-v','--videopath'):
            kwargs["path"].append(arg)
        elif opt in ('-t','--title'):
            kwargs["title"] = arg
        elif opt in ('-d','--desc'):
            kwargs["desc"] = arg
        elif opt in ('-c','--cover'):
            kwargs["cover"] = arg
        elif opt in ('-i','--tid'):
            kwargs["tid"] = int(arg)
        elif opt in ('-T','--tags'):
            kwargs["tags"] = list(arg.split(','))
        elif opt in ('-n','--nonOriginal'):
            kwargs["nonOriginal"] = True
        elif opt in ('-s','--source'):
            kwargs["source"] = arg
        elif opt in ('-D','--DelayTime'):
            kwargs["dtime"] = int(arg)
    main(**kwargs)