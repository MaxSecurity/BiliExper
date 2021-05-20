
__all__ = (
    'Audio',
    'AudioMenu',
    'AudioUploader',
    'CompilationUploader'
)

from . import bili, biliContext
import re, os, base64, time, math
from typing import Union, Dict, Sequence

class Audio(biliContext):
    '''B站音频下载类'''

    def __init__(self, 
                 biliapi: bili = None,
                 au_id: int = None, 
                 url: str = None,
                 audio_info: dict = None
                 ):
        '''
        biliapi    bili B站接口对象实例
        au_id      int  音频id
        url        str  音频url
        audio_info dict 音频信息
        '''
        super(Audio, self).__init__(biliapi)

        if au_id:
            ...
        elif url:
            find = re.findall('au([0-9]+)', url)
            if find:
                au_id = int(find[0])
            else:
                raise ValueError("不正确的网址")
        elif not audio_info:
            raise ValueError("au_id与url至少提供一个")

        self.update(au_id, audio_info)

    def update(self, 
               au_id: int,
               audio_info: dict = None
               ) -> None:
        '''
        更新数据
        '''
        if not audio_info:
            audio_info = self._api.audioInfo(au_id)["data"]
        self._au_id = audio_info["id"]
        self._title = audio_info["title"]
        self._author = audio_info["author"]
        self._duration = audio_info["duration"]
        self._lyric = audio_info["lyric"].replace("http:", "https:") if audio_info["lyric"] else None

    def getRealUrl(self):
        '''获取当前音频的真实下载地址'''
        return self._api.audioUrl(self._au_id)["data"]["cdns"][0]

    def download(self, 
                 path: str = None
                 ) -> None:
        '''
        下载当前音频和歌词(如果存在)
        path str 存放的文件夹路径
        '''
        self.downloadAudio(path)
        self.downloadLyric(path)

    def downloadAudio(self, 
                      path: str = None
                      ) -> None:
        '''
        下载当前音频
        path str 存放的文件夹路径
        '''
        if path:
            if not os.path.exists(path):
                os.makedirs(path)
        else:
            path = os.getcwd()
        path = os.path.join(path, self._title + '.m4a')
        with open(path, 'wb') as fp:
            for x in self._api.getUrlStream(self.getRealUrl()):
                fp.write(x)

    def downloadLyric(self, 
                      path: str = None
                      ) -> None:
        '''
        下载当前音频的歌词(如果存在)
        path str 存放的文件夹路径
        '''
        if not self._lyric:
            return
        if path:
            if not os.path.exists(path):
                os.makedirs(path)
        else:
            path = os.getcwd()
        path = os.path.join(path, self._title + '.lrc')
        with open(path, 'wb') as fp:
            fp.write(self._api.getUrl(self._lyric))

    @property
    def au_id(self) -> int:
        return self._au_id

    @property
    def title(self) -> str:
        return self._title

    @property
    def author(self) -> str:
        return self._author

    @property
    def duration(self) -> int:
        return self._duration

    @property
    def has_lyric(self) -> bool:
        return bool(self._lyric)

    def __repr__(self) -> str:
        return f'id:{self._au_id}; title:{self._title}; author:{self._author}; duration:{self._duration}秒; has_lyric:{self.has_lyric}'

class AudioMenu(biliContext):
    '''B站音频菜单类'''

    def __init__(self, 
                 biliapi: bili = None,
                 am_id: int = None, 
                 url: str = None
                 ):
        '''
        biliapi    bili B站接口对象实例
        am_id      int  音频菜单id
        url        str  音频菜单url
        '''
        super(AudioMenu, self).__init__(biliapi)

        if am_id:
            ...
        elif url:
            find = re.findall('am([0-9]+)', url)
            am_id = int(find[0])
        else:
            raise ValueError("am_id与url至少提供一个")

        info = self._api.audioMenuInfo(am_id) #获取菜单信息
        assert info["code"] == 0
        if not info["data"]:
            raise ValueError("不正确的音频菜单id")
        self._am_id = info["data"]["menuId"]
        self._title = info["data"]["title"]
        self._author = info["data"]["uname"]
        #self._type = info["data"]["type"]

        info = self._api.audioMenuList(self._am_id) #获取菜单信息
        self._audio_list = []
        for audio in info["data"]["data"]:
            self._audio_list.append(Audio(self._api, audio_info=audio))
        while info["data"]["pageCount"] != info["data"]["curPage"]:
            info = self._api.audioMenuList(self._am_id)
            for audio in info["data"]["data"]:
                self._audio_list.append(Audio(self._api, audio_info=audio))

    def downloadAll(self, 
                    path: str = None
                    ) -> None:
        '''
        下载当前菜单所有音频和歌词(如果存在)
        path str 存放的文件夹路径
        '''
        for audio in self:
            audio.download(path)

    @property
    def am_id(self) -> int:
        return self._am_id

    @property
    def title(self) -> str:
        return self._title

    @property
    def author(self) -> str:
        return self._author

    def __repr__(self) -> str:
        return f'id:{self._am_id}; title:{self._title}; author:{self._author}; num:{len(self)}'

    def __getitem__(self, key) -> Audio:
        return self._audio_list[key]

    def __len__(self) -> int:
        return len(self._audio_list)

class AudioUploader(biliContext):
    '''B站音频上传类'''
    _categories = (
        (1, '原创'), (2, '翻唱/翻奏'), (48, '改编/remix'), (3, '人声演唱'), 
        (4, 'VOCALOID歌手'), (5, '人力鬼畜'), (6, '纯音乐/ 演奏'), (7, '流行'), 
        (8, '古风'), (9, '摇滚'), (10, '民谣'), (11, '电子'), (12, '舞曲'), 
        (13, '说唱'), (14, '轻音乐'), (15, '阿卡贝拉'), (16, '爵士'), (17, '乡村'), 
        (18, 'R&B/Soul'), (19, '古典'), (20, '民族'), (21, '英伦'), (22, '金属'), 
        (23, '朋克'), (24, '蓝调'), (25, '雷鬼'), (26, '世界音乐'), (27, '拉丁'), 
        (28, '另类/独立'), (29, 'New Age'), (30, '后摇'), (31, 'Bossa Nova'), 
        (32, '华语'), (33, '日语'), (34, '英语'), (35, '韩语'), (36, '粤语'), 
        (37, '其他语种'), (38, '动 画'), (39, '游戏'), (40, '影视'), (41, '网络歌曲'), 
        (42, '同人'), (43, '偶像'), (44, '广播剧'), (45, '有声故事'), (47, '其他')
        )

    def __init__(self,
                 biliapi: bili
                 ):
        '''
        biliapi     bili  B站接口对象实例
        '''
        super(AudioUploader, self).__init__(biliapi)

        self._data = {
            "lyric_url": "",
            "cover_url": "",
            "song_id": 0,
            "album_id": 0,
            "mid": self._api._uid,
            "cr_type": 2,
            "creation_type_id": 47,
            #"music_type_id": 3,
            #"style_type_id": 7,
            #"theme_type_id": 41,
            #"language_type_id": 32,
            #"origin_title": "", 
            #"origin_url": "",
            "avid": "",
            "tid": "",
            "cid": "", 
            "compilation_id": "",
            "title": "",
            "intro": "",
            "member_with_type":[
                    {"m_type":1,"members":[]},
                    {"m_type":2,"members":[]},
                    {"m_type":3,"members":[]},
                    {"m_type":4,"members":[]},
                    {"m_type":5,"members":[]},
                    {"m_type":6,"members":[]},
                    {"m_type":7,"members":[]},
                    {"m_type":8,"members":[]},
                    {"m_type":9,"members":[]},
                    {"m_type":10,"members":[]},
                    {"m_type":11,"members":[]},
                    {"m_type":127,"members":[{"name":self._api._name,"mid":self._api._uid}]}
                    ],
            "song_tags": [],
            "create_time": 0,
            "activity_id": 0,
            "is_bgm": 1,
            "source": 0
            }

    def setSongId(self,
                  song_id: int
                  ) -> None:
        '''
        设置音频id
        song_id int 音频id
        '''
        self._data["song_id"] = song_id

    def setTid(self,
               tid: int
               ) -> None:
        '''
        设置分区类型
        tid int 分区id(整数)，如174代表生活->其他分区
        '''
        self._data["tid"] = tid

    def setIntro(self,
                 intro: str
                 ) -> None:
        '''
        设置音频简介
        intro str 音频简介
        '''
        self._data["intro"] = intro

    def setTitle(self,
                 title: str
                 ) -> None:
        '''
        设置音频标题
        title str 音频标题
        '''
        self._data["title"] = title

    def setAssociatedVideo(self,
                           avid: str,
                           cid: int
                           ) -> None:
        '''
        设置关联视频
        avid str 视频av号，必须带av前缀，如"av456982307"
        cid  int 视频cid，因为有分P所以av号不足以定位一个视频，还需要提供cid
        '''
        self._data["avid"] = avid
        self._data["cid"] = cid

    def addSinger(self,
                  singer: str,
                  mid: int = 0
                  ) -> None:
        '''
        在已有的基础上添加歌唱者
        singer str 歌唱者
        mid    int 歌唱者id，非B站用户或不提供默认为0
        '''
        self._data["member_with_type"][0]["members"].append({"name": author, "mid": mid})

    def setSingers(self,
                  singers: Sequence[Union[str, Sequence[Union[str, int]]]]
                  ) -> None:
        '''
        设置歌唱者
        singers Sequence[Union[str, Sequence[Union[str, int]]]] 歌唱者数组，如("作者1", "作者2")或(("作者1", 作者1的mid), ("作者2", 作者2的mid))
        '''
        self._setMembers(singers, 0)

    def setLyricist(self,
                    lyricists: Sequence[Union[str, Sequence[Union[str, int]]]]
                    ) -> None:
        '''
        设置作词者
        lyricists Sequence[Union[str, Sequence[Union[str, int]]]] 作词者数组，如("作者1", "作者2")或(("作者1", 作者1的mid), ("作者2", 作者2的mid))
        '''
        self._setMembers(lyricists, 1)

    def setComposers(self,
                     composers: Sequence[Union[str, Sequence[Union[str, int]]]]
                     ) -> None:
        '''
        设置作曲者
        composers Sequence[Union[str, Sequence[Union[str, int]]]] 作曲者数组，如("作者1", "作者2")或(("作者1", 作者1的mid), ("作者2", 作者2的mid))
        '''
        self._setMembers(composers, 2)

    def setArrangers(self,
                     arrangers: Sequence[Union[str, Sequence[Union[str, int]]]]
                     ) -> None:
        '''
        设置编曲者
        arrangers Sequence[Union[str, Sequence[Union[str, int]]]] 编曲者数组，如("作者1", "作者2")或(("作者1", 作者1的mid), ("作者2", 作者2的mid))
        '''
        self._setMembers(arrangers, 3)

    def setPostProduction(self,
                          post_production: Sequence[Union[str, Sequence[Union[str, int]]]]
                          ) -> None:
        '''
        设置混音/后期制作者
        post_production Sequence[Union[str, Sequence[Union[str, int]]]] 混音/后期制作者数组，如("作者1", "作者2")或(("作者1", 作者1的mid), ("作者2", 作者2的mid))
        '''
        self._setMembers(post_production, 4)

    def setCoverMaker(self,
                      cover_maker: Sequence[Union[str, Sequence[Union[str, int]]]]
                      ) -> None:
        '''
        设置封面制作者
        cover_maker Sequence[Union[str, Sequence[Union[str, int]]]] 封面制作者数组，如("作者1", "作者2")或(("作者1", 作者1的mid), ("作者2", 作者2的mid))
        '''
        self._setMembers(cover_maker, 6)

    def setSoundSource(self,
                       sound_source: Sequence[Union[str, Sequence[Union[str, int]]]]
                       ) -> None:
        '''
        设置音源(仅洛天依等虚拟歌手需要)
        sound_source Sequence[Union[str, Sequence[Union[str, int]]]] 音源数组，如("作者1", "作者2")或(("作者1", 作者1的mid), ("作者2", 作者2的mid))
        '''
        self._setMembers(sound_source, 7)

    def setTuners(self,
                  tuners: Sequence[Union[str, Sequence[Union[str, int]]]]
                  ) -> None:
        '''
        设置调音师
        tuners Sequence[Union[str, Sequence[Union[str, int]]]] 调音师数组，如("作者1", "作者2")或(("作者1", 作者1的mid), ("作者2", 作者2的mid))
        '''
        self._setMembers(tuners, 8)

    def setInstrumentalists(self,
                            instrumentalists: Sequence[Union[str, Sequence[Union[str, int]]]]
                            ) -> None:
        '''
        设置演奏者
        instrumentalists Sequence[Union[str, Sequence[Union[str, int]]]] 演奏者数组，如("作者1", "作者2")或(("作者1", 作者1的mid), ("作者2", 作者2的mid))
        '''
        self._setMembers(instrumentalists, 9)

    def setInstruments(self,
                       instruments: Sequence[str]
                       ) -> None:
        '''
        设置乐器
        instruments Sequence[str] 乐器数组，如("乐器1", "乐器2")
        '''
        self._setMembers(instruments, 10)

    def addOriginAuthor(self,
                        author: str,
                        mid: int = 0
                        ) -> None:
        '''
        在已有的基础上添加本家作者(类型为翻唱时才需要)
        author str 本家作者名
        mid    int 本家作者id，非B站用户或不提供默认为0
        '''
        self._data["member_with_type"][5].append({"name": author, "mid": mid})

    def setOriginAuthors(self,
                        authors: Sequence[Union[str, Sequence[Union[str, int]]]] 
                        ) -> None:
        '''
        设置本家作者(类型为翻唱时才需要)
        authors Sequence[Union[str, Sequence[Union[str, int]]]]  本家作者数组，如("作者1", "作者2")或(("作者1", 作者1的mid), ("作者2", 作者2的mid))
        '''
        self._setMembers(authors, 5)

    def setOriginTitle(self,
                       title: str
                       ) -> None:
        '''
        添加本家视频标题(类型为翻唱时才需要)
        title str 本家视频标题
        '''
        self._data["origin_title"] = title

    def setOriginUrl(self,
                     url: str
                     ) -> None:
        '''
        添加本家视频url链接(类型为翻唱时才需要)
        url str 本家视频链接
        '''
        self._data["origin_url"] = url

    def setActivityId(self,
                      activity_id: tuple
                      ) -> None:
        '''
        设置音频活动id
        activity_id int 音频稿件可以参加的活动的id
        '''
        self._data["activity_id"] = activity_id

    def addTag(self,
               song_tag: str
               ) -> None:
        '''
        在已有标签的基础上增加标签
        song_tag str 音频标签
        '''
        self._data["song_tags"].append({"tagName":song_tag})

    def setTags(self,
               song_tags: Sequence[str] 
               ) -> None:
        '''
        设置音频标签(覆盖已经设置过的标签)
        song_tags Sequence[str] 音频标签字符串数组
        '''
        self._data["song_tags"] = [{"tagName":song_tag} for song_tag in song_tags]

    def setCreationType(self,
                        creation_type: Union[int, str] 
                        ) -> None:
        '''
        设置音频创作类型，仅音频分类为"音乐"时需要，音频分类为"有声节目"时不需要
        creation_type Union[int, str]  设置创作类型，可提供类型id(整数)或者类型字符串，如"原创"，"翻唱"
        '''
        self._setType(creation_type, "creation_type")

    def setStyleType(self,
                     style_type: Union[int, str] 
                     ) -> None:
        '''
        设置音频风格类型，仅音频分类为"音乐"时需要(不是必选)，音频分类为"有声节目"时不需要
        style_type Union[int, str] 设置风格类型，可提供类型id(整数)或者类型字符串，如"流行"，"古风"
        '''
        self._setType(style_type, "style_type")

    def setThemeType(self,
                     theme_type: Union[int, str]
                     ) -> None:
        '''
        设置音频主题来源，仅音频分类为"音乐"时需要(不是必选)，音频分类为"有声节目"时不需要
        theme_type Union[int, str] 设置主题来源，可提供类型id(整数)或者类型字符串，如"动画"，"游戏"
        '''
        self._setType(theme_type, "theme_type")
    
    def setLanguageType(self,
                        language_type: Union[int, str]
                        ) -> None:
        '''
        设置音频语言，仅音频分类为"音乐"时需要(必选)，音频分类为"有声节目"时不需要
        language_type Union[int, str] 设置语言类型，可提供类型id(整数)或者类型字符串，如"华语"，"日语"
        '''
        self._setType(language_type, "language_type")

    def setMusicType(self,
                     music_type: Union[int, str]
                     ) -> None:
        '''
        设置音频声音类型，本方法会自动设置音频分类为"音乐"或"有声节目"而不提供独立的音频分类设置方法
        music_type Union[int, str] 设置声音类型，可提供类型id(整数)或者类型字符串，如"人声演唱"，"广播剧"
        '''
        id = self._setType(music_type, "music_type")
        if id < 44:
            self._data["cr_type"] = 1
        else:
            self._data["cr_type"] = 2

    def setImage(self,
                 image: str
                 ) -> None:
        '''
        设置音频封面
        image str 封面的本地路径或者url
        '''
        if image.startswith('http'):
            self._data["cover_url"] = image
        elif os.path.isfile(image):
            self._data["cover_url"] = self.uploadImage(image)
        else:
            raise ValueError('image参数必须为图片url或本地图片路径')

    def setLyric(self,
                 lyric: str
                 ) -> None:
        '''
        设置音频歌词
        Lyric str 歌词url或者歌词本地路径或者歌词内容 （若给一个歌词文件路径,必须为utf-8编码）
        '''
        if lyric.startswith('http'):
            self._data["lyric_url"] = lyric
        elif os.path.isfile(lyric):
            with open(lyric, 'r') as fp:
                self._data["lyric_url"] = self.uploadLyric(fp.read())
        else:
            self._data["lyric_url"] = self.uploadLyric(lyric)

    def setAlbumId(self,
                   album_id: int
                   ) -> None:
        '''
        设置歌曲所在专辑id，歌曲发布后自动添加到相应专辑
        album_id int 专辑id
        '''
        self._data["album_id"] = album_id

    def setSongFile(self,
                    filepath: str
                    ) -> None:
        '''
        设置歌曲文件并设置歌曲id(song_id)和标题(title)
        filepath  str  音频路径
        '''
        id, title = self.uploadAudio(filepath)
        self.setSongId(id)
        self.setTitle(title)

    def uploadAudio(self, 
                    filepath: str, 
                    fsize: int = 8388608
                    ) -> tuple:
        '''
        上传本地音频文件,返回歌曲id(song_id)和文件名
        filepath  str  音频路径
        fsize     int  音频分块大小,默认为8388608,没有必要请勿修改
        '''
        path, name = os.path.split(filepath)#分离路径与文件名
        preffix = os.path.splitext(name)[0]
        with open(filepath, 'rb') as f: 
            size = f.seek(0, 2) #获取文件大小
            chunks = math.ceil(size / fsize) #获取分块数量
            retobj = self._api.videoPreupload(name, size, "uga%2Fbup") #申请上传
            auth = retobj["auth"]
            endpoint = retobj["endpoint"]
            biz_id = retobj["biz_id"]
            upos_uri = retobj["upos_uri"][6:]
            url = f'https:{endpoint}{upos_uri}'  #音频上传路径
            upload_id = self._api.videoUploadId(url, auth)["upload_id"] #得到上传id

            #开始上传
            parts = [] #分块信息
            f.seek(0, 0)
            for i in range(chunks): #单线程分块上传，官方支持三线程
                data = f.read(fsize) #一次读取一个分块大小
                self._api.videoUpload(url, auth, upload_id, data, i, chunks, i*fsize, size)#上传分块
                parts.append({"partNumber":i+1,"eTag":"etag"}) #添加分块信息，partNumber从1开始
        
        retobj = self._api.videoUploadInfo(url, auth, parts, name, upload_id, biz_id, "uga%2Fbup")
        assert retobj["OK"] == 1
        return biz_id, preffix

    def uploadImage(self, 
                    filepath: str
                    ) -> str:
        '''
        上传本地图片，返回图片链接，用于音频封面上传
        filepath  str  图片路径
        返回      str  图片url
        '''
        suffix = os.path.splitext(filepath)[-1]
        with open(filepath,'rb') as f:
            code = base64.b64encode(f.read()).decode()
        return self._api.audioImageUpload(f'data:image/{suffix};base64,{code}')["data"]#.replace('http://', 'https://')
        #与bili.videoUpcover方法类似，audio,video,article都有相应的图片上传方法可以通用,不知道B站区分这么仔细干啥

    def uploadLyric(self, 
                    lyric: str
                    ) -> str:
        '''
        上传本地歌词，返回歌词链接，用于设置歌词
        lyric  str  歌词内容
        返回   str  歌词url
        '''
        return self._api.audioLyricUpload(self._data["song_id"], lyric)["data"]#.replace('http://', 'https://')

    def submit(self) -> (int, str):
        '''
        提交音频稿件
        返回 (int, str) 返回音频id和提交信息，若音频id为0则提交失败
        '''
        self._data["create_time"] = int(time.time())
        res = self._api.audioSubmit(self._data)
        if res["code"] == 0:
            return res["data"], res["msg"]
        else:
            return 0, res["msg"]

    def _setMembers(self,
                    members: tuple or list,
                    id: int
                    ) -> None:
        if isinstance(members, tuple) or isinstance(members, list):
            _list = []
            for x in members:
                if isinstance(x, str):
                    _list.append({"name": x, "mid": 0})
                else:
                    _list.append({"name": x[0], "mid": x[1]})
            self._data["member_with_type"][id]["members"] = _list
        else:
            raise ValueError(name+'类型错误，必须使用元组或列表类型的字符串数组')

    def _setType(self,
                 type: int or str,
                 name: str
                 ) -> None:
        id = 0
        if isinstance(type, int):
            id = type
        elif isinstance(type, str):
            for type in self._categories:
                if type in type[1]:
                    id = type[0]
                    break
        if not id:
            raise ValueError(name+'类型错误，请使用正确的类型')
        self._data[name+"_id"] = id
        return id

class CompilationUploader(biliContext):
    '''B站音频合辑上传类'''
    _categories = ((102, '人声演唱'), (103, 'VOCALOID歌手'), (104, '人力鬼畜'), (105, '纯音乐/演奏'), 
                   (106, '原创'), (107, '翻唱/翻奏'), (108, '改编/remix'), (109, '华语'), (110, '日语'), 
                   (111, '英语'), (112, '韩语'), (113, '粤语'), (114, '其他语种'), (115, '动画'), 
                   (116, '游戏'), (117, '影视'), (118, '网络歌曲'), (119, '同人'), (120, '偶像'), 
                   (121, '流行'), (122, '古风'), (123, '摇滚'), (124, '民谣'), (125, '电子'), (126, '舞曲'), 
                   (127, '说唱'), (128, '轻音乐'), (129, '阿卡贝拉'), (130, '爵士'), (131, '乡村'), 
                   (132, 'R&B/Soul'), (133, '古典'), (134, '民族'), (135, '英伦'), (136, '金属'), 
                   (137, '朋克'), (138, '蓝调'), (139, '雷鬼'), (140, '世界音乐'), (141, '拉丁'), 
                   (142, '另类/独立'), (143, 'New Age'), (144, '后摇'), (145, 'Bossa Nova'), (146, '音乐'), 
                   (147, '有声节目'), (148, '广播剧'), (149, '有声故事'), (150, 'ASMR'), (151, '其他')
                   )

    class _audio(object):
        '''B站音频上传信息类'''

        def __init__(self,
                     username: str,
                     uid: int,
                     song_id: int,
                     title: str
                 ):
            self._data = {
                "lyric_url":None,
                "song_id":song_id,
                "title":title,
                "member_with_type":[
                    {"m_type":1,"members":[]},
                    {"m_type":2,"members":[]},
                    {"m_type":3,"members":[]},
                    {"m_type":4,"members":[]},
                    {"m_type":5,"members":[]},
                    {"m_type":6,"members":[]},
                    {"m_type":7,"members":[]},
                    {"m_type":8,"members":[]},
                    {"m_type":9,"members":[]},
                    {"m_type":10,"members":[]},
                    {"m_type":11,"members":[]},
                    {"m_type":127,"members":[{"name":username,"mid":uid}]}],
                "song_tags":[],"mid":uid}

        def setLyricUrl(self,
                        lyric_url: str
                        ) -> None:
            '''
            设置歌词链接
            lyric_url str 歌词链接
            '''
            self._data["lyric_url"] = lyric_url

        @property
        def songId(self) -> int:
            return self._data["song_id"]

        #这里将AudioUploader类的方法导入到本类
        setSongId = AudioUploader.setSongId
        setTitle = AudioUploader.setTitle
        addTag = AudioUploader.addTag
        setTags = AudioUploader.setTags
        setSingers = AudioUploader.setSingers
        setLyricist = AudioUploader.setLyricist
        setComposers = AudioUploader.setComposers
        setArrangers = AudioUploader.setArrangers
        setPostProduction = AudioUploader.setPostProduction
        setCoverMaker = AudioUploader.setCoverMaker
        setSoundSource = AudioUploader.setSoundSource
        setTuners = AudioUploader.setTuners
        setInstrumentalists = AudioUploader.setInstrumentalists
        setInstruments = AudioUploader.setInstruments
        setOriginAuthors = AudioUploader.setOriginAuthors
        _setMembers = AudioUploader._setMembers

    def __init__(self,
                 biliapi: bili
                 ):
        '''
        biliapi   bili  B站接口对象实例
        '''
        super(CompilationUploader, self).__init__(biliapi)

        self._data = {
            "cover_url":"",
            "intro":"",
            "is_synch":1,
            "song_counts":0,
            "song_ids":[],
            "dict_items":[],
            "title":""
            }

    def createAudio(self,
                    audio_path: str,
                    lyric: str = None
                    ) -> _audio:
        '''
        上传音频文件，创建一个音频
        audio_path str 音频文件路径
        lyric str 歌词文件路径或者歌词内容字符串
        返回 音频对象
        '''
        song_id, title = AudioUploader.uploadAudio(self, filepath)
        audio = self._audio(self._api._name, self._api._uid, song_id, title)
        if lyric:
            self.addLyricToAudio(audio, lyric)
        return audio

    def addLyricToAudio(self,
                        audio: _audio,
                        lyric: str
                        ) -> None:
        '''
        在音频上添加歌词
        audio 由createAudio方法返回的音频 
        lyric str 歌词文件路径或者歌词内容字符串
        '''
        if os.path.isfile(lyric):
            with open(lyric, 'r') as fp:
                lyric = self._api.audioLyricUpload(song_id, fp.read())["data"]
        else:
            lyric = self._api.audioLyricUpload(song_id, lyric)["data"]
        audio.setLyricUrl(lyric)

    def addAudioWithCommit(self,
                           audio: _audio
                           ) -> str:
        '''
        将单个音频添加到本合辑，音频会立即提交审核
        audios 由createAudio方法返回的音频构成的数组
        返回 str 提交信息，为None则提交成功，否则为错误信息字符串
        '''
        res = self._api.audioCompilationSongSubmit(audio._data)
        if res["code"] == 0:
            self._data["song_ids"].append(audio.songId)
            return None
        else:
            return res["msg"]

    def setAudiosWithCommit(self,
                            audios: list
                            ) -> list:
        '''
        将多个音频添加到本合辑(会删除已经添加到本合辑的音频)，音频会立即提交审核
        audio 由createAudio方法返回的音频
        返回 list 提交信息列表，为None则对应音频提交成功，否则为错误信息字符串
        '''
        ids_list = []
        ret_list = []
        for audio in audios:
            res = self._api.audioCompilationSongSubmit(audio._data)
            if res["code"] == 0:
                ids_list.append(audio.songId)
                ret_list.append(None)
            else:
                ret_list.append(res["msg"])
        self._data["song_ids"] = ids_list
        return ret_list

    def addType(self,
                type: Union[int, str]
                ) -> None:
        '''
        添加合辑音频类型
        type Union[int, str] 音频类型id(整数)或音频字符串 如105与"纯音乐"等价,123与"摇滚"等价
        '''
        if isinstance(type, str):
            for _type in self._categories:
                if type in _type[1]:
                    self._data["dict_items"].append({"type_id":_type[0],"type_name":_type[1]})
                    break
        elif isinstance(type, int):
            for _type in self._categories:
                if type == _type[0]:
                    self._data["dict_items"].append({"type_id":_type[0],"type_name":_type[1]})
                    break
        else:
            raise ValueError('type类型必须为整数或字符串')

    def setTypes(self,
                types: Sequence[Union[int, str]]
                ) -> None:
        '''
        设置合辑音频类型(删除已设置类型)
        types Sequence[Union[int, str]] 音频类型列表，每个音频类型为整数或字符串
        '''
        items = []
        for type in types:
            if isinstance(type, str):
                for _type in self._categories:
                    if type in _type[1]:
                        items.append({"type_id":_type[0],"type_name":_type[1]})
                        break
            elif isinstance(type, int):
                for _type in self._categories:
                    if type == _type[0]:
                        items.append({"type_id":_type[0],"type_name":_type[1]})
                        break
            else:
                raise ValueError('type类型必须为整数或字符串')
        self._data["dict_items"] = items

    def submit(self) -> (int, str):
        '''
        提交音频合辑
        返回 (int, str) 返回合辑id和提交信息，若合辑id为0则提交失败
        '''
        self._data["song_counts"] = len(self._data["song_ids"])
        res = self._api.audioCompilationSubmit(self._data)
        if res["code"] == 0:
            return res["data"], res["msg"]
        else:
            return 0, res["msg"]

    #这里将AudioUploader类的方法导入到本类
    setIntro = AudioUploader.setIntro
    setTitle = AudioUploader.setTitle
    uploadImage = AudioUploader.uploadImage
    setImage = AudioUploader.setImage