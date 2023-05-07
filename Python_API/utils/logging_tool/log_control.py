import logging
import time
from logging import handlers
from typing import Text
import colorlog
from common.setting import ensure_path_sep


class LogHandler:
    """日志封装打印封装"""
    # 日志级别关系映射
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    def __init__(self,
                 filename: Text,
                 level: Text = 'info',
                 when: Text = 'D',
                 fmt: Text = '%(levelname)-8s%(asctime)s%(name)s:%(filename)s:%(lineno)d %(message)s'):
        """
        filename: 日志文件名
        level: 日志记录级别
        when: 日志文件的切割时间
        fmt: 日志记录格式
        """
        # 创建日志记录器
        self.logger = logging.getLogger(filename)
        # 日志颜色
        formatter = self.log_color()
        # 设置日志格式
        format_str = logging.Formatter(fmt)
        # 设置日志级别
        self.logger.setLevel(self.level_relations.get(level))
        # 控制台输出
        screen_output = logging.StreamHandler()
        # 设置控制台显示的格式
        screen_output.setFormatter(formatter)
        """
        创建定时轮换日志文件的处理器对象
        filename: 日志文件的路径和文件名
        when: 日志文件的轮换时间间隔
        backupCount: 保留的旧日志文件数
        encoding: 日志文件编码格式
        """
        time_rotating = handlers.TimedRotatingFileHandler(
            filename=filename,
            when=when,
            backupCount=3,
            encoding='utf-8'
        )
        # 设置写入文件格式
        time_rotating.setFormatter(format_str)
        # 添加到日志记录器中
        self.logger.addHandler(screen_output)
        self.logger.addHandler(time_rotating)
        # 调用函数拼接路径
        self.log_path = ensure_path_sep('\\logs\\log.log')

    @classmethod
    def log_color(cls):
        """设置日志颜色"""
        log_colors_config = {
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red'
        }
        # 创建日志格式化对象，格式化日志输出内容
        formatter = colorlog.ColoredFormatter(
            '%(log_color)s[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s',
            log_colors=log_colors_config
        )
        return formatter


# 获取当前时间
now_time_day = time.strftime('%Y-%m-%d', time.localtime())
# 定义日志处理器对象，记录不同级别的日志信息
INFO = LogHandler(ensure_path_sep(f'\\logs\\info-{now_time_day}.log'), level='info')
ERROR = LogHandler(ensure_path_sep(f'\\logs\\error-{now_time_day}.log'), level='error')
WARNING = LogHandler(ensure_path_sep(f'\\logs\\waring-{now_time_day}.log'))