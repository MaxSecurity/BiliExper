__version__ = '1.2.1'
__author__ = '星辰(happy888888)'

__all__ = tuple()

from importlib import import_module
from importlib.util import find_spec
from typing import Union, Mapping, Sequence
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

    class biliContext(object):
        '''B站接口上下文基类，通过继承本类实现python上下文协议'''

        def __init__(self,
                     params: Union[bili, Union[Mapping[str, str], Sequence[Mapping[str, str]]], None] = None
                     ):
            '''
            params        dict  包含cookie或(access_token和refresh_token)或(username+password)的字典
            params        bili  B站接口对象实例
            params        None  缺省
            '''
            if isinstance(params, bili):
                self._api = params
                self._owner = False
                return

            self._api = bili()
            self._owner = True

            if not params:
                return

            if isinstance(params, Mapping):
                self._api = bili()
                if 'SESSDATA' in params:
                    if not self._api.login_by_cookie(params):
                        self.close()
                        raise ValueError('cookie无效')
                elif 'access_token' in params and 'refresh_token' in params:
                    if not self._api.login_by_access_token(params["access_token"], params["refresh_token"], True):
                        self.close()
                        raise ValueError('access_token或refresh_token无效')
                elif 'username' in params and 'password' in params:
                    if not self._api.login_by_password(params["username"], params["password"]):
                        self.close()
                        raise ValueError('username或password无效')
                else:
                    self.close()
                    raise ValueError('传入的字典不包含登录信息')
            elif isinstance(params, Sequence):
                if not self._api.login_by_cookie(params):
                    self.close()
                    raise ValueError('cookie无效')
            else:
                raise ValueError('未包含合法的登录信息')

        def close(self):
            '''关闭'''
            if self._owner:
                self._owner = False
                self._api.close()

        def __del__(self):
            self.close()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.close()

    for moudle_name in ('Manga',                        #这些模块依赖于同步接口模块
                        'Video',
                        'Downloader',
                        'Article',
                        'Dynamic',
                        'Danmu2Ass',
                        'Audio',
                        ):
        if find_spec('.' + moudle_name, __name__):
            moudle = import_module('.' + moudle_name, __name__)   #__name__为py内置变量，指代本模块的名字str，这里通过名字加载模块
            for class_name in moudle.__all__:
                _global[class_name] = getattr(moudle, class_name) #将模块下的类加载到本文件的命名空间
            __all__ += moudle.__all__