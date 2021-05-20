# -*- coding: utf-8 -*-
from BiliClient import (VideoParser, Downloader, bili, Danmu2Ass)
import sys, re, time, curses, os
from getopt import getopt
from json import dump
try:
    from json5 import load
except:
    from json import load

is_win = os.name == 'nt'

ReverseProxy = 'http://biliapi.8box.top/playerproxy' #解析接口代理

for path in ('./user.json', './config/user.json', '/etc/BiliExp/user.json', None):
    if os.path.exists(path):
        break

def get_input_tasks(video_parser: VideoParser) -> list:
    '''通过控制台输入获得下载任务'''
    ret = []
    reverse = input('是否使用内部代理(可下载港澳台)(y/n)：').upper() == 'Y'
    add_another = True
    while add_another:
        url = input('请输入视频链接(或者av,bv号)：')
        video_parser.parser(url)
        print(f'当前视频标题为：{video_parser.getTitle()}')
        video_list = video_parser.all()
        if len(video_list) == 1:
            video = video_list[0]
        else:
            for ii in range(len(video_list)):
                print(f'{ii+1}. {video_list[ii]}')
            P = int(input('请输入要下载的分P序号：'))
            video = video_list[P-1]

        if reverse:
            video_stream_list = video.allStream(reverse_proxy=ReverseProxy)
        else:
            video_stream_list = video.allStream()

        for ii in range(len(video_stream_list)):
            print(f'{ii+1}. {video_stream_list[ii]}')

        P = int(input('请输入要下载的视频流序号：'))
        video_stream = video_stream_list[P-1]
        ret.append(video_stream)
        print('成功添加一个下载任务.....')
        add_another = input('是否再添加一个任务(y:再添加一个/n:立即开始下载)：').upper() == 'Y'
    return ret

def get_arg_tasks(video_parser: VideoParser, tasks: list) -> list:
    '''通过参数列表输入获得下载任务'''
    ret = []
    for xx in tasks:
        video_parser.parser(xx[0])
        video_list = video_parser.all()
        video_len = len(video_list)
        videos_P = set()
        for P in xx[1].split(','):
            if '-' in P:
                start, end = P.split('-')
                for i in range(int(start), int(end)+1):
                    if i <= video_len:
                        videos_P.add(i-1)
            else:
                if int(P) <= video_len:
                    videos_P.add(int(P)-1)
        for x in videos_P:
            video_stream_list = video_list[x].allStream(ReverseProxy if xx[3] == 1 else '')
            if not video_stream_list:
                continue
            if xx[2] < len(video_stream_list) - 1:
                ret.append(video_stream_list[xx[2]])
            else:
                ret.append(video_stream_list[-1])
    return ret

def downloader_put_tasks(downloader, tasks, path: str):
    '''将下载任务放进下载器'''
    if not os.path.exists(path):
        os.makedirs(path)
    for xx in tasks:
        downloader.add(url=xx.url, 
                       name=xx.fliename, 
                       dst=os.path.join(path, xx.fliename), 
                       headers={
                           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                           "Referer":"https://www.bilibili.com/"
                           })

def show(stdscr, tasklist: list, tasknum: tuple or list) -> None:
    stdscr.clear()
    if is_win:
        for ii in range(len(tasklist)):
            stdscr.addstr(ii*3, 0, ' '.join(f'正在下载:{tasklist[ii]["name"]}'))
            per = tasklist[ii]["completedLength"] / tasklist[ii]["totalLength"]
            perlen = int(per * 40)
            stdscr.addstr(ii*3+1, 0, f"进 度 : [{'*' * perlen}{' ' * (40 - perlen)}] {per*100:.2f}%")
        stdscr.addstr(ii*3+3, 0, f'任 务 总 数 {tasknum[0]}个 ,正 在 下 载 {tasknum[1]}个 ,等 待 中 {tasknum[2]}个 ,下 载 完 成 {tasknum[3]}个 ,失 败 任 务 {tasknum[4]}个 ')
    else:
        for ii in range(len(tasklist)):
            stdscr.addstr(ii*2, 5, f'正在下载: {tasklist[ii]["name"]}')
            per = tasklist[ii]["completedLength"] / tasklist[ii]["totalLength"]
            perlen = int(per * 40)
            stdscr.addstr(ii*2+1, 0, f"进度: [{'*' * perlen}{' ' * (40 - perlen)}] {per*100:.2f}%")
        stdscr.addstr(ii*2+2, 0, f'任务总数{tasknum[0]}个,正在下载{tasknum[1]}个,等待中{tasknum[2]}个,下载完成{tasknum[3]}个,失败任务{tasknum[4]}个')
    stdscr.refresh()

def queryDownloaderInfo(downloader):
    task_nums = [0, 0, 0, 0, 0]
    active_task = []
    for x in downloader.queryAll():
        task_nums[0] += 1
        if x["status"] == "active":
            task_nums[1] += 1
            active_task.append(x)
        elif x["status"] == "waiting":
            task_nums[2] += 1
        elif x["status"] == "over":
            task_nums[3] += 1
        elif x["status"] == "failed":
            task_nums[4] += 1

    return active_task, task_nums

def display(downloader: Downloader) -> None:
    '''显示进度'''
    stdscr = curses.initscr()
    curses.noecho()
    stdscr.keypad(True)
    while True:
        time.sleep(2)
        active_task, task_nums = queryDownloaderInfo(downloader)
        if not (task_nums[1] or task_nums[2]):
            break
        show(stdscr, active_task, task_nums)
    curses.endwin()

def download_danmu(tasks: list, path: str):
    '''下载弹幕'''
    if not os.path.exists(path):
        os.makedirs(path)
    for xx in tasks:
        xml = bili.dmList(xx.cid)
        Danmu2Ass(xml).toAssFile(os.path.join(path, xx.fliename + '.ass'))

def main(*args, **kwargs):
    biliapi = bili()
    if path:
        with open(path,'r',encoding='utf-8-sig') as fp:
            userData = load(fp)
        if userData["SESSDATA"] and \
           biliapi.login_by_cookie({"SESSDATA": userData["SESSDATA"]}):
            ...
        elif userData["access_token"] and \
            userData["refresh_token"] and \
            biliapi.login_by_access_token(userData["access_token"], userData["refresh_token"], True):
            userData["SESSDATA"] = biliapi.SESSDATA
            userData["bili_jct"] = biliapi.bili_jct
            userData["access_token"] = biliapi.access_token
            userData["refresh_token"] = biliapi.refresh_token
            with open(path,'w',encoding='utf-8') as fp:
                dump(userData, fp, ensure_ascii=False, indent=4)
        elif userData["username"] and \
            userData["password"] and \
            biliapi.login_by_password(userData["username"], userData["password"]):
            userData["SESSDATA"] = biliapi.SESSDATA
            userData["bili_jct"] = biliapi.bili_jct
            userData["access_token"] = biliapi.access_token
            userData["refresh_token"] = biliapi.refresh_token
            with open(path,'w',encoding='utf-8') as fp:
                dump(userData, fp, ensure_ascii=False, indent=4)
        else:
            print("当前处于未登录状态")
    else:
        print("当前处于未登录状态")

    video_parser = VideoParser(biliapi=biliapi)
    if kwargs["tasklist"]:
        tasks = get_arg_tasks(video_parser, kwargs["tasklist"])
    else:
        tasks = get_input_tasks(video_parser)

    del video_parser
    del biliapi

    if kwargs["ass"]:
        download_danmu(tasks, kwargs["path"])

    downloader = Downloader()
    downloader_put_tasks(downloader, tasks, kwargs["path"])
    downloader.startAll()
    display(downloader)
    print("下载结束")

if __name__=="__main__":
    kwargs = {
       "tasklist": [],
       "path": '.',
       "ass": False
        }
    episode, quality, proxy, video = [], [], [], []
    opts, args = getopt(sys.argv[1:], "hVav:e:q:p:x:", ["help", "version", "ass", "video=", "episode=", "quality=", "path=", "proxy="])
    for opt, arg in opts:
        if opt in ('-h','--help'):
            print('videoDownloader -p <下载文件夹> -a -v <视频1> -e <分集数> -q <质量序号> -v <视频2> -e <分集数> -q <质量序号> ...')
            print(' -a --ass       下载视频时附带ass文件,配合支持ass字幕的播放器可以显示弹幕')
            print(' -p --path      下载保存的路径，提供一个文件夹路径，没有会自动创建文件夹，默认为当前文件夹')
            print(' -v --video     下载的视频地址，支持链接，av号(avxxxxx)，BV号(BVxxxxxx)，ep，ss')
            print(' -e --episode   分p数，只对多P视频和多集的番剧有效，不提供默认为1，多个用逗号分隔，连续用减号分隔  -e 2,3,5-7,10 表示2,3,5,6,7,10集')
            print(' -q --quality   视频质量序号，0为能获取的最高质量(默认)，1为次高质量，数字越大质量越低')
            print(' -x --proxy     是否使用接口代理(可下载仅港澳台)，0为不使用(默认)，1为使用代理')
            print('注意，一个 -v 参数对应一个 -e(-q, -x) 参数，如果出现两个 -v 参数但只有一个 -e(-q, -x) 参数则只应用于第一个，可以有多个 -v 参数以一次性下载多个视频')
            print(' -V --version   显示版本信息')
            print(' -h --help      显示帮助信息')
            exit()
        elif opt in ('-V','--version'):
            print('B站视频下载器 videoDownloader v1.2.1')
            exit()
        elif opt in ('-p','--path'):
            kwargs["path"] = arg.replace(r'\\', '/')
        elif opt in ('-v','--video'):
            video.insert(0, arg)
        elif opt in ('-e','--episode'):
            episode.insert(0, arg)
        elif opt in ('-q','--quality'):
            quality.insert(0, int(arg))
        elif opt in ('-x','--proxy'):
            proxy.insert(0, int(arg))
        elif opt in ('-a','--ass'):
            kwargs["ass"] = True

    q = 0
    while video:
        e, x = '1', 0
        if episode:
            e = episode.pop()
        if proxy:
            x = proxy.pop()
        if quality:
            q = quality.pop()
        kwargs["tasklist"].append([video.pop(), e, q, x])

    main(**kwargs)