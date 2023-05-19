import ast
import json
from typing import Text, Dict
from jsonpath import jsonpath
from utils import config
from utils.cache_control.cache_control import CacheHandler
from utils.logging_tool.log_control import WARNING
from utils.mysql_tool.mysql_control import MysqlDB
from utils.other_tools.exceptions import JsonpathExtractionFailed, ValueNotFoundError
from utils.other_tools.jsonpath_date_replace import jsonpath_replace
from utils.other_tools.modles import ResponseData, SendRequest, ParamPrepare, TearDown
from utils.read_files_tools.regular_control import regular, cache_regular, sql_regular
from utils.requests_tool.request_control import RequestControl


class TearDownHandler:
    """处理yaml格式后置请求"""
    def __init__(self, res: 'ResponseData'):
        self._res = res

    @classmethod
    def jsonpath_replace_data(cls, replace_key: Text, replace_value: Dict):
        """
        通过jsonpath判断出需要替换数据的位置
        :param replace_key: 替换的json路径
        :param replace_value: 替换的值
        :return:
        """
        # 分割字符串
        _change_data = replace_key.split('.')
        # 获取替换后的数据
        _new_data = jsonpath_replace(
            change_data=_change_data,
            key_name='_teardown_case',
            data_switch=False
        )
        # 判断replace_value不是字符串
        if not isinstance(replace_value, str):
            _new_data += f' = {replace_value}'
        else:
            _new_data += f' = "{replace_value}"'
        return _new_data

    @classmethod
    def get_cache_name(cls, replace_key: Text, resp_case_data: Dict):
        """获取缓存名称，提取数据写入缓存"""
        # 检查'$set_cache{'是否在replace_key中，'}'是否在replace_key中
        if '$set_cache{' in replace_key and '}' in replace_key:
            # 获取'$set_cache{'的开始索引
            start_index = replace_key.index('$set_cache{')
            # 获取'$set_cache{'的结束索引
            end_index = replace_key.index('}', start_index)
            # 从replace_key中提取旧的缓存名称
            old_name = replace_key[start_index:end_index + 2]
            # 从old_name中提取缓存名称
            cache_name = old_name[11:old_name.index("}")]
            # 用新的值更新缓存
            CacheHandler.update_cache(cache_name=cache_name, value=resp_case_data)

    @classmethod
    def regular_testcase(cls, teardown_case: Dict):
        """处理测试用例中的动态数据"""
        # 转换成字符串并应用正则表达式
        test_case = regular(str(teardown_case))
        # 获取缓存数据
        test_case = ast.literal_eval(cache_regular(str(test_case)))
        return test_case

    @classmethod
    def teardown_http_requests(cls, teardown_case: Dict) -> 'ResponseData':
        """发送后置请求"""
        # 获取处理好的测试用例
        test_case = cls.regular_testcase(teardown_case)
        # 获取响应数据
        res = RequestControl(test_case).http_request(dependent_switch=False)
        return res

    def dependent_type_response(self, teardown_case_data: 'SendRequest', resp_data: Dict):
        """
        判断依赖类型为当前执行用例响应内容
        :param teardown_case_data: teardown中用例内容
        :param resp_data: 需要替换的内容
        :return:
        """
        # 获取要替换的key值
        _replace_key = teardown_case_data.replace_key
        # 获取响应数据中对应的值
        _response_dependent = jsonpath(obj=resp_data, expr=teardown_case_data.jsonpath)
        # 如果响应数据中存在要替换的key值，则进行替换
        if _response_dependent is not False:
            _resp_case_data = _response_dependent[0]
            data = self.jsonpath_replace_data(
                replace_key=_replace_key,
                replace_value=_resp_case_data
            )
        else:
            raise JsonpathExtractionFailed(
                f"jsonpath提取失败，替换内容: {resp_data} \n"
                f"jsonpath: {teardown_case_data.jsonpath}"
            )
        return data

    def dependent_type_request(self, teardown_case_data: Dict, request_data: Dict):
        """
        判断依赖类型为请求内容
        :param teardown_case_data: teardown中的用例内容
        :param request_data: 需要替换的内容
        :return:
        """
        try:
            # 获取请求数据中对应的值，用于缓存
            _request_set_value = teardown_case_data['set_value']
            # 获取请求数据中对应的值
            _request_dependent = jsonpath(obj=request_data, expr=teardown_case_data['jsonpath'])
            # 如果请求数据中存在要缓存的值，则进行缓存处理
            if _request_dependent is not False:
                _request_case_data = _request_dependent[0]
                # 将要缓存的值存储到缓存中
                self.get_cache_name(
                    replace_key=_request_set_value,
                    resp_case_data=_request_case_data
                )
            else:
                raise JsonpathExtractionFailed(
                    f"jsonpath提取失败，替换内容: {request_data} \n"
                    f"jsonpath: {teardown_case_data['jsonpath']}"
                )
        except KeyError as exc:
            raise ValueNotFoundError('teardown中缺少set_value参数，请检查用例是否正确') from exc

    def dependent_self_response(self, teardown_case_data: 'ParamPrepare', res: Dict, resp_data: Dict):
        """
        判断依赖类型为依赖用例ID自己响应的内容
        :param teardown_case_data: teardown中用例内容
        :param res: 需要替换的内容
        :param resp_data: 接口响应内容
        :return:
        """
        try:
            # 获取要缓存的值，并存储到缓存中
            _set_value = teardown_case_data.set_cache
            _response_dependent = jsonpath(obj=res, expr=teardown_case_data.jsonpath)
            # 如果响应数据中存在要缓存的值，则进行缓存处理
            if _response_dependent is not False:
                _resp_case_data = _response_dependent[0]
                # 将要缓存的值存储到缓存中
                CacheHandler.update_cache(cache_name=_set_value, value=_resp_case_data)
                self.get_cache_name(
                    replace_key=_set_value,
                    resp_case_data=_resp_case_data
                )
            else:
                raise JsonpathExtractionFailed(
                    f"jsonpath提取失败，替换内容: {resp_data} \n"
                    f"jsonpath: {teardown_case_data.jsonpath}")
        except KeyError as exc:
            raise ValueNotFoundError('teardown中缺少set_cache参数，请检查用例是否正确')

    @classmethod
    def dependent_type_cache(cls, teardown_case: 'SendRequest'):
        """判断依赖类型从缓存中处理"""
        # 判断该teardown_case是否为cache类型的依赖
        if teardown_case.dependent_type == 'cache':
            # 获取缓存的名称、要替换的变量名和替换后的数据
            _cache_name = teardown_case.cache_data
            # 获取要替换的key值
            _replace_key = teardown_case.replace_key
            _change_data = _replace_key.split('.')
            _new_data = jsonpath_replace(
                change_data=_change_data,
                key_name='_teardown_case',
                data_switch=False
            )
            value_type = ['int:', 'bool:', 'list:', 'dict:', 'tuple:', 'float:']
            # 判断缓存的值类型，如果是value_type列表中的类型，则直接从缓存中获取并替换
            if any(i in _cache_name for i in value_type) is True:
                _cache_data = CacheHandler.get_cache(_cache_name.split(':')[1])
                _new_data += f' = {_cache_data}'
            else:
                _cache_name = CacheHandler.get_cache(_cache_name)
                _new_data += f' = "{_change_data}"'
            return _new_data

    def send_request_handler(self, data: 'TearDown', resp_data: Dict, request_data: Dict):
        """
        后置请求数据
        :param data: 清理操作对应的数据
        :param resp_data: 清理操作执行后的响应结果
        :param request_data: 发送请求的参数
        :return:
        """
        # 获取发送请求数据
        _send_request = data.send_request
        # 获取用例的id
        _case_id = data.case_id
        # 从缓存中获取用例数据
        _teardown_case = CacheHandler.get_cache(_case_id)
        # 遍历请求数据
        for i in _send_request:
            # 判断依赖类型为cache
            if i.dependent_type == 'cache':
                # 从缓存中获取依赖数据，并赋值给对应的变量
                exec(self.dependent_type_cache(teardown_case=i))
            # 判断依赖类型为response
            if i.dependent_type == 'response':
                # 从响应中获取依赖的数据，并赋值给对应的变量
                exec(
                    self.dependent_type_response(
                        teardown_case_data=i,
                        resp_data=resp_data
                    )
                )
            # 判断依赖类型为request
            elif i.dependent_type == 'request':
                # 从发送请求时使用的参数中获取依赖数据，并赋值给对应的变量
                self.dependent_type_request(
                    teardown_case_data=i,
                    request_data=request_data
                )
        # 将缓存的用例数据转换为符合pytest的对象
        test_case = self.regular_testcase(_teardown_case)
        # 执行HTTP请求清理操作
        self.teardown_http_requests(test_case)

    def param_prepare_request_handler(self, data: 'TearDown', resp_data: Dict):
        """前置请求处理"""
        # 获取用例的id
        _case_id = data.case_id
        # 获取前置用例数据
        _teardown_case = CacheHandler.get_cache(_case_id)
        # 获取参数
        _param_prepare = data.param_prepare
        # 发送请求并获取响应结果
        res = self.teardown_http_requests(_teardown_case)
        # 遍历参数数据
        for i in _param_prepare:
            # 判断参数是否依赖于自身响应数据
            if i.dependent_type == 'self_response':
                # 调用依赖自身响应数据的方法
                self.dependent_self_response(
                    teardown_case_data=i,
                    resp_data=resp_data,
                    res=json.loads(res.response_data)
                )

    def teardown_handle(self):
        """区分前置"""
        # 拿到用例信息
        _teardown_data = self._res.teardown
        # 获取接口的响应内容
        _resp_data = self._res.response_data
        # 获取接口的请求参数
        _request_data = self._res.yaml_data.data
        # 判断如果没有teardown
        if _teardown_data is not None:
            # 遍历用例
            for _data in _teardown_data:
                # 用例执行后清理参数或状态是否为空
                if _data.param_prepare is not None:
                    # 将参数存储到缓存中
                    self.param_prepare_request_handler(
                        data=_data,
                        resp_data=json.loads(_resp_data)
                    )
                # 测试用例执行后发送请求清理状态是否为空
                elif _data.send_request is not None:
                    # 发送HTTP请求，将响应结果存入缓存
                    self.send_request_handler(
                        data=_data,
                        request_data=_request_data,
                        resp_data=json.loads(_resp_data)
                    )
        # 执行清理数据库中的相关数据
        self.teardown_sql()

    def teardown_sql(self):
        """处理后置sql"""
        sql_data = self._res.teardown_sql
        _response_data = self._res.response_data
        if sql_data is not None:
            for i in sql_data:
                if config.mysql_db.switch:
                    _sql_data = sql_regular(value=i, res=json.loads(_response_data))
                    MysqlDB().execute(cache_regular(_sql_data))
                else:
                    WARNING.logger.warning(f'数据库为关闭状态，跳过sql:{i}')