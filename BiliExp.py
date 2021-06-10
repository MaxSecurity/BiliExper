# -*- coding: utf-8 -*-
import asyncio, time, logging, sys, io, os
import encodings.idna
from importlib import import_module
from collections import OrderedDict
from getopt import getopt
from BiliClient import asyncbili
import tasks
try:
    from json5 import loads
except:
    from json import loads

main_version = (1, 2, 1)
main_version_str = '.'.join(map(str, main_version))

def version_compare(version: str):
    ver = tuple(map(int, version.strip().split('.')))
    for ii in range(len(main_version)):
        if ver[ii] < main_version[ii]:
            return False
    return True

def initlog(log_file: str, log_console: bool, msg_raw: bool = False):
    '''初始化日志参数'''
    logger_raw = logging.getLogger()
    logger_raw.setLevel(logging.INFO)
    formatter1 = logging.Formatter("[%(levelname)s]: %(message)s")
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')#输出到日志文件
            file_handler.setFormatter(formatter1)
            logger_raw.addHandler(file_handler)
        except:
            ...
    if log_console:
        console_handler = logging.StreamHandler(stream=sys.stdout) #输出到控制台
        console_handler.setFormatter(formatter1)
        logger_raw.addHandler(console_handler)
    formatter2 = logging.Formatter("%(message)s")
    if msg_raw:
        log_raw = io.StringIO() #用于记录完整日志
        strio_handler = logging.StreamHandler(stream=log_raw) #输出到log_raw用于消息推送
        strio_handler.setFormatter(formatter2)
        logger_raw.addHandler(strio_handler)
        return log_raw
    return None

def init_message(configData: dict):
    '''初始化消息推送'''
    if 'webhook' in configData and 'variable' in configData["webhook"]:
        tasks.webhook.set(configData["webhook"])
        if 'msg_raw' in configData["webhook"]["variable"]:
            log_raw = initlog(configData["log_file"], configData["log_console"], True)
            tasks.webhook.addMsgStream('msg_raw', log_raw)
        else:
            initlog(configData["log_file"], configData["log_console"])
        if 'msg_simple' in configData["webhook"]["variable"]:
            tasks.webhook.addMsgStream('msg_simple')
    else:
        initlog(configData["log_file"], configData["log_console"])

def load_config(path: str) -> OrderedDict:
    '''加载配置文件'''
    if path:
        with open(path,'r',encoding='utf-8') as fp:
            return loads(fp.read(), object_pairs_hook=OrderedDict)
    else:
        for path in ('./config/config.json', './config.json', '/etc/BiliExp/config.json'):
            if os.path.exists(path):
                with open(path,'r',encoding='utf-8') as fp:
                    return loads(fp.read(), object_pairs_hook=OrderedDict)
        raise RuntimeError('未找到配置文件')

async def start(configData: dict):
    '''开始任务'''
    config_version = configData.get('version', '1.0.0')
    if version_compare(config_version):
        logging.info(f'当前程序版本为v{main_version_str},配置文件版本为v{config_version}')
    else:
        logging.warning(f'当前程序版本为v{main_version_str},配置文件版本为v{config_version},可更新配置文件')
        tasks.webhook.addMsg('msg_simple', '有新版本配置文件可供使用\n')
    
    await asyncio.wait([run_user_tasks(user, configData["default"]) for user in configData["users"]]) #执行任务
    await tasks.webhook.send() #推送消息

async def run_user_tasks(user: dict,           #用户配置
                         default: dict          #默认配置
                         ) -> None:
    async with asyncbili() as biliapi:
        try:
            if not await biliapi.login_by_cookie(user["cookieDatas"]):
                logging.warning(f'id为{user["cookieDatas"]["DedeUserID"]}的账户cookie失效，跳过此账户后续操作')
                tasks.webhook.addMsg('msg_simple', f'id为{user["cookieDatas"]["DedeUserID"]}的账户cookie失效\n')
                return
        except Exception as e: 
            logging.warning(f'登录验证id为{user["cookieDatas"]["DedeUserID"]}的账户失败，原因为{str(e)}，跳过此账户后续操作')
            return

        show_name = user.get("show_name", "")
        if show_name:
            biliapi.name = show_name

        logging.info(f'{biliapi.name}: 等级{biliapi.level},经验{biliapi.myexp},剩余硬币{biliapi.mycoin}')
        tasks.webhook.addMsg('msg_simple', f'{biliapi.name}: 等级{biliapi.level},经验{biliapi.myexp},剩余硬币{biliapi.mycoin}\n')

        task_array = [] #存放本账户所有任务

        for task in default: #遍历任务列表，把需要运行的任务添加到task_array

            try:
                task_module = import_module(f'tasks.{task}') #加载任务模块
            except ModuleNotFoundError:
                logging.error(f'{biliapi.name}: 未找到任务模块{task}')
                continue

            task_function = getattr(task_module, task, None)
            if not task_function:
                logging.error(f'{biliapi.name}: 未找到任务{task}的入口函数')
                continue

            if task in user["tasks"]:
                if isinstance(user["tasks"][task], bool):
                    if user["tasks"][task]:
                        task_array.append(task_function(biliapi))
                elif isinstance(user["tasks"][task], dict):
                    if 'enable' in user["tasks"][task] and user["tasks"][task]["enable"]:
                        task_array.append(task_function(biliapi, user["tasks"][task]))
            else:
                if isinstance(default[task], bool):
                    if default[task]:
                        task_array.append(task_function(biliapi))
                elif isinstance(default[task], dict):
                    if 'enable' in default[task] and default[task]["enable"]:
                        task_array.append(task_function(biliapi, default[task]))

        if task_array:
            await asyncio.wait(task_array)        #异步等待所有任务完成

def main(*args, **kwargs):
    try:
        configData = load_config(kwargs.get("config", None))
    except Exception as e: 
        print(f'配置加载异常，原因为{str(e)}，退出程序')
        sys.exit(6)

    if 'log' in kwargs:
        configData["log_file"] = kwargs["log"]

    init_message(configData) #初始化消息推送

    #启动任务
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start(configData))



if __name__=="__main__":
    kwargs = {}
    opts, args = getopt(sys.argv[1:], "hvc:l:",["configfile=","logfile="])
    for opt, arg in opts:
        if opt in ('-c','--configfile'):
            kwargs["config"] = arg
        elif opt in ('-l','--logfile'):
            kwargs["log"] = arg
        elif opt == '-h':
            print('BliExp -c <configfile> -l <logfile>')
            sys.exit()
        elif opt == '-v':
            print(f'BiliExp v{main_version_str}')
            sys.exit()
while True: #死循环 每一个小时运行一次配置
    main(**kwargs)
    time.sleep(3600)

# while True: #每天某个时间段运行配置
#     time_now = time.strftime("%H:%M:%S", time.localtime()) # 刷新
#     if time_now == "11:30:00": #此处设置每天定时的时间
#         main(**kwargs)
#         time.sleep(2) # 因为以秒定时，所以暂停2秒，使之不会在1秒内执行多次