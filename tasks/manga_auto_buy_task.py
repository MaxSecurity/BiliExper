from BiliClient import asyncbili
from .push_message_task import webhook
import logging

async def manga_auto_buy_task(biliapi: asyncbili, 
                              task_config: dict #任务配置
                              ) -> None: 

    def _filter2list(mfilter: str) -> list:
        '''根据filter获得数组'''
        result = []
        S1 = mfilter.split(';')
        for x in S1:
            if x != '':
                S2 = x.split('|')
                result.append((S2[0],S2[1]))
        return result

    async def _get_filter_by_favorite() -> str:
        '''通过漫画关注列表获取filter字符串'''
        _list = (await biliapi.mangaListFavorite())["data"]
        result = ''
        for x in _list:
            result = f'{result};{x["comic_id"]}|1-'
        return result

    def get_need_buy_eplist(mfilter: str, all_ep_list: list):
        '''通过所有eplist和过滤条件获得需要购买的漫画ep_id列表'''
        L1 = mfilter.split(',')
        length = len(all_ep_list)
        if length == 0:
            return  []
        nums = []
        for x in L1:
            if '-' in x:
                L2 = x.split('-')
                if L2[1] == '':
                    nums.extend(list(range(int(L2[0]),length)))
                else:
                    nums.extend(list(range(int(L2[0]),int(L2[1]))))
            else:
                nums.append(int(x))
        result = []
        for ii in range(length-1,-1,-1):
            if all_ep_list[ii]["ord"] in nums and all_ep_list[ii]["is_locked"]:
                result.append([all_ep_list[ii]["id"], all_ep_list[ii]["ord"], f'{all_ep_list[ii]["short_title"]} {all_ep_list[ii]["title"]}'])
        return result

    async def buy_manga_by_coupon(ep_id: 'int 漫画章节id'):
        '''通过漫读劵买漫画'''
        data = (await biliapi.mangaGetEpisodeBuyInfo(ep_id))["data"] #获取购买信息
        if not data["allow_coupon"]:
            raise Exception('本漫画不允许漫读劵购买')
        if data["recommend_coupon_id"] == 0:
            raise Exception('可能没有足够的漫读劵了')
        if not data["is_locked"]:
            raise Exception('漫画没有锁定，不用购买')
        data = await biliapi.mangaBuyEpisode(ep_id, 2, data["recommend_coupon_id"])
        if data["code"] != 0:
            raise Exception(data["msg"])

    coupons_will_expire = 0
    try:
        coupons_data = (await biliapi.mangaGetCoupons())["data"]
        for x in coupons_data["user_coupons"]:
            if x["will_expire"] != 0:
                coupons_will_expire += x["remain_amount"]
    except Exception as e: 
        logging.warning(f'{biliapi.name}: 获取漫读劵数量失败，原因为:{str(e)}，跳过漫画兑换')
        webhook.addMsg('msg_simple', f'{biliapi.name}:获取漫读劵异常\n')
        return

    if coupons_will_expire == 0:
        logging.info(f'{biliapi.name}: 没有即将过期的漫读劵，跳过购买')
        return

    if task_config["mode"] == 2:
        buy_list = _filter2list(task_config["filter"])
    elif task_config["mode"] == 1:
        try:
            buy_list = _filter2list((await _get_filter_by_favorite()))
        except Exception as e: 
            logging.warning(f'{biliapi.name}: 获取追漫列表失败，原因为:{str(e)}，跳过漫画兑换')
            webhook.addMsg('msg_simple', f'{biliapi.name}:获取追漫列表失败\n')
            return

    if len(buy_list) == 0:
        logging.info(f'{biliapi.name}: 没有需要购买的漫画，跳过消费即将过期漫读劵')
        return

    su = er = 0
    for x in buy_list:
        try:
            manga_detail = (await biliapi.mangaDetail(x[0]))["data"]
        except Exception as e: 
            logging.warning(f'{biliapi.name}: 获取mc为{x[0]} 的漫画信息失败，原因为:{str(e)}')
            er += 1
            continue

        list_need_buy = get_need_buy_eplist(x[1], manga_detail["ep_list"])
        if len(list_need_buy) == 0:
            logging.info(f'{biliapi.name}: 漫画 ({manga_detail["title"]})没有需要购买的话数')
            continue
        for y in list_need_buy:
            try:
                await buy_manga_by_coupon(y[0])
                coupons_will_expire -= 1
                logging.info(f'{biliapi.name}: 购买漫画({manga_detail["title"]})的章节({y[2]})成功')
                su += 1
            except Exception as e: 
                logging.warning(f'{biliapi.name}: 购买漫画({manga_detail["title"]})的章节({y[2]})失败，原因为:{str(e)}')
                er += 1
            if not coupons_will_expire > 0:
                break
        if not coupons_will_expire > 0:
            break

    logging.info(f'{biliapi.name}: 即将过期漫读劵消费完成')
    if er > 0:
        webhook.addMsg('msg_simple', f'{biliapi.name}:花费漫读劵成功{su}张,发生错误{er}次\n')