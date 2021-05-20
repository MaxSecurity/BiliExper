# -*- coding: utf-8 -*-
import requests, re
from BiliClient import Article
try:
    from json5 import load
except:
    from json import load

with open('config/config.json','r',encoding='utf-8') as fp:
    configData = load(fp)

num = 18 #只爬取18张图,可以调大，如果中间网络异常会丢失几张图，最终数量可能达不到
PHPSESSID = '52458730_wl3M43DP4ulPM1iDt1WVqFMJNksegvG1' #必填，登录后获得的cookie


#创建B站专栏
article = Article(configData["users"][0]["cookieDatas"], "每日美图") #创建B站专栏草稿,并设置标题
content = article.Content() #创建content类编写文章正文
content.startP().add('所有图片均转载于').startB().add('网络').endB().add('，如有侵权请联系我，我会立即').startB().add('删除').endB().endP().br()
     #开始一段正文    添加正文           开始加粗  加粗文字  结束加粗                                                           结束一段文字  换行

#下面开始爬取P站图片
session = requests.session()
session.trust_env = True
session.proxies = {'http': '127.0.0.1:10809','https': '127.0.0.1:10809'}
session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36",
            "Referer": "https://www.pixiv.net/",
            "Accept-Encoding": "gzip, deflate, br",
            "Cookie": f'PHPSESSID={PHPSESSID}' #这里需要已登录的有效的PHPSESSID
            })
picList = session.get("https://www.pixiv.net/ajax/top/illust?mode=all&lang=zh").json()["body"]["thumbnails"]["illust"]
pics = []
imageUrl = ''
for i in range(num):
    id = picList[i]["id"]
    title = picList[i]["title"]
    url = f'https://www.pixiv.net/artworks/{id}'
    try:
        res = session.get(url)
        findurl = re.findall('.*?\"original\":\"(.*?)\"\}.*',res.text)[0]
        res = session.get(findurl) #这里得到P站图片
        imageUrl = article.imageFile2Url(res.content) #这里上传到B站，得到图片链接
    except:
        raise
    content.startP().startB().add(f'{i+1}.').endB().endP().picUrl(imageUrl, title) #将图片链接插入文章内容
                    #序号加粗                            插入图片链接(站内图片链接)和图片标题

article.setImage(imageUrl)  #将最后一张图片设置为专栏缩略图
article.setCategory(4)  #将专栏分类到"动画 → 动漫杂谈"
article.setOriginal(0)  #设置为非原创专栏,因为是转载的
article.save() #保存专栏至B站草稿箱
#article.submit() #发布专栏，注释掉后需要到article.getAid(True)返回的网址去草稿箱手动提交
