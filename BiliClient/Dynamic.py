
__all__ = (
    'Dynamic',
)

from typing import Union, Dict, Any
from _io import FileIO, BytesIO
from . import bili, biliContext

class DynamicContent(biliContext):
    '''文本类用来处理B站动态格式'''

    def __init__(self, biliapi: bili):
        super(DynamicContent, self).__init__(biliapi)
        self._content = ''
        self._control = []
        self._at_uids = []
        self._pictures = None
        self._extension = {"emoji_type":1,"from":{"emoji_type":1},"flag_cfg":{}}
        self._type = 4

    def add(self, text: str):
        '''添加内容'''
        self._content = f'{self._content}{text}'
        return self

    def at(self, uname: str = None, uid: int = 0):
        '''@用户
        uname  str 用户名
        uid    int 用户uid

        请尽量提供用户名和uid两个参数，或者uid这一个参数，如果只单独提供uname可能导致@到其他用户名相似的用户
        '''
        if uname and uid:
            ...
        elif uname:
            ret = self._api.dynamicAtSearch(uname)
            if ret["code"] != 0:
                raise ValueError(f'搜索用户名({uname})失败(ret["message"])')
            uid = ret["data"]["groups"][0]["items"][0]["uid"]
        elif uid:
            ret = self._api.getSpaceInfo(uid)
            if ret["code"] == -404:
                raise ValueError(f'uid为{uid}的用户不存在')
            elif ret["code"] != 0:
                raise ValueError(f'获取uid为{uid}的用户名失败(ret["message"])')
            uname = ret["data"]["name"]
        else:
            raise ValueError('uname与uid至少提供一个')

        self._control.append({"location":len(self._content),"type":1,"length":len(uname)+2,"data":f'{uid}'})
        self._at_uids.append(f'{uid}')
        self._content = f'{self._content}@{uname} '

        return self

    def picUrl(self, 
               url: str, 
               width: int = 0, 
               height: int = 0,
               size: int = 0
               ):
        '''
        插入站内图片链接
        url    str   图片链接
        width  int   图片宽度，单位为像素
        height int   图片高度，单位为像素
        size   float 图片大小，单位为KB
        '''
        if self._type != 0:
            self._pictures = []
            self._type = 0
        data = {"img_src": url}
        if width:
            data["img_width"] = width
        if height:
            data["img_height"] = height
        if height:
            data["img_size"] = size
        self._pictures.append(data)
        return self

    def picFile(self, file: Union[FileIO, BytesIO, bytes, str]):
        '''
        插入本地图片文件或Bytes对象
        file  FileIO   图片文件IO对象
        file  BytesIO  图片字节串IO对象
        file  bytes    图片字节串
        file  str      图片文件路径
        '''
        if isinstance(file, str):
            with open(file, 'rb') as f:
                ret = self._api.drawImageUpload(f)
                size = f.tell()
        else:
            if isinstance(file, FileIO) or isinstance(file, BytesIO):
                size = file.seek(0, 2) / 1000 #获取文件大小
                file.seek(0, 0)
            elif isinstance(file, bytes):
                size = len(file) / 1000
            ret = self._api.drawImageUpload(file)

        if ret["code"] != 0:
            raise Exception(f'上传图片失败({ret["message"]})')

        return self.picUrl(ret["data"]["image_url"], ret["data"]["image_width"], ret["data"]["image_height"], size)

    def vote(self, 
             vote: Dict[str, Any],
             title: str = None
             ):
        '''
        插入站内投票
        vote  Dict[str, Any]  投票结构体字典
        title str             动态中显示的投票标题，为空则使用vote参数中的title字段
        '''
        ret = self._api.articleCreateVote(vote)
        if ret["code"] != 0:
            raise Exception(f'创建抽奖失败({ret["message"]})')
        if not title:
            title = vote["title"]
        self._extension["vote_cfg"] = {"vote_id":ret["data"]["vote_id"],"title":title}
        self._control.append({"data":"3","length":len(title)+1,"location":len(self._content)+1,"type":3})
        self._content = f'{self._content} {title} '
        return self

    def __getitem__(self, key):
        if key == 'type':
            return self._type
        elif key == 'content':
            return self._content
        elif key == 'extension':
            return self._extension
        elif key == 'at_uids':
            return self._at_uids
        elif key == 'ctrl':
            return self._control
        elif key == 'pictures' and self._type == 0:
            return self._pictures
        raise KeyError(key)

    def keys(self):
        if self._type == 4:
            return ('type', 'content', 'extension', 'at_uids', 'ctrl')
        elif self._type == 0:
            return ('type', 'pictures', 'content', 'extension', 'at_uids', 'ctrl')
        else:
            raise ValueError()

class Dynamic(biliContext):
    '''B站动态类,用于发表B站动态'''

    def __init__(self, biliapi: bili):
        super(Dynamic, self).__init__(biliapi)
        self._content = DynamicContent(biliapi)

    def Content(self) -> DynamicContent:
        '''动态内容'''
        return self._content

    def submit(self):
        '''提交动态'''
        if self._content["type"] == 4:
            ret = self._api.dynamicCreate(**self._content)
        elif self._content["type"] == 0:
            ret = self._api.dynamicCreateDraw(**self._content)
        else:
            raise ValueError()

        if ret["code"] == 0:
            return 0, ret["data"]["dynamic_id_str"]
        else:
            return ret["code"], ret["message"]