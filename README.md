<div align="center"> 
<h1 align="center">
BiliExp
</h1>

![image](https://user-images.githubusercontent.com/67217225/96542531-d6bcdb80-12d4-11eb-81e1-49f3d3b85dfe.png)
<br>
[![](https://img.shields.io/badge/author-%E6%98%9F%E8%BE%B0-red "作者")](https://github.com/happy888888/ )
![](https://img.shields.io/badge/dynamic/json?label=GitHub%20Followers&query=%24.data.totalSubs&url=https%3A%2F%2Fapi.spencerwoo.com%2Fsubstats%2F%3Fsource%3Dgithub%26queryKey%3Dhappy888888&labelColor=282c34&color=181717&logo=github&longCache=true "关注数量")
<br>
![](https://img.shields.io/github/stars/happy888888/BiliExp.svg?style=plastic&logo=appveyor "Star数量")
![](https://img.shields.io/github/forks/happy888888/BiliExp.svg?style=plastic&logo=stackshare "Fork数量")
[![](https://img.shields.io/badge/LICENCE-SATA-BLUE.svg?style=plastic "协议")](https://github.com/zTrix/sata-license)
![](https://img.shields.io/badge/python->=3.6-GREEN.svg?style=social "python版本")
![](https://img.shields.io/github/contributors/happy888888/BiliExp "贡献者")
![](https://img.shields.io/github/downloads/happy888888/BiliExp/total?style=flat-square "下载量")
<br>
![](https://img.shields.io/docker/pulls/happy888888/biliexp?color=purple "docker拉取数")
![](https://img.shields.io/docker/image-size/happy888888/biliexp "docker镜像大小")

</div>

| ↳ Stargazers | ↳ Forkers |
|  :---:  | :---:  |
| [![Stargazers repo roster for @happy888888/BiliExp](https://reporoster.com/stars/happy888888/BiliExp)](https://github.com/happy888888/BiliExp/stargazers)  | [![Forkers repo roster for @happy888888/BiliExp](https://reporoster.com/forks/happy888888/BiliExp)](https://github.com/happy888888/BiliExp/network/members) |

# 项目说明

本项目为bilibili(哔哩哔哩,以下简称B站)助手，涵盖了B站视频主站，直播，漫画等领域，提供B站自动化养号(服务器挂机,多账户)，视频音频漫画下载，视频专栏音乐投稿等工具集，方便大家更好地使用B站。如果您对本项目有新的建议，想在本项目上添加新的功能，欢迎贡献你的想法，帮助本项目更好地发展。

</br>[转至目录快速使用](#目录)

## 主要功能
**一、B站自动操作脚本BiliExp.py**

* [x] 每日获取经验(投币(支持自定义up主)、点赞、分享视频) 
* [x] 自动转发互动抽奖并评论点赞(官抽，非官抽支持指定关键字如"#互动抽奖#",支持跟踪转发模式)(Actions上默认1天执行1次，1次转发过去1天的动态，云函数上每次只转发过去10分钟的动态，建议修改为每10分钟执行1次)
* [x] 获取主站@和私聊消息提醒(便于多账号抽奖时获取中奖信息)
* [x] 参与官方转盘抽奖活动(目前没有自动搜集活动的功能,需要在配置文件config/activities.json里面手动指定活动列表)
* [x] 每日直播签到
* [x] 直播挂机(获取小心心,点亮粉丝牌，云函数默认关闭此功能，Actions上默认每次每个粉丝牌房间分别挂机45分钟)
* [x] 直播自动送出快过期礼物(默认送出两天内过期的礼物)
* [x] 直播天选时刻抽奖 (支持条件过滤，云函数默认搜索1次后立即退出，Actions上默认执行45分钟后退出，云函数上建议10分钟执行1次)
* [x] 直播应援团每日签到 
* [ ] ~~直播开启宝箱领取银瓜子(本活动已结束，不知道B站以后会不会再启动)~~ 
* [x] 每日兑换银瓜子为硬币 
* [x] 自动领取大会员每月权益(B币劵，优惠券)
* [x] 自动花费大会员剩余B币劵(支持给自己充电、兑换成金瓜子或者兑换成漫读劵)
* [x] 漫画APP每日签到
* [x] 自动花费即将过期漫读劵(默认不开启)
* [x] 自动积分兑换漫画福利券(需中午12点启动，默认不开启)
* [x] 自动领取大会员漫画每月福利劵
* [ ] ~~自动参加每月"站友日"活动(本活动已结束，不知道B站以后会不会再启动)~~
* [x] 定时清理无效动态(转发的过期抽奖，失效动态，支持自定义关键字，非官方渠道抽奖无法判断是否过期，默认不开启本功能)
* [x] 风纪委员投票(云函数默认没有案件立即退出，Actions默认45分钟内没有案件自动退出，云函数上建议每20分钟运行1次)

***默认所有任务每天只执行1次***，但建议***云函数***上***风纪投票***，***抽奖转发***，***天选时刻***等任务每天***多次***执行，***Actions***上***风纪投票***，***天选时刻***，***直播挂机(领小心心)***等任务可以***设置更长的超时时间***(默认45分钟后退出)。
</br>使用这些功能可以参考一下[部分功能推荐配置](https://github.com/happy888888/BiliExp/issues/178)

</br>[转至目录快速使用](#目录)
</br>

**二、脚本up主系列**
* python实现B站专栏的编写，排版和发表
* python实现B站视频稿件的上传和发布
* python实现B站音频(lrc歌词)稿件(单曲和合辑)的上传和发布
</br>(例子和教程请参考[专栏、视频和音频的发表(面向开发者)](/机器人up主#python实现B站发布专栏视频和音频的方法)

</br>[命令行视频投稿工具](#使用说明视频投稿部分)

**三、B站漫画下载mangaDownloader.py**
* [x] 支持使用账号密码登录下载已解锁部分
* [x] 支持下载app端限时免费漫画(需登录)
* [x] 支持合并为单个pdf文件
</br>[快速使用](#使用方式下载器部分)
</br>

**四、B站视频下载videoDownloader.py**
* [x] 支持使用账号密码登录下载大会员视频
* [x] 支持下载港澳台番剧(内置一个反向代理接口，接口源码见"player_proxy"文件夹，支持阿里/腾讯云函数部署此接口)
* [x] 支持下载弹幕(转成ass字幕文件,需要用支持ass字幕的播放器打开,目前只支持滚动弹幕和顶部/底部弹幕,不支持高级弹幕)
</br>[快速使用](#使用方式下载器部分)
</br>

# 目录

- [项目说明](#项目说明)
  - [主要功能](#主要功能)
- [目录](#目录)
- [使用说明(仅自动操作脚本部分)](#使用方式仅自动操作脚本部分)
  - [零、部分功能推荐配置](https://github.com/happy888888/BiliExp/issues/178)
  - [一、只使用Actions(推荐)](#方式一推荐只使用github-actions)
  - [二、使用腾讯云函数(Actions部署)](#方式二使用腾讯云函数)
  - [三、使用阿里云函数(Actions部署)(不推荐)](#方式三不推荐使用阿里云函数)
  - [四、windows本地部署(依靠任务计划启动)](#方式四windows本地部署)
  - [五、linux本地部署(依靠crontab启动,shell自动下载安装)](#方式五linux本地部署)
  - [六、docker部署](#方式六docker安装)
  - [七、openwrt等路由器部署](#方式七openwrt等路由器部署)
- [使用说明(下载器部分)](#使用方式下载器部分)
- [使用说明(视频投稿部分)](#使用说明视频投稿部分)
- [使用说明(专栏、视频和音频的发表,面向开发者)](/机器人up主#python实现B站发布专栏视频和音频的方法)
- [更新日志](#更新日志)
- [欢迎打赏](#打赏)
- [获得B站账户cookies方法](#获得cookies方法)
- [一些实用的B站PC浏览器辅助小脚本](/browser_assist#这里是一些用于b站的浏览器辅助脚本)
  - [使用方式(仅适用pc浏览器)](/browser_assist#使用方式)
  - [脚本](/browser_assist#脚本列表)
    - [过期抽奖动态删除(目前已集成到自动操作脚本)](/browser_assist#所有过期抽奖动态删除)
    - [破解专栏不可复制](/browser_assist#b站专栏不可复制破解)
    - [删除关注up主](/browser_assist#删除关注的up主慎用)
    - [删除互粉粉丝](/browser_assist#删除互粉的粉丝慎用)
    - [关注话题页面up主(抽奖话题)](/browser_assist#关注话题页面up主主要是抽奖话题)
    - [b站自动新人答题](/browser_assist#b站自动答题非原创未测试)
</br>

## 使用方式(仅自动操作脚本部分)

***详细配置文件在/config/config.json，云函数部署后在/src/config/config.json，Actions上应使用secrets定义所有配置而不能直接修改config.json！！！***

### 方式一(推荐)、只使用github Actions
* 1.准备
    *  1.1 一个或多个B站账号，以及登录后获取的SESSDATA，bili_jct，DedeUserID (获取方式见下方示意图)
	   `浏览器打开B站主页--》按F12打开开发者工具--》application--》cookies`
	   
       <div align="center"><img src="https://s1.ax1x.com/2020/09/23/wjM09e.png" width="800" height="450" title="获取cookies示例"></div>
    *  1.2 fork本项目
	   本步骤目的是将Actions Workflow文件(.github/workflows/run_BiliExp.yml)文件放到你自己的仓库，当然你也可以不fork直接新建一个仓库将***.github/workflows/run_BiliExp.yml***文件放进去(路径保持一致)，如果这样做请不要跳过步骤3
* 2.部署
    *  2.1 在fork后的github仓库(或者你新建的存放run_BiliExp.yml的仓库)的 “Settings” --》“Secrets” 中添加"Secrets"，name(不用在意大小写)和value分别为：
        *  2.1.1 name为"biliconfig"           value为B站账号登录信息(可多个)，格式如下
        ```
        SESSDATA(账号1)
        bili_jct(账号1)
        uid(账号1)
		uid(账号2)
		bili_jct(账号2)
		SESSDATA(账号2)
		(多个账户继续加在后面，不用考虑每个账号三个参数的先后顺序)
        ```
        例如下面这样(例子为两个账号)
        ```
        e1272654%vfdawi241825%2C8dc06*a1
        0a9081cc53856314783d195f5ddbadf3
        203953353
        
        2035453
        dfs425cc53856351d4d5195f5ddbakb2
        e1412354%afdoii534825%2Cbbc06*a1
        ```
		注：每行一个cookie项(SESSDATA bili_jct uid或者空行)，***不规定顺序***但必须一个账户三个参数填完才能开始填下一个账户的参数
		![image](https://user-images.githubusercontent.com/67217225/98549976-73700900-22d6-11eb-9356-22802456da50.png)
        *  2.1.2 (可选)name为"push_message"           value为推送SCKEY或email或telegramBot_token或SKEY用于消息推送，格式如下
        ```
        SCU10xxxxxxxxxxxxxxxd547519b62d027xxxxxxxxx20f3578cbe6
		example@qq.com
		1443793198:AAEI9TGazdrj4Jh6X6B7CvuAKX4IivEb450,1459469720
		efa28782a2b4a7b25daz12f7d595ae26
        ```
		注：每行一个推送参数(SCKEY email telegramBot_token SKEY或者空行)，***可以同时提供多个或不提供SCKEY或email或telegramBot_token或SKEY，填写后会同时推送***,<br>
		***使用telegramBot的注意，除了填写token,还要填写chat_id,在同一行用逗号隔开***,比如例子提供的意思是telegram token为`1443793198:AAEI9TGazdrj4Jh6X6B7CvuAKX4IivEb450`,chat_id为`1459469720`,<br>
		***SCKEY来自server酱(微信推送)，email为你的邮箱，SKEY来自酷推(QQ推送)***
        *  2.1.3 (可选)name为"advconfig"           value为/config/config.json文件的所有内容(直接复制粘贴整个文件)
		***此项为详细配置文件，可配置所有细节参数，可直接替代前两个secrets也可以与前两个secrets共同使用，注意此项不存在时直接使用默认配置***<br>
		如果使用***天选时刻***，***风纪委员投票***和 ***直播心跳(获取小心心)*** 功能可参考 [部分功能推荐配置](https://github.com/happy888888/BiliExp/issues/178)
    *  2.2 添加完上面的"Secrets"后，进入"Actions" --》"run BiliExp"，点击右边的"Run workflow"即可第一次启动
        *  2.2.1 首次fork可能要去actions(正上方的actions不是Settings里面的actions)里面同意使用actions条款，如果"Actions"里面没有"run BiliExp"，点一下右上角的"star"，"run BiliExp"就会出现在"Actions"里面(先按照主分支说明切换分支否则找不到对应的Actions)
		![image](https://user-images.githubusercontent.com/67217225/98933791-16659480-251c-11eb-9713-c3dbcc6321bf.png)
		![image](https://user-images.githubusercontent.com/67217225/98934269-c935f280-251c-11eb-8bce-b8fa04c68cb8.png)
        *  2.2.2 第一次启动后，脚本会每天12:00自动执行，不需要再次手动执行(第一次手动执行这个步骤不能忽略)。
* 3.其他secrets
    *  3.1 repository
	   (可选)仓库名称，指定Actions执行时从哪个仓库获取代码，此项不存在时默认为你自己的仓库(也就是fork后的仓库)，也可以填写我的仓库`happy888888/BiliExp`
    *  3.2 ref
	   (可选)仓库分支名称或者sha，指定Actions执行时从仓库的哪个分支获取代码，此项不存在时默认为仓库默认分支的最新一次提交，也可以填写`master`
	```
	这两个secrets是用来当Actions和代码不在同一个仓库里使用的
	可以将 .github/workflows/run_BiliExp.yml 文件放到其他仓库里执行而不是fork本仓库
	当然fork本身是携带代码的，不需要配置这两个secrets即可使用
	```

### 方式二、使用腾讯云函数

* 1.准备
* 1.1开通云函数 SCF 的腾讯云账号，在[访问秘钥页面](https://console.cloud.tencent.com/cam/capi)获取账号的 TENCENT_SECRET_ID，TENCENT_SECRET_KEY
> 注意！为了确保权限足够，获取这两个参数时不要使用子账户！此外，腾讯云账户需要[实名认证](https://console.cloud.tencent.com/developer/auth)。
* 1.2依次登录 [SCF 云函数控制台](https://console.cloud.tencent.com/scf) 和 [SLS 控制台](https://console.cloud.tencent.com/sls) 开通相关服务，确保您已开通服务并创建相应[服务角色](https://console.cloud.tencent.com/cam/role) **SCF_QcsRole、SLS_QcsRole**
* 1.3一个或多个B站账号，以及登录后获取的SESSDATA，bili_jct，DedeUserID ([获得B站账户cookies方法](#获得cookies方法))
* 1.4fork本项目
* 2.部署
*  2.1 在fork后的github仓库的 “Settings” --》“Secrets” 中添加"Secrets"，name和value分别为：
    *  2.1.1 name为"TENCENT_SECRET_ID"           value为腾讯云用户SecretID(需要主账户，子账户可能没权限)
    *  2.1.2 name为"TENCENT_SECRET_KEY"          value为腾讯云账户SecretKey
		![image](https://user-images.githubusercontent.com/67217225/96539780-7aef5400-12ce-11eb-9af6-696286a44885.png)
		注意图片上的***BILICONFIG***仅供Actions使用，***云函数仍需要部署后在云函数控制台中/config/config.json文件中手动填入账号cookie***
*  2.2 添加完上面 2个"Secrets"后，进入"Actions"(上面那个不是Secrets下面那个) --》"deploy for serverless"，点击右边的"Run workflow"即可部署至腾讯云函数(如果出错请在红叉右边点击"deploy for serverless"查看部署任务的输出信息找出错误原因)
    *  2.2.1 首次fork可能要去actions里面同意使用actions条款，如果"Actions"里面没有"deploy for serverless"，点一下右上角的"star"，"deploy for serverless"就会出现在"Actions"里面
    *  2.2.2 部署完成后一定要去云函数控制台将账号cookie填写到/config/config.json文件中

### 方式三(不推荐)、使用阿里云函数

目前有发现在Actions内无法ping通阿里云函数的域名，部署可能出现超时现象

* 1.准备
    *  这里直接参考[腾讯云函数部署步骤](#方式二使用腾讯云函数)

* 2.部署
    *  2.1在fork后的github仓库的 “Settings” --》“Secrets” 中添加"Secrets"，name和value分别为：
        *  2.1.1 name为"ACCOUNT_ID"           value为阿里云用户的账号ID
        *  2.1.2 name为"ACCESS_KEY_ID"        value为阿里云账户AccessKeyID(需要主账户，子账户可能没权限)
        *  2.1.3 name为"ACCESS_KEY_SECRET"    value为阿里云账户accessKeySecret
		![image](https://user-images.githubusercontent.com/67217225/96539780-7aef5400-12ce-11eb-9af6-696286a44885.png)
    *  2.2这里直接参考[腾讯云函数部署步骤](#方式二使用腾讯云函数)中的2.2步骤

### 方式四、windows本地部署

* 1.准备
    *  1.1一个或多个B站账号，以及登录后获取的SESSDATA，bili_jct，DedeUserID ([获得B站账户cookies方法](#获得cookies方法))
    *  1.2进入右边的[release](https://github.com/happy888888/BiliExp/releases) ,下载BiliExp-win32_64开头的压缩包

* 2.部署
    *  2.1解压步骤1.2下载的压缩包，并放置到合适位置(比如E:\Program Files)
    *  2.2进入解压后产生的config文件夹，配置config.json文件(包含功能的启用和账号cookie的配置)
    *  2.3退出config文件夹返回上层，运行setup_for_windows.bat文件(需要管理员权限)，按照提示即可完成安装。脚本将会在每天12:00启动(依赖于计划任务)。

***如果电脑上已经安装python3环境，比起使用release版本，更推荐直接下载代码到本地运行，因为release版本可能是老旧的版本***
	
### 方式五、linux本地部署

* 1.准备
    *  1.1一个或多个B站账号，以及登录后获取的SESSDATA，bili_jct，DedeUserID ([获得B站账户cookies方法](#获得cookies方法))

* 2.部署
    *  2.1执行如下命令，并按照提示安装
	      ```
		  wget https://glare.now.sh/happy888888/BiliExp/BiliExp-Linux-64 && mv BiliExp-Linux-64* BiliExp.tar && tar xvf BiliExp.tar && cd BiliExp && sudo chmod 755 setup_for_linux.sh && sudo ./setup_for_linux.sh
		  ```
    *  2.2安装成功后，可去/etc/BiliExp/config.json文件中进行详细配置，脚本将会在每天12:00启动(依赖于crontab)。

***如果服务器上已经安装python3环境，比起使用release版本，更推荐直接clone代码到本地运行，因为release版本可能是老旧的版本***

### 方式六、docker安装

[docker hub地址](https://registry.hub.docker.com/repository/docker/happy888888/biliexp) 

* 1.准备
    *  1.1一个或多个B站账号，以及登录后获取的SESSDATA，bili_jct，DedeUserID (获取方式见最下方示意图),可选：SCKEY，email用于微信或邮箱的消息推送
    *  1.2安装docker(以安装可忽略) `curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun`

* 2.部署
    *  2.1填写本项目下config/config.json文件，放到本地任意文件夹下(以路径 '/home/user/Biliexp' 为例)
    *  2.2执行如下命令，运行BiliExp
	      ```
		  docker run \
		  -v /home/user/Biliexp:/BiliExp \
		  happy888888/biliexp:runner-latest 
		  ```
    *  2.3其他参数
	      ```
		  docker run \
		  -v /home/user/Biliexp:/BiliExp \
		  happy888888/biliexp:runner-latest \
		  -t <tag> \
		  -d \
		  -c <cron>
		  ```
		  `<tag>`表示版本号,可以使用`latest`(不指定时默认,表示最新版),`newest`(表示拉取最新主分支代码执行),指定版本号例如`1.1.0`,当指定版本号时代码会缓存到挂载的路径(上面的例子是主机的`/home/user/Biliexp/code-cache`目录),不指定版本号为每次拉取github代码<br>
		  `-d`指定本参数时容器不会退出，而是在每天中午12:00执行代码<br>
		  `<cron>`表示cron表达式,指定后会按照指定表达式的时间执行，默认为`0 12 * * *`即每天中午12点执行,此项参数在不指定`-d`时无效<br>
		  
		  例子,每天8点执行BiliExp 1.1.0版本<br>
	      ```
		  docker run -d -v /home/user/Biliexp:/BiliExp happy888888/biliexp:runner-latest -t 1.1.0 -d -c "0 8 * * *"
		  ```
* 3.支持平台
    |  平台   | tag标签  |
    |  ----  | ----  |
    | windows/linux(x64)  | runner-latest |
    | linux(arm32)  | runner-arm-latest |
    | linux(arm64)  | runner-arm64-latest |
	
* 4.注意事项
    *  4.1docker镜像中不包含本项目代码，docker启动时会自动下载
    *  4.2下载代码的版本号由参数`-t`指定，只有指定`-t 版本号`时才会缓存代码下次使用，`-t latest`和`-t newest`均为每次下载代码
    *  4.3缓存代码后每次只会执行缓存的代码,要更新版本必须删除缓存才会重新下载新代码(指定了`-t latest`(默认)和`-t newest`除外)
    *  4.4日志也存放在挂载目录中，且增量保存，可以定时清理
	
* 5.其他docker版本
除了不带代码的`runner`版本，也有携带代码的`happy888888/biliexp:latest`,`happy888888/biliexp:arm64-latest`版本docker镜像可以使用，这些版本执行后会立即退出不能指定参数常驻后台

### 方式七、openwrt等路由器部署

***此方式难度较大，如果能用其他方式请尽量使用其他方式***

* 1.准备
    *  1.1一个或多个B站账号，以及登录后获取的SESSDATA，bili_jct，DedeUserID (获取方式见最下方示意图),可选：SCKEY，email用于微信或邮箱的消息推送
    *  1.2使用xshell等工具,登录openwrt(padavan等)路由器，使用命令安装python3
	   ```
	   opkg update
	   opkg install python3-light
	   ```
    *  1.3安装python `aiohttp`库
	   `aiohttp`库在`openwrt`(`padavan`)等路由器的opkg软件源上并没有直接的安装包，需要自己下载项目源码在openwrt平台上构建<br>
	   如果你的路由器架构是`mipsel`，可以下载我编译好的依赖库(与本项目代码一起打包),[BiliExp_with_aiohttp-mipsel.zip](https://github.com/happy888888/BiliExp/files/5673033/BiliExp.zip)

* 2.部署
    *  2.1下载本项目代码(步骤1.3压缩包包含代码),解压,填写config/config.json文件
    *  2.2通过`xftp`(`WinScp`)等软件把解压的文件夹上传到路由器内(比如路径为/root/BiliExp)
    *  2.3设置crontab使代码定时启动
	   使用xshell等工具,登录openwrt(padavan等)路由器，输入命令
	   ```
	   echo "0 12 * * * /usr/bin/python3 /root/BiliExp/BiliExp.py -c /root/BiliExp/config/config.json" >> "/etc/crontabs/root"
	   ```
	   也可以在路由器网页上寻找类似***计划任务***的功能,在默认添加一行`0 12 * * * /usr/bin/python3 /root/BiliExp/BiliExp.py -c /root/BiliExp/config/config.json`并保存
	   ![image](https://user-images.githubusercontent.com/67217225/101779806-b10fbe00-3b30-11eb-987b-f4b88ee3fa16.png)
	   
* 3.注意事项
    *  3.1在步骤1.3中我提供的依赖库只有"mipse"架构的路由器能使用,其他架构的路由器只能自行编译"aiohttp"库并安装
    *  3.2本项目依赖的库较大，不能外接U盘的路由器最好不要使用
    *  3.3 x86架构的软路由最好直接使用docker

</br></br></br>

## 使用方式(下载器部分)

* 1.转至[release](https://github.com/happy888888/BiliExp/releases) ，下载BiliDownloader，解压。
* 2.将账户密码填入config文件夹中的user.json文件(linux可将文件放入/etc/BiliExp/user.json)
* 3.使用videoDownloader
    ```
	命令行参数
	videoDownloader -a -p <下载文件夹> -v <视频1> -e <分集数> -q <质量序号> -v <视频2> -e <分集数> -q <质量序号> ...
	-a --ass       下载视频时附带ass文件,配合支持ass字幕的播放器可以显示弹幕
	-p --path      下载保存的路径，提供一个文件夹路径，没有会自动创建文件夹，默认为当前文件夹
	-v --video     下载的视频地址，支持链接，av号(avxxxxx)，BV号(BVxxxxxx)，ep，ss
	-e --episode   分p数，只对多P视频和多集的番剧有效，不提供默认为1，多个用逗号分隔，连续用减号分隔  -e 2,3,5-7,10 表示2,3,5,6,7,10集
	-q --quality   视频质量序号，0为能获取的最高质量(默认)，1为次高质量，数字越大质量越低
	-x --proxy     是否使用接口代理(可下载仅港澳台)，0为不使用(默认)，1为使用代理
	注意，一个 -v 参数对应一个 -e(-q, -x) 参数，如果出现两个 -v 参数但只有一个 -e(-q, -x) 参数则只应用于第一个，可以有多个 -v 参数以一次性下载多个视频
	-V --version   显示版本信息
	-h --help      显示帮助信息
	
	使用例子
	windows上(假如文件在D:\bilidownloader\videoDownloader.exe)，下载BV1qt411x7yQ的1,2,3,6集到D:\download目录
	打开cmd执行如下命令
	cd /d D:\bilidownloader
	videoDownloader -v BV1qt411x7yQ -e 1-3,6 -p D:\download
	
	linux上(提前将videoDownloader移动到/usr/local/bin)，下载BV1qt411x7yQ的1,2,3,6集到用户的download目录
	shell中执行
	videoDownloader -v BV1qt411x7yQ -e 1-3,6 -p ~/download
	```
* 4.使用mangaDownloader
    ```
	命令行参数
	mangaDownloader -p <下载文件夹> -m <漫画> -e <章节数> -f
	-p --path      下载保存的路径，提供一个文件夹路径，没有会自动创建文件夹，默认为当前文件夹
	-m --manga     下载的漫画mc号，整数
	-e --episode   章节数，不提供默认下载所有章节，多个用逗号分隔，连续用减号分隔  -e 2,3,5-7,10 表示2,3,5,6,7,10章节，注意番外也算一个章节
	-f --pdf       下载后合并为一个pdf
	-V --version   显示版本信息
	-h --help      显示帮助信息
	
	使用例子
	windows上(假如文件在D:\bilidownloader\mangaDownloader.exe)，下载漫画mc28565的3,9,12,13,14章到D:\download目录
	打开cmd执行如下命令
	cd /d D:\bilidownloader
	mangaDownloader -m 28565 -e 3,9,12-14 -p D:\download
	
	linux上(提前将mangaDownloader移动到/usr/local/bin)，下载漫画mc28565的3,9,12,13,14章到用户的download目录
	shell中执行
	mangaDownloader -m 28565 -e 3,9,12-14 -p ~/download
	```

</br></br></br>

## 使用说明(视频投稿部分)
* 1.转至[release](https://github.com/happy888888/BiliExp/releases) ，下载videoUploader，解压。
* 2.将账户密码填入config文件夹中的user.json文件(linux可将文件放入/etc/BiliExp/user.json)
* 3.使用videoUploader
    ```
	命令行参数
	VideoUploader -v <视频文件路径> -t <视频标题> -d <视频简介> -c <视频封面图片路径> -t <视频标签> -n -s <非原创时视频来源 网址>
	-v --videopath     视频文件路径
	-t --title         视频标题，不指定默认为视频文件名
	-d --desc          视频简介，不指定默认为空
	-c --cover         视频封面图片路径，不提供默认用官方提供的第一张图片
	-i --tid           分区id，默认为174，即生活,其他分区
	-T --tags          视频标签，多个标签用半角逗号隔开，带空格必须打引号，不提供默认用官方推荐的前两个标签
	-n --nonOriginal   勾选转载，不指定本项默认为原创
	-s --source        -n参数存在时指定转载源视频网址
	-D --DelayTime     发布时间戳,10位整数,官方的延迟发布,时间戳距离现在必须大于4小时
	-V --version       显示版本信息
	-h --help          显示帮助信息
	以上参数中只有-v --videopath为必选参数，其他均为可选参数
	
	使用例子
	windows上(假如程序在D:\VideoUploader\VideoUploader.exe,视频在D:\VideoUploader\测试视频.mp4)
	打开cmd执行如下命令
	cd /d D:\VideoUploader
	VideoUploader -v "D:\VideoUploader\测试视频.mp4"
	
	linux上(提前将VideoUploader移动到/usr/local/bin,视频文件在/root/upload/测试视频.mp4)
	shell中执行
	VideoUploader -v "/root/upload/测试视频.mp4"
	```

</br></br></br>

## 更新日志

### 2021/02/26更新

* 1.漫画视频下载，视频稿件上传功能支持账号密码登录
* 2.视频稿件支持多P上传
* 3.漫画下载器支持限时免费漫画下载

</br>

### 2021/01/19更新

* 1.导入Actions分支的所有修改

</br>

### 2021/01/05更新

* 1.优化配置文件加载
* 2.解决漫画下载器文件名非法的问题
* 3.导入Actions分支的所有修改

</br>

### 2020/12/09更新

* 1.完善音频稿件发布和下载部分
* 2.完善助手脚本docker部署方法

</br>

### 2020/12/01更新

* 1.视频下载器支持下载弹幕转ass字幕文件
* 2.修复部分bug

</br>

### 2020/11/30更新

* 1.支持命令行上传B站视频稿件

</br>

### 2020/11/19更新

* 1.漫画视频下载器支持命令行参数
* 2.更新说明

</br>

### 2020/11/18更新

* 1.增加docker部署方式

</br>

### 2020/11/06更新

* 1.修复若干bug
* 2.增加一个Downloader.py类用于视频下载，移除对aria2的依赖

</br>

### 2020/10/20更新

* 1.发布release版

</br>

### 2020/10/16更新

* 1.将云函数部分与BiliExp-Actions分支合并，重构这部分所有代码，并调整文件结构

</br>

### 2020/10/1更新

* 1.B站漫画增加自动领取每月大会员赠送的漫读劵。
* 2.B站漫画增加自动参与站友日活动(默认关闭)。
* 3.增加每月28号自动将没有使用的B币劵充电给自己的账户。

</br>

### 2020/09/27更新

* 1.互动抽奖方式改为转发并评论(听说能提高中奖率🤑🤩)。

</br>

### 2020/09/26更新

* 1.增加email推送。

</br>

### 2020/09/24更新

* 1.移除云函数脚本中的doActivity.py和其配置文件。

</br>

### 2020/09/23更新

* 1.更新Actions，部署前执行账号检查，应对有的人账号配置错误部署后脚本执行失败且找不出原因的情况。
* 2.新增分支BiliExp-Actions，使依赖于云函数的功能只需要github Actions就能使用，不需要使用云函数。

</br>

### 2020/09/22更新

* 1.更新BiliExp.py直接自动获取每月大会员权益(B币劵，优惠券)功能
* 2.增加mangaTask.py自动用即将过期的漫读劵兑换漫画(自动购买追漫列表(默认)或者手动指定购买列表),自动用积分兑换福利券(默认关闭),合并以前的mangaClockIn.py文件到此文件
* 3.彻底将直播开启宝箱领取银瓜子的功能从云函数中移除。

</br>

### 2020/09/17更新

* 1.更新BiliLottery.py转发抽奖的逻辑，避免动态太多导致抽奖动态转发的遗漏
* 2.增加videoDownloader.py下载B站视频
* 3.增加models/aria2py.py用于B站视频的下载
* 4.增加/player_proxy/player_proxy.js用于代理B站视频解析接口(需要部署到阿里云函数港澳台服务器)

</br>

### 2020/09/02更新

* 1.增加topicRepost.py转发话题列表(抽奖话题)(不包含在云函数内)
* 2.增加cancelAttention.py一键取关所有up主(不包含在云函数内)
* 3.增加mangaDownloader.py下载B站漫画，支持合并转pdf
* 3.删除四个已经失效的活动，现在几乎没有可以白嫖B站的官方抽奖活动了，参加(官方抽奖)活动的功能可能会取消

</br>

### 2020/08/28更新

* 1.截至今天，B站直播开时间宝箱领取银瓜子的活动已经结束
* 2.B站官方活动里面的 "夏日不宅宣言" 活动和 "新星计划-暑假赛" 活动已经结束，新增加"最强安利王"活动

</br>

### 2020/08/25更新

* 1.增加送出即将过期的直播礼物的功能
* 2.增加直播心跳维持在线状态的功能(非大老爷用户在线时长并不能加经验)

</br>

### 2020/08/22更新

* 1.使用Actions实现脚本自动部署到阿里云，代替本文最下方的手动部署方式(已删除)

</br>

### 2020/08/21更新

* 1.增加doActivity.py用于参加B站官方活动(抽奖类) 活动列表 https://www.bilibili.com/blackboard/x/act_list/
    *  活动列表(抽奖类)存放在config/activity.json中
        *  每个活动都有过期时间(目前的大部分活动都将在8.30日前过期)，活动中抽奖也有参与次数限制
        *  有的活动每天固定赠送抽奖次数，有的活动需要转发，还有的活动需要关注投币点赞甚至投稿才能获得抽奖次数，本脚本只能做每天固定赠送抽奖次数，和转发获得抽奖次数的活动
        *  活动过期或添加新活动均需手动更新activity.json，有新活动或者活动是否过期都可以在上面活动列表网址查看
    * 本人首次在"舞见大合集"活动中抽中一个"小电视抱枕"，第一次在B站中抽中实物，记录一下☺️
* 2.增加cleanDynamic.py用于清理转发的动态
    *  清理的转发动态包括:①互动抽奖过期的动态；②两个月前带#互动抽奖#标签的动态；③被原up主删除的动态
* 3.用户配置文件仅需要cookies，不需要再获取客户端的access_key，access_key从用户配置文件移除，用户配置文件由userData/userData.py改为config/config.json，账户检查脚本由userData/check.py移动到check.py


</br>

### 2020/08/07更新

* 1.增加B站视频上传api
* 2.增加一个自动转载视频并发布的例子(youtube一键转B站)

</br>

### 2020/08/06更新

* 1.发现B站app的access_key与漫画app通用，调整了app相关api的结构
* 2.新增加Article类实现专栏的自动发表,Article.Content类实现B站专栏内容的排版(支持插入B站所有标签)
* 3.增加两个自动发表B站专栏的例子(1.收集自己动态里的抽奖内容并发表到专栏；2.自动收集P站图片并转载到专栏(此脚本发表的图片通不过B站审核))
* 4.利用B站专栏的图片上传接口可能能实现把B站当做免费图床？(大雾)？

</br></br>

## 打赏
如果觉得本项目好用，对你有所帮助，欢迎打赏支持一下本项目发展！！！

<div align="center">

<img src="https://user-images.githubusercontent.com/67217225/99527309-8d48d480-29d7-11eb-8f4e-7034dbd91baf.png" width="600" title="支付宝，微信，QQ扫码赞助" style="display:block;" />

</div>

</br>

#### 获得cookies方法
B站操作需要的cookie数据可以按照以下方式获取
浏览器打开B站主页--》按F12打开开发者工具--》application--》cookies
<div align="center"><img src="https://s1.ax1x.com/2020/09/23/wjM09e.png" width="800" height="450" title="获取cookies示例"></div>

