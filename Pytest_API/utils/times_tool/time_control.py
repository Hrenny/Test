import time


def now_time():
    """获取当前时间"""
    localtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    return localtime