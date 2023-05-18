import os
from typing import Text, Union
from utils.read_files_tools.yaml_control import GetYamlData
from utils import config
from utils.cache_control.cache_control import CacheHandler
from utils.other_tools.modles import TestCaseEnum, Method, RequestType, TestCase


class CaseDataCheck:
    """yaml数据解析，判断数据填写是否符合规范"""
    def __init__(self, file_path):
        self.file_path = file_path
        # 判断地址是否存在
        if os.path.exists(self.file_path) is False:
            raise FileNotFoundError('用例地址未找到')
        self.case_data = None
        self.case_id = None

    def _assert(self, attr: Text):
        # 断言用例数据中是否包含指定的参数
        assert attr in self.case_data.keys(), (
            f"用例ID为 {self.case_id} 的用例中缺少 {attr} 参数，请确认用例内容是否编写规范."
            f"当前用例文件路径：{self.file_path}"
        )

    def check_params_exit(self):
        # 遍历列表， _value2member_map_.keys() 返回一个包含所有枚举成员的列表
        for enum in list(TestCaseEnum._value2member_map_.keys()):
            # 判断第二个枚举的值是否为true
            if enum[1]:
                # 将第一个值进行断言
                self._assert(enum[0])

    def check_params_right(self, enum_name, attr):
        """
        检查参数是否合法
        :param enum_name: 传入一个枚举类型的参数
        :param attr: 传入一个字符串
        :return:
        """
        # 获取枚举类型中所有成员的名称
        _member_names_ = enum_name._member_names_
        # 将attr字符串转换成大写，并进行断言
        assert attr.upper() in _member_names_, (
            f"用例ID为 {self.case_id} 的用例中 {attr} 填写不正确，"
            f"当前框架中只支持 {_member_names_} 类型."
            f"如需新增 method 类型，请联系管理员."
            f"当前用例文件路径：{self.file_path}"
        )
        return attr.upper()

    @property
    def get_method(self):
        """获取用例请求方法类型是否符合要求"""
        return self.check_params_right(Method, self.case_data.get(TestCaseEnum.METHOD.value[0]))

    @property
    def get_host(self):
        """请求地址拼接"""
        host = (
            self.case_data.get(TestCaseEnum.HOST.value[0]) +
            self.case_data.get(TestCaseEnum.URL.value[0])
        )
        return host

    @property
    def get_request_type(self):
        """获取用例请求方法类型是否符合要求"""
        return self.check_params_right(
            RequestType,
            self.case_data.get(TestCaseEnum.REQUEST_TYPE.value[0])
        )

    @property
    def get_assert(self):
        # 获取预期结果数据
        _assert_data = self.case_data.get(TestCaseEnum.ASSERT_DATA.value[0])
        # 断言数据不为空
        assert _assert_data is not None, (
            f"用例ID为{self.case_id}未添加断言，用例路径：{self.file_path}"
        )
        return _assert_data

    @property
    def get_sql(self):
        # 获取需要执行的sql
        _sql = self.case_data.get(TestCaseEnum.SQL.value[0])
        # 判断数据库开关未开启状态，且sql不为空
        if config.mysql_db.switch and _sql is None:
            return None
        return _sql

    @property
    def get_dependence_case_data(self):
        # 获取依赖的其他测试用例
        _dep_data = self.case_data.get(TestCaseEnum.DE_CASE.value[0])
        # 判断数据是否为空
        if _dep_data:
            # 断言依赖的其他用例数据不为空
            assert self.case_data.get(TestCaseEnum.DE_CASE_DATA.value[0]) is not None, (
                f"程序中检测到您的 case_id 为 {self.case_id} 的用例存在依赖，但是 {_dep_data} 缺少依赖数据."
                f"如已填写，请检查缩进是否正确， 用例路径: {self.file_path}"
            )
        # 返回依赖的其他用例数据
        return self.case_data.get(TestCaseEnum.DE_CASE_DATA.value[0])


class CaseData(CaseDataCheck):
    def case_process(self, case_id_switch: Union[None, bool] = None):
        """处理用例数据，并生成可执行的测试用例"""
        # 获取用例数据
        data = GetYamlData(self.file_path).get_yaml_data()
        case_list = []
        # 遍历用例数据
        for key, values in data.items():
            # 公共配置的数据，与用例数据不同，需要单独处理
            if key != 'case_common':
                # 存储用例数据
                self.case_data = values
                # 存储用例的id
                self.case_id = key
                # 断言用例是否存在必要参数
                super().check_params_exit()
                # 获取用例中的数据
                case_date = {
                    'method': self.get_method,
                    'is_run': self.case_data.get(TestCaseEnum.IS_RUN.value[0]),
                    'url': self.get_host,
                    'detail': self.case_data.get(TestCaseEnum.DETAIL.value[0]),
                    'headers': self.case_data.get(TestCaseEnum.HEADERS.value[0]),
                    'requestType': super().get_request_type,
                    'data': self.case_data.get(TestCaseEnum.DATA.value[0]),
                    'dependence_case': self.case_data.get(TestCaseEnum.DE_CASE.value[0]),
                    'dependence_case_data': self.get_dependence_case_data,
                    'current_request_set_cache': self.case_data.get(TestCaseEnum.CURRENT_RE_SET_CACHE.value[0]),
                    'sql': self.get_sql,
                    'assert_data': self.get_assert,
                    'setup_sql': self.case_data.get(TestCaseEnum.SETUP_SQL.value[0]),
                    'teardown': self.case_data.get(TestCaseEnum.TEARDOWN.value[0]),
                    'teardown_sql': self.case_data.get(TestCaseEnum.TEARDOWN_SQL.value[0]),
                    'sleep': self.case_data.get(TestCaseEnum.SLEEP.value[0])
                }
                # 判断用例id为True
                if case_id_switch is True:
                    # 用用例id作为key值，并将用例以字典的方式存入列表
                    case_list.append({key: TestCase(**case_date).dict()})
                else:
                    # 将用例以字典的方式存入列表
                    case_list.append(TestCase(**case_date).dict())
        return case_list


class GetTestCase:
    @staticmethod
    def case_data(case_id_lists):
        case_lists = []
        # 遍历列表
        for i in case_id_lists:
            # 根据用例id找到该用例的数据
            _data = CacheHandler.get_cache(i)
            # 将获取到的数据添加到列表
            case_lists.append(_data)
        return case_lists