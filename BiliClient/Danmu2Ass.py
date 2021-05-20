
__all__ = (
    'Danmu2Ass',
)

from xml.dom.minidom import parse, parseString, Element
from _io import FileIO

class Danmu2Ass:
    '''弹幕转ass类'''
    ass_head = '''[Script Info]
ScriptType: v4.00+
Collisions: Normal
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Danmu, Microsoft YaHei, 64, &H00FFFFFF, &H00FFFFFF, &H00000000, &H00000000, 0, 0, 0, 0, 100, 100, 0.00, 0.00, 1, 1, 0, 2, 20, 20, 20, 0

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    class Danmu:
        def __init__(self,
                     content: str,
                     time: float,
                     type: int,
                     fontsize: int,
                     coler: int
                     ):
            '''
            content  str   弹幕内容
            time     float 弹幕在视频中出现时间(秒)
            type     int   弹幕类型
            fontsize int   字体大小
            coler    int   十进制颜色
            '''
            self._content = content
            self._time = time
            self._type = type
            self._fontsize = fontsize
            self._coler = f'{coler:06x}' #转换成16进制字符串,字符串长度为6
            self._coler = self._coler[4:6] + self._coler[2:4] + self._coler[0:2] #高位在后,低位在前

        def toDialogue(self, 
                       pos_y: int = 0
                       ) -> str:
            '''
            弹幕转换为ass字幕对话
            pos_y int 字幕纵坐标偏移，滚动弹幕和顶部弹幕为到顶部的距离，底部弹幕为到底部的距离
            '''
            length = len(self)
            size = 32
            if self.type == 1: #滚动弹幕，没有2和3....
                return fr'Dialogue: 3,{self.timeFormat(self.time)},{self.timeFormat(self.time+13)},Danmu,,0000,0000,0000,,{{\move({1920+length*size}, {pos_y}, -{length*size}, {pos_y})\c&H{self.coler}\3c&HFFFFFF}}{self.content}'
            elif self.type == 5: #顶部弹幕
                return fr'Dialogue: 3,{self.timeFormat(self.time)},{self.timeFormat(self.time+4)},Danmu,,0000,0000,0000,,{{\a6\pos(960, {pos_y})\c&H{self.coler}\3c&HFFFFFF}}{self.content}'
            elif self.type == 4: #底部弹幕
                return fr'Dialogue: 3,{self.timeFormat(self.time)},{self.timeFormat(self.time+4)},Danmu,,0000,0000,0000,,{{\a6\pos(960, {1080-pos_y})\c&H{self.coler}\3c&HFFFFFF}}{self.content}'
            elif self.type == 6: #逆向弹幕
                return fr'Dialogue: 3,{self.timeFormat(self.time)},{self.timeFormat(self.time+13)},Danmu,,0000,0000,0000,,{{\move(-{length*size}, {pos_y}, {1920+length*size}, {pos_y})\c&H{self.coler}\3c&HFFFFFF}}{self.content}'
            elif self.type == 7: #精准定位弹幕，暂未实现
                ...
            elif self.type == 8: #高级弹幕，暂未实现
                ...
            return ''

        @property
        def content(self) -> str:
            return self._content

        @property
        def time(self) -> float:
            return self._time

        @property
        def type(self) -> int:
            return self._type

        @property
        def fontsize(self) -> int:
            return self._fontsize

        @property
        def coler(self) -> float:
            return self._coler

        @staticmethod
        def timeFormat(time: float) -> str:
            h = int(time // 3600)
            m = int(time % 3600 // 60)
            s = time - 3600 * h - 60 * m
            return f'{h}:{m}:{s:05.2f}'

        def __len__(self) -> int:
            return len(self._content)

    def __init__(self, 
                 xml_str:str = None,
                 xml_file:FileIO or str = None
                 ):
        '''
        xml_str  str           B站弹幕xml格式字符串
        xml_file FileIO or str B站弹幕xml格式文件对象或文件路径
        '''
        if xml_str:
            danmus = parseString(xml_str).documentElement.getElementsByTagName("d")
        elif xml_file:
            danmus = parse(xml_file).documentElement.getElementsByTagName("d")
        else:
            raise ValueError('xml_str与xml_file至少提供一个')
        self._danmus = []
        for dm in danmus:
            attrs = tuple(dm.getAttribute("p").split(','))
            self._danmus.append(Danmu2Ass.Danmu(dm.childNodes[0].data,
                                                 float(attrs[0]),
                                                 int(attrs[1]),
                                                 int(attrs[2]),
                                                 int(attrs[3]),
                                                 ))
        self._danmus.sort(key=lambda x:x.time)

    def toAssFile(self, 
              ass_file: FileIO or str
              ) -> None:
        '''
        将当前弹幕转换并输出到ass文件
        xml_file FileIO or str ass格式文件对象或文件路径
        '''
        own = False
        if isinstance(ass_file, str):
            own = True
            fp = open(ass_file, 'w', encoding='utf-8')
        elif isinstance(ass_file, FileIO):
            fp = ass_file
        else:
            raise ValueError('参数必须为文件路径字符串或FileIO')

        fp.write(Danmu2Ass.ass_head)
        for danmu in self._dialogue_generator():
            fp.write(danmu)
            fp.write('\n')

        if own and fp:
            fp.close()

    def toAss(self) -> str:
        '''将当前弹幕转换成ass格式'''
        dm = Danmu2Ass.ass_head
        dm += '\n'.join(self._dialogue_generator())
        return dm

    def _dialogue_generator(self):
        pos_y = [64, 64, 64]
        for danmu in self._danmus:
            if danmu.type == 1:
                yield danmu.toDialogue(pos_y[0])
                if pos_y[0] > 700:
                    pos_y[0] = 0
                pos_y[0] += 64
            elif danmu.type == 4:
                yield danmu.toDialogue(pos_y[1])
                if pos_y[1] > 400:
                    pos_y[1] = 0
                pos_y[1] += 64
            elif danmu.type == 5:
                yield danmu.toDialogue(pos_y[2])
                if pos_y[2] > 400:
                    pos_y[2] = 0
                pos_y[2] += 64