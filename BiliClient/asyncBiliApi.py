# -*- coding: utf-8 -*-
from aiohttp import ClientSession
from typing import Iterable, Mapping, Dict, Awaitable, Any, Optional
import time, json

_default_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
    "Referer": "https://www.bilibili.com/",
    'Connection': 'keep-alive'
    }

class asyncBiliApi(object):
    '''B站异步接口类'''
    def __init__(self,
                 headers: Optional[Dict[str, str]]
                 ):
        if not headers:
            headers = _default_headers
        
        self._islogin = False
        self._show_name = None
        self._session = ClientSession(
                headers = headers,
                trust_env = True
                )
    
    async def login_by_cookie(self, 
                              cookieData, 
                              checkBanned=True, 
                              strict=False
                              ) -> Awaitable[bool]:
        '''
        登录并获取账户信息
        cookieData dict 账户cookie
        checkBanned bool 检查是否被封禁
        strict bool 是否严格限制cookie在.bilibili.com域名之下
        '''
        if strict:
            from yarl import URL
            self._session.cookie_jar.update_cookies(cookieData, URL('https://.bilibili.com'))
        else:
            self._session.cookie_jar.update_cookies(cookieData)

        await self.refreshInfo()
        if not self._islogin:
            return False

        if 'bili_jct' in cookieData:
            self._bili_jct = cookieData["bili_jct"]
        else:
            self._bili_jct = ''

        self._isBanned = None
        if checkBanned:
            code = (await self.likeCv(7793107))["code"]
            if code != 0 and code != 65006 and code != -404:
                self._isBanned = True
                import warnings
                warnings.warn(f'{self._name}:账号异常，请检查bili_jct参数是否有效或本账号是否被封禁')
            else:
                self._isBanned = False

        return True

    @property
    def banned(self):
        '''是否账号被异常封禁'''
        return self._isBanned

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
        '''获取用于显示的用户名'''
        return self._show_name

    @name.setter
    def name(self, name: str) -> None:
        '''设置用于显示的用户名'''
        self._show_name = name

    @property
    def username(self) -> str:
        '''获取登录的账户用户名'''
        return self._name

    @property
    def uid(self) -> int:
        '''获取登录的账户uid'''
        return self._uid

    @property
    def level(self) -> int:
        '''获取登录的账户等级'''
        return self._level

    async def refreshInfo(self) -> Awaitable:
        '''刷新账户信息(需要先登录)'''
        ret = await self.getWebNav()
        if ret["code"] != 0:
            self._islogin = False
            return

        self._islogin = True
        self._name = ret["data"]["uname"]
        self._uid = ret["data"]["mid"]
        self._vip = ret["data"]["vipType"]
        self._level = ret["data"]["level_info"]["current_level"]
        self._verified = ret["data"]["mobile_verified"]
        self._coin = ret["data"]["money"]
        self._exp = ret["data"]["level_info"]["current_exp"]
        if not self._show_name:
            self._show_name = self._name

    def refreshCookie(self) -> None:
        '''刷新cookie(需要先登录)'''
        cookies = {}
        keys = ("SESSDATA","bili_jct","DedeUserID","LIVE_BUVID")
        for x in self._session.cookie_jar:
            if x.key in keys:
                cookies[x.key] = x.value
        self._session.cookie_jar.clear()
        self._session.cookie_jar.update_cookies(cookies)

    async def getFollowings(self, 
                            uid: int = None, 
                            pn: int = 1, 
                            ps: int = 50, 
                            order: str = 'desc', 
                            order_type: str = 'attention'
                            ) -> Awaitable[Dict[str, Any]]:
        '''
        获取指定用户关注的up主
        uid int 账户uid，默认为本账户，非登录账户只能获取20个*5页
        pn int 页码，默认第一页
        ps int 每页数量，默认50
        order str 排序方式，默认desc
        order_type 排序类型，默认attention
        '''
        if not uid:
            uid = self._uid
        url = f'https://api.bilibili.com/x/relation/followings?vmid={uid}&pn={pn}&ps={ps}&order={order}&order_type={order_type}'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def spaceArticle(self, 
                            uid: int = None,
                            pn: int = 1, 
                            ps: int = 30, 
                            sort: str = 'publish_time', 
                            ) -> Awaitable[Dict[str, Any]]:
        '''
        获取指定up主空间专栏投稿信息
        uid int 账户uid，默认为本账户
        pn int 页码，默认第一页
        ps int 每页数量，默认50
        sort str 排序方式，默认publish_time
        '''
        if not uid:
            uid = self._uid
        url = f'https://api.bilibili.com/x/space/article?mid={uid}&pn={pn}&ps={ps}&sort={sort}'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def spaceArcSearch(self, 
                          uid: int = None,
                          pn: int = 1, 
                          ps: int = 100, 
                          tid: int = 0,
                          order: str = 'pubdate', 
                          keyword: str = ''
                          ) -> Awaitable[Dict[str, Any]]:
        '''
        获取指定up主空间视频投稿信息
        uid int 账户uid，默认为本账户
        pn int 页码，默认第一页
        ps int 每页数量，默认50
        tid int 分区 默认为0(所有分区)
        order str 排序方式，默认pubdate
        keyword str 关键字，默认为空
        '''
        if not uid:
            uid = self._uid
        url = f'https://api.bilibili.com/x/space/arc/search?mid={uid}&pn={pn}&ps={ps}&tid={tid}&order={order}&keyword={keyword}'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def search(self, 
                     keyword: str = '',
                     context: str = '',
                     page: int = 1,
                     tids: int = 0,
                     order: str = '', 
                     duration: int = 0,
                     search_type: str = 'video'
                     ) -> Awaitable[Dict[str, Any]]:
        '''
        获取指定视频投稿信息
        keyword str 关键字
        context str 未知
        page int 页码，默认第一页
        tids int 分区 默认为0(所有分区)
        order str 排序方式，默认为空(综合排序)
        duration int 时长过滤，默认0(所有时长)
        search_type str 搜索类型，默认video(视频)
        '''
        params = {
            "keyword": keyword,
            "context": context,
            "page": page,
            "tids": tids,
            "order": order,
            "duration": duration,
            "search_type": search_type,
            "single_column": 0,
            "__refresh__": "true",
            "tids_2": '',
            "_extra": ''
            }
        url = 'https://api.bilibili.com/x/web-interface/search/type'
        async with self._session.get(url, params=params, verify_ssl=False) as r:
            return await r.json()

    async def followUser(self, 
                         followid: int, 
                         type: int = 1
                         ):
        '''
        关注或取关up主
        followid int 要操作up主的uid
        type int 操作类型 1关注 0取关
        '''
        url = "https://api.vc.bilibili.com/feed/v1/feed/SetUserFollow"
        post_data = {
            "type": type,
            "follow": followid,
            "csrf_token": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()

    async def getMyGroups(self) -> Awaitable[Dict[str, Any]]:
        '''取应援团列表'''
        url = "https://api.vc.bilibili.com/link_group/v1/member/my_groups"
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def expRewardInfo(self) -> Awaitable[Dict[str, Any]]:
        '''取经验获取信息'''
        url = "https://api.bilibili.com/x/member/web/exp/reward"
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def joinGroup(self,
                        group_id: int,
                        mobi_app: str = 'web'
                        ) -> Awaitable[Dict[str, Any]]:
        '''
        加入应援团
        group_id    int  应援团id
        mobi_app    str  平台
        '''
        url = "https://api.vc.bilibili.com/link_group/v1/group/join_group_without_agree"
        post_data = {
            "group_id": group_id,
            "mobi_app": mobi_app,
            "build": 0,
            "csrf": self._bili_jct,
            "csrf_token": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()

    async def groupSign(self,
                        group_id: int,
                        owner_id: int
                        ) -> Awaitable[Dict[str, Any]]:
        '''
        应援团签到
        group_id int 应援团id
        owner_id int 应援团所有者uid
        '''
        url = f'https://api.vc.bilibili.com/link_setting/v1/link_setting/sign_in?group_id={group_id}&owner_id={owner_id}'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()
        #{"code":700017,"msg":"不能加入多个同一UP的应援团哦~","message":"不能加入多个同一UP的应援团哦~","data":{"group_id":-1}}

    async def getRelationTags(self) -> Awaitable[Dict[str, Any]]:
        '''取关注用户分组列表'''
        url = "https://api.bilibili.com/x/relation/tags"
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def getRelationTag(self,
                             tagid: int,
                             mid: int = None,
                             pn: int = 1,
                             ps: int = 50,
                             ) -> Awaitable[Dict[str, Any]]:
        '''取关注用户分组用户列表'''
        if not mid:
            mid = self._uid
        url = f"https://api.bilibili.com/x/relation/tag?mid={mid}&tagid={tagid}&pn={pn}&ps={ps}"
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def relationTagsAddUser(self,
                                  fids: int,
                                  tagids: int
                                  ) -> Awaitable[Dict[str, Any]]:
        '''
        将用户加入关注分组
        fids    int  用户名称
        tagids  int  分组id
        '''
        url = "https://api.bilibili.com/x/relation/tags/addUsers"
        post_data = {
            "fids": fids,
            "tagids": tagids,
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()

    async def createRelationTag(self,
                                tag: str
                                ) -> Awaitable[Dict[str, Any]]:
        '''
        创建用户分组
        tag  str  分组名称
        '''
        url = "https://api.bilibili.com/x/relation/tag/create"
        post_data = {
            "tag": tag,
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()

    async def getRelationByUid(self,
                          uid: int
                          ) -> Awaitable[Dict[str, Any]]:
        '''
        判断与某个up关系
        是否关注，关注时间，是否拉黑.....
        uid int up主uid
        '''
        url = f"https://api.bilibili.com/x/relation?fid={uid}"
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def getRelation(self,
                          tagid: int = 0,
                          pn: int = 1,
                          ps: int = 50
                          )-> dict:
        '''
        取关注分组内up主列表
        tagid int 分组id
        '''
        url = f"https://api.bilibili.com/x/relation/tag?tagid={tagid}&pn={pn}&ps={ps}"
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def getWebNav(self) -> Awaitable[Dict[str, Any]]:
        '''取导航信息'''
        url = "https://api.bilibili.com/x/web-interface/nav"
        async with self._session.get(url, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def getReward(self) -> Awaitable[Dict[str, Any]]:
        '''取B站经验信息'''
        url = "https://account.bilibili.com/home/reward"
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()
    
    async def likeCv(self, 
                     cvid: int, 
                     type=1) -> Awaitable[Dict[str, Any]]:
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
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()

    async def vipPrivilegeReceive(self, 
                                  type: int = 1
                                  ) -> Awaitable[Dict[str, Any]]:
        '''
        领取B站大会员权益
        type int 权益类型，1为B币劵，2为优惠券
        '''
        url = 'https://api.bilibili.com/x/vip/privilege/receive'
        post_data = {
            "type": type,
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()

    async def vipPrivilegeList(self) -> Awaitable[Dict[str, Any]]:
        '''获取B站大会员权益列表(B币劵，优惠券)'''
        url = 'https://api.bilibili.com/x/vip/privilege/my'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def getUserWallet(self, 
                            platformType: int = 3
                            ) -> Awaitable[Dict[str, Any]]:
        '''
        获取账户钱包信息
        platformType int 平台类型
        '''
        url = 'https://pay.bilibili.com/paywallet/wallet/getUserWallet'
        post_data = {
            "platformType": platformType
            }
        async with self._session.post(url, json=post_data, verify_ssl=False) as r:
            return await r.json()

    async def elecPayBcoin(self, 
                      uid: int, 
                      num: int = 5
                      ) -> Awaitable[Dict[str, Any]]:
        '''
        用B币给up主充电
        uid int up主uid
        num int B币数量
        '''
        url = 'https://api.bilibili.com/x/ugcpay/web/v2/trade/elec/pay/quick'
        post_data = {
            "bp_num": num,
            "is_bp_remains_prior": True,
            "up_mid": uid,
            "otype": 'up',
            "oid": uid,
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()

    async def getDanmuInfo(self,
                           roomid: int
                           ) -> Awaitable[Dict[str, Any]]:
        '''
        查询直播间弹幕服务器
        roomid int 真实房间id，非短id
        '''
        url = f'https://api.live.bilibili.com/xlive/web-room/v1/index/getDanmuInfo?id={roomid}&type=0'
        async with self._session.get(url, verify_ssl=False) as r:
            ret = await r.json()
        return ret
        #{"code":0,"message":"0","ttl":1,"data":{"group":"live","business_id":0,"refresh_row_factor":0.125,"refresh_rate":100,"max_delay":5000,"token":"vaG2ohBUDKuY_jkQKdXZt9fioOBO_kxGzv60xj_8YAIehdpbY_BwIMkUnS5wkyaU1lTBe0J8HQbo0ki6gNeqwEfc3W5SCNICTC7NxyVW_V0gTu_4Kf3MROvRCU_E87RpA9R24znPV0M=","host_list":[{"host":"tx-bj-live-comet-03.chat.bilibili.com","port":2243,"wss_port":443,"ws_port":2244},{"host":"hw-sh-live-comet-05.chat.bilibili.com","port":2243,"wss_port":443,"ws_port":2244},{"host":"broadcastlv.chat.bilibili.com","port":2243,"wss_port":443,"ws_port":2244}]}}

    async def xliveSecondGetList(self, 
                                 parent_area_id: int = 1,
                                 area_id: int = 0,
                                 sort_type: str = '',
                                 page: int = 1,
                                 platform: str = 'web'
                                 ) -> Awaitable[Dict[str, Any]]:
        '''
        获取指定分区直播间列表
        parent_area_id   int  大分区id  2网游 3手游 6单机 1娱乐 5电台 9虚拟主播 10生活 11学习
        area_id          int  小分区id  0为全部小分区，不同大分区有不同的小分区
        sort_type        str  排序方法  第一次请求为空，所有排序方法的值在本方法的返回值["data"]["new_tags"]里提供
        page             int  页数
        platform         str  平台，任意字符串
        '''
        url = f'https://api.live.bilibili.com/xlive/web-interface/v1/second/getList?platform={platform}&parent_area_id={parent_area_id}&area_id={area_id}&sort_type={sort_type}&page={page}'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def xliveGetRoomList(self, 
                               parent_area_id: int = 1,
                               area_id: int = 0,
                               sort_type: str = '',
                               page: int = 1,
                               platform: str = 'web'
                               ) -> Awaitable[Dict[str, Any]]:
        '''
        获取指定分区直播间列表
        parent_area_id   int  大分区id  2网游 3手游 6单机 1娱乐 5电台 9虚拟主播 10生活 11学习
        area_id          int  小分区id  0为全部小分区，不同大分区有不同的小分区
        sort_type        str  排序方法  第一次请求为空，所有排序方法的值在本方法的返回值["data"]["new_tags"]里提供
        page             int  页数
        platform         str  平台，任意字符串
        '''
        url = f'https://api.live.bilibili.com/room/v3/area/getRoomList?platform={platform}&parent_area_id={parent_area_id}&area_id={area_id}&sort_type={sort_type}&page={page}'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def xliveRoomInit(self, 
                            id: int = 1
                            ) -> Awaitable[Dict[str, Any]]:
        '''
        获取房间初始化信息(房间短id转长id)
        id int 直播间id
        '''
        url = f'https://api.live.bilibili.com/room/v1/Room/room_init?id={id}'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def xliveFansMedal(self, 
                           page: int = 1,
                           pageSize: int = 10,
                           ) -> Awaitable[Dict[str, Any]]:
        '''
        获取粉丝牌
        page int 页码
        pageSize int 字体颜色
        '''
        url = f'https://api.live.bilibili.com/fans_medal/v5/live_fans_medal/iApiMedal?page={page}&pageSize={pageSize}'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def xliveAnchorCheck(self,
                               roomid: int
                               ) -> Awaitable[Dict[str, Any]]:
        '''
        查询直播天选时刻
        roomid int 真实房间id，非短id
        '''
        url = f'https://api.live.bilibili.com/xlive/lottery-interface/v1/Anchor/Check?roomid={roomid}'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def xliveAnchorJoin(self,
                              id: int,
                              gift_id: int,
                              gift_num: int,
                              platform: str = 'pc'
                              ) -> Awaitable[Dict[str, Any]]:
        '''
        参与直播天选时刻
        id int 天选时刻id
        gift_id int 礼物id
        gift_num int 礼物数量
        '''
        url = 'https://api.live.bilibili.com/xlive/lottery-interface/v1/Anchor/Join'
        post_data = {
            "id": id,
            "gift_id": gift_id,
            "gift_num": gift_num,
            "platform": platform,
            "csrf_token": self._bili_jct,
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()
        #{"code":400,"data":null,"message":"余额不足","msg":"余额不足"}

    async def xlivePkJoin(self,
                          id: int,
                          room_id: int,
                          ) -> Awaitable[Dict[str, Any]]:
        '''
        参与直播大乱斗抽奖
        id       int   大乱斗id
        room_id  int   房间id
        '''
        url = 'https://api.live.bilibili.com/xlive/lottery-interface/v2/pk/join'
        post_data = {
            "id": id,
            "room_id": room_id,
            "type": "pk",
            "csrf_token": self._bili_jct,
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()

    async def xliveFeedHeartBeat(self) -> Awaitable[Dict[str, Any]]:
        '''直播心跳 feed'''
        url = 'https://api.live.bilibili.com/relation/v1/Feed/heartBeat'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()
        #{"code":0,"msg":"success","message":"success","data":{"open":1,"has_new":0,"count":0}}

    async def xliveMsgSend(self, 
                           roomid: int,
                           msg: str,
                           color: int = 16777215,
                           fontsize: int = 25,
                           mode: int = 1,
                           bubble: int = 0,
                           ) -> Awaitable[Dict[str, Any]]:
        '''
        直播间发送消息
        roomid int 直播间id
        msg str 要发送的消息
        color int 字体颜色
        fontsize int 字体大小
        mode int 发送模式，应该是控制滚动，底部这些
        bubble int 未知
        '''
        url = 'https://api.live.bilibili.com/msg/send'
        post_data = {
            "color": color,
            "fontsize": fontsize,
            "mode": mode,
            "msg": msg,
            "rnd": int(time.time()),
            "roomid": roomid,
            "bubble": bubble,
            "csrf_token": self._bili_jct,
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()

    async def xliveBp2Gold(self, 
                           num: int = 5, 
                           platform: str = 'pc'
                           ) -> Awaitable[Dict[str, Any]]:
        '''
        B币劵购买金瓜子
        num int 花费B币劵数量，目前1B币=1000金瓜子
        platform str 平台
        '''
        #此接口抓包于网页https://link.bilibili.com/p/center/index中金瓜子购买
        url = 'https://api.live.bilibili.com/xlive/revenue/v1/order/createOrder'
        post_data = {
            "platform": platform,
            "pay_bp": num * 1000, #兑换瓜子数量，目前1B币=1000金瓜子
            "context_id": 1, #未知作用
            "context_type": 11, #未知作用
            "goods_id": 1, #商品id
            "goods_num": num, #商品数量，这里是B币数量
            #"csrf_token": self._bili_jct,
            #"visit_id": 'acq5hn53owg0',#这两个不需要也能请求成功，csrf_token与csrf一致
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()
        #{"code":1300014,"message":"b币余额不足","ttl":1,"data":null}
        #{"code":0,"message":"0","ttl":1,"data":{"status":2,"order_id":"2011042258413961167422787","gold":0,"bp":0}}

    async def xliveSign(self) -> Awaitable[Dict[str, Any]]:
        '''B站直播签到'''
        url = "https://api.live.bilibili.com/xlive/web-ucenter/v1/sign/DoSign"
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def xliveGetRecommendList(self) -> Awaitable[Dict[str, Any]]:
        '''B站直播获取首页前10条直播'''
        url = f'https://api.live.bilibili.com/relation/v1/AppWeb/getRecommendList'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def xliveGetRoomInfo(self,
                               room_id: int
                               ) -> Awaitable[Dict[str, Any]]:
        '''
        B站直播获取房间信息
        room_id int 房间id
        '''
        url = f'https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom?room_id={room_id}'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def xliveGiftBagList(self) -> Awaitable[Dict[str, Any]]:
        '''B站直播获取背包礼物'''
        url = 'https://api.live.bilibili.com/xlive/web-room/v1/gift/bag_list'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def xliveBagSend(self,
                           biz_id,
                           ruid,
                           bag_id, 
                           gift_id, 
                           gift_num, 
                           storm_beat_id=0, 
                           price=0, 
                           platform="pc"
                           ) -> Awaitable[Dict[str, Any]]:
        '''
        B站直播送出背包礼物
        biz_id int 房间号
        ruid int up主的uid
        bag_id int 背包id
        gift_id int 背包里的礼物id
        gift_num int 送礼物的数量
        storm_beat_id int
        price int 礼物价格
        platform str 平台
        '''
        url = 'https://api.live.bilibili.com/gift/v2/live/bag_send'
        post_data = {
            "uid": self._uid,
            "gift_id": gift_id,
            "ruid": ruid,
            "send_ruid": 0,
            "gift_num": gift_num,
            "bag_id": bag_id,
            "platform": platform,
            "biz_code": "live",
            "biz_id": biz_id,
            #"rnd": rnd, #直播开始时间
            "storm_beat_id": storm_beat_id,
            "price": price,
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()

    async def xliveGiftSend(self,
                           biz_id: int,
                           ruid: int,
                           gift_id: int, 
                           gift_num: int,
                           price: int = 0, 
                           storm_beat_id: int = 0,
                           platform: str = "pc"
                           ) -> Awaitable[Dict[str, Any]]:
        '''
        B站直播送出礼物
        biz_id         int 房间号
        ruid           int up主的uid
        gift_id        int 礼物id, 银瓜子为1(银瓜子100),吃瓜为20004(金瓜子100),冰阔落为20008(金瓜子1000)
        gift_num       int 送礼物的数量
        storm_beat_id  int
        price          int 礼物价格，目前都是0
        platform       str 平台
        '''
        url = 'https://api.live.bilibili.com/gift/v2/Live/send'
        post_data = {
            "uid": self._uid,
            "gift_id": gift_id,
            "ruid": ruid,
            "send_ruid": 0,
            "gift_num": gift_num,
            "coin_type": 'silver' if gift_id == 1 else 'gold',
            "bag_id": 0,
            "platform": platform,
            "biz_code": "live",
            "biz_id": biz_id,
            #"rnd": rnd, #直播开始时间
            "storm_beat_id": storm_beat_id,
            "price": price,
            "csrf": self._bili_jct,
            "csrf_token": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()
        #{"code":0,"msg":"success","message":"success","data":{"tid":"1609908157110100001","uid":615201,"uname":"Soulycoris","face":"https://i2.hdslb.com/bfs/face/6d57b8a7c852c9faa9f014a59876088e7eb6cf63.jpg","guard_level":0,"ruid":8466742,"rcost":431,"gift_id":1,"gift_type":5,"gift_name":"辣条","gift_num":1,"gift_action":"投喂","gift_price":100,"coin_type":"silver","total_coin":100,"pay_coin":100,"metadata":"","fulltext":"","rnd":"1609908000","tag_image":"","effect_block":1,"extra":{"wallet":{"gold":2900,"silver":514,"discount_id":0,"wallet_tid":"261638120","order_id":"","goods_id":0},"gift_bag":{"bag_id":0,"gift_num":0},"top_list":[],"follow":null,"medal":null,"title":null,"pk":{"pk_gift_tips":"","crit_prob":-1},"fulltext":"","event":{"event_score":0,"event_redbag_num":0},"capsule":null,"lottery_id":""},"blow_switch":0,"send_tips":"赠送成功","discount_id":0,"gift_effect":{"super":0,"combo_timeout":0,"super_gift_num":0,"super_batch_gift_num":0,"batch_combo_id":"","broadcast_msg_list":[],"small_tv_list":[],"beat_storm":null,"combo_id":"","smallTVCountFlag":true},"send_master":null,"crit_prob":-1,"combo_stay_time":3,"combo_total_coin":0,"demarcation":1,"magnification":1,"combo_resources_id":1,"is_special_batch":0,"send_gift_countdown":6,"bp_cent_balance":0,"price":0,"left_num":0,"need_num":0,"available_num":0}}

    async def xliveGetUserInfo(self) -> Awaitable[Dict[str, Any]]:
        '''B站直播获取用户信息'''
        url = 'https://api.live.bilibili.com/xlive/web-ucenter/user/get_user_info'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()
        #{"code":0,"message":"0","ttl":1,"data":{"uid":xxx,"uname":"xxx","face":"https://i0.hdslb.com/bfs/face/2e79160cf78dd083c9aef01798e6335920930b66.jpg","billCoin":0.1,"silver":632,"gold":566,"achieve":70,"vip":0,"svip":0,"user_level":8,"user_next_level":9,"user_intimacy":29800,"user_next_intimacy":100000,"is_level_top":0,"user_level_rank":"\u003e50000","user_charged":0,"identification":1}}
    
    async def coin(self, 
                   aid: int, 
                   num: int = 1, 
                   select_like: int = 1
                   ) -> Awaitable[Dict[str, Any]]:
        '''
        给指定av号视频投币
        aid int 视频av号
        num int 投币数量
        select_like int 是否点赞
        '''
        url = "https://api.bilibili.com/x/web-interface/coin/add"
        post_data = {
            "aid": aid,
            "multiply": num,
            "select_like": select_like,
            "cross_domain": "true",
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()

    async def coinCv(self,
                    cvid: int, 
                    num: int = 1, 
                    upid: int = 0, 
                    select_like: int = 1
                    ) -> Awaitable[Dict[str, Any]]:
        '''
        给指定cv号专栏投币
        cvid int 专栏id
        num int 投币数量
        upid int 专栏up主uid
        select_like int 是否点赞
        '''
        url = "https://api.bilibili.com/x/web-interface/coin/add"
        if upid == 0: #up主id不能为空，需要先请求一下专栏的up主
            info = await self.articleViewInfo(cvid)
            upid = info["data"]["mid"]
        post_data = {
            "aid": cvid,
            "multiply": num,
            "select_like": select_like,
            "upid": upid,
            "avtype": 2,#专栏必为2，否则投到视频上面去了
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()

    async def articleViewInfo(self, 
                              cvid: int
                              ) -> Awaitable[Dict[str, Any]]:
        '''
        获取专栏信息
        cvid int 专栏id
        '''
        url = f'https://api.bilibili.com/x/article/viewinfo?id={cvid}'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def xliveWebHeartBeat(self, 
                     hb: str = None, 
                     pf: str = None
                     ) -> Awaitable[Dict[str, Any]]:
        '''
        B站直播间心跳
        hb str 请求信息(base64编码) "{周期}|{uid}|1|0"
        pf str 平台 "web"
        '''
        params = {}
        if hb:
            params["hb"] = hb
        if pf:
            params["pf"] = pf
        url = 'https://live-trace.bilibili.com/xlive/rdata-interface/v1/heartbeat/webHeartBeat'
        async with self._session.get(url, params=params, verify_ssl=False) as r:
            return await r.json()

    async def xliveGetBuvid(self) -> str:
        '''获得B站直播buvid参数'''
        #先查找cookie
        for x in self._session.cookie_jar:
            if x.key == 'LIVE_BUVID':
                return x.value
        #cookie中找不到，则请求一次直播页面
        url = 'https://live.bilibili.com/3'
        async with self._session.head(url, verify_ssl=False) as r:
            cookies = r.cookies['LIVE_BUVID']
        return str(cookies)[23:43]

    async def xliveHeartBeatX(self, 
                              parent_area_id: int,
                              area_id: int,
                              room_id: int,
                              num: int,
                              uuid: str,
                              ets: int,
                              benchmark: str,
                              interval: int,
                              secret_rule: list
                     ) -> Awaitable[Dict[str, Any]]:
        '''
        B站直播间内部心跳（第n>1次心跳）
        parent_area_id   int  大分区id  2网游 3手游 6单机 1娱乐 5电台 9虚拟主播 10生活 11学习
        area_id          int  小分区id  0为全部小分区，不同大分区有不同的小分区
        room_id          int  直播间id
        num              int  心跳轮次
        uuid             str  uuid标识符
        ets              int  上次心跳时间戳timestamp
        benchmark        str  上次心跳参数     data -> secret_key
        interval         int  上次心跳时间间隔 data -> heartbeat_interval
        secret_rule      list 上次心跳加密规则 data -> secret_rule
        '''
        buvid = await self.xliveGetBuvid()
        post_data = {
            "id": f'[{parent_area_id},{area_id},{num},{room_id}]',
            "device": f'["{buvid}","{uuid}"]',
            "ts": int(time.time() * 1000),
            "ets": ets,
            "benchmark": benchmark,
            "time": interval,
            "ua": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/63.0.3239.108',
            "csrf_token": self._bili_jct,
            "csrf": self._bili_jct,
            }
        enc_server = 'https://1578907340179965.cn-shanghai.fc.aliyuncs.com/2016-08-15/proxy/bili_server/heartbeat/'
        async with self._session.post(enc_server, json={"t":post_data,"r":secret_rule}, verify_ssl=False) as r:
            post_data["s"] = await r.text()

        url = 'https://live-trace.bilibili.com/xlive/data-interface/v1/x25Kn/X'
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()

    async def xliveHeartBeatE(self, 
                              parent_area_id: int,
                              area_id: int,
                              room_id: int,
                              num: int,
                              uuid: str,
                              ) -> Awaitable[Dict[str, Any]]:
        '''
        B站进入直播间心跳（第1次心跳）
        parent_area_id   int  大分区id  2网游 3手游 6单机 1娱乐 5电台 9虚拟主播 10生活 11学习
        area_id          int  小分区id  0为全部小分区，不同大分区有不同的小分区
        room_id          int  直播间id
        num              int  心跳轮次
        uuid             str  uuid标识符
        '''
        buvid = await self.xliveGetBuvid()
        post_data = {
            "id": f'[{parent_area_id},{area_id},{num},{room_id}]',
            "device": f'["{buvid}","{uuid}"]',
            "ts": int(time.time() * 1000),
            "is_patch": 0, 
            "heart_beat": [], #短时间多次进入直播间，is_patch为1，heart_beat传入xliveHeartBeatX所需要的所有数据
            "ua": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/63.0.3239.108',
            "csrf_token": self._bili_jct,
            "csrf": self._bili_jct
            }
        url = 'https://live-trace.bilibili.com/xlive/data-interface/v1/x25Kn/E'
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def get_home_medals(self) -> Awaitable[Dict[str, Any]]:
        '''获得佩戴的勋章'''
        url = "https://api.live.bilibili.com/fans_medal/v1/fans_medal/get_home_medals"
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def report(self, 
                     aid: int, 
                     cid: int, 
                     progres: int
                     ) -> Awaitable[Dict[str, Any]]:
        '''
        B站上报视频观看进度
        aid int 视频av号
        cid int 视频cid号
        progres int 观看秒数
        '''
        url = "http://api.bilibili.com/x/v2/history/report"
        post_data = {
            "aid": aid,
            "cid": cid,
            "progres": progres,
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()

    async def share(self, 
                    aid
                    ) -> Awaitable[Dict[str, Any]]:
        '''
        分享指定av号视频
        aid int 视频av号
        '''
        url = "https://api.bilibili.com/x/web-interface/share/add"
        post_data = {
            "aid": aid,
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()

    async def xliveGetStatus(self) -> Awaitable[Dict[str, Any]]:
        '''B站直播获取金银瓜子状态'''
        url = "https://api.live.bilibili.com/pay/v1/Exchange/getStatus"
        async with self._session.get(url, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def silver2coin(self) -> Awaitable[Dict[str, Any]]:
        '''银瓜子兑换硬币'''
        url = "https://api.live.bilibili.com/pay/v1/Exchange/silver2coin"
        post_data = {
            "csrf_token": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()

    async def getRegions(self, 
                         rid=1, 
                         num=6
                         ) -> Awaitable[Dict[str, Any]]:
        '''
        获取B站分区视频信息
        rid int 分区号
        num int 获取视频数量
        '''
        url = "https://api.bilibili.com/x/web-interface/dynamic/region?ps=" + str(num) + "&rid=" + str(rid)
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def mangaClockIn(self, 
                     platform="android"
                     ) -> Awaitable[Dict[str, Any]]:
        '''
        模拟B站漫画客户端签到
        platform str 平台
        '''
        url = "https://manga.bilibili.com/twirp/activity.v1.Activity/ClockIn"
        post_data = {
            "platform": platform
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def mangaGetPoint(self) -> Awaitable[Dict[str, Any]]:
        '''获取漫画积分'''
        url = f'https://manga.bilibili.com/twirp/pointshop.v1.Pointshop/GetUserPoint'
        async with self._session.post(url, json={}, verify_ssl=False) as r:
            return await r.json()

    async def mangaShopExchange(self, 
                                product_id: int, 
                                point: int, 
                                product_num=1) -> Awaitable[Dict[str, Any]]:
        '''
        漫画积分商城兑换
        product_id int 商品id
        point int 商品需要积分数量
        product_num int 兑换商品数
        '''
        url = f'https://manga.bilibili.com/twirp/pointshop.v1.Pointshop/Exchange'
        post_data = {
            "product_id": product_id,
            "point": point,
            "product_num": product_num
            }
        async with self._session.post(url, json=post_data, verify_ssl=False) as r:
            return await r.json()

    async def mangaGetVipReward(self) -> Awaitable[Dict[str, Any]]:
        '''获取漫画大会员福利'''
        url = 'https://manga.bilibili.com/twirp/user.v1.User/GetVipReward'
        async with self._session.post(url, json={"reason_id":1}, verify_ssl=False) as r:
            return await r.json()

    async def mangaComrade(self, 
                           platform="web"
                           ) -> Awaitable[Dict[str, Any]]:
        '''
        站友日漫画卷兑换查询
        platform str 平台
        '''
        url = f'https://manga.bilibili.com/twirp/activity.v1.Activity/Comrade?platform={platform}'
        async with self._session.post(url, json={}, verify_ssl=False) as r:
            return await r.json()

    async def mangaPayBCoin(self, 
                            pay_amount: int, 
                            product_id: int = 1, 
                            platform: str = 'web'
                            ) -> Awaitable[Dict[str, Any]]:
        '''
        B币购买漫画
        pay_amount int 购买数量
        product_id int 购买商品id
        platform str 平台
        '''
        url = f'https://manga.bilibili.com/twirp/pay.v1.Pay/PayBCoin?platform={platform}'
        post_data = {
            "pay_amount": str(pay_amount),
            "product_id": product_id
            }
        async with self._session.post(url, json=post_data, verify_ssl=False) as r:
            return await r.json()

    async def mangaGetCoupons(self, 
                              not_expired=True, 
                              page_num=1, 
                              page_size=50, 
                              tab_type=1,
                              platform="web"
                              ) -> Awaitable[Dict[str, Any]]:
        '''
        获取账户中的漫读劵信息
        not_expired bool
        page_num int 页数
        page_size int 每页大小
        tab_type int
        platform str 平台
        '''
        url = f'https://manga.bilibili.com/twirp/user.v1.User/GetCoupons?platform={platform}'
        post_data = {
            "not_expired": not_expired,
            "page_num": page_num,
            "page_size": page_size,
            "tab_type": tab_type
            }
        async with self._session.post(url, json=post_data, verify_ssl=False) as r:
            return await r.json()

    async def mangaListFavorite(self, 
                                page_num=1, 
                                page_size=50, 
                                order=1, 
                                wait_free=0, 
                                platform='web'
                                ) -> Awaitable[Dict[str, Any]]:
        '''
        B站漫画追漫列表
        page_num int 页数
        page_size int 每页大小
        order int 排序方式
        wait_free int 显示等免漫画
        platform str 平台
        '''
        url = 'https://manga.bilibili.com/twirp/bookshelf.v1.Bookshelf/ListFavorite?platform={platform}'
        post_data = {
            "page_num": page_num,
            "page_size": page_size,
            "order": order,
            "wait_free": wait_free
            }
        async with self._session.post(url, json=post_data, verify_ssl=False) as r:
            return await r.json()

    async def mangaDetail(self, 
                          comic_id: int, 
                          device='pc', 
                          platform='web'
                          ) -> Awaitable[Dict[str, Any]]:
        '''
        获取漫画信息
        comic_id int 漫画id
        device str 设备
        platform str 平台
        '''
        url = f'https://manga.bilibili.com/twirp/comic.v1.Comic/ComicDetail?device={device}&platform={platform}'
        post_data = {
            "comic_id": comic_id
            }
        async with self._session.post(url, json=post_data, verify_ssl=False) as r:
            return await r.json()

    async def mangaGetEpisodeBuyInfo(self, 
                               ep_id: int, 
                               platform="web"
                               ) -> Awaitable[Dict[str, Any]]:
        '''
        获取漫画购买信息
        ep_id int 漫画章节id
        platform str 平台
        '''
        url = f'https://manga.bilibili.com/twirp/comic.v1.Comic/GetEpisodeBuyInfo?platform={platform}'
        post_data = {
            "ep_id": ep_id
            }
        async with self._session.post(url, json=post_data, verify_ssl=False) as r:
            return await r.json()

    async def mangaBuyEpisode(self, 
                        ep_id: int, 
                        buy_method=1, 
                        coupon_id=0, 
                        auto_pay_gold_status=0, 
                        platform="web"
                        ) -> Awaitable[Dict[str, Any]]:
        '''
        购买漫画
        ep_id int 漫画章节id
        buy_method int 购买参数
        coupon_id int 漫读劵id
        auto_pay_gold_status int 自动购买
        platform str 平台
        '''
        url = f'https://manga.bilibili.com/twirp/comic.v1.Comic/BuyEpisode?&platform={platform}'
        post_data = {
            "buy_method": buy_method,
            "ep_id": ep_id
            }
        if coupon_id:
            post_data["coupon_id"] = coupon_id
        if auto_pay_gold_status:
            post_data["auto_pay_gold_status"] = auto_pay_gold_status
        async with self._session.post(url, json=post_data, verify_ssl=False) as r:
            return await r.json()

    async def mangaAddFavorite(self, 
                               comic_id: int
                               ) -> Awaitable[Dict[str, Any]]:
        '''
        将漫画添加进追漫列表
        comic_id int 漫画id
        '''
        url = 'https://manga.bilibili.com/twirp/bookshelf.v1.Bookshelf/AddFavorite'
        post_data = {
            "comic_id": comic_id
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()
        #{'code': 0, 'msg': '', 'data': {'first_fav_status': {'25902': True}}}

    async def mangaAddHistory(self, 
                              comic_id: int,
                              ep_id: int
                              ) -> Awaitable[Dict[str, Any]]:
        '''
        添加漫画观看历史
        comic_id int 漫画id
        ep_id    int 章节id
        '''
        url = 'https://manga.bilibili.com/twirp/bookshelf.v1.Bookshelf/AddHistory'
        post_data = {
            "comic_id": comic_id,
            "ep_id": ep_id
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()
        #{"code":0,"msg":"","data":{}}

    async def mangaGetCoupons(self) -> Awaitable[Dict[str, Any]]:
        '''获取漫画劵明细'''
        url = 'https://manga.bilibili.com/twirp/user.v1.User/GetCoupons'
        post_data = {
            "not_expired": True,
            "page_num": 1,
            "page_size": 30,
            "tab_type": 1
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()
        #{'code': 0, 'msg': '', 'data': {'total_remain_amount': 0, 'user_coupons': [], 'coupon_info': {'new_coupon_num': 0, 'coupon_will_expire': 0, 'rent_will_expire': 0, 'new_rent_num': 0, 'discount_will_expire': 0, 'new_discount_num': 0, 'month_ticket_will_expire': 0, 'new_month_ticket_num': 0, 'silver_will_expire': 0, 'new_silver_num': 0, 'remain_item': 0, 'remain_discount': 1, 'remain_coupon': 0, 'remain_silver': 31}}}

    async def mangaGetStates(self) -> Awaitable[Dict[str, Any]]:
        '''获取漫画劵状态'''
        url = 'https://manga.bilibili.com/twirp/user.v1.User/GetStates'
        async with self._session.post(url, verify_ssl=False) as r:
            return await r.json()

    async def activityAddTimes(self, 
                               sid: str, 
                               action_type: int
                               ) -> Awaitable[Dict[str, Any]]:
        '''
        增加B站活动的参与次数
        sid str 活动的id
        action_type int 操作类型
        '''
        url = 'https://api.bilibili.com/x/activity/lottery/addtimes'
        post_data = {
            "sid": sid,
            "action_type": action_type,
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()

    async def activityDo(self, 
                         sid: str, 
                         type: int
                         ) -> Awaitable[Dict[str, Any]]:
        '''
        参与B站活动
        sid str 活动的id
        type int 操作类型
        '''
        url = 'https://api.bilibili.com/x/activity/lottery/do'
        post_data = {
            "sid": sid,
            "type": type,
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()

    async def activityMyTimes(self, 
                              sid: str
                              ) -> Awaitable[Dict[str, Any]]:
        '''
        获取B站活动次数
        sid str 活动的id
        '''
        url = f'https://api.bilibili.com/x/activity/lottery/mytimes?sid={sid}'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def getDynamic(self, 
                         offset_dynamic_id: int = 0,
                         type_list=268435455
                         ) -> Awaitable[Dict[str, Any]]:
        '''取B站用户动态数据'''
        if offset_dynamic_id:
            url = f'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/dynamic_history?uid={self._uid}&offset_dynamic_id={offset_dynamic_id}&type={type_list}'
        else:
            url = f'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/dynamic_new?uid={self._uid}&type_list={type_list}'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def getDynamicDetail(self, 
                         dynamic_id: int
                         ) -> Awaitable[Dict[str, Any]]:
        '''
        获取动态内容
        dynamic_id int 动态id
        '''
        url = f'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail?dynamic_id={dynamic_id}'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def dynamicReplyAdd(self, 
                              oid: int, 
                              message="", 
                              type=11, 
                              plat=1
                              ) -> Awaitable[Dict[str, Any]]:
        '''
        评论动态
        oid int 动态id
        message str 评论信息
        type int 评论类型，动态时原创则填11，非原创填17
        plat int 平台
        '''
        url = "https://api.bilibili.com/x/v2/reply/add"
        post_data = {
            "oid": oid,
            "plat": plat,
            "type": type,
            "message": message,
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()

    async def dynamicLike(self, 
                          dynamic_id: int, 
                          like: int = 1
                          ) -> Awaitable[Dict[str, Any]]:
        '''
        点赞动态
        dynamic_id int 动态id
        like int 1为点赞,2为取消点赞
        '''
        url = "https://api.vc.bilibili.com/dynamic_like/v1/dynamic_like/thumb"
        post_data = {
            "uid": self._uid,
            "dynamic_id": dynamic_id,
            "up": like,
            "csrf_token": self._bili_jct,
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()

    async def dynamicRepost(self, 
                            dynamic_id: int, 
                            content="", 
                            extension='{"emoji_type":1}'
                            ) -> Awaitable[Dict[str, Any]]:
        '''
        转发动态
        dynamic_id int 动态id
        content str 转发评论内容
        extension str_json
        '''
        url = "https://api.vc.bilibili.com/dynamic_repost/v1/dynamic_repost/repost"
        post_data = {
            "uid": self._uid,
            "dynamic_id": dynamic_id,
            "content": content,
            "at_uids": '',
            "ctrl": '[]',
            "extension": extension,
            "csrf": self._bili_jct,
            "csrf_token": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()
        #{"code":0,"msg":"","message":"","data":{"result":0,"errmsg":"符合条件，允许发布","_gt_":0}}

    async def dynamicRepostReply(self, 
                                 rid: int, 
                                 content="", 
                                 type=1, 
                                 repost_code=3000, 
                                 From="create.comment", 
                                 extension='{"emoji_type":1}'
                                 ) -> Awaitable[Dict[str, Any]]:
        '''
        转发动态
        rid int 动态id
        content str 转发评论内容
        type int 类型
        repost_code int 转发代码
        From str 转发来自
        extension str_json
        '''
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
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()

    async def dynamicCreate(self, 
                            content: str, 
                            ctrl: Iterable[Mapping[str, str]] = ()
                            ) -> Awaitable[Dict[str, Any]]:
        '''
        创建动态(纯文本动态,图片动态请用dynamicCreateDraw方法)
        content str                         动态内容(内容中有@请看ctrl参数，否则忽略ctrl参数)
        ctrl    Iterable[Mapping[str, str]] 控制字段，比如动态内容为"你好@呵呵 再见"，
                                            控制字段为[{"location":2,"type":1,"length":4,"data":"84667"}],
                                            其中2为@出现的位置("你"为0,"好"为1,"@"为2,必须精确)，
                                            类型,为1就行，
                                            4为@的用户名称长度加2(@字符本身与后面必须跟上的空格各占一个长度,"@呵呵 "占4个字符,注意末尾空格)，
                                            84667为@的用户uid(字符串形式而不是整数)，
                                            如果没有控制字段则content中@是无效的，会被当做纯文本而不能点击
                                            尚不清楚利用此参数是否能"指桑骂槐"
        '''
        url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/create'
        post_data = {
            "dynamic_id": 0,
            "rid": 0, #没发现其他取值，非转发的动态一般取0，转发的就不同了
            "type": 4, #动态类型，纯文本动态为4，非纯文本动态的其他类型动态并不能使用本方法进行创建，包括图片动态，定时动态等有其他接口
            "content": content,
            "extension": '{"emoji_type":1,"from":{"emoji_type":1},"flag_cfg":{}}',
            "at_uids": ",".join([u["data"] for u in ctrl if "type" in u and u["type"] == 1]), # @的用户的uid，多个用逗号(,)隔开
            "ctrl": json.dumps(ctrl),
            "up_choose_comment": 0,
            "up_close_comment": 0,
            "csrf": self._bili_jct,
            "csrf_token": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()
        #{"code":500103,"msg":"你忘记写内容啦","message":"你忘记写内容啦","data":{}}
        #{"code":0,"msg":"","message":"","data":{"result":0,"errmsg":"; Create dynamic:475557908802625377, res:0, result:1; Push create kafka:0; Push create databus:0; Register comment result:0; Add outbox result:1; Send at_msg result:0","dynamic_id":475557908802625377,"create_result":1,"dynamic_id_str":"475557908802625377","_gt_":0}}

    async def getSpaceDynamic(self, 
                              uid: int = 0,
                              offset_dynamic_id: int = ''
                              ) -> 'dict':
        '''
        取B站空间的动态列表
        uid int B站用户uid
        '''
        if uid == 0:
            uid = self._uid
        url = f'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={uid}&need_top=0&offset_dynamic_id={offset_dynamic_id}'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def removeDynamic(self, 
                            dynamic_id: int
                            ) -> Awaitable[Dict[str, Any]]:
        '''
        删除自己的动态
        dynamic_id int 动态id
        '''
        url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/rm_dynamic'
        post_data = {
            "dynamic_id": dynamic_id,
            "csrf_token": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()

    async def getLotteryNotice(self, 
                               dynamic_id: int
                               ) -> Awaitable[Dict[str, Any]]:
        '''
        取指定抽奖信息
        dynamic_id int 抽奖动态id
        '''
        url = f'https://api.vc.bilibili.com/lottery_svr/v1/lottery_svr/lottery_notice?dynamic_id={dynamic_id}'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def getLotteryInfoWeb(self, 
                                room_id: int
                                ) -> Awaitable[Dict[str, Any]]:
        '''
        取直播间抽奖信息
        room_id int 直播间id
        '''
        url = f'https://api.live.bilibili.com/xlive/lottery-interface/v1/lottery/getLotteryInfoWeb?roomid={room_id}'
        async with self._session.get(url, headers={"Referer":f'https://live.bilibili.com/{room_id}'}, verify_ssl=False) as r:
            return await r.json()

    async def StormCheck(self,
                   room_id: int
                   ) -> Awaitable[Dict[str, Any]]:
        url = f'https://api.live.bilibili.com/lottery/v1/Storm/check?roomid={room_id}'
        async with self._session.get(url, headers={"Referer":f'https://live.bilibili.com/{room_id}'}, verify_ssl=False) as r:
            return await r.json()

    async def juryInfo(self) -> Awaitable[Dict[str, Any]]:
        '''
        取当前账户风纪委员状态
        '''
        url = 'https://api.bilibili.com/x/credit/jury/jury'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def juryCaseObtain(self) -> Awaitable[Dict[str, Any]]:
        '''
        拉取一个案件用于风纪委员投票
        '''
        url = 'https://api.bilibili.com/x/credit/jury/caseObtain'
        post_data = {
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()

    async def juryCaseOpinion(self,
                              cid: int,
                              pn: int = 1,
                              ps: int = 10
                              ) -> Awaitable[Dict[str, Any]]:
        '''
        拉取一个案件用于风纪委员投票
        '''
        url = f'https://api.bilibili.com/x/credit/jury/case/opinion?cid={cid}&pn={pn}&ps={ps}'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def juryCaseInfo(self,
                           cid: int
                           ) -> Awaitable[Dict[str, Any]]:
        '''
        获取风纪委员案件详细信息
        '''
        url = f'https://api.bilibili.com/x/credit/jury/caseInfo?cid={cid}'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def juryCase(self,
                       cid: int
                       ) -> Awaitable[Dict[str, Any]]:
        '''
        获取风纪委员案件结果
        '''
        url = f'https://api.bilibili.com/x/credit/jury/juryCase?cid={cid}'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def juryVote(self,
                       cid: int,
                       **kwargs #非必选参数太多以可变参数列表传入
                       ) -> Awaitable[Dict[str, Any]]:
        '''
        风纪委员投票
        cid int 案件ID
        以下为可选参数，如果需要必须用参数名称的方式调用本函数
        vote int 投票类型 0 未投票；1 封禁；2 否；3 弃权；4 删除
        content str 理由
        likes list[int] 整数数组，支持的观点
        hates list[int] 整数数组，反对的观点
        attr int 是否匿名 0 匿名；1 不匿名
        apply_type int 是否更改原因 0 保持原来原因；1 投票给新原因
        origin_reason int 原始原因
        apply_reason int 新原因
            1 刷屏
            2 抢楼
            3 发布色情低俗信息
            4 发布赌博诈骗信息
            5 发布违禁相关信息
            6 发布垃圾广告信息
            7 发布人身攻击言论
            8 发布侵犯他人隐私信息
            9 发布引战言论
            10 发布剧透信息
            11 恶意添加无关标签
            12 恶意删除他人标签
            13 发布色情信息
            14 发布低俗信息
            15 发布暴力血腥信息
            16 涉及恶意投稿行为
            17 发布非法网站信息
            18 发布传播不实信息
            19 发布怂恿教唆信息
            20 恶意刷屏
            21 账号违规
            22 恶意抄袭
            23 冒充自制原创
            24 发布青少年不良内容
            25 破坏网络安全
            26 发布虚假误导信息
            27 仿冒官方认证账号
            28 发布不适宜内容
            29 违反运营规则
            30 恶意创建话题
            31 发布违规抽奖
            32 恶意冒充他人
        '''
        url = 'https://api.bilibili.com/x/credit/jury/vote'
        post_data = {
            "cid": cid,
            "csrf": self._bili_jct,
            **kwargs #所有可选参数
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()

    async def accInfo(self,
                      uid: int
                      ) -> None:
        '''
        获取指定用户的空间个人信息
        uid int 用户uid
        '''
        url = f'https://api.bilibili.com/x/space/acc/info?mid={uid}'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()

    async def getMsgNotify(self) -> Awaitable[Dict[str, Any]]:
        '''获取主站消息提示(恢复，@，赞，系统提示等)'''
        url = f'https://api.vc.bilibili.com/link_setting/v1/link_setting/get?msg_notify=1&show_unfollowed_msg=1&build=0&mobi_app=web'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()
        #{"code":0,"msg":"ok","message":"ok","data":{"show_unfollowed_msg":0,"msg_notify":1,"set_like":0,"set_comment":0,"set_at":0,"is_group_fold":1,"should_receive_group":1,"receive_unfollow_msg":1,"followed_reply":0,"keys_reply":0,"recv_reply":0,"voyage_reply":0,"_gt_":0}}

    async def msgFeedUnread(self) -> Awaitable[Dict[str, Any]]:
        '''获取主站未读消息(恢复，@，赞，系统提示等)数量'''
        url = f'https://api.bilibili.com/x/msgfeed/unread?build=0&mobi_app=web'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()
        #{"code":0,"message":"0","ttl":1,"data":{"at":1,"chat":0,"like":0,"reply":0,"sys_msg":0,"up":0}}

    async def msgFeedAt(self) -> Awaitable[Dict[str, Any]]:
        '''获取主站未读的@消息具体内容'''
        url = f'https://api.bilibili.com/x/msgfeed/at?build=0&mobi_app=web'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()
        #{"code":0,"message":"0","ttl":1,"data":{"at":1,"chat":0,"like":0,"reply":0,"sys_msg":0,"up":0}}

    async def getSessions(self,
                          session_type: int = 1,
                          sort_rule: int = 2,
                          size: int = None,
                          mobi_app: str = 'web'
                          ) -> Awaitable[Dict[str, Any]]:
        '''
        获取主站消息中心的消息
        session_type   int 对话类型，目前已知1是私信消息，3是应援团消息，其他取值未知
        sort_rule      int 排序方式，2为时间倒序，其他取值未知
        size           int 返回消息数量，可以忽略本参数
        mobi_app       str 客户端类型
        '''
        url = f'https://api.vc.bilibili.com/session_svr/v1/session_svr/get_sessions?session_type={session_type}&group_fold=1&unfollow_fold=0&sort_rule={sort_rule}&build=0&mobi_app={mobi_app}'
        if size:
            url = f'{url}&size={size}'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()
        #{"code":0,"msg":"ok","message":"ok","data":{"session_list":[{"talker_id":203984353,"session_type":1,"top_ts":0,"is_follow":1,"is_dnd":0,"ack_seqno":14,"ack_ts":1609766791060393,"session_ts":1609767856196942,"unread_count":1,"last_msg":{"sender_uid":203984353,"receiver_type":1,"receiver_id":8466742,"msg_type":1,"content":"{\"content\":\"666\"}","msg_seqno":15,"timestamp":1609767856,"at_uids":[0],"msg_key":6913900296672394953,"msg_status":0,"notify_code":""},"can_fold":0,"status":0,"max_seqno":15,"new_push_msg":0,"setting":0}],"has_more":1,"_gt_":0}}

    async def sessionUpdateAck(self,
                               talker_id: int,
                               ack_seqno: int,
                               session_type: int = 1,
                               mobi_app: str = 'web'
                               ) -> Awaitable[Dict[str, Any]]:
        '''
        确认主站消息中心的消息(即设置未读消息为已读)
        talker_id      int 对话对方的uid
        ack_seqno      int 确认的消息号，一个消息号对应一条消息的序号，随着消息条数递增
        session_type   int 对话类型，目前已知1是私信消息，3是应援团消息，其他取值未知
        mobi_app       str 客户端类型
        '''
        url = 'https://api.vc.bilibili.com/session_svr/v1/session_svr/update_ack'
        post_data = {
            "talker_id": talker_id,
            "session_type": session_type,
            "ack_seqno": ack_seqno,
            "build": 0,
            "mobi_app": mobi_app,
            "csrf_token": self._bili_jct,
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()
        #{"code":0,"msg":"ok","message":"ok","data":[]}

    async def sendMsg(self,
                      receiver_id: int,
                      content: Optional[str] = None,
                      image_url: Optional[str] = None,
                      mobi_app: str = 'web'
                      ) -> Awaitable[Dict[str, Any]]:
        '''
        主站消息中心的发送消息
        receiver_id    int 对话对方的uid
        content        str 消息的文本内容，当发送文本消息时填写，与image_url参数强制二选一
        image_url      str 消息的图片链接，当发送图片时填写，与content参数强制二选一
        mobi_app       str 客户端类型
        '''
        if not (content or image_url):
            raise ValueError('content参数与image_url参数必填一个')
        url = 'https://api.vc.bilibili.com/web_im/v1/web_im/send_msg'
        post_data = {
            "msg[sender_uid]": self._uid,
            "msg[receiver_id]": receiver_id,
            "msg[receiver_type]": 1,
            "msg[msg_type]": 1 if content else 2,
            "msg[msg_status]": 0,
            "msg[content]": f'{{"content":"{content}"}}' if content else f'{{"url":"{image_url}"}}',
            #{"url":"http://i0.hdslb.com/bfs/album/82fa5c3b97dc733160b0b7d6198eb037329bb01b.jpg","height":1120,"width":720,"imageType":"jpeg","original":1,"size":170}
            "msg[new_face_version]": 0,
            "msg[timestamp]": int(time.time()),
            "msg[dev_id]": "D75CA37F-E130-457E-A6FD-D2DA00EA5C92",
            "from_firework": 0,
            "build": 0,
            "mobi_app": mobi_app,
            "csrf_token": self._bili_jct,
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            return await r.json()
        #{"code":1600001,"message":"您的账号可能存在风险，暂时无法发送消息，请确保账号资料属实并绑定真实手机号码","ttl":1,"data":{}}

    async def getRoomIdByUid(self,
                             uid: int
                             ) -> Awaitable[Dict[str, Any]]:
        '''通过uid获得直播间id
        uid  int  用户uid
        '''
        url = f'https://api.live.bilibili.com/room/v2/Room/room_id_by_uid?uid={uid}'
        async with self._session.get(url, verify_ssl=False) as r:
            return await r.json()
        #{"code":0,"msg":"ok","message":"ok","data":{"room_id":22725017}}

    async def wsConnect(self, url: str):
        '''
        创建一个websocket
        url  str  url链接
        '''
        return await self._session.ws_connect(url, verify_ssl=False)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc) -> None:
        await self.close()

    async def close(self) -> None:
        await self._session.close()


