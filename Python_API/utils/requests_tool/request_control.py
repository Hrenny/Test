import ast
import os
import random
import time
import urllib
import requests
import urllib3
from requests_toolbelt import MultipartEncoder
from common.setting import ensure_path_sep
from utils import config
from utils.logging_tool.log_decorator import log_decorator
from utils.logging_tool.run_time_decorator import execution_duration
from utils.mysql_tool.mysql_control import AssertExecution
from utils.other_tools.allure_data.allure_tools import allure_attach, allure_step_no, allure_step
from utils.other_tools.modles import TestCase, ResponseData, RequestType
from utils.read_files_tools.regular_control import cache_regular
from utils.requests_tool.dependent_case import DependentCase
from utils.requests_tool.set_current_request_cache import SetCurrentRequestCache

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class RequestControl:
    """封装请求"""

    def __init__(self, yaml_case):
        self.__yaml_case = TestCase(**yaml_case)

    def file_data_exit(self, file_data):
        """上传文件时，data参数是否存在"""
        try:
            _data = self.__yaml_case
            for key, value in ast.literal_eval(cache_regular(str(_data)))['data'].items():
                if 'multipart/form-data' in str(self.__yaml_case.headers.values()):
                    file_data[key] = str(value)
                else:
                    file_data[key] = value
        except KeyError:
            pass

    @classmethod
    def multipart_data(cls, file_data):
        """处理上传文件的数据"""
        multipart = MultipartEncoder(fields=file_data,
                                     boundary='-----------------------------' + str(random.randint(int(1e28), int(1e29 - 1))))
        return multipart

    @classmethod
    def check_headers_str_null(cls, headers):
        """兼容用户未填写headers"""
        headers = ast.literal_eval(cache_regular(str(headers)))
        if headers is None:
            headers = {'headers': None}
        else:
            for key, value in headers.items():
                if not isinstance(value, str):
                    headers[key] = str(value)
        return headers

    @classmethod
    def multipart_in_headers(cls, request_data, header):
        """判断处理header为Content-Type:multipart/form-data"""
        header = ast.literal_eval(cache_regular(str(header)))
        request_data = ast.literal_eval(cache_regular(str(request_data)))
        if header is None:
            header = {'headers': None}
        else:
            # 将header中的int转换成str
            for key, value in header.items():
                if not isinstance(value, str):
                    header[key] = str(value)
            if 'multipart/form-data' in str(header.values()):
                # 判断参数不为空，并参数是字典类型
                if request_data and isinstance(request_data, dict):
                    # 当Content-Type为multipart/form-data时，需要将数据类型转换成str
                    for key, value in request_data.items():
                        if not isinstance(value, str):
                            request_data[key] = str(value)
                    request_data = MultipartEncoder(request_data)
                    header['Content-Type'] = request_data.content_type
        return request_data, header

    def file_prams_exit(self):
        """判断上传文件接口，文件参数是否存在"""
        try:
            params = self.__yaml_case.data['params']
        except KeyError:
            params = None
        return params

    @classmethod
    def text_encode(cls, text):
        """unicode解码"""
        return text.encode('utf-8').decode('utf-8')

    @classmethod
    def repsonse_elapsed_total_seconds(cls, res):
        """获取接口响应时长"""
        try:
            return round(res.elapsed.total_seconds() * 1000, 2)
        except AttributeError:
            return 0.00

    def upload_file(self):
        """判断处理上传文件"""
        _files = []
        file_data = {}
        self.file_data_exit(file_data)
        _data = self.__yaml_case.data
        for key, value in ast.literal_eval(cache_regular(str(_data)))['file'].items():
            file_path = ensure_path_sep('\\Files\\' + value)
            file_data[key] = (value, open(file_path, 'rb'), 'application/octet-stream')
            _files.append(file_data)
            allure_attach(source=file_path, name=value, extension=value)
        multipart = self.multipart_data(file_data)
        self.__yaml_case.headers['Content-Type'] = multipart.content_type
        params_data = ast.literal_eval(cache_regular(str(self.file_prams_exit())))
        return multipart, params_data, self.__yaml_case

    def request_type_for_json(self, headers, method, **kwargs):
        """判断请求类型为json格式"""
        _headers = self.check_headers_str_null(headers)
        _data = self.__yaml_case.data
        _url = self.__yaml_case.url
        res = requests.request(
            method=method,
            url=cache_regular(str(_url)),
            json=ast.literal_eval(cache_regular(str(_data))),
            data={},
            headers=_headers,
            verify=False,
            params=None,
            **kwargs
        )
        return res

    def request_type_for_none(self, headers, method, **kwargs):
        """判断requestType为None"""
        _headers = self.check_headers_str_null(headers)
        _url = self.__yaml_case.url
        res = requests.request(
            method=method,
            url=cache_regular(_url),
            data=None,
            headers=_headers,
            verify=False,
            params=None,
            **kwargs
        )
        return res

    def request_type_for_params(self, headers, method, **kwargs):
        """处理requestType为params"""
        _data = self.__yaml_case.data
        url = self.__yaml_case.url
        if _data is not None:
            params_data = '?'
            for key, value in _data.items():
                if value is None or value == "":
                    params_data += (key + '&')
                else:
                    params_data += (key + '=' + str(value) + '&')
            url = self.__yaml_case.url + params_data[:-1]
        _headers = self.check_headers_str_null(headers)
        res = requests.request(
            method-method,
            url=cache_regular(url),
            headers=_headers,
            verify=False,
            data={},
            params=None,
            **kwargs
        )
        return res

    def request_type_for_file(self, method, headers, **kwargs):
        """处理requestType为file类型"""
        multipart = self.upload_file()
        yaml_data = multipart[2]
        _headers = multipart[2].headers
        _headers = self.check_headers_str_null(_headers)
        res = requests.request(
            method=method,
            url=cache_regular(yaml_data.url),
            data=multipart[0],
            params=multipart[1],
            headers=ast.literal_eval(cache_regular(str(_headers))),
            verify=False,
            **kwargs
        )
        return res

    def request_type_for_data(self, headers, method, **kwargs):
        """判断requestType类型为data类型"""
        data = self.__yaml_case.data
        _data, _headers = self.multipart_in_headers(
            ast.literal_eval(cache_regular(str(data))),
            headers
        )
        _url = self.__yaml_case.url
        res = requests.request(
            method=method,
            url=cache_regular(_url),
            data=_data,
            headers=_headers,
            verify=False,
            **kwargs
        )
        return res

    @classmethod
    def get_export_api_filename(cls, res):
        """处理导出文件"""
        content_disposition = res.headers.get('content-disposition')
        # 分割字符串，提取文件名
        filename_code = content_disposition.split('=')[-1]
        # url解码
        filename = urllib.parse.unquote(filename_code)
        return filename

    def request_type_for_export(self, headers, method, **kwargs):
        """判断requestType为export导出类型"""
        _headers = self.check_headers_str_null(headers)
        _data = self.__yaml_case.data
        _url = self.__yaml_case.url
        res = requests.request(
            method=method,
            url=cache_regular(_url),
            json=ast.literal_eval(cache_regular(str(_data))),
            headers=_headers,
            verify=False,
            stream=False,
            data={},
            **kwargs
        )
        filepath = os.path.join(ensure_path_sep("\\File\\"), self.get_export_api_filename(res))
        if res.status_code == 200:
            if res.text:
                with open(filepath, 'wb') as file:
                    for chunk in res.iter_content(chunk_size=1):
                        file.write(chunk)
            else:
                print('文件为空')
        return res

    @classmethod
    def _request_body_handler(cls, data, request_type):
        """处理请求参数"""
        if request_type.upper() == 'PARAMS':
            return None
        else:
            return data

    @classmethod
    def _sql_data_handler(cls, sql_data, res):
        """处理sql参数"""
        # 判断数据开关，开启返回相应数据
        if config.mysql_db.switch and sql_data is not None:
            sql_data = AssertExecution().assert_execution(sql=sql_data, resp=res.json())
        else:
            sql_data = {'sql': None}
        return sql_data

    def _check_params(self, res, yaml_data: 'TestCase') -> 'ResponseData':
        data = ast.literal_eval(cache_regular(str(yaml_data.data)))
        _data = {
            'url': res.url,
            'is_run': yaml_data.is_run,
            'detail': yaml_data.detail,
            'response_data': res.text,
            'request_body': self._request_body_handler(data, yaml_data.requestType),
            'method': res.request.method,
            'sql_data': self._sql_data_handler(sql_data=ast.literal_eval(cache_regular(str(yaml_data.sql))), res=res),
            'yaml_data': yaml_data,
            'headers': res.request.headers,
            'cookie': res.cookies,
            'assert_data': yaml_data.assert_data,
            'res_time': self.repsonse_elapsed_total_seconds(res),
            'status_code': res.status_code,
            'teardown': yaml_data.teardown,
            'teardown_sql': yaml_data.teardown_sql,
            'body': data
        }
        return ResponseData(**_data)

    @classmethod
    def api_allure_step(cls, *, url, headers, method, data, assert_data, res_time, res):
        """在allure中记录请求数据"""
        allure_step_no(f'请求URL:{url}')
        allure_step_no(f'请求方式:{method}')
        allure_step('请求头：', headers)
        allure_step('请求数据：', data)
        allure_step('预期数据：', assert_data)
        _res_time = res_time
        allure_step_no(f'响应耗时:{str(_res_time)}')
        allure_step('响应结果：', res)

    @log_decorator(True)
    @execution_duration(3000)
    def http_request(self, dependent_switch=True, **kwargs):
        """请求封装"""
        requests_type_mapping = {
            RequestType.JSON.value: self.request_type_for_json,
            RequestType.NONE.value: self.request_type_for_none,
            RequestType.PARAMS.value: self.request_type_for_params,
            RequestType.FILE.value: self.request_type_for_file,
            RequestType.DATA.value: self.request_type_for_data,
            RequestType.EXPORT.value: self.request_type_for_export
        }
        is_run = ast.literal_eval(cache_regular(str(self.__yaml_case.is_run)))
        # 判断用例是否执行
        if is_run is True or is_run is None:
            if dependent_switch is True:
                DependentCase(self.__yaml_case).get_dependent_data()
            res = requests_type_mapping.get(self.__yaml_case.requestType)(
                headers=self.__yaml_case.headers,
                method=self.__yaml_case.method,
                **kwargs
            )
            if self.__yaml_case.sleep is not None:
                time.sleep(self.__yaml_case.sleep)
            _res_data = self._check_params(res=res, yaml_data=self.__yaml_case)
            self.api_allure_step(
                url=_res_data.url,
                headers=str(_res_data.headers),
                method=_res_data.method,
                data=str(_res_data.body),
                assert_data=str(_res_data.assert_data),
                res_time=str(_res_data.res_time),
                res=_res_data.response_data
            )
            # 当前请求数据存入缓存中
            SetCurrentRequestCache(
                current_request_set_cache=self.__yaml_case.current_request_set_cache,
                request_data=self.__yaml_case.data,
                response_data=res
            ).set_caches_main()
            return _res_data