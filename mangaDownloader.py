# -*- coding: utf-8 -*-
from BiliClient import MangaDownloader, bili
import os, sys
from getopt import getopt
from json import dump
try:
    from json5 import load
except:
    from json import load

for path in ('./user.json', './config/user.json', '/etc/BiliExp/user.json', None):
    if path and os.path.exists(path):
        break

def print_format(string, way, width, fill= ' ',ed = ''):
    count = 0
    for word in string:
        if (word >='\u4e00' and word <= '\u9fa5') or word in ['；','：','，','（','）','！','？','——','……','、','》','《']:
            count+=1
    width = width-count if width>=count else 0
    print('{0:{1}{2}{3}}'.format(string,fill,way,width),end = ed,flush=True)

def manga_to_PDF(dir_path, one_file=True, width=None, height=None):
    if dir_path[-1] == '\\' or dir_path[-1] == '/':
        dir_path = dir_path[0:-1]
    if not os.path.isdir(dir_path):
        raise ValueError('传入的路径并非文件夹')

    from fitz import Document, Pixmap, Rect
    from glob import _iglob as glob

    if one_file:
        title = os.path.basename(dir_path)
        with Document() as doc:
            for file_path in glob(os.path.join(dir_path, "*", "*.jpg"), False, False):
                pixmap = Pixmap(file_path)
                if width and height:
                    pixmap = Pixmap(pixmap, width, height, None)
                elif width:
                    pixmap = Pixmap(pixmap, width, int(pixmap.height / pixmap.width * width), None)
                elif height:
                    pixmap = Pixmap(pixmap, int(pixmap.width / pixmap.height * height), height, None)
                rect = Rect(0, 0, pixmap.width, pixmap.height)
                page = doc.newPage(width=pixmap.width, height=pixmap.height)
                page.insertImage(rect, pixmap=pixmap)
            doc.save(os.path.join(dir_path, title + ".pdf"), deflate=True)

    else:
        for chap in glob(os.path.join(dir_path, "*"), False, True):
            title = os.path.basename(chap)
            with Document() as doc:
                for file_path in glob(os.path.join(chap, "*.jpg"), False, False):
                    pixmap = Pixmap(file_path)
                    if width and height:
                        pixmap = Pixmap(pixmap, width, height, None)
                    elif width:
                        pixmap = Pixmap(pixmap, width, int(pixmap.height / pixmap.width * width), None)
                    elif height:
                        pixmap = Pixmap(pixmap, int(pixmap.width / pixmap.height * height), height, None)
                    rect = Rect(0, 0, pixmap.width, pixmap.height)
                    page = doc.newPage(width=pixmap.width, height=pixmap.height)
                    page.insertImage(rect, pixmap=pixmap)
                doc.save(os.path.join(dir_path, title + ".pdf"), deflate=True)

def download_interactive(mag: MangaDownloader):
    id = int(input('请输入B站漫画id(整数，不带mc前缀)：'))
    path = input('请输入保存路径(默认当前目录)：')
    pdf = input('下载后是否合并为一个pdf(y/n)：')
    if not path:
        path = os.getcwd()

    mag.setComicId(id)
    print(f'开始下载漫画 "{mag.getTitle()}"')
    for ret in mag.downloadAll(path):
        print_format(ret.name, '<', 30)
        if ret.code == MangaDownloader.DownloadCode.Ok:
            print(' 下载成功')
        elif ret.code == MangaDownloader.DownloadCode.Locked:
            print(' 没有解锁')
        elif ret.code == MangaDownloader.DownloadCode.Error:
            print(' 下载失败')
    print('下载任务结束')

    if pdf.upper() == 'Y':
        print("正在合并下载图片为pdf")
        manga_to_PDF(os.path.join(path, title))
        print("合并完成")

def download_task(mag: MangaDownloader, params):
    title = mag.getTitle()
    print(f'开始下载漫画 "{title}"')
    if params["episode"]:
        ep_list = mag.getIndex()
        ep_len = len(ep_list)
        ep_P = set()
        for P in params["episode"].split(','):
            if '-' in P:
                start, end = P.split('-')
                for i in range(int(start), int(end)+1):
                    if i <= ep_len:
                        ep_P.add(i-1)
            else:
                if int(P) <= ep_len:
                    ep_P.add(int(P)-1)
        download = mag.downloadIndexes(ep_P, params["path"])
    else:
        download = mag.downloadAll(params["path"])

    for ret in download:
        print_format(ret.name, '<', 30)
        if ret.code == MangaDownloader.DownloadCode.Ok:
            print(' 下载成功')
        elif ret.code == MangaDownloader.DownloadCode.Locked:
            print(' 没有解锁')
        elif ret.code == MangaDownloader.DownloadCode.Error:
            print(' 下载失败')
    print('下载任务结束')

def main(*args, **kwargs):
    interactive_mode = not (kwargs["manga"] or kwargs["pdf"])
    biliapi = bili()
    if interactive_mode or kwargs["manga"]:
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
            
    manga = MangaDownloader(biliapi)
    if interactive_mode:
        download_interactive(manga)
    else:
        if kwargs["manga"]:
            manga.setComicId(kwargs["manga"])
            download_task(manga, kwargs)
            kwargs["path"] = os.path.join(kwargs["path"], manga.getTitle())
        if kwargs["pdf"]:
            print("正在合并下载图片为pdf")
            manga_to_PDF(kwargs["path"], kwargs["split"], kwargs["width"], kwargs["height"])
            print("合并完成")

if __name__=="__main__":
    kwargs = {
        "manga": None,
        "episode": None,
        "pdf": False,
        "width": None, 
        "height": None,
        "split": True,
        "path": os.getcwd()
        }
    opts, args = getopt(sys.argv[1:], "hVfm:e:p:", ["help", "version", "pdf", "split", "manga=", "episode=", "path=", "width=", "height="])
    for opt, arg in opts:
        if opt in ('-h','--help'):
            print('mangaDownloader -p <下载文件夹> -m <漫画> -e <章节数> -f --width=<PDF每页宽度> --height=<PDF每页高度> --split')
            print(' -p --path      下载保存的路径，提供一个文件夹路径，没有会自动创建文件夹，不提供默认为当前文件夹')
            print(' -m --manga     下载的漫画mc号，整数')
            print(' -e --episode   章节数，不提供默认下载所有章节，多个用逗号分隔，连续用减号分隔  -e 2,3,5-7,10 表示2,3,5,6,7,10章节，注意番外也算一个章节')
            print(' -f --pdf       下载后合并为一个pdf，如果未指定-m --manga参数，则直接合并-p --path指定的文件夹内的jpg图片')
            print('    --width     合并为pdf时指定每页宽度(像素)，若未指定 --height 则会按漫画比例自适应高度，仅当使用-f --pdf参数后有效，否则忽略')
            print('    --height    合并为pdf时指定每页高度(像素)，若未指定 --width  则会按漫画比例自适应宽度，仅当使用-f --pdf参数后有效，否则忽略')
            print('    --split     合并为pdf时拆分每个章节为一个pdf，仅当使用-f --pdf参数后有效，否则忽略')
            print(' -V --version   显示版本信息')
            print(' -h --help      显示帮助信息')
            exit()
        elif opt in ('-V','--version'):
            print('B站漫画下载器 mangaDownloader v1.2.1')
            exit()
        elif opt in ('-p','--path'):
            kwargs["path"] = arg
        elif opt in ('-m','--manga'):
            kwargs["manga"] = int(arg)
        elif opt in ('-e','--episode'):
            kwargs["episode"] = arg
        elif opt in ('-f','--pdf'):
            kwargs["pdf"] = True
        elif opt == '--split':
            kwargs["split"] = False
        elif opt == '--width':
            kwargs["width"] = int(arg)
        elif opt == '--height':
            kwargs["height"] = int(arg)
    main(**kwargs)