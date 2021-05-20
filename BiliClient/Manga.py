
__all__ = (
    'MangaDownloader',
)

from . import bili, biliContext
from requests.sessions import Session
from typing import Iterable, Generator, List, Union, Dict, Any
import os, re
from enum import Enum

class DownloadCode(Enum):
    Ok     =  0
    Error  =  1
    Locked =  2

class DownloadResult(object):
    def __init__(self, 
                 code: DownloadCode, 
                 ep_id: int, 
                 title: str, 
                 name: str
                 ):
        self.code = code
        self.ep_id = ep_id
        self.title = title
        self.name = name

class MangaDownloader(biliContext):
    '''B站漫画下载类'''

    DownloadCode = DownloadCode

    def __init__(self, 
                 biliapi: bili = None,
                 comic_id: int = 0
                 ):
        '''
        biliapi     bili  B站接口对象实例
        comic_id    int   漫画id
        '''
        super(MangaDownloader, self).__init__(biliapi)

        if comic_id:
            self.setComicId(comic_id)
        else:
            self._manga_detail = None

    def setComicId(self, comic_id: int) -> None:
        '''
        设置当前漫画id
        comic_id    int   漫画id
        '''
        self._manga_detail = self._api.mangaDetail(comic_id)["data"]
        self._comic_id = self._manga_detail["id"]
        self._manga_detail["ep_list"].sort(key=lambda elem: elem["ord"])
        self._chapters = {x["id"]:x for x in self._manga_detail["chapters"]}

    def getIndex(self) -> List[Dict[str, Any]]:
        '''获取漫画章节数据(列表)'''
        return self._manga_detail["ep_list"]

    def getTitle(self) -> str:
        '''获取漫画名称'''
        return re.sub('[\/:*?"<>|]', '', self._manga_detail["title"]).strip()

    def getAuthors(self) -> List[str]:
        '''获取漫画作者名称'''
        return self._manga_detail["author_name"]

    def getCover(self) -> str:
        '''获取漫画封面图片链接'''
        return self._manga_detail["vertical_cover"]

    def getNum(self) -> int:
        '''获取漫画章节数量'''
        return len(self._manga_detail["ep_list"])

    def getDownloadList(self, 
                        ep_id: int
                        ) -> List[str]:
        '''
        获取漫画章节中所有图片的真实url
        ep_id  int  章节id
        '''
        data = self._api.mangaImageIndex(ep_id)["data"]["images"]   #获取一个章节的所有图片网址
        url_list = [x["path"] for x in data]
        data = self._api.mangaImageToken(url_list)["data"]          #通过图片网址获得图片token
        return [f'{x["url"]}?token={x["token"]}' for x in data]      #将图片网址和token拼接在一起组合成真实网址

    def _isLocked(self, ep_data: Dict[str, Any]) -> bool:
        '''
        判断漫画是否被锁定
        ep_data dict 漫画数据
        '''
        if ep_data.get("is_locked", True):
            if ep_data["chapter_id"] != 0 and ep_data["chapter_id"] in self._chapters:
                return self._chapters[ep_data["chapter_id"]].get("is_locked", True)
            return True
        return False

    def downloadEp(self, 
                   ep_id: int, 
                   path: str = "."
                   ) -> None:
        '''
        下载一个章节
        ep_id  int      章节id
        path   str      下载储存文件夹路径
        '''
        if not os.path.exists(path):
            os.mkdir(path)

        _list = self.getDownloadList(ep_id)

        for ii in range(len(_list)):
            with open(os.path.join(path, f'{ii+1:0>2}.jpg'), 'wb') as f:
                f.write(self._api._session.get(_list[ii]).content)

    def downloadIndexes(self, 
                        index: Union[int, Iterable[int]], 
                        path: str
                        ) -> Generator[DownloadResult, None, None]:
        '''
        下载指定序号对应的章节
        index  int,Iterable[int]  下载章节序号或序号列表,序号从0开始
        path   str                下载储存文件夹路径
        '''
        path = os.path.join(path, self.getTitle())
        if not os.path.exists(path):
            os.makedirs(path)
        
        bq = len(str(self.getNum()))
        mlist = self.getIndex()

        if isinstance(index, int):
            index = list(index)

        if isinstance(index, Iterable):
            for ii in index:
                title = re.sub('[\/:*?"<>|]','', mlist[ii]["title"]).strip()
                if title.replace(' ', '') == '':
                    title = mlist[ii]["short_title"]
                name = f'{mlist[ii]["ord"]:0>{bq}}-{title}'
                if not self._isLocked(mlist[ii]):
                    try:
                        self.downloadEp(mlist[ii]['id'], os.path.join(path, name))
                    except:
                        yield DownloadResult(DownloadCode.Error, mlist[ii]['id'], title, name)
                    else:
                        yield DownloadResult(DownloadCode.Ok, mlist[ii]['id'], title, name)
                else:
                    yield DownloadResult(DownloadCode.Locked, mlist[ii]['id'], title, name)
        else:
            raise ValueError('index必须为整数或整数可迭代类型')

    def downloadAll(self, 
                    path: str
                    ) -> Generator[DownloadResult, None, None]:
        '''
        下载漫画所有章节
        path   str                下载储存文件夹路径
        '''
        path = os.path.join(path, self.getTitle())
        if not os.path.exists(path):
            os.makedirs(path)
        
        bq = len(str(self.getNum()))
        for x in self.getIndex():
            title = re.sub('[\/:*?"<>|]','', x["title"]).strip()
            if title.replace(' ', '') == '':
                title = x["short_title"]
            name = f'{x["ord"]:0>{bq}}-{title}'
            if not self._isLocked(x):
                try:
                    self.downloadEp(x['id'], os.path.join(path, name))
                except:
                    yield DownloadResult(DownloadCode.Error, x['id'], title, name)
                else:
                    yield DownloadResult(DownloadCode.Ok, x['id'], title, name)
            else:
                yield DownloadResult(DownloadCode.Locked, x['id'], title, name)