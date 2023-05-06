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
        self.logger = logging.getLogger(filename)
        formatter = self.log_color()
        # 设置日志格式
        format_str = logging.Formatter(fmt)
        # 设置日志级别
        self.logger.setLevel(self.level_relations.get(level))
        # 控制台输出
        screen_output = logging.StreamHandler()
        # 设置控制台显示的格式
        screen_output.setFormatter(formatter)
        time_rotating = handlers.TimedRotatingFileHandler(
            filename=filename,
            when=when,
            backupCount=3,
            encoding='utf-8'
        )
        # 设置写入文件格式
        time_rotating.setFormatter(format_str)
        self.logger.addHandler(screen_output)
        self.logger.addHandler(time_rotating)
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
        formatter =  colorlog.ColoredFormatter(
            '%(log_color)s[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s',
            log_colors = log_colors_config
        )
        return formatter


now_time_day = time.strftime('%Y-%m-%d', time.localtime())
INFO = LogHandler(ensure_path_sep(f'\\logs\\info-{now_time_day}.log'), level='info')
ERROR = LogHandler(ensure_path_sep(f'\\logs\\error-{now_time_day}.log'), level='error')
WARNING = LogHandler(ensure_path_sep(f'\\logs\\waring-{now_time_day}.log'))

if __name__ == '__main__':
    ERROR.logger.error('测试')