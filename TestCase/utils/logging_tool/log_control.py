"""
日志封装，可设置不同等级的日志颜色
"""
import logging
from logging import handlers
from typing import Text
import colorlog
import time
from common.setting import ensure_path_sep


class LogHandler:
    """日志打印封装"""
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
        :param filename:
        :param level:
        :param when:
        :param fmt: %(asctime)s:日志事件发生的时间
                    %(levelname)s:该日志记录的日志级别
                    %(message)s:日志记录的文本内容
                    %(name)s:所使用的日志器名称
                    %(pathname)s:调用日志记录函数的文件的全路径
                    %(filename)s:调用日志记录函数的文件
                    %(funcName)s:调用日志记录函数的函数名
                    %(lineo)d:调用日志记录函数的代码所在的行号
        """
        self.logger = logging.getLogger(filename)
        formatter_color = self.log_color()
        # 设置日志格式
        format_str = logging.Formatter(fmt)
        # 设置日志级别
        self.logger.setLevel(self.level_relations.get(level))
        # 往屏幕上输出
        screen_output = logging.StreamHandler()
        # 设置屏幕上显示的格式
        screen_output.setFormatter(formatter_color)
        # 往文件中写入 指定间隔时间自动生成文件的处理器
        time_rotating = handlers.TimedRotatingFileHandler(
            filename=filename,
            when=when,
            backupCount=3,
            encoding='utf-8'
        )
        # 设置文件里写入的格式
        time_rotating.setFormatter(format_str)
        # 把对象加到logger中
        self.logger.addHandler(screen_output)
        self.logger.addHandler(time_rotating)
        self.log_path = ensure_path_sep('\\logs\\logs.logs')


    @classmethod
    def log_color(cls):
        """设置日志颜色"""
        log_colors_config = {
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        }
        formatter_color = colorlog.ColoredFormatter(
            '%(log_color)s[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s',
            log_colors=log_colors_config
        )
        return formatter_color


now_time_day = time.strftime('%Y-%m-%d', time.localtime())
INFO = LogHandler(ensure_path_sep(f'\\logs\\info-{now_time_day}.logs'), level='info')
ERROR = LogHandler(ensure_path_sep(f'\\logs\\error-{now_time_day}.logs'), level='error')
WARNING = LogHandler(ensure_path_sep(f'\\logs\\warning-{now_time_day}.logs'))

if __name__ == '__main__':
    ERROR.logger.error('测试')