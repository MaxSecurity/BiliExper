__version__ = '1.2.0'
__author__ = '星辰(happy888888)'

__all__ = tuple()

from importlib import import_module
from importlib.util import find_spec
_global = globals()   #本文件的命名空间，存放本文件内所有变量

if find_spec('.asyncBiliApi', __name__):
    from .asyncBiliApi import asyncBiliApi as asyncbili #B站接口模块，由aiohttp模块实现异步http请求
    __all__ += ('asyncbili',)
    for moudle_name in ('asyncXliveWs',                  #这些模块依赖于异步接口模块
                        ):
        if find_spec('.' + moudle_name, __name__):
            moudle = import_module('.' + moudle_name, __name__)   #__name__为py内置变量，指代本模块的名字str，这里通过名字加载模块
            for class_name in moudle.__all__:
                _global[class_name] = getattr(moudle, class_name) #将模块下的类加载到本文件的命名空间
            __all__ += moudle.__all__

if find_spec('.BiliApi', __name__):
    from .BiliApi import BiliApi as bili                #B站接口模块，由requests模块实现同步http请求
    __all__ += ('bili',)
    for moudle_name in ('Manga',                        #这些模块依赖于同步接口模块
                        'Video',
                        'Downloader',
                        'Article',
                        'Danmu2Ass',
                        'Audio',
                        ):
        if find_spec('.' + moudle_name, __name__):
            moudle = import_module('.' + moudle_name, __name__)   #__name__为py内置变量，指代本模块的名字str，这里通过名字加载模块
            for class_name in moudle.__all__:
                _global[class_name] = getattr(moudle, class_name) #将模块下的类加载到本文件的命名空间
            __all__ += moudle.__all__