
__all__ = (
    'asyncXliveRoomMsgGenerator',
    'asyncXliveRoomMsgGeneratorMulti'
    )

from . import asyncbili
from aiohttp import ClientWebSocketResponse, WSMessage, WSMsgType
from asyncio import sleep, Queue, get_event_loop, run_coroutine_threadsafe
from concurrent.futures import Future
from zlib import decompress
import json
from typing import Union, Dict, List

class asyncXliveRoomMsgGenerator():
    '''B站直播间消息异步生成器(每个生成器维护一条websocket连接)'''

    def __init__(self, 
                 roomid: int, 
                 biliapi: asyncbili = None, 
                 clientver: str = '2.6.0'
                 ):
        '''
        room_id   int        B站直播间id，必须是长id
        biliapi   asyncbili  B站异步会话
        clientver str        直播协议版本号
        '''
        self._roomid = roomid
        self._clientver = clientver
        if biliapi is None:
            self._api = asyncbili()
            self._ownner = True
        else:
            self._api = biliapi
            self._ownner = False
        self._ws = self._fut = None
        self._data_buf = b''

    async def _enterRoom(self):
        '''初始化(进入并验证房间)'''
        data = (await self._api.getDanmuInfo(self._roomid))["data"] #获取直播间服务器
        host = data["host_list"][0]["host"] #获取服务器列表，这里取第一个服务器
        token = data["token"]               #获取服务器验证令牌
        data = {                            #构建服务器验证数据包
            "uid":0,
            "roomid":self._roomid,
            "protover":2,
            "platform":"web",
            "clientver":self._clientver,
            "type":2,
            "key":token
            }
        self._ws = await self._api.wsConnect(f'wss://{host}/sub') #连接服务器
        await self._sendJson(data, 7)                             #发送验证包
        msg = await self._ws.receive()                            #获得服务器回复
        if msg.type != WSMsgType.BINARY or msg.data != b'\x00\x00\x00\x1a\x00\x10\x00\x01\x00\x00\x00\x08\x00\x00\x00\x01{"code":0}':
            raise RuntimeError('进入房间失败')                    #判断是否成功连接

    async def _heratBeatLoop(self):
        '''直播间心跳，每30s一次'''
        while True:
            await sleep(30)
            await self._sendHeratBeat()

    async def _sendJson(self, 
                       json_dict: dict, 
                       type: int
                       ) -> None:
        '''
        发送json数据包，必须先进入直播间
        json_dict  dict json数据
        type       int  数据类型
        '''
        data = json.dumps(json_dict).encode('utf-8')
        data =  (len(data)+16).to_bytes(4, 'big') +\
            (16).to_bytes(2, 'big') +\
            (1).to_bytes(2, 'big') +\
            (type).to_bytes(4, 'big') +\
            (1).to_bytes(4, 'big') +\
            data
        await self._ws.send_bytes(data)

    async def _sendHeratBeat(self):
        '''发送心跳数据包'''
        await self._ws.send_bytes(b'\x00\x00\x00\x1a\x00\x10\x00\x01' +
                            b'\x00\x00\x00\x02\x00\x00\x00\x01' + 
                            b'5b\x6f\x62\x6a\x65\x63\x74\x20' + 
                            b'4f\x62\x6a\x65\x63\x74\x5d'
                            )

    async def close(self):
        '''关闭'''
        if self._fut:
            self._fut.cancel()
        if self._ws:
            await self._ws.close()
        if self._ownner:
            await self._api.close()

    def __aiter__(self):
        return self

    async def __anext__(self):
        if len(self._data_buf) == 0:
            msg: WSMessage = await self._ws.receive()
            if msg.type in (WSMsgType.CLOSE,
                            WSMsgType.CLOSING,
                            WSMsgType.CLOSED):
                raise StopAsyncIteration
            self._data_buf = msg.data

        data = self._data_buf
        #解析数据头
        length = int.from_bytes(data[0:4], 'big') #int32 大端模式
        type = int.from_bytes(data[6:8], 'big')   #int16 大端模式
        code = int.from_bytes(data[8:12], 'big')  #int32 大端模式
        #解析数据体
        if type == 2: #数据zlib压缩，解压后再重新解析
            self._data_buf = decompress(data[16:length])
            return await self.__anext__()
        else:         #数据为原始字节串
            self._data_buf = data[length:]
            if code == 3: #数据体为整数
                return 1, int.from_bytes(data[16:length], 'big')
            else:         #数据体为json
                return 2, json.loads(data[16:length])

    async def __aenter__(self):
        await self._enterRoom()
        self._fut = run_coroutine_threadsafe(self._heratBeatLoop(), get_event_loop())
        return self

    async def __aexit__(self, *exc) -> None:
        await self.close()


class asyncXliveRoomMsgGeneratorMulti():
    '''B站直播间消息异步生成器(相同房间复用同一个消息生成器)'''

    _axmrmgMap: Dict[int, List[Union[asyncXliveRoomMsgGenerator, List[Queue], Future]]] = {}  
    #直播间id为key，房间消息生成器和异步消息队列列表和消息循环Future组成的三维列表为value的Dict(map)

    def __init__(self, 
                 roomid: int, 
                 clientver: str = '2.6.0'
                 ):
        '''
        room_id   int        B站直播间id，必须是长id
        clientver str        直播协议版本号
        '''
        self._room_id = roomid
        self._Queue = Queue()    #创建一个队列用于读取消息
        if roomid in self._axmrmgMap:
            self._axmrmgMap[roomid][1].append(self._Queue) #若此房间的消息生成器已经创建，则向消息队列列表里增加当前队列
        else:                                               #否则新建一个房间消息生成器并启动消息循环，避免对同一个房间创建多个消息生成器
            self._axmrmgMap[roomid] = [
                asyncXliveRoomMsgGenerator(roomid=roomid, clientver=clientver), 
                [self._Queue],
                None
                ]

    @classmethod
    async def _msgLoop(cls, room_id):
        '''异步消息循环，负责把直播间消息生成器获得的消息存放到消息队列列表里所有消息队列中'''
        async for msg in cls._axmrmgMap[room_id][0]:
            for queue in cls._axmrmgMap[room_id][1]:
                await queue.put(msg)

        #循环退出时，向队列加入退出码0通知所有生成器退出循环
        for queue in cls._axmrmgMap[room_id][1]:
                await queue.put((0, None))

    def __aiter__(self):
        return self

    async def __anext__(self):
        msg = await self._Queue.get()
        if msg[0] == 0:               #收到退出码终止循环
            raise StopAsyncIteration
        return msg

    async def __aenter__(self):
        if not self._axmrmgMap[self._room_id][2]:                 #如果当前房间的生成器没有初始化
            await self._axmrmgMap[self._room_id][0].__aenter__()  #进入房间(初始化)
            self._axmrmgMap[self._room_id][2] = run_coroutine_threadsafe(self._msgLoop(self._room_id), get_event_loop()) #启动异步消息循环
        return self

    async def __aexit__(self, *exc) -> None:
        self._axmrmgMap[self._room_id][1].remove(self._Queue) #退出时将消息队列移除消息队列列表
        if len(self._axmrmgMap[self._room_id][1]) == 0:          #若消息队列列表为空，说明所有该房间的消息生成器都已经退出了
            self._axmrmgMap[self._room_id][2].cancel()           #取消异步消息循环
            await self._axmrmgMap[self._room_id][0].__aexit__()  #断开生成器与服务器的连接