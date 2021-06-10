
__all__ = (
    'Article',
)

from typing import Union, Dict
from _io import FileIO, BytesIO
from . import bili, biliContext

class ArticleContent(biliContext):
    '''文本类用来处理B站奇葩的专栏提交格式'''

    def __init__(self, biliapi: bili, content: str = ""):
        super(ArticleContent, self).__init__(biliapi)
        self._content = content

    def setRawContent(self, content: str):
        '''设置原始内容字符串'''
        self._content = content

    def add(self, text: str):
        '''添加内容'''
        self._content = f'{self._content}{text}'
        return self

    def startH(self):
        '''开始一个标题'''
        self._content = f'{self._content}<h1>'
        return self

    def endH(self):
        '''结束一个标题'''
        self._content = f'{self._content}</h1>'
        return self

    def startP(self, align: str = ""):
        '''
        开始一段正文
        align str 值为left，center， right其中一种
        '''
        if align == "":
            self._content = f'{self._content}<p>'
        elif align == "left":
            self._content = f'{self._content}<p style="text-align: left;">'
        elif align == "center":
            self._content = f'{self._content}<p style="text-align: center;">'
        elif align == "right":
            self._content = f'{self._content}<p style="text-align: right;">'
        else:
            self._content = f'{self._content}<p>'
        return self

    def endP(self):
        '''结束一段正文'''
        self._content = f'{self._content}</p>'
        return self

    def startD(self):
        '''开始一段带删除线的文字'''
        self._content = f'{self._content}<span style="text-decoration: line-through;">'
        return self

    def endD(self):
        '''结束一段带删除线的文字'''
        self._content = f'{self._content}</span>'
        return self

    def startS(self, size=16):
        '''开始一段大小为size的文字'''
        self._content = f'{self._content}<span class="font-size-{size}">'
        return self

    def endS(self):
        '''结束一段特定大小的文字'''
        self._content = f'{self._content}</span>'
        return self

    def startB(self):
        '''开始一段加粗的文字'''
        self._content = f'{self._content}<strong>'
        return self

    def endB(self):
        '''结束一段加粗的文字'''
        self._content = f'{self._content}</strong>'
        return self

    def startY(self):
        '''开始一段引用'''
        self._content = f'{self._content}<blockquote>'
        return self

    def endY(self):
        '''结束一段引用'''
        self._content = f'{self._content}</blockquote>'
        return self

    def br(self):
        '''插入换行，不用结束，一般新段默认换行'''
        self._content = f'{self._content}<p><br/></p>'
        return self

    def line(self, type: int = 0):
        '''
        插入一段分割线，不用结束
        type  int  分割线类型
        '''
        ll = ('<figure class="img-box" contenteditable="false"><img src="//i0.hdslb.com/bfs/article/0117cbba35e51b0bce5f8c2f6a838e8a087e8ee7.png" class="cut-off-1"/></figure>',
                '<figure class="img-box" contenteditable="false"><img src="//i0.hdslb.com/bfs/article/4aa545dccf7de8d4a93c2b2b8e3265ac0a26d216.png" class="cut-off-2"/></figure>',
                '<figure class="img-box" contenteditable="false"><img src="//i0.hdslb.com/bfs/article/71bf2cd56882a2e97f8b3477c9256f8b09f361d3.png" class="cut-off-3"/></figure>',
                '<figure class="img-box" contenteditable="false"><img src="//i0.hdslb.com/bfs/article/db75225feabec8d8b64ee7d3c7165cd639554cbc.png" class="cut-off-4"/></figure>',
                '<figure class="img-box" contenteditable="false"><img src="//i0.hdslb.com/bfs/article/4adb9255ada5b97061e610b682b8636764fe50ed.png" class="cut-off-5"/></figure>',
                '<figure class="img-box" contenteditable="false"><img src="//i0.hdslb.com/bfs/article/02db465212d3c374a43c60fa2625cc1caeaab796.png" class="cut-off-6"/></figure>')
        self._content = f'{self._content}{ll[type]}'
        return self

    def startU(self):
        '''开始一段无序列表'''
        self._content = f'{self._content}<ul class=" list-paddingleft-2">'
        return self

    def endU(self):
        '''结束一段无序列表'''
        self._content = f'{self._content}</ul>'
        return self

    def startO(self):
        '''开始一段有序列表'''
        self._content = f'{self._content}<ol class=" list-paddingleft-2">'
        return self

    def endO(self):
        '''结束一段有序列表'''
        self._content = f'{self._content}</ol>'
        return self

    def startL(self):
        '''开始列表中的一列'''
        self._content = f'{self._content}<li>'
        return self

    def endL(self):
        '''结束列表中的一列'''
        self._content = f'{self._content}</li>'
        return self

    def startA(self, url=""):
        '''插入站内链接,链接说明文字请用add方法添加'''
        self._content = f'{self._content}<a href="{url}">'
        return self

    def endA(self):
        '''结束插入站内链接'''
        self._content = f'{self._content}</a>'
        return self

    def picUrl(self, 
               url: str = "", 
               text: str = "", 
               width: str = "", 
               height: str = ""
               ):
        '''
        插入站内图片链接
        url    str 图片链接
        text   str 图片说明
        width  str 图片宽度，比如15px，25%
        height str 图片高度，比如15px，25%
        '''
        self._content = f'{self._content}<figure contenteditable="false" class="img-box"><img src="{url}" '
        if width:
            self._content = f'{self._content}width="{width}" '
        if height:
            self._content = f'{self._content}height="{height}" '
        self._content = f'{self._content}/><figcaption class="caption" contenteditable="">{text}</figcaption></figure>'
        return self

    def picFile(self, 
                file: Union[FileIO, BytesIO], 
                text: str = "", 
                width: str ="", 
                height: str = ""
                ):
        '''
        插入本地图片文件或Bytes对象
        file  FileIO   图片文件对象
        file  BytesIO  图片字节串对象
        text   str 图片说明
        width  str 图片宽度，比如15px，25%
        height str 图片高度，比如15px，25%
        '''
        ret = self._api.articleUpcover(file)
        picurl = ret["data"]["url"].replace("http", "https")
        return self.picUrl(picurl, text, width, height)

    def vote(self, vote: dict):
        '''
        插入站内投票
        vote  dict  投票结构体字典
        '''
        id = self._api.articleCreateVote(vote)["data"]["vote_id"]
        self._content = f'{self._content}<figure class="img-box" contenteditable="false"><img src="//i0.hdslb.com/bfs/article/a9fb8e570e9683912de228446e606745cce62aa6.png" class="vote-display" data-vote-id="{id}"/><figcaption class="vote-title web-vote" contenteditable="">{vote["title"]}</figcaption></figure>'
        return self

    def card(self, 
             id: Union[str, int],
             type: str
             ):
        '''
        插入引用标签
        id    Union[str, int]  标签id，如果是视频标签，则是视频av号，专栏标签则是专栏aid
        type  str              标签类型
                               video: 视频标签
                               article:专栏标签
                               fanju:番剧标签
                               music:音乐标签
                               shop:会员购标签
                               caricature:漫画标签
                               live:直播标签
        '''
        def video():
            ret = self._api.articleCardsBvid(id)
            picurl = ret["data"][id]["pic"]
            picurl = picurl.replace("http", "https")
            aid = ret["data"][id]["aid"]
            return f'<figure class="img-box" contenteditable="false"><img src="{picurl}" aid="{aid}" class="video-card nomal" type="nomal"/></figure>'
        def article():
            ret = self._api.articleCardsCvid(id)
            picurl = ret["data"]["banner_url"]
            picurl = picurl.replace("http", "https")
            aid = ret["data"]["id"]
            return f'<figure class="img-box" contenteditable="false"><img src="{picurl}" aid="{aid}" class="article-card" type="normal"/></figure>'
        def fanju():
            ret = self._api.articleCardsCvid(id)
            picurl = ret["data"]["cover"]
            picurl = picurl.replace("http", "https")
            return f'<figure class="img-box" contenteditable="false"><img src="{picurl}" aid="{id}" class="fanju-card" type="normal"/></figure>'
        def music():
            ret = self._api.articleCardsCvid(id)
            picurl = ret["data"]["cover_url"]
            picurl = picurl.replace("http", "https")
            return f'<figure class="img-box" contenteditable="false"><img src="{picurl}" aid="{id}" class="music-card" type="normal"/></figure>'
        def shop():
            ret = self._api.articleCardsCvid(id)
            picurl = ret["data"]["performance_image"]
            picurl = picurl.replace("http", "https")
            return f'<figure class="img-box" contenteditable="false"><img src="{picurl}" aid="{id}" class="shop-card" type="normal"/></figure>'
        def caricature():
            ret = self._api.articleMangas(id)
            picurl = ret["data"][id]["vertical_cover"]
            picurl = picurl.replace("http", "https")
            return f'<figure class="img-box" contenteditable="false"><img src="{picurl}" aid="{id}" class="caricature-card nomal" type="nomal"/></figure>'
        def live():
            ret = self._api.articleCardsCvid(id)
            picurl = ret["data"]["cover"]
            picurl = picurl.replace("http", "https")
            aid = ret["data"]["room_id"]
            return f'<figure class="img-box" contenteditable="false"><img src="{picurl}" aid="{aid}" class="live-card" type="normal"/></figure>'

        index = {
            "video": video,
            "article": article,
            "fanju": fanju,
            "music": music,
            "shop": shop,
            "caricature": caricature,
            "live": live,
            }
        if type in index:
            self._content = f'{self._content}{index[type]()}'
        return self

    @property
    def content(self):
        '''原始内容'''
        return self._content

class Article(biliContext):
    '''B站专栏类,用于发表B站专栏'''

    def __init__(self, 
                 biliapi: bili, 
                 tilte: str = "",
                 content: str = "", 
                 aid: int = 0, 
                 category: int = 0, 
                 list_id: int = 0, 
                 tid: int = 4, 
                 original: int = 1, 
                 image_urls: str = "", 
                 origin_image_urls: str = ""
                 ):
        '''
        biliapi            bili  B站接口对象实例
        tilte              str   专栏标题
        content            str   专栏内容字符串
        aid                int   专栏或专栏草稿的aid，不提供则创建新草稿
        category           int   专栏分类
        list_id            int   文集编号，默认不添加到文集
        tid                int   专栏分区
        original           int   是否是原创专栏
        image_urls         str   封面图片网址
        origin_image_urls  str   封面图片网址
        '''
        super(Article, self).__init__(biliapi)

        self._tilte = tilte
        self._content = ArticleContent(self._api, content)
        self.setContent(content)
        self._category = category
        self._list_id = list_id
        self._tid = tid
        self._original = original
        self.setImage(origin_image_urls, image_urls)
        if(aid == 0):
            ret = self._api.createArticle(tilte, content, aid, category, list_id, tid, original, image_urls, origin_image_urls)
            self._aid = ret["data"]["aid"]
        else:
            self._aid = aid

    def Content(self) -> ArticleContent:
        '''专栏内容'''
        return self._content

    def setTilte(self, tilte: str):
        '''设置专栏标题'''
        self._tilte = tilte

    def setCategory(self, category: int):
        '''设置专栏分类'''
        self._category = category

    def setListId(self, list_id: int):
        '''设置文集编号'''
        self._list_id = list_id

    def setTid(self, tid: int):
        '''设置专栏类型'''
        self._tid = tid

    def setOriginal(self, original: int = 1):
        '''设置专栏是否为原创,原创为1,非原创为0'''
        self._original = original

    def setImage(self, origin_image_urls: str, image_urls: str = None):
        '''
        设置专栏缩略图
        origin_image_urls  str 缩略图原图在文章中的网址
        image_urls         str 缩略图网址
        '''
        self._origin_image_urls = origin_image_urls
        if image_urls:
            self._image_urls = image_urls
        else:
            self._image_urls = origin_image_urls

    def setContent(self, content: Union[str, Content]):
        '''设置文章内容'''
        if isinstance(content, str):
            self._content.setRawContent(content)
        elif isinstance(content, ArticleContent):
            self._content = content
        else:
            raise ValueError("content参数必须为字符串或ArticleContent对象")

    def getAid(self, url: bool = False):
        '''
        获取创建文章的aid或url
        url bool 是否返回网址，True为返回网址(可通过url在网页上修改此文章)，False为返回aid号
        '''
        if url:
            return f'https://member.bilibili.com/v2#/upload/text/edit?aid={self._aid}'
        else:
            return self._aid

    def refresh(self):
        '''如果在本程序外(例如网页上)修改了本文章,执行此方法同步内容到本地'''
        ret = self._api.getArticle(self._aid)
        self._tilte = ret["data"]["tilte"]
        self._content.setRawContent(ret["data"]["content"])
        self._category = ret["data"]["category"]["id"]
        if(ret["data"]["list"] != None):
            self._list_id = ret["data"]["list"]["id"]
        self._tid = ret["data"]["template_id"]
        self._original = ret["data"]["original"]
        self._image_urls = ret["data"]["image_urls"][0]
        self._origin_image_urls = ret["data"]["origin_image_urls"][0] #这里可能有丢失封面的问题

    def save(self):
        '''保存至B站上草稿箱,不发布,网页上可编辑'''
        return self._api.createArticle(self._tilte, self._content.content, self._aid, self._category, self._list_id, self._tid, self._original, self._image_urls, self._origin_image_urls)

    def submit(self):
        '''发布至B站上，必须先使用save方法保存到B站草稿箱'''
        return self._api.createArticle(self._tilte, self._content.content, self._aid, self._category, self._list_id, self._tid, self._original, self._image_urls, self._origin_image_urls, True)

    def delself(self):
        '''删除当前文章草稿'''
        self._api.deleteArticle(self._aid)

    def imageFile2Url(self, 
                      file: Union[FileIO, BytesIO]
                      ):
        return self._api.articleUpcover(file)["data"]["url"].replace("http", "https")