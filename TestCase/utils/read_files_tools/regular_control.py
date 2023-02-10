import re
import datetime
import random
from datetime import date, timedelta, datetime
from jsonpath import jsonpath
from faker import Faker
from utils.logging_tool.log_control import ERROR
from utils.cache_process.cache_control import CacheHandler

class Context:
    """正则替换"""
    def __init__(self):
        self.faker = Faker(locale='zh-CN')

    @classmethod
    def random_int(cls):
        """随机数"""
        _data = random.randint(0, 5000)
        return _data

    def get_phone(self):
        """随机生成手机号"""
        phone = self.faker.phone_number()
        return phone

    def get_id_number(self):
        """随机生成身份证号码"""
        id_number = self.faker.ssn()
        return id_number

    def get_female_name(self):
        """女生姓名"""
        female_name = self.faker.name_female()
        return female_name

    def get_male(self):
        """男生姓名"""
        male_name = self.faker.name_male()
        return male_name

    def get_email(self):
        """生成邮箱"""
        email = self.faker.email()
        return email

    @classmethod
    def self_operated_id(cls):
        """自营店铺ID"""
        operated_id = 212
        return operated_id

    @classmethod
    def get_time(cls):
        """计算当前时间"""
        now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return now_time

    @classmethod
    def today_date(cls):
         """获取今日0点整时间"""
         _today = date.today().strftime('%Y-%m-%d') + '00:00:00'
         return str(_today)

    @classmethod
    def time_after_week(cls):
        """获取一周后12点整的时间"""
        _time_after_week = (date.today() + timedelta(days=+6)).strftime('%Y-%m-%d') + '00:00:00'
        return _time_after_week

    @classmethod
    def host(cls):
        """获取接口域名"""
        # from utils import config
        # return config.host
        pass

    @classmethod
    def app_host(cls):
        """获取app的host"""
        # from utils import config
        # return config.app_host
        pass


def sql_json(js_path, res):
    """提前sql中的json数据"""
    _json_data = jsonpath(res, js_path)[0]
    if _json_data is False:
        raise ValueError(f'sql中的jsonpath获取失败{res},{js_path}')
    return jsonpath(res, js_path)[0]


def sql_reguarl(value, res=None):
    """这里处理sql中的依赖数据通过获取接口响应的jsonpath的值进行替换"""
    sql_json_list = re.findall(r'\$json\((.*?)\)\$', value)
    for i in sql_json_list:
        pattern = re.compile(r'\$json\(' + i.replace('$', '\$').replace('[', '\[') + r'\)\$')
        key = str(sql_json(i, res))
        value = re.sub(pattern, key, value, count=1)
    return value


def cache_regular(value):
    """通过正则的方式，读取缓存中的内容"""
    regular_dates = re.findall(r'\$cache\{(.*?)\}', value)
    for regular_data in regular_dates:
        value_types = ['int:', 'bool:', 'list:', 'dict:', 'tuple:', 'float:']
        if any(i in regular_data for i in value_types) is True:
            value_types = regular_data.split(":")[0]
            regular_data = regular_data.split(":")[1]
            pattern = re.compile(r'\'\$cache\{' + value_types.spilt(":")[0] + ":" + regular_data + r'\}\'')
        else:
            patern = re.compile(r'\$cache\{' + regular_data.replace('$', '\$').replace('[', '\[') + r'\}')
        try:
            cache_data = CacheHandler.get_cache(regular_data)
            value = re.sub(pattern, str(cache_data), value)
        except Exception:
            pass
    return value


def regular(target):
    """正则替换请求数据"""
    try:
        regular_pattern = r'\${{.*?}}'
        while re.findall(regular_pattern, target):
            key = re.search(regular_pattern, target).group(1)
            value_types = ['int:', 'bool:', 'list:', 'dict:', 'tuple:', 'float:']
            if any(i in key for i in value_types) is True:
                func_name = key.spilt(':')[1].split('(')[0]
                value_name = key.split(':')[1].split('(')[1][:-1]
                if value_name == "":
                    value_data = getattr(Context(), func_name)()
                else:
                    value_data = getattr(Context(), func_name)(*value_name.split(","))
                regular_int_pattern = r'\'\${{.*?}}\''
                target = re.sub(regular_int_pattern, str(value_data), target, 1)
            else:
                func_name = key.split("(")[0]
                value_name = key.split("(")[1][:-1]
                if value_name == "":
                    value_data = getattr(Context(), func_name)()
                else:
                    value_data = getattr(Context(), func_name)(*value_name.split(","))
                target = re.sub(regular_pattern, str(value_data), target, 1)
            return target
    except AttributeError:
        ERROR.logger.error('未找到对应的替换的数据，请检查数据是否正确%S', target)
        raise


if __name__ == "__main__":
    a = "${{host()}} aaa"
    b = regular(a)