
__all__ = (
    'Downloader',
)

import threading, asyncio, time, aiohttp, io
from typing import Dict
from types import MappingProxyType

class _downloader_thread(threading.Thread):
    '''下载器线程'''
    def __init__(self, max_task_num: int = 3):
        threading.Thread.__init__(self)
        self._max_task_num = max_task_num
        self._loop = asyncio.get_event_loop()
        self._loop.run_until_complete(self._init_session())
        self._run_queue = asyncio.Queue(maxsize=max_task_num)
        self._wait_queue = asyncio.Queue()
        self._task_dict = {}

    @property
    def queue(self):
        '''返回队列'''
        return self._queue

    @property
    def loop(self):
        '''返回循环'''
        return self._loop

    @property
    def task_dict(self):
        '''返回任务字典映射'''
        return MappingProxyType(self._task_dict)

    async def task_loop(self) -> None:
        while True:
            id = await self._wait_queue.get()
            if id is None:
                for _ in range(self._max_task_num):
                    await self._run_queue.put(None)
                break
            await self._run_queue.put(id)
            asyncio.run_coroutine_threadsafe(self.start_task(id), self._loop)
        self._close.set_result(None)

    def add_task(self, id: int, name: str, url: str, dst: str, headers: Dict[str, str], max_connect_num: int) -> None:
        '''添加任务'''
        self._task_dict[id] = {
            "id": id,
            "status": "not start",
            "name": name,
            "url": url,
            "dst": dst,
            "headers": headers,
            "max_connect_num": max_connect_num,
            "connecting_num": 0,
            "continuable": "unkown",
            "totalLength": -1,
            "completedLength": 0
            }

    async def put_task_to_queue(self, id: int):
        self._task_dict[id]["status"] = "wait"
        await self._wait_queue.put(id)

    def run(self):
        try:
            self._loop.run_until_complete(self.task_loop())
        finally:
            self._loop.close()

    async def stop_safe(self):
        self._close = self._loop.create_future()
        await self._wait_queue.put(None)
        await self._close
        await self._session.close()

    async def _init_session(self):
        self._session = aiohttp.ClientSession()

    async def _fecth_worker(self, taskinfo: dict, queue: asyncio.Queue):
        CHUNK_SIZE = 1048576
        taskinfo["connecting_num"] += 1
        while True:
            if taskinfo["status"] == "canceled":
                break
            if queue.empty():
                break
            task = await queue.get()
            _headers = task[2].copy()
            if len(task) == 5:
                _headers.update({"Range":f'bytes={task[3]}-{task[3]+task[4]}'})
                ii = task[3]
                async with self._session.get(task[1], headers=_headers, verify_ssl=False) as r:
                    while True:
                        if taskinfo["status"] == "canceled":
                            break
                        data = await r.content.read(CHUNK_SIZE)
                        if not data:
                            break
                        task[0].seek(ii, 0)
                        task[0].write(data)
                        datalen = len(data)
                        ii += datalen
                        taskinfo["completedLength"] += datalen
            elif len(task) == 3:
                ii = 0
                async with self._session.get(task[1], headers=_headers, verify_ssl=False) as r:
                    while True:
                        if taskinfo["status"] == "canceled":
                            break
                        data = await r.content.read(CHUNK_SIZE)
                        if not data:
                            break
                        task[0].seek(ii, 0)
                        task[0].write(data)
                        datalen = len(data)
                        ii += datalen
                        taskinfo["completedLength"] += datalen
        taskinfo["connecting_num"] -= 1

    async def start_task(self, id: int):
        try:
            taskinfo = self._task_dict[id]
            _headers = taskinfo["headers"].copy()
            async with self._session.head(taskinfo["url"], headers=_headers) as r:
                if r.status < 200 or r.status >= 300:
                    taskinfo["status"] = 'http bad'
                    return
                if "content-length" in r.headers:
                    taskinfo["totalLength"] = int(r.headers["content-length"])
                else:
                    taskinfo["continuable"] = False
        
            if not taskinfo["continuable"] == False:
                _headers["range"] = 'bytes=0-10'
                async with self._session.head(taskinfo["url"], headers=_headers) as r:
                    if r.status < 200 or r.status >= 300:
                        taskinfo["status"] = 'http bad'
                        return
                    taskinfo["continuable"] = "content-range" in r.headers

            try:
                file = open(taskinfo["dst"], "wb")
            except:
                taskinfo["status"] = 'file open failed'
            else:
                queue = asyncio.Queue()
                if taskinfo["continuable"] and taskinfo["max_connect_num"] > 1:
                    CHUNK_SIZE = 1048576 * 8
                    CHUNK_NUM = taskinfo["totalLength"] // CHUNK_SIZE
                    for jj in range(CHUNK_NUM):
                        queue.put_nowait((file, taskinfo["url"], taskinfo["headers"], jj*CHUNK_SIZE, CHUNK_SIZE))
                    queue.put_nowait((file, taskinfo["url"], taskinfo["headers"], CHUNK_NUM*CHUNK_SIZE, taskinfo["totalLength"] - CHUNK_NUM*CHUNK_SIZE))
                    fecth_workers = [self._fecth_worker(taskinfo, queue) for ii in range(taskinfo["max_connect_num"])]
                    taskinfo["status"] = "active"
                    await asyncio.wait(fecth_workers)
                    if taskinfo["status"] != "canceled":
                        taskinfo["status"] = "over"
                else:
                    queue.put_nowait((file, taskinfo["url"], taskinfo["headers"]))
                    fecth_workers = [self._fecth_worker(taskinfo, queue)]
                    taskinfo["status"] = "active"
                    await asyncio.wait(fecth_workers)
                    if taskinfo["status"] != "canceled":
                        taskinfo["status"] = "over"
            finally:
                if file:
                    file.close()
        except:
            pass
        finally:
            await self._run_queue.get()

    def cancel_task(self, id: int):
        self._task_dict[id]["status"] = "canceled"

class Downloader(object):
    '''下载器'''
    def __init__(self):
        self._thread = _downloader_thread()
        self._task_dict = self._thread.task_dict
        self._thread.start()

    def __del__(self):
        asyncio.run_coroutine_threadsafe(self._thread.stop_safe(), self._thread.loop)
        del self._thread

    def add(self, name: str, url: str, dst: str, headers: Dict[str, str] = {}, max_connect_num: int = 4) -> int:
        '''
        添加一个下载任务到下载器
        name str 任务名称
        url str 链接地址
        dst str 保存路径
        headers dict http协议头
        max_connect int 最大连接数
        '''
        id = int(time.time() * 100000)
        self._thread.add_task(id, name, url, dst, headers, max_connect_num)
        time.sleep(0.01)
        return id
    
    def start(self, id: int) -> bool:
        '''
        添加任务进下载队列
        id int 任务id
        '''
        if id in self._task_dict:
            asyncio.run_coroutine_threadsafe(self._thread.put_task_to_queue(id), self._thread.loop)
            return True
        else:
            return False

    def cancel(self, id: int) -> bool:
        '''
        取消下载
        id int 任务id
        '''
        if id in self._task_dict:
            self._thread.cancel_task(id)
            return True
        else:
            return False

    def query(self, id: int) -> None:
        '''
        查询任务状态
        id int 任务id
        '''
        if id in self._task_dict:
            return self._task_dict[id]
        return None

    def queryAll(self) -> list:
        '''
        查询所有任务状态
        '''
        return [self._task_dict[x] for x in self._task_dict]

    def startAll(self) -> None:
        '''
        开始所有任务
        '''
        for x in self._task_dict:
            asyncio.run_coroutine_threadsafe(self._thread.put_task_to_queue(x), self._thread.loop)

    def cancelAll(self) -> None:
        '''
        取消所有任务
        '''
        for x in self._task_dict:
            self._thread.cancel_task(x)