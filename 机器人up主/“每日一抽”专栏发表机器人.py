# -*- coding: utf-8 -*-
from BiliClient import bili
from BiliClient import Article
import time
try:
    from json5 import load
except:
    from json import load

# 本程序为B站专栏机器人，可以收集整理动态中一段时间内的抽奖消息，并整理
# 后发布到B站专栏中，效果看例子 https://www.bilibili.com/read/cv7055733

def listLott(cookie, endTime, startTime):
    "返回动态中从startTime到endTime之间的所有抽奖信息，endTime>startTime且endTime最好不要离当前时间太远"
    def lottInfo(lott):
        a = (("first_prize","second_prize","third_prize"),
             ("first_prize_cmt","second_prize_cmt","third_prize_cmt"),
             ("first_prize_pic","second_prize_pic","third_prize_pic"))
        array = []
        for i in range(3):
            if lott[a[0][i]]:
                xx = []
                xx.append(lott[a[1][i]])
                xx.append(str(lott[a[0][i]]))
                if lott[a[2][i]]:
                    xx.append(lott[a[2][i]])
                array.append(xx)
            else:
                break
        return array

    try:
        biliapi = bili()
        biliapi.login_by_cookie(cookie)
    except Exception as e: 
        print(f'登录验证id为{data["DedeUserID"]}的账户失败，原因为{str(e)}，跳过后续所有操作')
        return
    lottinfo = []
    datas = biliapi.getDynamic()
    for x in datas:
        stime = x["desc"]["timestamp"]
        if(stime > endTime):
            continue
        if(stime < startTime):
            break
        if 'extension' in x and 'lott' in x["extension"]: #若抽奖标签存在
            uname = x["desc"]["user_profile"]["info"]["uname"]  #动态的主人的用户名
            dyid = x["desc"]["dynamic_id"]  #动态id
            lott = biliapi.getLotteryNotice(dyid)["data"]
            etime = lott["lottery_time"]
            lottinfo.append({
                "name": uname,
                "stime": stime,
                "etime": etime,
                "dyid": dyid,
                "lott": lottInfo(lott)
                })
    return lottinfo

def buildContent(article, list):
    "编写专题文章正文"
    content = article.Content() #创建content类写文章正文
    content.br()\
        .picUrl("//i0.hdslb.com/bfs/article/d74e83cf96a9028eb3e280d5f877dce53760a7e2.jpg", width="640", height="400") #插入图片

    i = 0
    dengji = ("一等奖为：","二等奖为：","三等奖为：")
    for x in list:
        i += 1
        content.startP().add(f'{i}.抽奖发起者：{x["name"]}').endP()\
            .startP().add(f'发起时间：{time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(x["stime"]))}').endP()\
            .startP().add(f'开奖时间：{time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(x["etime"]))}').endP()\
            .startP().add('抽奖链接：').startA(f'https://t.bilibili.com/{x["dyid"]}').add('抽奖').endA().endP()
        ii = 0
        for y in x["lott"]:
            content.startP().add(dengji[ii]).startB().add(y[0]).endB().\
                add(',人数为').startB().add(y[1]).endB().endP()
            if len(y) == 3:
                content.picUrl(y[2], y[0], "30%", "30%") #如果抽奖有图片就插入图片,长宽为30%
            ii += 1

def main(*args):
    with open('config/config.json','r',encoding='utf-8') as fp:
        configData = load(fp)

    now_time = int(time.time())
    endtime = now_time - now_time % 86400 + time.timezone #今天0点
    starttime = endtime - 86400 #昨天0点
    list = listLott(configData["users"][0]["cookieDatas"], endtime, starttime) #返回自己动态里从starttime到endtime的所有抽奖信息
    article = Article(configData["users"][0]["cookieDatas"], "互动抽奖系列--每日一抽") #创建B站专栏,并设置标题
    buildContent(article, list) #创建文章内容

    article.setImage("//i0.hdslb.com/bfs/article/d74e83cf96a9028eb3e280d5f877dce53760a7e2.jpg","//i0.hdslb.com/bfs/article/05dd9f784a5426b59a85ba33cf0c9a13cab521be.jpg")
                #设置缩略图,本地图片请用article.articleUpcover()方法转换为链接
                #article.articleUpcover()方法可以上传图片，甚至可以把B站当成一个图床

    article.setOriginal(1) #将专栏设置为原创
    article.save() #保存专栏至B站草稿箱
    #article.submit() #发布专栏，注释掉后需要到article.getAid(True)返回的网址去草稿箱手动提交

if __name__=="__main__":
    main()