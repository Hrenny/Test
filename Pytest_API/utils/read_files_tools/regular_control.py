import re
from jsonpath import jsonpath
from utils.cache_control.cache_control import CacheHandler
from utils.logging_tool.log_control import ERROR


class Context:
    @classmethod
    def host(cls):
        """返回url"""
        from utils import config
        return config.host


def sql_json(js_path, res):
    """
    提取sql中的json数据
    :param js_path: json的路径
    :param res: json的响应数据
    :return:
    """
    # 查询json的路径
    _json_data = jsonpath(res, js_path)[0]
    # 判断是否查询失败
    if _json_data is False:
        raise ValueError(f'sql中的jsonpath获取失败{res}, {js_path}')
    return _json_data


def sql_regular(value, res=None):
    """处理sql中的依赖数据，通过获取接口响应的jsonpath的值进行替换"""
    # 查找所有与正则匹配的值
    sql_json_list = re.findall(r'\$json\((.*?)\)\$', value)
    # 遍历列表
    for i in sql_json_list:
        # 编译正则表达式对象
        pattern = re.compile(r'\$json\(' + i.replace('$', '\$').replace('[', '\[') + r'\)\$')
        # 获取jsonpath值
        key = str(sql_json(i, res))
        # value匹配到的字符串，替换成key
        value = re.sub(pattern, key, value, count=1)
    return value


def cache_regular(value):
    """通过正则的方式，读取缓存中的内容"""
    # 正则匹配，返回列表
    regular_dates = re.findall(r'\$cache\{(.*?)\}', value)
    # 遍历列表
    for regular_data in regular_dates:
        value_types = ['int:', 'bool:', 'list:', 'dict:', 'tuple:', 'float:']
        # 判断是否匹配列表中的类型
        if any(i in regular_data for i in value_types) is True:
            # 对字符串进行分隔，取第一个值
            value_types = regular_data.split(':')[0]
            # 对字符串进行分隔，取第二个值
            regular_data = regular_data.split(':')[1]
            # 编译正则表达式对象
            pattern = re.compile(r'\'\$cache\{' + value_types.split(':')[0] + ':' + regular_data + r'\}\'')
        else:
            # 编译正则表达式对象
            pattern = re.compile(r'\$cache\{' + regular_data.replace('$', '\$').replace('[', '\[') + r'\}')
        try:
            # 获取缓存数据
            cache_data = CacheHandler.get_cache(regular_data)
            # value中匹配到的字符串,替换成cache_data
            value = re.sub(pattern, str(cache_data), value)
        except Exception:
            pass
    return value


def regular(target):
    """使用正则替换请求数据"""
    try:
        regular_patten = r'\${{(.*?)}}'
        # 判断正则是否匹配成功
        while re.findall(regular_patten, target):
            # 获取匹配到的第一个值
            key = re.search(regular_patten, target).group(1)
            value_types = ['int:', 'bool:', 'list:', 'dict:', 'tuple:', 'float:']
            # 判断key是否匹配列表中的类型
            if any(i in key for i in value_types) is True:
                # 先以:对key进行分隔，取第二个值，在对第二个值以(进行分隔，取第一个值
                func_name = key.split(":")[1].split("(")[0]
                # 先以:对key进行分隔，取第二个值，在对第二个值以(进行分隔，取第二个值，然后进行切片取最后一个值
                value_name = key.split(":")[1].split("(")[1][:-1]
                # 判断是否为空
                if value_name == "":
                    # 调用Context()类的方法
                    value_data = getattr(Context, func_name)()
                else:
                    # 调用Context()类的方法，并传参
                    value_data = getattr(Context, func_name)(*value_name.split(","))
                regular_int_pattern = r'\'\${{(.*?)}}\''
                # target中第一个匹配到的字符串,替换成value_data
                target = re.sub(regular_int_pattern, str(value_data), target, 1)
            else:
                # 分隔字符串，取第一个值
                func_name = key.split('(')[0]
                # 分隔字符串，取第二个值，对第二个值进行切片，取最后一个值
                value_name = key.split('(')[1][:-1]
                # 判断是否为空
                if value_name == "":
                    # 调用Context()类的方法
                    value_data = getattr(Context(), func_name)()
                else:
                    # 调用Context()类的方法，并传参
                    value_data = getattr(Context(), func_name)(*value_name.split(","))
                # target中第一个匹配到的字符串,替换成value_data
                target = re.sub(regular_patten, str(value_data), target, 1)
        return target

    except AttributeError:
        ERROR.logger.error('未找到对应的替换数据，请检查数据是否正确%s', target)
        raise
    except IndexError:
        ERROR.logger.error('yaml中的${{}}函数方法不正确,正确语法实例：${{get_time()}}')
        raise