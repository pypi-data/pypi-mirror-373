import inspect
import os
import platform
import socket
import sys
import time

from loguru import logger

# from utils.log_context import CURRENT_UID, REQUEST_ID

APP_NAME = "digitalHuman"
IS_SERVER = platform.system().lower() == "linux"
ENV_IDC = socket.gethostname() in ["VM-2-35-tencentos"]


def creat_time_os():
    creat_time = time.strftime("%Y-%m-%d", time.localtime())

    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    log_path_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    logs_path = os.path.join(log_path_dir, "logs", creat_time)
    if os.path.exists(logs_path):
        return logs_path
    else:
        try:
            os.makedirs(logs_path)
        except Exception as e:
            print(e)
        return logs_path


def get_log_file_path():
    if IS_SERVER:
        creat_time_str = time.strftime("%Y-%m-%d", time.localtime())
        dir = f"/usr/local/yunji/logs/{APP_NAME}/"
        if not os.path.exists(dir):
            os.makedirs(dir)
        log_file_path = os.path.join(dir, f"{APP_NAME}_{creat_time_str}.log")
    else:
        # 输出到文件，并按天分割和压缩
        logs_path = creat_time_os()
        # 日志文件名：由用例脚本的名称，结合日志保存路径，得到日志文件的绝对路径
        log_file_path = os.path.join(logs_path, sys.argv[0].split('/')[-1].split('.')[0]) + '.log'

    return log_file_path


# 提供日志功能
class uru_logger:
    # 去除默认控制台输出
    # logger.remove()

    # 输出日志格式

    def __init__(self):
        # logger_format = "{time:YYYY-MM-DD HH:mm:ss,SSS} | {level} | [{thread}]| {message}"
        # ES能够正常解析的日志格式
        if ENV_IDC:
            logger_format = "[{time:YYYY-MM-DD HH:mm:ss.SSS}] [{level}] [idc] {message}"  # thread:"idc"线上标记
        else:
            logger_format = "[{time:YYYY-MM-DD HH:mm:ss.SSS}] [{level}] [{thread.name}] {message}"
        logger.remove()  # 这里是不让他重复打印
        logger.add(sys.stderr,  # 这里是不让他重复打印
                   level="DEBUG",
                   format=logger_format
                   )
        file_log_level = "INFO" if ENV_IDC else "DEBUG"
        logger.add(
            get_log_file_path(),
            encoding="utf-8",
            format=logger_format,
            level=file_log_level,
            rotation="500MB",
            retention="5 days",
            # colorize=True,
            compression="zip")
        self.creat_time = time.strftime("%Y-%m-%d", time.localtime())
        self.log = logger

    def check_format(self):
        if time.strftime("%Y-%m-%d", time.localtime()) != self.creat_time:
            self.__init__()


uru_logger_log = uru_logger()


def log_info(*args):
    '''
    info log信息
    :param message:
    :return:
    '''
    uru_logger_log.check_format()
    _log('info', *args)


def log_debug(*args):
    '''
    debug log信息
    :param message:
    :return:
    '''
    uru_logger_log.check_format()
    _log('debug', *args)


def log_error(*args):
    '''
    error log信息
    :param message:
    :return:
    '''
    uru_logger_log.check_format()
    _log('error', *args)


def log_warning(*args):
    '''
    error warning信息
    :param message:
    :return:
    '''
    uru_logger_log.check_format()
    _log('warning', *args)


def _get_caller_info():
    # 获取上一帧的信息
    frame = inspect.stack()[3]
    # 解析文件名，行号，函数名
    module = inspect.getmodule(frame[0])
    # filename = os.path.basename(frame.filename)
    lineno = frame.lineno
    function_name = frame.function
    module_name = ""
    if module:
        module_name = module.__name__
    if IS_SERVER:  # ES日志不带行号
        return f"{module_name}.{function_name}"
    else:
        return f"{module_name}.{function_name}:{lineno}"


def _log(level, *args):
    caller_info = _get_caller_info()
    msg = ' '.join(map(str, args))
    # uid = CURRENT_UID.get()
    uid_str = ""
    request_id = ""
    # if uid:
    #     uid_str = f"[uid:{uid}]"
    # request_id = REQUEST_ID.get() or ""
    full_msg = f"[{caller_info}] - [t: s: p:{request_id}] {uid_str}{msg}"  # traceId: spanId: pSpanId:
    getattr(uru_logger_log.log, level)(full_msg)


def log_test():
    log_debug("click start")
    log_info({"uid": "123", "event": "click"})
    log_error("request fail")
    log_warning("now warning")


if __name__ == '__main__':
    log_test()
    print(get_log_file_path())
