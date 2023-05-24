import ast
import os
import random
import time
import urllib
import jsonpath
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
from utils.requests_tool.set_current_request_cache import SetCurrentRequestCache
# 禁用 InsecureRequestWarning 警告信息
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class RequestControl:
    """封装请求"""

    def __init__(self, yaml_case):
        # 用例数据
        self.__yaml_case = TestCase(**yaml_case)

    def file_data_exit(self, file_data):
        """上传文件时，data参数是否存在"""
        try:
            # 获取用例数据
            _data = self.__yaml_case
            # 获取用例中的data数据进行遍历
            for key, value in ast.literal_eval(cache_regular(str(_data)))['data'].items():
                # 判断请求头中是否包含multipart/form-data
                if 'multipart/form-data' in str(self.__yaml_case.headers.values()):
                    file_data[key] = str(value)
                else:
                    file_data[key] = value
        except KeyError:
            pass

    @classmethod
    def multipart_data(cls, file_data):
        """处理上传文件的数据，构建一个适合上传文件的 multipart/form-data 请求体 """
        multipart = MultipartEncoder(fields=file_data,
                                     boundary='-----------------------------' + str(random.randint(int(1e28), int(1e29 - 1))))
        return multipart

    @classmethod
    def check_headers_str_null(cls, headers):
        """兼容用户未填写headers"""
        # 获取请求头数据
        headers = ast.literal_eval(cache_regular(str(headers)))
        # 判断请求头数据是否为空
        if headers is None:
            headers = {'headers': None}
        else:
            # 遍历请求头数据
            for key, value in headers.items():
                # 判断值不是字符串
                if not isinstance(value, str):
                    headers[key] = str(value)
        return headers

    @classmethod
    def multipart_in_headers(cls, request_data, header):
        """判断处理header为Content-Type:multipart/form-data"""
        # 获取请求头数据
        header = ast.literal_eval(cache_regular(str(header)))
        # 获取响应数据
        request_data = ast.literal_eval(cache_regular(str(request_data)))
        # 判断请求头为空
        if header is None:
            header = {'headers': None}
        else:
            # 遍历请求头数据
            for key, value in header.items():
                # 判断值不是字符串
                if not isinstance(value, str):
                    # 将header中的int转换成str
                    header[key] = str(value)
            # 判断请求头中是否包含multipart/form-data
            if 'multipart/form-data' in str(header.values()):
                # 判断参数不为空，并参数是字典类型
                if request_data and isinstance(request_data, dict):
                    # 当Content-Type为multipart/form-data时，需要将数据类型转换成str
                    for key, value in request_data.items():
                        if not isinstance(value, str):
                            request_data[key] = str(value)
                    # 构建请求体
                    request_data = MultipartEncoder(request_data)
                    # 设置数据请求类型
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
        # 用于存储文件数据的列表
        _files = []
        # 用于存储文件的字典
        file_data = {}
        self.file_data_exit(file_data)
        # 获取用例数据
        _data = self.__yaml_case.data
        # 遍历用例中的文件名
        for key, value in ast.literal_eval(cache_regular(str(_data)))['file'].items():
            # 拼接文件路径
            file_path = ensure_path_sep('\\Files\\' + value)
            # 将文件数据添加到字典中
            file_data[key] = (value, open(file_path, 'rb'), 'application/octet-stream')
            _files.append(file_data)
            # 将文件添加到allure报告中
            allure_attach(source=file_path, name=value, extension=value)
        # 将文件数据转换成multipart/form-data格式
        multipart = self.multipart_data(file_data)
        # 将Content-Type设置为multipart/form-data
        self.__yaml_case.headers['Content-Type'] = multipart.content_type
        # 将参数数据转换成字典
        params_data = ast.literal_eval(cache_regular(str(self.file_prams_exit())))
        return multipart, params_data, self.__yaml_case

    def request_type_for_json(self, headers, method, **kwargs):
        """判断请求类型为json格式"""
        # 转换请求头格式
        _headers = self.check_headers_str_null(headers)
        # 获取用例中的data
        _data = self.__yaml_case.data
        # 获取用例中的url
        _url = self.__yaml_case.url
        # 发送http请求
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
        # 转换请求头格式
        _headers = self.check_headers_str_null(headers)
        # 获取用例中的url
        _url = self.__yaml_case.url
        # 发送http请求
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
        # 获取用例中的data数据
        _data = self.__yaml_case.data
        # 获取用例中的url
        url = self.__yaml_case.url
        # 判断data数据不为空
        if _data is not None:
            params_data = '?'
            # 遍历data数据
            for key, value in _data.items():
                # 判断值为空
                if value is None or value == "":
                    # 对key进行拼接
                    params_data += (key + '&')
                else:
                    # 拼接params
                    params_data += (key + '=' + str(value) + '&')
            # 拼接url
            url = self.__yaml_case.url + params_data[:-1]
        # 转换请求头
        _headers = self.check_headers_str_null(headers)
        #进行http请求
        res = requests.request(
            method=method,
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
        # 获取需要上传的文件
        multipart = self.upload_file()
        # 获取用例数据
        yaml_data = multipart[2]
        # 获取请求头
        _headers = multipart[2].headers
        # 转换请求头
        _headers = self.check_headers_str_null(_headers)
        # 发送http请求
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
        # 获取用例中的data数据
        data = self.__yaml_case.data
        # 获取处理后的data数据和请求头数据
        _data, _headers = self.multipart_in_headers(
            ast.literal_eval(cache_regular(str(data))),
            headers
        )
        # 获取用例中的url
        _url = self.__yaml_case.url
        # 发送http请求
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
        """获取导出数据的文件名"""
        # 获取响应头中的 Content-Disposition 属性
        content_disposition = res.headers.get('content-disposition')
        # 根据 Content-Disposition 属性，获取文件名的编码
        filename_code = content_disposition.split('=')[-1]
        # 对文件名进行 URL 解码，获取原始文件名
        filename = urllib.parse.unquote(filename_code)
        return filename

    def request_type_for_export(self, headers, method, **kwargs):
        """判断requestType为export导出类型"""
        # 转换请求头数据
        _headers = self.check_headers_str_null(headers)
        # 获取用例中的data数据
        _data = self.__yaml_case.data
        # 获取用例中的url
        _url = self.__yaml_case.url
        # 发送http请求
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
        # 拼接完整的文件路径
        filepath = os.path.join(ensure_path_sep("\\File\\"), self.get_export_api_filename(res))
        # 判断响应状态码为200
        if res.status_code == 200:
            # 判断数据是否为空
            if res.text:
                # 以写的模式打开文件
                with open(filepath, 'wb') as file:
                    # 获取响应数据进行遍历
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
            # 处理sql语句
            sql_data = AssertExecution().assert_execution(sql=sql_data, resp=res.json())
        else:
            sql_data = {'sql': None}
        return sql_data

    def _check_params(self, res, yaml_data: 'TestCase') -> 'ResponseData':
        # 获取用例数据
        data = ast.literal_eval(cache_regular(str(yaml_data.data)))
        # 用例数据
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
            'token': cache_regular('$cache{login_token}'),
            'assert_data': yaml_data.assert_data,
            'res_time': self.repsonse_elapsed_total_seconds(res),
            'status_code': res.status_code,
            'teardown': yaml_data.teardown,
            'teardown_sql': yaml_data.teardown_sql,
            'body': data
        }
        # 将用例数据存入缓存
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

    @log_decorator(True)  # 记录请求日志
    @execution_duration(3000) # 限制请求的最大响应为3秒
    def http_request(self, dependent_switch=True, **kwargs):
        """请求封装"""
        from utils.requests_tool.dependent_case import DependentCase
        # 根据yaml文件中的请求类型，获取对应的请求方法
        requests_type_mapping = {
            RequestType.JSON.value: self.request_type_for_json,
            RequestType.NONE.value: self.request_type_for_none,
            RequestType.PARAMS.value: self.request_type_for_params,
            RequestType.FILE.value: self.request_type_for_file,
            RequestType.DATA.value: self.request_type_for_data,
            RequestType.EXPORT.value: self.request_type_for_export
        }
        # 是否执行用例
        is_run = ast.literal_eval(cache_regular(str(self.__yaml_case.is_run)))
        # 判断用例是否执行
        if is_run is True or is_run is None:
            # 是否开启依赖用例
            if dependent_switch is True:
                # 获取依赖用例
                DependentCase(self.__yaml_case).get_dependent_data()
            # 获取HTTP请求响应的结果
            res = requests_type_mapping.get(self.__yaml_case.requestType)(
                headers=self.__yaml_case.headers,
                method=self.__yaml_case.method,
                **kwargs
            )
            # 用例是否设置等待时间
            if self.__yaml_case.sleep is not None:
                time.sleep(self.__yaml_case.sleep)
            # 获取响应数据
            _res_data = self._check_params(res=res, yaml_data=self.__yaml_case)
            # 将请求数据和响应数据传入api_allure_step
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
            # 返回响应数据
            return _res_data