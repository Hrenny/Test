import ast
import json
from jsonpath import jsonpath
from utils import config
from utils.assertion import assert_type
from utils.logging_tool.log_control import WARNING
from utils.other_tools.exceptions import AssertTypeError
from utils.other_tools.modles import AssertMethod, load_module_functions
from utils.read_files_tools.regular_control import cache_regular


class AssertUtil:
    def __init__(self, assert_data, sql_data, request_data, response_data, status_code):
        """
        :param assert_data: 断言数据
        :param sql_data: sql数据
        :param request_data: 请求数据
        :param response_data: 响应数据
        :param status_code: 响应状态码
        """
        self.response_data = response_data
        self.request_data = request_data
        self.sql_data = sql_data
        self.assert_data = assert_data
        # sql启用状态
        self.sql_switch = config.mysql_db.switch
        self.status_code = status_code

    @staticmethod  # 静态方法
    def literal_eval(attr):
        """从缓存中获取数据，判断是否合法类型，是将数据转换成相应的数据类型"""
        return ast.literal_eval(cache_regular(str(attr)))

    @property  # 将方法变成属性调用
    def get_assert_data(self):
        """获取断言数据"""
        # 断言是否为空，如果为空抛出异常，指出哪个类没有属性
        assert self.assert_data is not None, (f"'{self.__class__.__name__}' should either include a 'assert_data' attribute,")
        # 从缓存中获取数据，判断是否合法类型，是将数据转换成相应的数据类型
        return ast.literal_eval(cache_regular(str(self.assert_data)))

    @property  # 将方法变成属性调用
    def get_type(self):
        # 断言判断数据中是否包含type属性，没有抛出异常
        assert 'type' in self.get_assert_data.keys(), (f"断言数据：'{self.get_assert_data}'中缺少'type'属性")
        # 获取断言类型对应的枚举值
        name = AssertMethod(self.get_assert_data.get('type')).name
        return name

    @property  # 将方法变成属性调用
    def get_value(self):
        # 断言判断数据中是否包含value属性，没有抛出异常
        assert 'value' in self.get_assert_data.keys(), (f"断言数据:'{self.get_assert_data}'中缺少'value'属性")
        # 返回属性的值
        return self.get_assert_data.get('value')

    @property  # 将方法变成属性调用
    def get_jsonpath(self):
        # 断言判断数据中是否包含jsonpath属性，没有抛出异常
        assert 'jsonpath' in self.get_assert_data.keys(), (f"断言数据:'{self.get_assert_data}'中缺少'jsonpath'属性")
        # 返回属性的值
        return self.get_assert_data.get('jsonpath')

    @property  # 将方法变成属性调用
    def get_assert_type(self):
        # 断言判断数据中是否包含AssertType属性，没有抛出异常
        assert 'AssertType' in self.get_assert_data.keys(), (f"断言数据：'{self.get_assert_data}'中缺少'AsserType'属性")
        # 返回属性的值
        return self.get_assert_data.get('AssertType')

    @property  # 将方法变成属性调用
    def get_message(self):
        """获取断言描述，如未填写，则返回None"""
        return self.get_assert_data.get('message', None)

    @property  # 将方法变成属性调用
    def get_sql_data(self):
        """获取sql查询的结果"""
        # 判断数据库开关为开启，并需要数据库断言的情况下，未编写sql，则抛出异常
        if self.sql_switch_handle:
            assert self.sql_data != {'sql': None}, ('请在用例中添加要查询的SQL语句')
        # 处理mysql查询出来的数据类型如果是bytes类型，转换成str类型
        if isinstance(self.sql_data, bytes):
            return self.sql_data.decode('utf-8')
        # 提取数据
        sql_data = jsonpath(self.sql_data, self.get_value)
        # 断言提取的数据是否成功，失败抛出异常
        assert sql_data is not False, (f'数据库断言数据提取失败，提取对象:{self.sql_data}, 当前语法:{self.get_value}')
        # 判断数据的长度
        if len(sql_data) > 1:
            return sql_data
        # 返回第一个元素
        return sql_data[0]

    @staticmethod  # 静态方法
    def functions_mapping():
        """返回函数的字典"""
        return load_module_functions(assert_type)

    @property  # 将方法变成属性调用
    def get_response_data(self):
        """将数据转换成字典类型"""
        return json.loads(self.response_data)

    @property  # 将方法变成属性调用
    def sql_switch_handle(self):
        """判断数据库开关，如果未开启，则打印断言部分数据"""
        if self.sql_switch is False:
            WARNING.logger.warning(f'检测到数据库为关闭状态，程序跳过断言，断言值为：{self.get_assert_data}')
        return self.sql_switch

    def _assert(self, check_value, expect_value, message):
        """
        调用函数获取函数字典，根据get_type获取相应的函数，通过函数对比check_value, expect_value，不相等，抛出message
        :param check_value: 进行检查的值
        :param expect_value: 期望值
        :param message: 检查结果信息
        :return:
        """
        self.functions_mapping()[self.get_type](check_value, expect_value, str(message))

    @property  # 将方法变成属性调用
    def _assert_resp_data(self):
        # 提取数据
        resp_data = jsonpath(self.get_response_data, self.get_jsonpath)
        # 断言数据是否提取成功，失败抛出异常
        assert resp_data is not False, (f'jsonpath数据提取失败，提取对象：{self.get_response_data}, 当前语法：{self.get_jsonpath}')
        # 判断数据的长度
        if len(resp_data) > 1:
            return resp_data
        # 返回第一个元素
        return resp_data[0]

    @property  # 将方法变成属性调用
    def _assert_request_data(self):
        # 提取数据
        req_data = jsonpath(self.request_data, self.get_jsonpath)
        # 断言数据是否提取成功，失败抛出异常
        assert req_data is not False, (f'jsonpath数据提取失败，提取对象：{self.request_data}, 当前语法：{self.get_jsonpath}')
        # 判断数据的长度
        if len(req_data) > 1:
            return req_data
        # 返回第一个元素
        return req_data[0]

    def assert_type_handle(self):
        # 判断请求参数数据库断言
        if self.get_assert_type == 'R_SQL':
            self._assert(self._assert_request_data, self.get_sql_data, self.get_message)
        # 判断请求参数为响应数据库断言
        elif self.get_assert_type == 'SQL' or self.get_assert_type == 'D_sql':
            self._assert(self._assert_resp_data, self.get_sql_data, self.get_message)
        # 判断非数据库断言类型
        elif self.get_assert_type is None:
            self._assert(self._assert_resp_data, self.get_value, self.get_message)
        else:
            raise AssertTypeError('断言失败，目前只支持数据库断言和响应断言')


class Assert(AssertUtil):

    def assert_data_list(self):
        assert_list = []
        # 遍历断言数据
        for k, v in self.assert_data.items():
            # 判断是否响应状态码
            if k == 'status_code':
                # 断言响应状态码
                assert self.status_code == v, '响应状态码断言失败'
            else:
                # 将数据添加到列表
                assert_list.append(v)
        return assert_list

    def assert_type_handle(self):
        # 遍历列表
        for i in self.assert_data_list():
            self.assert_data = i
            # 调用父类方法进行断言
            super().assert_type_handle()