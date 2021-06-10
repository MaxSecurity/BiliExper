# python实现B站发布专栏、动态、视频和音频的方法

这里是使用python发布B站专栏、动态、视频和音频的方法，并带有4个例子和详细说明。

# 目录

- [项目说明](#python实现B站发布专栏和视频方法)
- [目录](#目录)
- [准备环境](#准备环境)
- [发布专栏稿件](#发布专栏稿件)
  - [创建一个专栏草稿](#创建一个专栏草稿)
  - [添加内容](#在专栏草稿上添加内容)
  - [添加复杂字体](#在专栏草稿上添加更复杂的内容)
  - [添加不同大小的字体和引用内容](#在专栏草稿上添加不同大小的字体和引用内容)
  - [添加有序列表和无序列表](#在专栏草稿上添加有序列表和无序列表)
  - [添加超链接文字(站内跳转链接)](#在专栏草稿上添加一个超链接文字站内跳转链接)
  - [添加图片](#在专栏草稿上添加一个图片)
  - [添加引用标签](#在专栏草稿上添加一个引用标签)
  - [添加投票](#在专栏草稿上添加一个投票)
  - [设置专栏信息](#设置专栏除内容外的详细信息)
- [发布动态](#发布动态)
- [发布视频稿件](#发布视频稿件)
- [发布音频稿件](#发布音频稿件)
  - [发布一个单曲音频稿件](#发布一个单曲音频稿件)
  - [发布一个合辑音频稿件](#发布一个合辑音频稿件)
- [例子(在本文件夹下)](#这里是一些机器人up主脚本)

</br>

## 准备环境

* 1.安装requests和aiohttp库分别用于http同步请求和异步请求
    ```
	pip install requests aiohttp
	```
* 2.在本地创建新项目，将本项目的***BiliClient***文件夹放到项目根目录中

## 发布专栏稿件

### 创建一个专栏草稿

```
from BiliClient import Article

cookies = { #这里是账号登录后获得的cookie
    "SESSDATA": "4a5f1c63%2C1617173721%2Cdf9fc*a1",
    "bili_jct": "cf28bac01cd7d443646907a5c4da8cf1",
    }

article = Article(cookies, "测试专栏") #创建一个测试专栏
```
执行上面代码后，就创建了一个标题为"测试专栏"的空专栏</br>
![image](https://user-images.githubusercontent.com/67217225/99678313-a2943080-2ab5-11eb-86f2-76498a0e11d7.png)

### 在专栏草稿上添加内容

```
from BiliClient import Article

cookies = { #这里是账号登录后获得的cookie
    "SESSDATA": "4a5f1c63%2C1617173721%2Cdf9fc*a1",
    "bili_jct": "cf28bac01cd7d443646907a5c4da8cf1",
    }

article = Article(cookies, "测试专栏") #创建一个测试专栏

content = article.Content() #创建一个专栏内容
content.startP().add('测试内容').endP()
# 开始一个段落   添加文字    结束一个段落

article.save() #保存内容至草稿箱，然后可以去B站专栏草稿箱看到
```
执行上面代码后，就创建了一个标题为"测试专栏"，内容为"测试内容"的专栏</br>
![image](https://user-images.githubusercontent.com/67217225/99679524-fd7a5780-2ab6-11eb-8aa1-3cd754d3aeb0.png)
总结，startP()与endP()之间可以包含一个段落的内容，用add()添加内容</br>
article.setContent(content)将创建的内容绑定到article专栏上</br>
article.save()保存专栏至B站草稿箱</br>


### 在专栏草稿上添加更复杂的内容

```
from BiliClient import Article

cookies = { #这里是账号登录后获得的cookie
    "SESSDATA": "4a5f1c63%2C1617173721%2Cdf9fc*a1",
    "bili_jct": "cf28bac01cd7d443646907a5c4da8cf1",
    }

article = Article(cookies, "测试专栏") #创建一个测试专栏

content = article.Content() #创建一个专栏内容
content.startH().add("测试标题").endH()
#     标题开始      添加文字      标题结束
content.startP().add('测试内容').endP()
#      段落开始   添加文字    段落结束
content.br() #换行，切换到下一行
content.startP().add('第二行测试内容：').startB().add('这里是加粗字体').endB().endP()
#      段落开始      添加文字             加粗开始      添加内容      加粗结束  段落结束
content.br() #换行，切换到下一行
content.startP().add('第三行测试内容：').startD().add('这里是下划线字体').endD().endP()
#      段落开始      添加文字             删除线开始      添加内容   删除线结束  段落结束

article.save() #保存内容至草稿箱，然后可以去B站专栏草稿箱看到
```
![image](https://user-images.githubusercontent.com/67217225/99682493-3a941900-2aba-11eb-98c7-1398fdf00c30.png)
总结，startB()和endB()之间可以包含一个加粗的内容</br>
startD()和endD()之间可以包含一个加删除线的内容</br>
br()切换到下一行</br>
大部分文本内容都可以直接嵌套</br>
可以看到上面每行之间***额外多了一个换行***(换了两次行)，因为B站默认段落结束就会换行，所以不用特地加一个br()来换行</br>

### 在专栏草稿上添加不同大小的字体和引用内容

```
from BiliClient import Article

cookies = { #这里是账号登录后获得的cookie
    "SESSDATA": "4a5f1c63%2C1617173721%2Cdf9fc*a1",
    "bili_jct": "cf28bac01cd7d443646907a5c4da8cf1",
    }

article = Article(cookies, "测试专栏")

content = article.Content()
content.startH().add("测试标题").endH()
content.startP().add('测试不同大小文字：').startS(12).add('小号字体').endS().startS(16).add('标准字体').endS().startS(20).add('大号字体').endS().startS(23).add('特大字体').endS().endP()
content.startP().add('测试引用内容：').startY().add('这里是引用内容').endY().endP()

article.save()
```
![image](https://user-images.githubusercontent.com/67217225/99684649-a6778100-2abc-11eb-906d-627e8ced29d5.png)
总结，startS()和endS()之间可以包含一个不同字体大小的内容，其中startS()还要提供一个字体大小，分别为12,16,20,23 </br>
startY()和endY()之间可以包含一段引用的内容</br>

### 在专栏草稿上添加有序列表和无序列表

```
from BiliClient import Article

cookies = { #这里是账号登录后获得的cookie
    "SESSDATA": "4a5f1c63%2C1617173721%2Cdf9fc*a1",
    "bili_jct": "cf28bac01cd7d443646907a5c4da8cf1",
    }

article = Article(cookies, "测试专栏")

content = article.Content()
content.startH().add("测试标题").endH()
content.startP().add("测试有序列表").endP()
content.startO()
content.startL().add('列表1').endL()
content.startL().add('列表2').endL()
content.startL().add('列表3').endL()
content.endO()
content.startP().add("测试无序列表").endP()
content.startU().startL().add('列表1').endL().startL().add('列表2').endL().startL().add('列表3').endL().endU()

article.save()
```
![image](https://user-images.githubusercontent.com/67217225/99686845-f48d8400-2abe-11eb-8a92-6fd00fbce140.png)
总结，startO()和endO()之间指定一个有序列表，startL()和endL()之间指定每个列表项的内容，有序列表前面会自动标记序号 </br>
startU()和endU()之间指定一个无序列表，startL()和endL()之间指定每个列表项的内容，无序列表前面会自动加一个黑点 </br>

### 在专栏草稿上添加一个超链接文字(站内跳转链接)

```
from BiliClient import Article

cookies = { #这里是账号登录后获得的cookie
    "SESSDATA": "4a5f1c63%2C1617173721%2Cdf9fc*a1",
    "bili_jct": "cf28bac01cd7d443646907a5c4da8cf1",
    }

article = Article(cookies, "测试专栏")

content = article.Content()
content.startH().add("测试标题").endH()
content.startP().add("测试超链接").startA("https://www.bilibili.com/video/BV12z4y1y72W").add("点击跳转到视频").endA().endP()

article.save()
```
![image](https://user-images.githubusercontent.com/67217225/99687914-26ebb100-2ac0-11eb-8c86-2a5286161fca.png)
总结，startA()和endA()之间指定一个蓝链(超链接)，startA()参数需要指定一个站内链接，目前B站不支持站外链接 </br>

### 在专栏草稿上添加一个图片

```
from BiliClient import Article

cookies = { #这里是账号登录后获得的cookie
    "SESSDATA": "4a5f1c63%2C1617173721%2Cdf9fc*a1",
    "bili_jct": "cf28bac01cd7d443646907a5c4da8cf1",
    }

article = Article(cookies, "测试专栏")

content = article.Content()
content.startH().add("测试标题").endH()
content.startP().add("测试B站站内图片链接").endP()
content.picUrl("https://i0.hdslb.com/bfs/article/d74e83cf96a9028eb3e280d5f877dce53760a7e2.jpg@1280w_800h.webp", "测试链接图片", "300px", "200px")
content.startP().add("测试插入本地图片").endP()
fp = open("E:\mydocument\desktop\下载.png", "rb")
content.picFile(article, fp, "测试本地图片", "50%", "50%")
fp.close()

article.save()
```
![image](https://user-images.githubusercontent.com/67217225/99689295-c8273700-2ac1-11eb-8029-b6086b665ecb.png)
总结，picUrl()可以插入一个B站站内图片，带四个参数分别为站内图片地址，图片下端说明(可不要),图片宽度和图片长度(可用单位px和%) </br>
picFile()可以插入一个本地图片(先用python open()函数打开)，注意第一个参数是前面创建过的article，第二个参数是打开的图片文件，后三个参数与picUrl()一致 </br>

### 在专栏草稿上添加一个引用标签

```
from BiliClient import Article

cookies = { #这里是账号登录后获得的cookie
    "SESSDATA": "4a5f1c63%2C1617173721%2Cdf9fc*a1",
    "bili_jct": "cf28bac01cd7d443646907a5c4da8cf1",
    }

article = Article(cookies, "测试专栏")

content = article.content()
content.startH().add("测试标题").endH()
content.startP().add("添加一个视频引用").endP()
content.card("BV1sA411x77G", "video")
content.startP().add("添加一个专栏引用").endP()
content.card("cv8425507", "article")
content.startP().add("添加一个番剧引用").endP()
content.card("ss34714", "fanju")
content.startP().add("添加一个音乐引用").endP()
content.card("au1669670", "music")
content.startP().add("添加一个会员购引用").endP()
content.card("pw30563", "shop")
content.startP().add("添加一个漫画引用").endP()
content.card("28951", "caricature")
content.startP().add("添加一个直播引用").endP()
content.card("lv22321043", "live")

article.save()
```
![image](https://user-images.githubusercontent.com/67217225/99697307-98306180-2aca-11eb-9da5-91c97715a822.png)
总结，card()可以插入一个B站引用卡片，需要三个参数分别为article，id和类型，***注意注意id的前缀*** </br>

### 在专栏草稿上添加一个投票

```
from BiliClient import Article

cookies = { #这里是账号登录后获得的cookie
    "SESSDATA": "4a5f1c63%2C1617173721%2Cdf9fc*a1",
    "bili_jct": "cf28bac01cd7d443646907a5c4da8cf1",
    }

article = Article(cookies, "测试专栏")

content = article.Content()
content.startH().add("测试标题").endH()
content.startP().add("添加一个投票").endP()
vote = {
    "title": "投票标题",
    "desc": "投票说明",
    "type": 0, #0为文字投票，1为图片投票
    "duration": 604800,#投票时长秒,604800为一个星期，即一个星期后停止投票
    "choice_cnt": 1, #最多选择几个，选项个数上限由下面options内选项个数决定，1为最多选择一个
    "options": [
        {
            "desc": "选项1",
            "cnt": 0,
            "idx": 1 #选项序号，第一个选项为1
        },
        {
            "desc": "选项2",
            "cnt": 0,
            "idx": 2 #选项序号，第二个选项为2，以此类推更多选项
        }
        ]
    }
content.vote(vote) #增加一个投票

article.save()
```
![image](https://user-images.githubusercontent.com/67217225/99760914-ceec9300-2b2f-11eb-845e-3e82f752a08e.png)
总结，vote()可以插入一个投票，第一个参数是创建的文章article，第二个参数是一个dict字典对象 </br>

### 设置专栏除内容外的详细信息并发布
这个例子将专栏分区设置为"动画 → 动漫杂谈"，并给专栏添加了封面，设置为原创专栏
```
from BiliClient import Article

cookies = { #这里是账号登录后获得的cookie
    "SESSDATA": "4a5f1c63%2C1617173721%2Cdf9fc*a1",
    "bili_jct": "cf28bac01cd7d443646907a5c4da8cf1",
    }

article = Article(cookies, "测试专栏")

article.setCategory(4) #设置专栏分类，0为默认，4为动画 → 动漫杂谈，5为动画 → 动漫资讯，.....

article.setTid(4) #设置封面类型，4为单图封面，3为三图封面

article.setImage("https//i0.hdslb.com/bfs/article/d74e83cf96a9028eb3e280d5f877dce53760a7e2.jpg")
#设置专栏封面，将会在其他人进入专栏前显示出来

# article.setListId(0) 这里可以设置专栏文集编号，将发布的专栏放在已有的专栏文集中，没有文集则不需要

article.setOriginal(1) #将专栏设置为原创，0为非原创

article.save()
article.submit() #一旦执行submit()，专栏会立即发布，save()只是保存到草稿箱，必须先save()再submit()
```
总结，setCategory()设置专栏分类，需要提供一个整数的分类编号 </br>
setTid()设置封面类型，提供一个整数作为类型编号，4为单图封面，3为三图封面 </br>
setImage()设置专栏封面，需要提供一个图片链接 </br>
setListId()设置专栏所属于的文集，需要提供一个整数的文集编号 </br>
setOriginal()设置专栏是否属于原创，1为原创，2为非原创 </br>
submit() 立即发布专栏，save()只是保存到草稿箱，必须先save()再submit() </br>

## 发布动态
这个例子将创建一个B站带图片和投票的动态
```
from BiliClient import Dynamic

cookies = { #这里是账号登录后获得的cookie
    "SESSDATA": "4a5f1c63%2C1617173721%2Cdf9fc*a1",
    "bili_jct": "cf28bac01cd7d443646907a5c4da8cf1",
    }

dynamic = Dynamic(cookies)

content = dynamic.Content()

content.add("这是一个测试动态----测试@别人").at('超级抽奖王', 203984353) #at推荐带uid，如果只有用户名搜索出来的uid可能不正确

content.add("测试添加一个测试话题").add(" #测试# ")

content.add("测试添加一个投票")
vote = {
    "title": "投票标题",
    "desc": "投票说明",
    "type": 0, #0为文字投票，1为图片投票
    "duration": 604800,#投票时长秒,604800为一个星期，即一个星期后停止投票
    "choice_cnt": 1, #最多选择几个，选项个数上限由下面options内选项个数决定，1为最多选择一个
    "options": [
        {
            "desc": "选项1",
            "cnt": 0,
            "idx": 1 #选项序号，第一个选项为1
        },
        {
            "desc": "选项2",
            "cnt": 0,
            "idx": 2 #选项序号，第二个选项为2，以此类推更多选项
        }
        ]
    }
content.vote(vote, "投票标题") #注意投票标题最多3个字，否则只会有前3个字变成蓝色，参考下图

content.add("测试添加图片")
content.picFile(r'E:\mydocument\desktop\njbnjbj.jpg') #注意图片在任何位置添加实际上都在动态末尾

dynamic.submit() #提交动态
```
![image](https://user-images.githubusercontent.com/67217225/112724884-5fa90480-8f50-11eb-8016-8587c51bbc89.png)

## 发布视频稿件
这个例子将本地文件`E:\测试视频.mp4`上传，将标题设置为"测试视频"，视频类型为转载，添加"搞笑"标签并把分区设置为 "生活，其他分区"
```
from BiliClient import VideoUploaderWeb as VideoUploader
import time

cookies = { #这里是账号登录后获得的cookie
    "SESSDATA": "4a5f1c63%2C1617173721%2Cdf9fc*a1",
    "bili_jct": "cf28bac01cd7d443646907a5c4da8cf1",
    }

video_uploader = VideoUploader(cookies, "测试视频") #创建一个视频发布任务，视频标题为"测试视频"
# video_uploader = VideoUploader(cookies) #也可以这样不提供标题，后面添加视频文件时自动使用文件名做标题

upvideo = video_uploader.uploadFile("E:\测试视频.mp4") #上传本地视频E:\测试视频.mp4到B站服务器

if not upvideo:  #这里判断视频是否上传成功
    print("上传失败")
    exit(0)

video_uploader.add(upvideo) #添加上面上传的视频到视频发布任务，一次发布多个视频(分P)需要使用VideoUploaderApp类而不是VideoUploaderWeb

video_uploader.setCopyright(2) #这个视频稿件是转载的
# video_uploader.setCopyright(1) #这个视频稿件是原创的

video_uploader.setSource("http://xx.com/") #如果是转载的，在这里添加源网址，发布后会显示在简介中，原创作品不需要

video_uploader.setDesc(f'这里是测试视频简介') #添加视频简介

print(video_uploader.getTags()) #视频上传后，官方会推荐几个视频标签，这里把他显示出来

video_uploader.setTag(["搞笑", "标签2", "标签3"]) #这里给视频设置多个标签

time.sleep(10) #下面获取视频封面，先等10s让官方有时间生成封面
pics = video_uploader.recovers(upvideo) #上面上传视频得到upvideo后，官方会自动提供几个封面选择作为视频封面
print(pics) #pics为上面获取的官方提供的封面，这里显示出来

video_uploader.setCover(pics[0]) #将官方给的第一个封面作为视频封面，也可以提供一个url自定义封面
#video_uploader.setCover(r"E:\1.jpg") #将本地图片设置为封面

video_uploader.setTid(174) #设置分区编号，174为 生活，其他分区

video_uploader.submit() #这里发布视频，发布后会审核

#video_uploader.delete() #这里删除视频，删除视频会扣除硬币
```

## 发布音频稿件

### 发布一个单曲音频稿件
这个例子将本地文件`E:\测试音频.mp3`上传，将标题设置为"测试音频"
```
from BiliClient import AudioUploader

cookies = { #这里是账号登录后获得的cookie
    "SESSDATA": "4a5f1c63%2C1617173721%2Cdf9fc*a1",
    "bili_jct": "cf28bac01cd7d443646907a5c4da8cf1",
    }

au = AudioUploader(cookies)
au.setSongFile(r'E:\测试音频.mp3')
#au.setTitle('测试音频') #不设置默认与文件名相同
au.setImage(r'E:\测试音频封面.jpg') #设置音频封面
au.setLyric(r'E:\测试音频歌词.lrc') #设置音频歌词，lrc歌词文件

au.setMusicType("人声演唱") #设置声音类型
au.setCreationType("原创") #设置创作类型
au.setLanguageType("华语") #设置音频语言
au.setThemeType("网络歌曲") #设置主题来源
au.setStyleType("流行") #设置风格类型

au.setSingers(["歌手1", "歌手2"]) #设置音频歌手(数组)
au.setLyricist(["作词者1", "作词者2"]) #设置音频作词者(数组)
au.setComposers(["作曲者1", "作曲者2"]) #设置音频歌手(数组)

au.setIntro("好听的歌") #设置音频简介

song_id, msg = au.submit()

if song_id:
    print(f'发布音频稿件成功，音频id为{song_id}')
else:
    print(f'发布音频稿件失败，信息为{msg}')
```

### 发布一个合辑音频稿件
这个例子将本地文件`E:\测试音频1.mp3`和`E:\测试音频2.mp3`上传，将音频合辑标题设置为"测试音频合辑"
```
from BiliClient import CompilationUploader

cookies = { #这里是账号登录后获得的cookie
    "SESSDATA": "4a5f1c63%2C1617173721%2Cdf9fc*a1",
    "bili_jct": "cf28bac01cd7d443646907a5c4da8cf1",
    }

cu = CompilationUploader(cookies) #创建合辑
aus = [] #数组存放音频

au = cu.createAudio(r'E:\测试音频1.mp3', r'E:\测试音频歌词1.lrc') #创建音频1
au.setSingers(["歌手1", "歌手2"]) #设置音频歌手(数组)
au.setLyricist(["作词者1", "作词者2"]) #设置音频作词者(数组)
au.setComposers(["作曲者1", "作曲者2"]) #设置音频歌手(数组)
aus.append(au) #添加到音频数组

au = cu.createAudio(r'E:\测试音频2.mp3', r'E:\测试音频歌词2.lrc') #创建音频2
au.setSingers(["歌手1", "歌手2"]) #设置音频歌手(数组)
au.setLyricist(["作词者1", "作词者2"]) #设置音频作词者(数组)
au.setComposers(["作曲者1", "作曲者2"]) #设置音频歌手(数组)
aus.append(au) #添加到音频数组

cu.setAudiosWithCommit(aus) #将音频1和音频2放进合辑，这一步提交音频进入B站审核状态

cu.setTitle('测试音频合辑') #设置合辑标题
cu.setImage(r'E:\测试音频封面.jpg') #设置合辑封面
cu.setIntro('合辑简介') #设置合辑简介
cu.setTypes(["人声演唱", "原创", "华语", "网络歌曲", "流行"]) #设置类型，数组

id, msg = cu.submit() #提交合辑，合辑进入审核状态，与音频审核是分开的

if song_id:
    print(f'发布音频合辑稿件成功，音频合辑id为{id}')
else:
    print(f'发布音频合辑稿件失败，信息为{msg}')
```

## 这里是一些机器人up主脚本

* “每日一抽”专栏发表机器人
    *  从动态中收集从昨天(0点)到今天(0点)的所有抽奖动态，整理后发表到专栏
    *  效果看我的B站专栏“每日一抽”系列 https://www.bilibili.com/read/cv7055733

* “随机图片”动态发布机器人
    *  从随机图片接口中下载张图片发布到动态

* “每日美图”专栏发表机器人
    *  从P站主页爬取一些图片，整理后发表到专栏
    *  有的图片无法通过审核
    *  效果看我的B站专栏“每日美图”系列 https://www.bilibili.com/read/cv7061587

* youtube视频搬运工
    *  利用pytube库下载youtube视频并转载到B站
    *  国内无法使用