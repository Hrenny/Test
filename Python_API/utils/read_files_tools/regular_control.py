import re

from utils.logging_tool.log_control import ERROR


class Context:
    @classmethod
    def host(cls):
        from utils import config
        return config.host

def regular(target):
    """使用正则替换请求数据"""
    try:
        regular_patten = r'\${{(.*?)}}'
        while re.findall(regular_patten, target):
            key = re.search(regular_patten, target).group(1)
            value_types = ['int:', 'bool:', 'list:', 'dict:', 'tuple:', 'float:']
            if any(i in key for i in value_types) is True:
                func_name = key.split(":")[1].split("(")[0]
                value_name = key.split(":")[1].split("(")[1][:-1]
                if value_name == "":
                    value_data = getattr(Context, func_name)()
                else:
                    value_data = getattr(Context, func_name)(*value_name.split(","))
                regular_int_pattern = r'\'\${{(.*?)}}\''
                target = re.sub(regular_int_pattern, str(value_data), target, 1)
            else:
                func_name = key.split('(')[0]
                value_name = key.split('(')[1][-1]
                if value_name == "":
                    value_data = getattr(Context(), func_name)()
                else:
                    value_data = getattr(Context(), func_name)(*value_name.split(","))
                target = re.sub(regular_patten, str(value_data), target, 1)
        return target

    except AttributeError:
        ERROR.logger.error('未找到对应的替换数据，请检查数据是否正确%s', target)
        raise
    except IndexError:
        ERROR.logger.error('yaml中的${{}}函数方法不正确,正确语法实例：${{get_time()}}')
        raise


if __name__ == '__main__':
    a = '${{host()}} aaa'
    b = regular(a)