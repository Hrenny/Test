import ast
from functools import wraps

from utils.logging_tool.log_control import INFO, ERROR
from utils.read_files_tools.regular_control import cache_regular


def log_decorator(switch: bool):
    """
    封装日志装饰器，打印请求详细
    :param switch: 日志开关
    :return:
    """
    def decorator(func):
        @wraps(func)  # 保留函数的信息
        def swapper(*args, **kwargs):
            # 判断日志为开启状态，才打印日志
            res = func(*args, **kwargs)
            # 判断日志开关为开启状态
            if switch:
                _log_msg = f"\n======================================================\n" \
                               f"用例标题: {res.detail}\n" \
                               f"请求路径: {res.url}\n" \
                               f"请求方式: {res.method}\n" \
                               f"请求头:   {res.headers}\n" \
                               f"请求内容: {res.request_body}\n" \
                               f"接口响应内容: {res.response_data}\n" \
                               f"接口响应时长: {res.res_time} ms\n" \
                               f"Http状态码: {res.status_code}\n" \
                               "====================================================="
                # 将数据转换成合法类型
                _is_run = ast.literal_eval(cache_regular(str(res.is_run)))
                # 判断日志开关打开或者为空，并且响应成功
                if _is_run in (True, None) and res.status_code == 200:
                    INFO.logger.info(_log_msg)
                else:
                    ERROR.logger.error(_log_msg)
            return res
        return swapper
    return decorator