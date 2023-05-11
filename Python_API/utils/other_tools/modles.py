#!/usr/bin/env python
# -- coding: utf-8 --
# author: albert time:2023/5/7
import types
from dataclasses import dataclass
from enum import Enum, unique
from typing import Text, Union, Dict, Any, Optional, List
from pydantic import BaseModel


class NotificationType(Enum):
    """自动化通知方式"""
    # 不通知
    DEFAULT = '0'
    # 企业微信通知
    WECHAT = '1'
    # 邮箱通知
    EMAIL = '2'


@dataclass  # 定义一个数据类
class TestMetrics:
    """用例执行数据"""
    # 测试通过数量
    passed: int
    # 测试失败数量
    failed: int
    # 测试异常数量
    broken: int
    # 测试跳过数量
    skipped: int
    # 测试总数
    total: int
    # 测试通过率
    pass_rate: float
    # 测试时间
    time: Text


class RequestType(Enum):
    """request请求发送，请求参数的数据类型"""
    # 请求内容为json格式
    JSON = 'JSON'
    # 请求内容参数列表
    PARAMS = 'PARAMS'
    # 请求内容的表单形式
    DATA = 'DATA'
    # 请求内容为文件
    FILE = 'FILE'
    # 导出数据
    EXPORT = 'EXPORT'
    # 请求为空
    NONE = 'NONE'


class TestCaseEnum(Enum):
    # 请求url，必填
    URL = ('url', True)
    # 请求地址，必填
    HOST = ('host', True)
    # 请求方法，必填
    METHOD = ('method', True)
    # 描述信息，必填
    DETAIL = ('detail', True)
    # 是否执行，必填
    IS_RUN = ('is_run', True)
    # 请求头，必填
    HEADERS = ('headers', True)
    # 请求类型，必填
    REQUEST_TYPE = ('requestType', True)
    # 请求数据，必填
    DATA = ('data', True)
    # 依赖的其他测试用例，必填
    DE_CASE = ('dependence_case', True)
    # 依赖的其他测试用例数据，选填
    DE_CASE_DATA = ('dependence_case_dara', False)
    # 是否设置缓存，选填
    CURRENT_RE_SET_CACHE = ("current_request_set_cache", False)
    # 需要执行的sql,选填
    SQL = ('sql', False)
    # 测试预期结果，必填
    ASSERT_DATA = ('assert', True)
    # 测试执行前需要执行的sql，选填
    SETUP_SQL = ('setup_sql', False)
    # 测试执行后需要执行的操作，选填
    TEARDOWN = ('teardown', False)
    # 测试执行后需要执行的sql，选填
    TEARDOWN_SQL = ("teardown_sql", False)
    # 测试用例执行前需要等待的时间，选填
    SLEEP = ('sleep', False)


class Method(Enum):
    """请求方式"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTION = "OPTION"


def load_module_functions(module):
    """获取module中方法的名称和所在的内存地址"""
    module_functions = {}
    # 获取所有变量的字典，进行遍历
    for name, item in vars(module).items():
        # 判断是否是函数
        if isinstance(item, types.FunctionType):
            module_functions[name] = item
    return module_functions


@unique  # 确保变量值唯一
class DependentType(Enum):
    """数据库依赖相关枚举"""
    # 响应结果
    RESPONSE = 'response'
    # 请求参数
    REQUEST = 'request'
    # 数据库中的数据
    SQL_DATA = 'sqlData'
    # 缓存中的数据
    CACHE = 'cache'


class Assert(BaseModel):
    """断言类型"""
    # 需要断言的JSON路径
    jsonpath: Text
    # 需要断言值的类型
    type: Text
    # 需要断言的值
    value: Any
    # 断言的类型
    AssertType: Union[None, Text] = None


class DependentData(BaseModel):
    """依赖的数据"""
    # 依赖的数据类型
    dependent_type: Text
    # 需要提取的json路径
    jsonpath: Text
    # 是否需要将提取的值缓存起来
    set_cache: Optional[Text]
    # 如果提取的值是字典类型，是否替换key
    replace_key: Optional[Text]


class DependentCaseData(BaseModel):
    """依赖的测试用例数据"""
    # 用例ID
    case_id: Text
    # 用例所依赖的数据
    dependent_data: Union[None, List[DependentData]] = None


class ParamPrepare(BaseModel):
    """依赖的数据类型"""
    # 依赖数据的类型
    dependent_type: Text
    # 依赖数据中提取数据的路径
    jsonpath: Text
    # 是否提取数据缓存
    set_cache: Text


class SendRequest(BaseModel):
    """设置缓存"""
    # 依赖类型
    dependent_type: Text
    # 依赖数据的json路径
    jsonpath: Optional[Text]
    # 依赖缓存数据的名称
    cache_data: Optional[Text]
    # 将响应数据设置为缓存
    set_cache: Optional[Text]
    # 替换请求参数名称
    replace_key: Optional[Text]


class TearDown(BaseModel):
    """测试用例执行后的操作"""
    # 用例id
    case_id: Text
    # 用例执行后清理参数或状态
    param_prepare: Optional[List['ParamPrepare']]
    # 测试用例执行后发送请求清理状态
    send_request: Optional[List['SendRequest']]


class CurrentRequestSetCache(BaseModel):
    """请求缓存"""
    # 缓存类型
    type: Text
    # 缓存json路径
    jsonpath: Text
    # 缓存名称
    name: Text


class ResponseData(BaseModel):
    """测试用例执行结果"""
    # 请求url
    url: Text
    # 是否运行用例
    is_run: Union[None, bool, Text]
    # 请求详细信息
    detail: Text
    # 响应数据
    response_data: Text
    # 请求体
    requests_body: Any
    # 请求方法
    method: Text
    # sql数据
    sql_data: Dict
    # 测试用例
    yaml_date: 'TestCase'
    # 请求头
    headers: Dict
    # cookie数据
    token: Dict
    # 断言数据
    assert_data: Dict
    # 响应时间
    res_time: Union[int, float]
    # 响应状态码
    status_code: int
    # 清理操作
    teardown: List['TearDown'] = None
    # 清理sql操作
    teardown_sql: Union[None, List]
    # 响应体
    body: Any


class MySqlDB(BaseModel):
    """数据库配置"""
    # 是否启用数据库
    switch: bool = False
    # 数据库地址
    host: Union[Text, None]
    # 账户名
    user: Union[Text, None]
    # 密码
    password: Union[Text, None] = None
    # 端口号
    port: Union[int, None] = 3306


class Webhook(BaseModel):
    """企业微信通知配置"""
    webhook: Union[Text, None]


class Email(BaseModel):
    """邮箱通知配置"""
    # 发送邮件的用户
    send_user: Union[Text, None]
    # 邮件服务器地址
    email_host: Union[Text, None]
    # 发送邮件的密钥
    stamp_key: Union[Text, None]
    # 收件邮箱
    send_list: Union[Text, None]


class Config(BaseModel):
    """存储项目的配置信息"""
    # 项目名称
    project_name: Text
    # 项目环境
    env: Text
    # 测试人
    tester_name: Text
    # 是否信息通知
    notification_type: Text = '0'
    # 是否生成excel报告
    excel_report: bool
    # 连接mysql配置信息
    mysql_db: "MySqlDB"
    # 镜像源
    mirror_source: Text
    # 发送微信通知配置信息
    wechat: "Webhook"
    # 发送邮件配置信息
    email: "Email"
    # 是否实时更新测试用例
    real_time_update_test_cases: bool = False
    # 测试url
    host: Text


class TestCase(BaseModel):
    """测试用例类型"""
    # 请求url
    url: Text
    # 请求方法
    method: Text
    # 描述信息
    detail: Text
    # 字典或文本类型的断言数据
    assert_data: Union[Dict, Text]
    # 请求头，字典或文本或None
    headers: Union[None, Dict, Text] = {}
    # 请求类型
    requestType: Text
    # 是否运行用例
    is_run: Union[None, bool, Text] = None
    # 请求参数
    data: Any = None
    # 是否依赖其他测试用例数据
    dependence_case: Union[None, bool] = False
    # 依赖测试用例数据
    dependence_case_data: Optional[Union[None, List["DependentCaseData"], Text]] = None
    # 需要执行的Sql
    sql: List = None
    # 在测试用例执行前执行的sql
    setup_sql: List = None
    # HTTP状态码
    status_code: Optional[int] = None
    # 测试用例执行后执行的sql
    teardown_sql: Optional[List] = None
    # 测试用例执行后执行的清理操作
    teardown: Union[List["TearDown"], None] = None
    # 将当前请求的数据存入缓存中
    current_request_set_cache: Optional[List["CurrentRequestSetCache"]]
    # 需要等待的时间
    sleep: Optional[Union[int, float]]


@unique  # 确保变量值唯一
class AllureAttachmentType(Enum):
    """allure报告的文件类型枚举"""
    Text = 'txt'
    CSV = 'csv'
    TSV = 'tsv'
    URI_LIST = 'uri'

    HTML = 'html'
    XML = 'xml'
    JSON = 'json'
    YAML = 'yaml'
    PCAP = 'pcap'

    PNG = 'png'
    JPG = 'jpg'
    SVG = 'svg'
    GIF = 'gif'
    BMP = 'bmp'
    TIFF = "tiff"

    MP4 = 'mp4'
    OGG = 'ogg'
    WEBM = "webm"

    PDF = 'pdf'


@unique  # 确保变量值唯一
class AssertMethod(Enum):
    """断言类型"""
    # 相等
    equals = "=="
    # 小于
    less_than = "lt"
    # 小于等于
    less_than_or_equals = "le"
    # 大于
    greater_than = "gt"
    # 大于等于
    greater_than_or_equals = "ge"
    # 不相等
    not_equals = "not_eq"
    # 字符串相等
    string_equals = "str_eq"
    # 字符串长度相等
    length_equals = "len_eq"
    # 字符串长度大于
    length_greater_than = "len_gt"
    # 字符串长度大于等于
    length_greater_than_or_equals = "len_ge"
    # 字符串长度小于
    length_less_than = "len_lt"
    # 字符串长度小于等于
    length_less_than_or_equals = "len_le"
    # 包含
    contains = 'contains'
    # 被包含
    contained_by = 'contained_by'
    # 开头
    startswith = 'startswith'
    # 结尾
    endswith = 'endswith'