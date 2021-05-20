# -*- coding: utf-8 -*-
from requests.sessions import Session
import requests, json, re, time
from _io import BufferedReader
from urllib.parse import quote, quote_plus
from typing import Union, Mapping, Sequence
try:
    import rsa
except:
    ...
else:
    import hashlib, base64
    APPKEY = 'aae92bc66f3edfab'
    APPSECRET = 'af125a0d5279fd576c1b4418a3e8276d'

class BiliApi(object):
    "B站api接口"

    def __init__(self):
        #创建session
        self._session = Session()
        #设置header
        self._session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
                "Referer": "https://www.bilibili.com/",
                'Connection': 'keep-alive'
             }
            )
        self._islogin = False
        self._access_token = None
        self._refresh_token = None

    def login_by_cookie(self, 
                        cookieData: Union[Mapping[str, str], Sequence[Mapping[str, str]]]
                        ) -> bool:
        '''
        登录并获取账户信息
        cookieData Union[Mapping[str, str], Sequence[Mapping[str, str]]] 账户cookie
        '''
        cj = self._session.cookies
        if isinstance(cookieData, Mapping):
            for name in cookieData:
                cj.set(name, cookieData[name])
        elif isinstance(cookieData, Sequence):
            for cookie in cookieData:
                cj.set(**{k:v for k,v in cookie.items() if k in ("name", "value", "path", "domain", "expires", "secure")})
        else:
            raise ValueError('cookieData格式不正确')
        ret = self._session.get("https://api.bilibili.com/x/web-interface/nav").json()
        if ret["code"] != 0:
            return False

        self._islogin = True
        if 'bili_jct' in cookieData:
            self._bili_jct = cookieData["bili_jct"]
        else:
            self._bili_jct = ''

        self._name = ret["data"]["uname"]
        self._uid = ret["data"]["mid"]
        self._vip = ret["data"]["vipType"]
        self._level = ret["data"]["level_info"]["current_level"]
        self._verified = ret["data"]["mobile_verified"]
        self._coin = ret["data"]["money"]
        self._exp = ret["data"]["level_info"]["current_exp"]
        return True

    def login_by_password(self, 
                          username: str, 
                          password: str
                          ) -> bool:
        '''
        通过账号密码登录
        username  str  账户名
        password  str  账户密码
        '''
        hash, pubkey = BiliApi._getKey(self)
        encrypted_password = BiliApi._encrypt_login_password(password, hash, pubkey)
        url_encoded_username = quote_plus(username)
        url_encoded_password = quote_plus(encrypted_password)

        post_data = {
            'appkey': APPKEY,
            'password': url_encoded_password,
            'platform': "pc",
            'ts': int(time.time()),
            'username': url_encoded_username
        }

        post_data['sign'] = BiliApi._sign_dict(post_data, APPSECRET)
        post_data['username'] = username
        post_data['password'] = encrypted_password

        ret = self._session.post(
            "https://passport.bilibili.com/api/oauth2/login",
            data=post_data
            ).json()

        if ret["code"] != 0:
            return False

        self._access_token = ret["data"]['access_token']
        self._refresh_token = ret["data"]['refresh_token']
        self._uid = ret["data"]['mid']
        return BiliApi.refreshToken(self)

    def login_by_access_token(self, 
                              access_token: str, 
                              refresh_token: str = None,
                              refreshToken: bool = False
                              ) -> bool:
        '''
        通过access_token(可选refresh_token)登录
        access_token  str  登录令牌，代表登录状态
        refresh_token str  刷新令牌，负责刷新access_token
        refreshToken  bool 是否马上刷新令牌，只有刷新令牌后才能得到cookie使用web接口，否则登录后只能使用app接口
        '''
        login_params = {
            'appkey': APPKEY,
            'access_token': access_token,
            'platform': "pc",
            'ts': int(time.time()),
        }
        login_params['sign'] = BiliApi._sign_dict(login_params, APPSECRET)

        ret = self._session.get(
            url="https://passport.bilibili.com/api/oauth2/info",
            params=login_params
        ).json()

        if ret["code"] != 0:
            return False

        self._access_token = ret["data"]["access_token"]
        self._refresh_token = refresh_token
        self._uid = ret["data"]["mid"]

        if refreshToken:
            return BiliApi.refreshToken(self)
        return True

    def refreshToken(self, 
                     access_token: str = None, 
                     refresh_token: str = None
                     ) -> bool:
        '''
        刷新当前令牌，并获得cookie
        access_token  str  登录令牌，代表登录状态
        refresh_token str  刷新令牌，负责刷新access_token
        '''
        if not access_token:
            access_token = self._access_token
        if not refresh_token:
            refresh_token = self._refresh_token

        if (not access_token) or (not refresh_token):
            return False

        post_data = {
            'appkey': APPKEY,
            'access_token': access_token,
            'access_key': access_token,
            'refresh_token': refresh_token,
            'ts': int(time.time()),
        }
        post_data['sign'] = BiliApi._sign_dict(post_data, APPSECRET)

        ret = self._session.post(
            url="https://passport.bilibili.com/api/v2/oauth2/refresh_token",
            data=post_data
            ).json()

        if 0 != ret["code"]:
            return False

        self._access_token = ret["data"]["token_info"]["access_token"]
        self._refresh_token = ret["data"]["token_info"]["refresh_token"]
        self._uid = ret["data"]["token_info"]["mid"]
        return BiliApi.login_by_cookie(self, ret["data"]["cookie_info"]["cookies"])

    @property
    def islogin(self):
        '''是否登录'''
        return self._islogin

    @property
    def myexp(self) -> int:
        '''获取登录的账户的经验'''
        return self._exp

    @property
    def mycoin(self) -> int:
        '''获取登录的账户的硬币数量'''
        return self._coin

    @property
    def vipType(self) -> int:
        '''获取登录的账户的vip类型'''
        return self._vip
    
    @property
    def name(self) -> str:
        '''获取登录的账户用户名'''
        return self._name

    @property
    def uid(self) -> int:
        '''获取登录的账户uid'''
        return self._uid

    @property
    def level(self) -> int:
        '''获取登录账户的等级'''
        return self._level

    @property
    def access_token(self) -> str:
        '''获取登录账户的access_token'''
        return self._access_token

    @property
    def access_token(self) -> str:
        '''获取登录账户的access_token'''
        return self._access_token

    @property
    def refresh_token(self) -> str:
        '''获取登录账户的access_token'''
        return self._refresh_token

    @property
    def SESSDATA(self):
        '''获取cookie SESSDATA'''
        return self._session.cookies.get("SESSDATA", "")

    @property
    def bili_jct(self):
        '''获取cookie bili_jct'''
        return self._session.cookies.get("bili_jct", "")

    def getWebNav(self):
        "取导航信息"
        url = "https://api.bilibili.com/x/web-interface/nav"
        return self._session.get(url).json()["data"]

    def getLevel(self):
        "获取登录的账户等级"
        return self._level

    def spaceArcSearch(self, uid: int, ps=50, pn=1, tid=0, keyword='', order='pubdate'):
        "取空间投稿信息"
        url = 'https://api.bilibili.com/x/space/arc/search?mid={uid}&ps={ps}&tid=0&pn={pn}&keyword={keyword}&order={order}'
        return self._session.get(url).json()

    @staticmethod
    def getId(url):
        "取B站指定视频链接的aid和cid号"
        content = requests.get(url, headers=Biliapi.__headers)
        match = re.search( 'https:\/\/www.bilibili.com\/video\/av(.*?)\/\">', content.text, 0)
        aid = match.group(1)
        match = re.search( '\"cid\":(.*?),', content.text, 0)
        cid = match.group(1)
        return {"aid": aid, "cid": cid}

    def likeCv(self, cvid: int, type=1) -> dict:
        '''
        点赞专栏
        cvid int 专栏id
        type int 类型
        '''
        url = 'https://api.bilibili.com/x/article/like'
        post_data = {
            "id": cvid,
            "type": type,
            "csrf": self._bili_jct
            }
        return self._session.post(url, post_data).json()

    def like(self, aid: int, like=1):
        "点赞视频"
        url = "https://api.bilibili.com/x/web-interface/archive/like"
        post_data = {
            "aid": aid,
            "like": like,
            "csrf": self._bili_jct
            }
        return self._session.post(url, post_data).json()

    def likeCv(self, cvid: int, type=1):
        "点赞专栏"
        url = 'https://api.bilibili.com/x/article/like'
        post_data = {
            "id": cvid,
            "type": type,
            "csrf": self._bili_jct
            }
        return self._session.post(url, post_data).json()

    def getCoin(self):
        "获取剩余硬币数"
        url = "https://api.bilibili.com/x/web-interface/nav?build=0&mobi_app=web"
        return int(self._session.get(url).json()["data"]["money"])

    def coinCv(self, cvid: int, num=1, upid=0, select_like=1):
        "给指定cv号专栏投币"
        url = "https://api.bilibili.com/x/web-interface/coin/add"
        if upid == 0:
            info = self.articleViewInfo(cvid)["data"]
            if info["coin"]: #官方限制专栏只能投一个币，但其实原创作品无论视频专栏都可以投两个币
                return {'code': 34005, 'message': '超过投币上限啦~', 'ttl': 1, 'data': {'like': False}}
            upid = info["mid"]
        post_data = {
            "aid": cvid,
            "multiply": num,
            "select_like": select_like,
            "upid": upid,
            "avtype": 2,#专栏必为2，否则投到视频上面去了
            "csrf": self._bili_jct
            }
        return self._session.post(url, post_data).json()

    def coin(self, aid: int, num=1, select_like=1):
        "给指定av号视频投币"
        url = "https://api.bilibili.com/x/web-interface/coin/add"
        post_data = {
            "aid": aid,
            "multiply": num,
            "select_like": select_like,
            "cross_domain": "true",
            "csrf": self._bili_jct
            }
        return self._session.post(url, post_data).json()

    def share(self, aid):
        "分享指定av号视频"
        url = "https://api.bilibili.com/x/web-interface/share/add"
        post_data = {
            "aid": aid,
            "csrf": self._bili_jct
            }
        return self._session.post(url, post_data).json()

    def report(self, aid, cid, progres):
        "B站上报观看进度"
        url = "https://api.bilibili.com/x/v2/history/report"
        post_data = {
            "aid": aid,
            "cid": cid,
            "progres": progres,
            "csrf": self._bili_jct
            }
        return self._session.post(url, post_data).json()

    def getHomePageUrls(self):
        "取B站首页推荐视频地址列表"
        url = "https://www.bilibili.com"
        content = self._session.get(url)
        match = re.findall( '<div class=\"info-box\"><a href=\"(.*?)\" target=\"_blank\">', content.text, 0)
        match = ["https:" + x for x in match]
        return match

    @staticmethod
    def getRegions(rid=1, num=6):
        "获取B站分区视频信息"
        url = "https://api.bilibili.com/x/web-interface/dynamic/region?ps=" + str(num) + "&rid=" + str(rid)
        datas = requests.get(url).json()["data"]["archives"]
        ids = []
        for x in datas:
            ids.append({"title": x["title"], "aid": x["aid"], "bvid": x["bvid"], "cid": x["cid"]})
        return ids

    @staticmethod
    def getRankings(rid=1, day=3):
        "获取B站分区排行榜视频信息"
        url = "https://api.bilibili.com/x/web-interface/ranking?rid=" + str(rid) + "&day=" + str(day)
        datas = requests.get(url).json()["data"]["list"]
        ids = []
        for x in datas:
            ids.append({"title": x["title"], "aid": x["aid"], "bvid": x["bvid"], "cid": x["cid"], "coins": x["coins"], "play": x["play"]})
        return ids

    def repost(self, dynamic_id, content="", extension='{"emoji_type":1}'):
        "转发B站动态"
        url = "https://api.vc.bilibili.com/dynamic_repost/v1/dynamic_repost/repost"
        post_data = {
            "uid": self._uid,
            "dynamic_id": dynamic_id,
            "content": content,
            "extension": extension,
            #"at_uids": "",
            #"ctrl": "[]",
            "csrf_token": self._bili_jct
            }
        return self._session.post(url, post_data).json()

    def dynamicReplyAdd(self, oid: int, message="", type=11, plat=1):
        "评论动态"
        url = "https://api.bilibili.com/x/v2/reply/add"
        post_data = {
            "oid": oid,
            "plat": plat,
            "type": type,
            "message": message,
            "csrf": self._bili_jct
            }
        return self._session.post(url, post_data).json()

    def dynamicRepostReply(self, rid, content="", type=1, repost_code=3000, From="create.comment", extension='{"emoji_type":1}'):
        "评论动态并转发"
        url = "https://api.vc.bilibili.com/dynamic_repost/v1/dynamic_repost/reply"
        post_data = {
            "uid": self._uid,
            "rid": rid,
            "type": type,
            "content": content,
            "extension": extension,
            "repost_code": repost_code,
            "from": From,
            "csrf_token": self._bili_jct
            }
        return self._session.post(url, post_data).json()

    def followed(self, followid: 'up的uid', isfollow=True):
        "关注或取关up主"
        url = "https://api.vc.bilibili.com/feed/v1/feed/SetUserFollow"
        post_data = {
            "type": 1 if isfollow else 0,
            "follow": followid,
            "csrf_token": self._bili_jct
            }
        return self._session.post(url, post_data).json()

    def followedModify(self, followid: 'up的uid', act=1, re_src=11):
        "改变关注状态(增加、删除关注的up)"
        url = "https://api.bilibili.com/x/relation/modify"
        post_data = {
            "fid": followid,
            "act": act,
            "re_src": re_src,
            "csrf": self._bili_jct
            }
        return self._session.post(url, post_data).json()

    def groupAddFollowed(self, followid: 'up的uid', tagids=0):
        "移动关注的up主的分组"
        url = "https://api.bilibili.com/x/relation/tags/addUsers?cross_domain=true"
        post_data = {
            "fids": followid,
            "tagids": tagids, #默认是0，特别关注是-10
            "csrf": self._bili_jct
            }
        return self._session.post(url, post_data).json()

    def getFollowing(self, uid=0, pn=1, ps=50, order='desc'):
        "获取指定账户的关注者(默认取本账户)"
        if uid == 0:
            uid = self._uid
        url = f"https://api.bilibili.com/x/relation/followings?vmid={uid}&pn={pn}&ps={ps}&order={order}"
        return self._session.get(url).json()

    def getTopicInfo(self, tag_name):
        "取B站话题信息"
        url = f'https://api.bilibili.com/x/tag/info?tag_name={tag_name}'
        return self._session.get(url).json()

    def getTopicList(self, tag_name):
        "取B站话题列表，返回一个可迭代对象"
        topic_id = self.getTopicInfo(tag_name)["data"]["tag_id"]
        url = f'https://api.vc.bilibili.com/topic_svr/v1/topic_svr/topic_new?topic_id={topic_id}'
        jsobj = self._session.get(url).json()
        cards = jsobj["data"]["cards"]
        for x in cards:
            yield x
        has_more = (jsobj["data"]["has_more"] == 1)
        while has_more:
            offset = jsobj["data"]["offset"]
            jsobj = self._session.get(f'https://api.vc.bilibili.com/topic_svr/v1/topic_svr/topic_history?topic_name={tag_name}&offset_dynamic_id={offset}').json()
            if not 'cards' in jsobj["data"]:
                break
            cards = jsobj["data"]["cards"]
            for x in cards:
                yield x
            has_more = (jsobj["data"]["has_more"] == 1)

    def getDynamicDetail(self, dynamic_id: int):
        "获取动态内容"
        url = f'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail?dynamic_id={dynamic_id}'
        return self._session.get(url).json()

    def getDynamicNew(self, type_list='268435455'):
        "取B站用户最新动态数据"
        url = f'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/dynamic_new?uid={self._uid}&type_list={type_list}'
        content = self._session.get(url)
        content.encoding = 'utf-8' #需要指定编码
        return json.loads(content.text)

    def getDynamic(self, type_list='268435455'):
        "取B站用户动态数据，生成器"
        url = f'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/dynamic_new?uid={self._uid}&type_list={type_list}'
        content = self._session.get(url)
        content.encoding = 'utf-8' #需要指定编码
        jsobj = json.loads(content.text)
        cards = jsobj["data"]["cards"]
        for x in cards:
            yield x
        hasnext = True
        offset = cards[len(cards) - 1]["desc"]["dynamic_id"]
        while hasnext:
            content = self._session.get(f'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/dynamic_history?uid={self._uid}&offset_dynamic_id={offset}&type={type_list}')
            content.encoding = 'utf-8'
            jsobj = json.loads(content.text)
            hasnext = (jsobj["data"]["has_more"] == 1)
            #offset = jsobj["data"]["next_offset"]
            cards = jsobj["data"]["cards"]
            for x in cards:
                yield x
            offset = cards[len(cards) - 1]["desc"]["dynamic_id"]

    def getMyDynamic(self, uid=0):
        "取B站用户自己的动态列表，生成器"
        import time
        def retry_get(url):
            times = 3
            while times:
                try:
                    jsobj = self._session.get(url, timeout=(10, 20)).json()
                    assert jsobj["code"] == 0
                    return jsobj
                except:
                    times -= 1
                    time.sleep(3)
            raise Exception(str(jsobj))

        if uid == 0:
            uid = self._uid
        url = f'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={uid}&need_top=1&offset_dynamic_id='
        hasnext = True
        offset = ''
        while hasnext:
            jsobj = retry_get(f'{url}{offset}')
            hasnext = (jsobj["data"]["has_more"] == 1)
            if not 'cards' in jsobj["data"]:
                continue
            cards = jsobj["data"]["cards"]
            for x in cards:
                yield x
            offset = x["desc"]["dynamic_id_str"]

    def removeDynamic(self, dynamic_id: int):
        "删除自己的动态"
        url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/rm_dynamic'
        post_data = {
            "dynamic_id": dynamic_id,
            "csrf_token": self._bili_jct
            }
        return self._session.post(url, post_data).json()

    def dynamicCreate(self, 
                      content: str, 
                      type: int = 4,
                      extension: dict = {},
                      at_uids: list = [],
                      ctrl: list = []
                      ) -> dict:
        '''创建动态(纯文本动态,图片动态请用dynamicCreateDraw方法)'''
        url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/create'
        post_data = {
            "dynamic_id": 0,
            "rid": 0,
            "type": type,
            "content": content,
            "extension": json.dumps(extension),
            "at_uids": ",".join(at_uids),
            "ctrl": json.dumps(ctrl),
            "up_choose_comment": 0,
            "up_close_comment": 0,
            "csrf": self._bili_jct,
            "csrf_token": self._bili_jct
            }
        return self._session.post(url, data=post_data).json()

    def dynamicCreateDraw(self, 
                          content: str, 
                          pictures: list,
                          type: int = 4,
                          extension: dict = {},
                          at_uids: list = [],
                          ctrl: list = []
                          ) -> dict:
        '''创建图片动态'''
        url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/create_draw'
        post_data = {
            "biz": 3,
            "category": 3,
            "type": type,
            "content": content,
            #"description": content,
            "pictures": json.dumps(pictures),
            #"title": "",
            #"tags": "",
            "setting": '{"copy_forbidden":0,"cachedTime":0}',
            "from": "create.dynamic.web",
            "extension": json.dumps(extension),
            "at_uids": ",".join(at_uids),
            "at_control": json.dumps(ctrl),
            "up_choose_comment": 0,
            "up_close_comment": 0,
            "csrf": self._bili_jct,
            "csrf_token": self._bili_jct
            }
        return self._session.post(url, data=post_data).json()

    def dynamicAtSearch(self,
                        uname: str
                        ):
        '''搜索用户名，获得uid
        uname  str  用户名'''
        url = f'https://api.vc.bilibili.com/dynamic_mix/v1/dynamic_mix/at_search?uid={self._uid}&keyword={uname}'
        return self._session.get(url).json()

    def drawImageUpload(self,
                        imageFile
                        ):
        '''上传图片到B站动态
        imageFile  BytesIO  图片文件'''
        url = 'https://api.vc.bilibili.com/api/v1/drawImage/upload'
        files = {
                "file_up":("up_image.jpg", imageFile),
                "biz":(None, "draw"),
                "category":(None, "daily")
                }
        return self._session.post(url, files=files, timeout=(15, 60)).json()

    def getLotteryNotice(self, dynamic_id: int):
        "取指定抽奖信息"
        url = f'https://api.vc.bilibili.com/lottery_svr/v1/lottery_svr/lottery_notice?dynamic_id={dynamic_id}'
        content = self._session.get(url)
        content.encoding = 'utf-8'#不指定会出错
        return json.loads(content.text)

    def getRelationStat(self, uid: int):
        "取指定账户关注信息"
        url = f'https://api.bilibili.com/x/relation/stat?vmid={uid}'
        return self._session.get(url).json()

    def getSpaceInfo(self, uid: int):
        "取指定账户空间信息"
        url = f'https://api.bilibili.com/x/space/acc/info?mid={uid}'
        return self._session.get(url).json()

    def getUserWallet(self, platformType=3):
        "获取账户钱包信息"
        url = 'https://pay.bilibili.com/paywallet/wallet/getUserWallet'
        post_data = {
            "platformType": platformType
            #"panelType": panelType,
            #"traceId": 'traceId',
            #"timestamp": timestamp,
            #"version": "1.0"
            }
        #{"code":0,"errno":0,"msg":"SUCCESS","message":"SUCCESS","showMsg":"","errtag":0,"data":{"mid":203984353,"totalBp":0.00,"defaultBp":0.00,"iosBp":0.00,"couponBalance":0,"availableBp":0.00,"unavailableBp":0.00,"unavailableReason":"苹果设备上充值的B币不能在其他平台的设备上进行使用","tip":null}}
        return self._session.post(url, json=post_data).json()

    def elecPay(self, uid: int, num=50):
        "用B币给up主充电，num >= 20"
        url = 'https://api.bilibili.com/x/ugcpay/trade/elec/pay/quick'
        post_data = {
            "elec_num": num,
            "up_mid": uid,
            "otype": 'up',
            "oid": uid,
            "csrf": self._bili_jct
            }
        #{"code":0,"message":"0","ttl":1,"data":{"mid":203984353,"up_mid":8466742,"order_no":"BTQPTQ8PQ95DN6CV46AG","elec_num":20,"exp":2,"status":4,"msg":""}}
        #{"code":0,"message":"0","ttl":1,"data":{"mid":0,"up_mid":0,"order_no":"","elec_num":0,"exp":0,"status":-4,"msg":"bp.to.battery http failed, invalid args, errNo=800409904: B 币余额不足"}}
        return self._session.post(url, post_data).json()

    def elecPayStatus(self, order_no: 'str 订单编号'):
        "充电订单状态查询"
        url = f'https://api.bilibili.com/x/ugcpay/trade/elec/pay/order/status?order_no={order_no}'
        #{"code":0,"message":"0","ttl":1,"data":{"order_no":"BTQPTQ8PQ95DN6CV46AG","mid":203984353,"status":1}}
        return self._session.get(url).json()

    def xliveSign(self):
        "B站直播签到"
        url = "https://api.live.bilibili.com/xlive/web-ucenter/v1/sign/DoSign"
        return self._session.get(url).json()

    def xliveGetStatus(self):
        "B站直播获取金银瓜子状态"
        url = "https://api.live.bilibili.com/pay/v1/Exchange/getStatus"
        return self._session.get(url).json()

    def silver2coin(self):
        "银瓜子兑换硬币"
        url = "https://api.live.bilibili.com/pay/v1/Exchange/silver2coin"
        post_data = {
            "csrf_token": self._bili_jct
            }
        return self._session.post(url, post_data).json()

    def articleViewInfo(self, cvid: int):
        "获取专栏信息"
        url = f'https://api.bilibili.com/x/article/viewinfo?id={cvid}'
        return self._session.get(url).json()

    def articleReplyMain(self, cvid: int, type=12):
        "获取专栏回复信息"
        url = f'https://api.bilibili.com/x/v2/reply/main?oid={cvid}&type={type}'
        return self._session.get(url).json()

    def articleListInfo(self, cvid: int):
        "通过单个专栏获取专栏文集信息"
        url = f'https://api.bilibili.com/x/article/listinfo?id={cvid}'
        return self._session.get(url).json()

    def listArticles(self, cvid: int):
        "获取专栏文集信息"
        url =  f'https://api.bilibili.com/x/article/list/web/articles?id={cvid}'
        return self._session.get(url).json()

    def listArticlesAll(self, cvid: int):
        "获取本人专栏文集信息"
        url =  f'https://api.bilibili.com/x/article/creative/list/articles/all?id={cvid}'
        return self._session.get(url).json()

    def createArticle(self, tilte="", content="", aid=0, category=0, list_id=0, tid=4, original=1, image_urls="", origin_image_urls="", submit=False):
        "发表专栏"
        post_data = {
            "title": tilte,
            "content": content,
            "category": category,#专栏分类,0为默认
            "list_id": list_id,#文集编号，默认0不添加到文集
            "tid": 4, #4为专栏封面单图,3为专栏封面三图
            "reprint": 0,
            "media_id": 0,
            "spoiler": 0,
            "original": original,
            "csrf": self._bili_jct
            }
        url = 'https://api.bilibili.com/x/article/creative/draft/addupdate'#编辑地址,发表前可以通过这个来编辑草稿,没打草稿不允许发表
        if aid:
            post_data["aid"] = aid
            if submit:
                url = 'https://api.bilibili.com/x/article/creative/article/submit'#正式发表地址
        if origin_image_urls and image_urls:
            post_data["origin_image_urls"] = origin_image_urls
            post_data["image_urls"] = image_urls
        return self._session.post(url, post_data).json()

    def deleteArticle(self, aid: int):
        "删除专栏"
        url = 'https://member.bilibili.com/x/web/draft/delete'
        post_data = {
            "aid": aid,
            "csrf": self._bili_jct
            }
        return self._session.post(url, post_data).json()

    def getArticle(self, aid: int):
        "获取专栏内容"
        url = f'https://api.bilibili.com/x/article/creative/draft/view?aid={aid}'
        return self._session.get(url).json()

    def articleUpcover(self, file):
        "上传本地图片,返回链接"
        url = 'https://api.bilibili.com/x/article/creative/article/upcover'
        files = {
            'binary':(file)
            }
        post_data = {
            "csrf": self._bili_jct
            }
        return self._session.post(url, post_data, files=files, timeout=(15, 60)).json()

    def articleCardsBvid(self, bvid: 'str 加上BV前缀'):
        "根据bv号获取视频信息，在专栏引用视频时使用"
        url = f'https://api.bilibili.com/x/article/cards?ids={bvid}&cross_domain=true'
        return self._session.get(url).json()

    def articleCardsCvid(self, cvid: 'str 加上cv前缀'):
        "根据cv号获取专栏，在专栏引用其他专栏时使用"
        url = f'https://api.bilibili.com/x/article/card?id={cvid}&cross_domain=true'
        return self._session.get(url).json()

    def articleCardsId(self, epid: 'str 加上ep前缀'):
        "根据ep号获取番剧信息，在专栏引用站内番剧时使用"
        return self.articleCardsCvid(epid)

    def articleCardsAu(self, auid: 'str 加上au前缀'):
        "根据au号获取音乐信息，在专栏引用站内音乐时使用"
        return self.articleCardsCvid(auid)

    def articleCardsPw(self, pwid: 'str 加上pw前缀'):
        "根据au号获取会员购信息，在专栏引用会员购时使用"
        return self.articleCardsCvid(pwid)

    def articleMangas(self, mcid: 'int 不加mc前缀'):
        "根据mc号获取漫画信息，在专栏引用站内漫画时使用"
        url = f'https://api.bilibili.com/x/article/mangas?ids={mcid}&cross_domain=true'
        return self._session.get(url).json()

    def articleCardsLv(self, lvid: 'str 加上lv前缀'):
        "根据lv号获取直播信息，在专栏引用站内直播时使用"
        return self.articleCardsCvid(lvid)

    def articleCreateVote(self, vote):
        "创建一个投票"
        '''
        vote = {
            "title": "投票标题",
            "desc": "投票说明",
            "type": 0, #0为文字投票，1为图片投票
            "duration": 604800,#投票时长秒,604800为一个星期
            "options":[
                {
                    "desc": "选项1",
                    "cnt": 0,#不知道什么意思
                    "idx": 1, #选项序号，第一个选项为1
                    #"img_url": "http://i0.hdslb.com/bfs/album/d74e83cf96a9028eb3e280d5f877dce53760a7e2.jpg",#仅图片投票需要
                },
                {
                    "desc": "选项2",
                    "cnt": 0,
                    "idx": 2, #选项序号，第二个选项为2
                    #"img_url": ""
                }
                ]
            }
        '''
        def _parseData(name: str, sub_data: dict or list, data: dict):
            '''内部函数，递归将多层dict转为单层dict'''
            if isinstance(sub_data, dict):
                for x in sub_data:
                    _parseData(f'{name}[{x}]', sub_data[x], data)
            elif isinstance(sub_data, list):
                for ii in range(len(sub_data)):
                    _parseData(f'{name}[{ii}]', sub_data[ii], data)
            else:
                data[name] = sub_data
        url = 'https://api.vc.bilibili.com/vote_svr/v1/vote_svr/create_vote'
        info = {}
        _parseData("info", vote, info)
        post_data = {
            #"info": vote, #不支持参数嵌套，用_parseData方法把嵌套参数转为单层
            **info,
            "csrf": self._bili_jct,
            "csrf_token": self._bili_jct
            }
        return self._session.post(url, post_data).json()

    def videoPreupload(self, filename, filesize, profile='ugcupos%2Fbup'):
        "申请上传，返回上传信息"
        from urllib.parse import quote
        name = quote(filename)
        url = f'https://member.bilibili.com/preupload?name={name}&size={filesize}&r=upos&profile={profile}&ssl=0&version=2.8.9&build=2080900&upcdn=bda2&probe_version=20200628&mid={self._uid}'
        return self._session.get(url).json()

    def videoPreuploadApp(self, profile='ugcfr%2Fpc3'):
        '''申请上传，返回上传信息(APP端)'''
        url = f'https://member.bilibili.com/preupload?access_key={self._access_token}&profile={profile}&mid={self._uid}'
        return self._session.get(url).json()

    def videoUploadId(self, url, auth):
        "向上传地址申请上传，得到上传id等信息"
        return self._session.post(f'{url}?uploads&output=json', headers={"X-Upos-Auth": auth}).json()

    def videoUpload(self, url, auth, upload_id, data, chunk, chunks, start, total):
        '''上传视频分块(web)'''
        size = len(data)
        end = start + size
        content = self._session.put(f'{url}?partNumber={chunk+1}&uploadId={upload_id}&chunk={chunk}&chunks={chunks}&size={size}&start={start}&end={end}&total={total}', data=data, headers={"X-Upos-Auth": auth})

    def videoUploadApp(self, url, filename, data, md5, chunk, chunks, version='1.6.0.1006'):
        '''上传视频分块(APP)'''
        files = {
            'version': (None, version),
            'filesize': (None, len(data)),
            'md5': (None, md5),
            'chunk': (None, chunk),
            'chunks': (None, chunks),
            'file':(filename, data, 'application/octet-stream')
            }
        return self._session.post(url, files=files).json()
        #{"OK": 1, "info": "Successful."}

    def videoUploadCompleteApp(self, url, filename, filesize, md5, chunks, version='1.6.0.1006'):
        '''上传视频分块完成(APP)'''
        post_data = {
            'version': (None, version),
            'filesize': (None, filesize),
            'name': (None, filename),
            'md5': (None, md5),
            'chunks': (None, chunks)
            }
        return self._session.post(url, post_data).json()
        #{"OK": 1, "info": "Successful."}

    def videoUploadInfo(self, url, auth, parts, filename, upload_id, biz_id, profile='ugcupos%2Fbup'):
        "查询上传视频信息"
        from urllib.parse import quote
        name = quote(filename)
        return self._session.post(f'{url}?output=json&name={name}&profile={profile}&uploadId={upload_id}&biz_id={biz_id}', json={"parts":parts}, headers={"X-Upos-Auth": auth}).json()

    def videoRecovers(self, fns: '视频编号'):
        "查询视频封面信息"
        url = f'https://member.bilibili.com/x/web/archive/recovers?fns={fns}'
        return self._session.get(url=url).json()

    def videoUpcover(self, cover: '封面图片base64字符串'):
        "上传视频封面(web端)"
        url = 'https://member.bilibili.com/x/vu/web/cover/up'
        post_data = {
            "cover": cover,
            "csrf": self._bili_jct
            }
        return self._session.post(url=url, data=post_data).json()

    def videoUpcoverApp(self, coverFile: '封面图片字节集或实现了read方法的文件对象'):
        "上传视频封面(APP端)"
        url = f'https://member.bilibili.com/x/vu/client/cover/up?access_key={self._access_token}'
        files = {
            "file": ("cover.png", coverFile)
            }
        return self._session.post(url=url, files=files).json()

    def videoTags(self, title: '视频标题', filename: "上传后的视频名称", typeid="", desc="", cover="", groupid=1, vfea=""):
        "上传视频后获得推荐标签(web端)"
        url = f'https://member.bilibili.com/x/web/archive/tags?typeid={typeid}&title={quote(title)}&filename=filename&desc={quote(desc)}&cover={cover}&groupid={groupid}&vfea={vfea}'
        return self._session.get(url=url).json()

    def videoTagsApp(self, title: '视频标题', typeid="", desc=""):
        "获得视频推荐标签(APP端)"
        url = f'https://member.bilibili.com/x/client/archive/tags?access_key={self._access_token}&typeid={typeid}&title={quote(title)}&desc={quote(desc)}&build=1006'
        return self._session.get(url=url).json()

    def videoAdd(self, videoData:"dict 视频参数"):
        "发布视频(web端)"
        url = f'https://member.bilibili.com/x/vu/web/add?csrf={self._bili_jct}'
        return self._session.post(url, json=videoData).json()

    def videoAddApp(self, videoData:"dict 视频参数"):
        "发布视频(APP端)"
        url = f'https://member.bilibili.com/x/vu/client/add?access_key={self._access_token}'
        return self._session.post(url, json=videoData).json()

    def videoPre(self):
        "视频预操作"
        url = 'https://member.bilibili.com/x/geetest/pre'
        return self._session.get(url=url).json()

    def videoDelete(self, aid, geetest_challenge, geetest_validate, geetest_seccode):
        "删除视频"
        url = 'https://member.bilibili.com/x/web/archive/delete'
        post_data = {
            "aid": aid,
            "geetest_challenge": geetest_challenge,
            "geetest_validate": geetest_validate,
            "geetest_seccode": geetest_seccode,
            "success": 1,
            "csrf": self._bili_jct
            }
        return self._session.post(url, post_data).json()

    @staticmethod
    def activityList(plat='2', mold=0, http=3, start_page=1, end_page=10):
        "获取B站活动列表，生成器"
        session = requests.sessions.Session()
        url = f'https://www.bilibili.com/activity/page/list?plat={plat}&mold={mold}&http={http}&page={start_page}'
        list = session.get(url).json()["data"]["list"]
        while len(list):
            for x in list:
                yield x
            if start_page == end_page:
                break
            start_page += 1
            url = f'https://www.bilibili.com/activity/page/list?plat={plat}&mold={mold}&http={http}&page={start_page}'
            list = session.get(url).json()["data"]["list"]
        session.close()

    @staticmethod
    def activityAll():
        "获取B站活动列表"
        url = 'https://member.bilibili.com/x/app/h5/activity/videoall'
        return requests.get(url).json()

    def activityAddTimes(self, sid: 'str 活动sid', action_type: 'int 操作类型'):
        "增加B站活动的参与次数"
        url = 'https://api.bilibili.com/x/activity/lottery/addtimes'
        post_data = {
            "sid": sid,
            "action_type": action_type,
            "csrf": self._bili_jct
            }
        #响应例子{"code":75405,"message":"获得的抽奖次数已达到上限","ttl":1}
        return self._session.post(url, post_data).json()

    def activityDo(self, sid: 'str 活动sid', type: 'int 操作类型'):
        "参与B站活动"
        #B站有时候举行抽奖之类的活动，活动页面能查出活动的sid
        post_data = {
            "sid": sid,
            "type": type,
            "csrf": self._bili_jct
            }
        #响应例子{"code":75415,"message":"抽奖次数不足","ttl":1,"data":null}
        return self._session.post('https://api.bilibili.com/x/activity/lottery/do', post_data).json()

    def activityMyTimes(self, sid: 'str 活动sid'):
        "获取B站活动次数"
        url = f'https://api.bilibili.com/x/activity/lottery/mytimes?sid={sid}'
        #响应例子{"code":0,"message":"0","ttl":1,"data":{"times":0}}
        return self._session.get(url=url).json()

    def xliveGetAward(self, platform="android"):
        "B站直播模拟客户端打开宝箱领取银瓜子"
        url = f'https://api.live.bilibili.com/lottery/v1/SilverBox/getAward?platform={platform}'
        return self._session.get(url).json()

    def xliveGetCurrentTask(self, platform="android"):
        "B站直播模拟客户端获取时间宝箱"
        url = f'https://api.live.bilibili.com/lottery/v1/SilverBox/getCurrentTask?platform={platform}'
        return self._session.get(url).json()

    def xliveGiftBagList(self):
        "B站直播获取背包礼物"
        url = 'https://api.live.bilibili.com/xlive/web-room/v1/gift/bag_list'
        return self._session.get(url=url).json()

    def xliveGetRecommendList(self):
        "B站直播获取首页前10条直播"
        url = f'https://api.live.bilibili.com/relation/v1/AppWeb/getRecommendList'
        return self._session.get(url=url).json()

    def xliveBagSend(self, biz_id, ruid, bag_id, gift_id, gift_num, storm_beat_id=0, price=0, platform="pc"):
        "B站直播送出背包礼物"
        url = 'https://api.live.bilibili.com/gift/v2/live/bag_send'
        post_data = {
            "uid": self._uid,
            "gift_id": gift_id, #背包里的礼物id
            "ruid": ruid, #up主的uid
            "send_ruid": 0,
            "gift_num": gift_num, #送礼物的数量
            "bag_id": bag_id, #背包id
            "platform": platform, #平台
            "biz_code": "live",
            "biz_id": biz_id, #房间号
            #"rnd": rnd, #直播开始时间
            "storm_beat_id": storm_beat_id,
            "price": price, #礼物价格
            "csrf": self._bili_jct
            }
        return self._session.post(url,post_data).json()

    def xliveGetRoomInfo(self, room_id: 'int 房间id'):
        "B站直播获取房间信息"
        url = f'https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom?room_id={room_id}'
        return self._session.get(url=url).json()

    def xliveWebHeartBeat(self, biz_id, last=11, platform="web"):
        "B站直播 直播间心跳"
        import base64
        hb = base64.b64encode(f'{last}|{biz_id}|1|0'.encode('utf-8')).decode()
        url = f'https://live-trace.bilibili.com/xlive/rdata-interface/v1/heartbeat/webHeartBeat?hb={hb}&pf={platform}'
        return self._session.get(url).json()

    def xliveHeartBeat(self):
        "B站直播 心跳(大约2分半一次)"
        url = f'https://api.live.bilibili.com/relation/v1/Feed/heartBeat'
        return self._session.get(url).json()

    def xliveUserOnlineHeart(self):
        "B站直播 用户在线心跳(很少见)"
        url = f'https://api.live.bilibili.com/User/userOnlineHeart'
        post_data = {
            "csrf": self._bili_jct
            }
        content = self._session.post(url, post_data)
        return self._session.post(url, post_data).json()

    def mangaClockIn(self, platform="android"):
        "模拟B站漫画客户端签到"
        url = "https://manga.bilibili.com/twirp/activity.v1.Activity/ClockIn"
        post_data = {
            "platform": platform
            }
        return self._session.post(url, post_data).json()

    def mangaGetWallet(self, platform="web"):
        "获取钱包信息"
        url = f'https://manga.bilibili.com/twirp/user.v1.User/GetWallet?platform={platform}'
        #{"code":0,"msg":"","data":{"remain_coupon":0,"remain_gold":0,"first_reward":false,"point":"1270","first_bonus_percent":0,"bonus_percent":0,"unusable_gold":0,"remain_item":0,"remain_tickets":0,"remain_discount":0,"account_level":0}}
        #                               劵的数量        金币数量         是否第一次充值          积分
        return self._session.post(url, json={}).json()

    def mangaComrade(self, platform="web"):
        "站友日漫画卷兑换查询"
        url = f'https://manga.bilibili.com/twirp/activity.v1.Activity/Comrade?platform={platform}'
        #{"code":0,"msg":"","data":{"now":"2020-09-20T21:10:38+08:00","received":0,"active":0,"lottery":0,"svip":1}}
        return self._session.post(url, json={}).json()

    def mangaGetEpisodeBuyInfo(self, ep_id: int, platform="web"):
        "获取漫画购买信息"
        url = f'https://manga.bilibili.com/twirp/comic.v1.Comic/GetEpisodeBuyInfo?platform={platform}'
        post_data = {
            "ep_id": ep_id
            }
        return self._session.post(url, json=post_data).json()

    def mangaBuyEpisode(self, ep_id: int, buy_method=1, coupon_id=0, auto_pay_gold_status=0, platform="web"):
        "购买漫画"
        url = f'https://manga.bilibili.com/twirp/comic.v1.Comic/BuyEpisode?&platform={platform}'
        post_data = {
            "buy_method": buy_method,
            "ep_id": ep_id
            }
        #{"buy_method":2,"ep_id":283578,"coupon_id":2064528,"auto_pay_gold_status":2}
        if coupon_id:
            post_data["coupon_id"] = coupon_id
        if auto_pay_gold_status:
            post_data["auto_pay_gold_status"] = auto_pay_gold_status

        #{"code":1,"msg":"没有足够的卡券使用次数，请刷新重试。","data":{"auto_use_item":""}}
        return self._session.post(url, json=post_data).json()

    def mangaGetTopic(self, page_num=1, platform='phone'):
        "B站漫画app活动中心列表"
        url = 'https://manga.bilibili.com/twirp/comic.v1.Comic/Topic'
        post_data = {
            "page_num": page_num,
            "platform": platform
            }
        return self._session.post(url, post_data).json()

    def mangaListFavorite(self, page_num=1, page_size=50, order=1, wait_free=0, platform='web'):
        "B站漫画追漫列表"
        url = 'https://manga.bilibili.com/twirp/bookshelf.v1.Bookshelf/ListFavorite?platform={platform}'
        post_data = {
            "page_num": page_num,
            "page_size": page_size,
            "order": order,
            "wait_free": wait_free
            }
        return self._session.post(url, json=post_data).json()

    def mangaPayBCoin(self, pay_amount: int, product_id=1, platform='web'):
        "B币购买漫画"
        url = f'https://manga.bilibili.com/twirp/pay.v1.Pay/PayBCoin?platform={platform}'
        post_data = {
            "pay_amount": pay_amount,
            "product_id": product_id
            }
        #{"code":0,"msg":"","data":{"id":"1600656017507211119"}}
        return self._session.post(url, json=post_data).json()

    def mangaGetBCoin(self, platform='web'):
        "获取B币与漫读劵的信息"
        url = f'https://manga.bilibili.com/twirp/pay.v1.Pay/GetBCoin?platform={platform}'
        #{"code":0,"msg":"","data":{"amount":0,"exchange_rate":100,"first_max_coin":18800,"first_bonus_percent":0,"bonus_percent":0,"coupon_rate":2,"coupon_exp":30,"point_rate":200,"coin_amount":0,"coupon_amount":0,"is_old_version":true}}
        return self._session.post(url, json={}).json()

    def mangaGetCoupons(self, not_expired=True, page_num=1, page_size=50, tab_type=1, platform='web'):
        "获取账户中的漫读劵信息"
        url = f'https://manga.bilibili.com/twirp/user.v1.User/GetCoupons?platform={platform}'
        post_data = {
            "not_expired": not_expired,
            "page_num": page_num,
            "page_size": page_size,
            "tab_type": tab_type
            }
        #{"code":0,"msg":"","data":{"total_remain_amount":4,"user_coupons":[{"ID":2093696,"remain_amount":2,"expire_time":"2020-10-21 10:40:17","reason":"B币兑换","type":"福利券","ctime":"2020-09-21 10:40:17","total_amount":2,"limits":[],"type_num":7,"will_expire":0,"discount":0,"discount_limit":0,"is_from_card":0},{"ID":2093703,"remain_amount":2,"expire_time":"2020-10-21 10:47:43","reason":"B币兑换","type":"福利券","ctime":"2020-09-21 10:47:43","total_amount":2,"limits":[],"type_num":7,"will_expire":0,"discount":0,"discount_limit":0,"is_from_card":0}],"coupon_info":{"new_coupon_num":0,"coupon_will_expire":0,"rent_will_expire":0,"new_rent_num":0,"discount_will_expire":0,"new_discount_num":0,"month_ticket_will_expire":0,"new_month_ticket_num":0,"silver_will_expire":0,"new_silver_num":0,"remain_item":0,"remain_discount":0,"remain_coupon":4,"remain_silver":0}}}
        return self._session.post(url, json=post_data).json()

    def mangaDetail(self, comic_id: int, device='android', version='3.7.0'):
        "获取漫画信息"
        url = 'https://manga.bilibili.com/twirp/comic.v1.Comic/ComicDetail'
        post_data = {
            "device": device,
            "version": version,
            "comic_id": comic_id
            }
        return self._session.post(url, post_data).json()

    def mangaGetPoint(self):
        "获取漫画积分"
        url = f'https://manga.bilibili.com/twirp/pointshop.v1.Pointshop/GetUserPoint'
        return self._session.post(url, json={}).json()

    def mangaShopList(self):
        "漫画积分商城列表"
        url = f'https://manga.bilibili.com/twirp/pointshop.v1.Pointshop/ListProduct'
        return self._session.post(url, json={}).json()

    def mangaShopExchange(self, product_id: int, point: int, product_num=1):
        "漫画积分商城兑换"
        url = f'https://manga.bilibili.com/twirp/pointshop.v1.Pointshop/Exchange'
        post_data = {
            "product_id": product_id,
            "point": point,
            "product_num": product_num
            }
        return self._session.post(url, json=post_data).json()

    def mangaImageToken(self, urls=[], device='pc', platform='web'):
        "获取漫画图片token"
        url = f'https://manga.bilibili.com/twirp/comic.v1.Comic/ImageToken?device={device}&platform={platform}'
        post_data = {
            "urls": json.dumps(urls)
            }
        return self._session.post(url, json=post_data).json()

    def mangaImageIndex(self, ep_id: int, device='android', version='3.7.0'):
        "获取漫画图片列表"
        url = 'https://manga.bilibili.com/twirp/comic.v1.Comic/GetImageIndex'
        post_data = {
            "device": device,
            "version": version,
            "ep_id": ep_id
            }
        return self._session.post(url, post_data).json()

    def mangaGetImageBytes(self, url: str):
        "获取漫画图片"
        return self._session.get(url).content

    def mangaGetVipReward(self):
        "获取漫画大会员福利"
        url = 'https://manga.bilibili.com/twirp/user.v1.User/GetVipReward'
        return self._session.post(url, json={"reason_id":1}).json()

    def vipPrivilegeMy(self):
        "B站大会员权益列表"
        url = 'https://api.bilibili.com/x/vip/privilege/my'
        #{"code":0,"message":"0","ttl":1,"data":{"list":[{"type":1,"state":1,"expire_time":1601481599},{"type":2,"state":0,"expire_time":1601481599}]}}
        return self._session.get(url).json()

    def vipPrivilegeReceive(self, type=1):
        "领取B站大会员权益"
        url = 'https://api.bilibili.com/x/vip/privilege/receive'
        post_data = {
            "type": type,
            "csrf": self._bili_jct
            }
        #{"code":69801,"message":"你已领取过该权益","ttl":1}
        return self._session.post(url, data=post_data).json()

    def webView(self, bvid: str):
        "通过bv号获取视频信息"
        url = f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}'
        return self._session.get(url).json()

    def webStat(self, aid: int):
        "通过av号获取视频信息"
        url = f'https://api.bilibili.com/x/web-interface/archive/stat?aid={aid}'
        return self._session.get(url).json()

    def playList(self, bvid='', aid=0):
        "获取播放列表"
        if bvid:
            url = f'https://api.bilibili.com/x/player/pagelist?bvid={bvid}'
        elif aid:
            url = f'https://api.bilibili.com/x/player/pagelist?bvid={aid}'
        return self._session.get(url).json()

    def epPlayList(self, ep_or_ss: str):
        "获取番剧播放列表"
        url = f'https://www.bilibili.com/bangumi/play/{ep_or_ss}'
        text = self._session.get(url, headers={'User-Agent':'Mozilla/5.0'}).text
        find = re.findall(r'window.__INITIAL_STATE__=({.*});\(function\(\)', text, re.S)
        return json.loads(find[0])

    def webPlayUrl(self, cid=0, aid=0, bvid='', epid=0, qn=16):
        "获取番剧播放地址(普通视频请用playerUrl方法)"
        url = 'https://api.bilibili.com/pgc/player/web/playurl'
        data = {"qn":qn}
        if cid:
            data["cid"] = cid
        if aid:
            data["avid"] = aid
        if bvid:
            data["bvid"] = bvid
        if epid:
            data["ep_id"] = epid
        #{'code': -10403, 'message': '抱歉您所在地区不可观看！'}
        #{'code': -10403, 'message': '大会员专享限制'}
        return self._session.get(url, params=data).json()

    def playerUrl(self, cid: int, aid=0, bvid='', qn=16, reverse_proxy=''):
        "获取视频播放地址"
        if reverse_proxy:
            url = reverse_proxy
        else:
            url = 'https://api.bilibili.com/x/player/playurl'
        #data = {"qn":qn,"cid":cid,'fnval':80}
        data = {"qn":qn,"cid":cid}
        if aid:
            data["avid"] = aid
        if bvid:
            data["bvid"] = bvid
        return self._session.get(url, params=data).json()

    def getRoomPlayInfo(self,
                        room_id: int,
                        protocol: str = '0,1',
                        format: str = '0,2',
                        codec: str = '0,1',
                        qn: int = 1000,
                        ptype: int = 16,
                        platform: str = 'web'
                        ) -> dict:
        '''B站直播获取视频流'''
        params = {
            "room_id": room_id,
            "protocol": protocol,
            "format": format,
            "codec": codec,
            "qn": qn,
            "ptype": ptype,
            "platform": platform
            }
        url = 'https://api.live.bilibili.com/xlive/web-room/v2/index/getRoomPlayInfo'
        return self._session.get(url, params=params).json()

    def audioMenuInfo(self, 
                      am_id: int
                      ) -> dict:
        '''
        查询音频菜单信息
        am_id int 音频菜单id
        return dict 音频菜单信息
        '''
        url = f'https://www.bilibili.com/audio/music-service-c/web/menu/info?sid={am_id}'
        return self._session.get(url).json()

    def audioMenuList(self, 
                      am_id: int,
                      pn: int = 1,
                      ps: int = 100
                      ) -> dict:
        '''
        查询音频菜单音乐列表
        am_id int 音频菜单id
        pn    int 页数
        ps    int 每页音频数
        return dict 音频列表信息
        '''
        url = f'https://www.bilibili.com/audio/music-service-c/web/song/of-menu?sid={am_id}&pn={pn}&ps={ps}'
        return self._session.get(url).json()

    def audioInfo(self, 
                  au_id: int
                  ) -> dict:
        '''
        查询音频信息
        au_id  int 音频id
        return dict 音频信息
        '''
        url = f'https://www.bilibili.com/audio/music-service-c/web/song/info?sid={au_id}'
        return self._session.get(url).json()

    def audioUrl(self, 
                 au_id: int,
                 privilege: int = 2,
                 quality: int = 2
                 ) -> dict:
        '''
        查询音频下载地址
        au_id     int  音频id
        privilege int
        quality   int
        return dict 音频下载地址
        '''
        url = f'https://www.bilibili.com/audio/music-service-c/web/url?sid={au_id}&privilege={privilege}&quality={quality}'
        return self._session.get(url).json()

    def audioCategories(self) -> dict:
        '''
        查询音频种类(中文)与type(整数)的对应关系
        返回  音频种类列表
        '''
        url = 'https://www.bilibili.com/audio/music-service/songs/categories'
        return self._session.get(url).json()

    def audioImageUpload(self,
                         image: str
                         ) -> dict:
        '''
        上传音频封面
        image str base64编码的图片数据
        返回  音频封面url
        '''
        url = 'https://www.bilibili.com/audio/music-service/songs/image'
        files = {
            'file': (None, image)
            }
        #注意是用multipart/form-data方式post，不能用data和json两个参赛而是用files
        return self._session.post(url, files=files).json()

    def audioActivityInfo(self) -> dict:
        '''
        查询音频投稿活动
        返回  音频活动列表
        '''
        url = 'https://www.bilibili.com/audio/music-service/songs/activityInfo'
        #{"code":72000000,"msg":"未获取到活动信息null","data":null}
        return self._session.get(url).json()

    def audioLyricUpload(self,
                         song_id: int,
                         lyric: str
                         ) -> dict:
        '''
        上传音频歌词
        song_id int  音频id
        lyric   str  音频信息
        返回    dict 歌词链接
        '''
        url = 'https://www.bilibili.com/audio/music-service/songs/lrc'
        data = {
            "song_id": song_id,
            "lrc": lyric
            }
        return self._session.post(url, data).json()

    def audioSubmit(self,
                    data: dict
                    ) -> dict:
        '''
        提交音频稿件
        data dict 音频信息
        返回  提交信息
        '''
        url = 'https://www.bilibili.com/audio/music-service/songs'
        #{"code":0,"msg":"success","data":1986498}
        return self._session.post(url, json=data).json()

    def audioCompilationSongSubmit(self,
                                   data: dict
                                   ) -> dict:
        '''
        提交合辑里单个音频
        data dict 音频信息
        返回  提交信息
        '''
        url = 'https://www.bilibili.com/audio/music-service/compilation/commit_songs'
        #{"code":0,"msg":"success","data":""}
        return self._session.post(url, json=data).json()

    def audioCompilationCategories(self) -> dict:
        '''
        查询音频种类(中文)与type(整数)的对应关系
        返回  音频种类列表
        '''
        url = 'https://www.bilibili.com/audio/music-service/compilation/compilation_categories'
        return self._session.get(url).json()

    def audioCompilationSubmit(self,
                               data: dict
                               ) -> dict:
        '''
        提交音频合辑
        data dict 音频合辑信息
        返回  提交信息
        '''
        url = 'https://www.bilibili.com/audio/music-service/compilation/commit_compilation'
        #{"code":0,"msg":"success","data":31655539}
        return self._session.post(url, json=data).json()

    def getUrlStream(self, 
                     url: str, 
                     chunk_size: int = 1048576
                     ) -> bytes:
        '''
        使用get方式读取url文件，生成器，每次返回最多chunk_size个字节
        url        str   网络文件的url
        chunk_size int   每次最多返回多少字节
        return     bytes 包含网络文件的字节
        '''
        res = self._session.get(url, stream=True)
        for chunk in res.iter_content(chunk_size=chunk_size):
            if chunk:
                yield chunk

    def getUrl(self, 
               url: str
               ) -> bytes:
        '''
        使用get方式读取url文件，生成器，每次返回最多chunk_size个字节
        url    str   网络文件的url
        return bytes 包含网络文件的字节
        '''
        return self._session.get(url).content

    @staticmethod
    def videoGetPart(url: str, start, end):
        "下载视频分段"
        headers = {"Range":f'bytes={start}-{end}',"Referer": "https://www.bilibili.com/"}
        return requests.get(url, headers=headers).content

    @staticmethod
    def dmList(oid: int):
        "获得弹幕xml"
        url = f'https://api.bilibili.com/x/v1/dm/list.so?oid={oid}'
        content = requests.get(url)
        content.encoding = 'utf-8'
        return content.text

    @staticmethod
    def dmHistory(oid: int, data: str):
        "获得历史弹幕xml"
        url = f'https://api.bilibili.com/x/v2/dm/history?type=1&oid={oid}&date={data}'
        content = requests.get(url)
        content.encoding = 'utf-8'
        return content.text

    @staticmethod
    def bv2av(bvid: str):
        '''B站bv号转av号'''
        tr = {'f': 0, 'Z': 1, 'o': 2, 'd': 3, 'R': 4, '9': 5, 'X': 6, 'Q': 7, 'D': 8, 'S': 9, 'U': 10, 'm': 11, '2': 12, '1': 13, 'y': 14, 'C': 15, 'k': 16, 'r': 17, '6': 18, 'z': 19, 'B': 20, 'q': 21, 'i': 22, 'v': 23, 'e': 24, 'Y': 25, 'a': 26, 'h': 27, '8': 28, 'b': 29, 't': 30, '4': 31, 'x': 32, 's': 33, 'W': 34, 'p': 35, 'H': 36, 'n': 37, 'J': 38, 'E': 39, '7': 40, 'j': 41, 'L': 42, '5': 43, 'V': 44, 'G': 45, '3': 46, 'g': 47, 'u': 48, 'M': 49, 'T': 50, 'K': 51, 'N': 52, 'P': 53, 'A': 54, 'w': 55, 'c': 56, 'F': 57}
        s = (11,10,3,8,4,6)
        xor = 177451812
        add = 8728348608
        r = 0
        for i in range(6):
            r += tr[bvid[s[i]]]*58**i
        return (r - add) ^ xor
        #return BiliApi.webView(bvid)["data"]["aid"]

    @staticmethod
    def av2bv(aid: int):
        '''B站av号转bv号'''
        table='fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
        s = (11,10,3,8,4,6)
        xor = 177451812
        add = 8728348608
        aid = (aid ^ xor) + add
        r = list('BV1  4 1 7  ')
        for i in range(6):
            r[s[i]] = table[aid//58**i%58]
        return ''.join(r)
        #return BiliApi.webStat(aid)["data"]["bvid"]

    def _getKey(self):
        '''获得登录秘钥'''
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': "application/json, text/javascript, */*; q=0.01"
        }
        post_data = {
            'appkey': APPKEY,
            'platform': "pc",
            'ts': int(time.time())
        }
        post_data['sign'] = BiliApi._sign_dict(post_data, APPSECRET)

        ret = self._session.post(
            'https://passport.bilibili.com/api/oauth2/getKey',
            headers=headers,
            data=post_data
            ).json()
        assert 0 == ret["code"]

        return ret["data"]["hash"], ret["data"]["key"]

    @staticmethod
    def _sign_str(data: str, app_secret: str):
        return hashlib.md5((data + app_secret).encode("utf-8")).hexdigest()

    @staticmethod
    def _sign_dict(data: dict, app_secret: str):
        data_str = []
        keys = list(data.keys())
        keys.sort()
        for key in keys:
            data_str.append("{}={}".format(key, data[key]))
        data_str = "&".join(data_str)
        data_str = data_str + app_secret
        return hashlib.md5(data_str.encode("utf-8")).hexdigest()

    @staticmethod
    def _encrypt_login_password(password, hash, pubkey):
        return base64.b64encode(rsa.encrypt(
            (hash + password).encode('utf-8'),
            rsa.PublicKey.load_pkcs1_openssl_pem(pubkey.encode()),
        ))

    def close(self):
        '''关闭'''
        self._session.close()

    def __del__(self):
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()