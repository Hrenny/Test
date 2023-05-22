import ast
import json

from common.setting import ensure_path_sep
from utils.read_files_tools.get_all_files_path import get_all_files


class ErrorTestCase:
    def __init__(self):
        self.test_case_path = ensure_path_sep('\\report\\html\\data\\test-cases\\')

    def get_error_case_data(self):
        """收集所有失败用例的数据"""
        path = get_all_files(self.test_case_path)
        files = []
        for i in path:
            with open(i, 'r', encoding='utf-8') as file:
                date = json.load(file)
                # 收集执行失败的用例数据
                if date['status'] == 'failed' or date['status'] == 'broken':
                    files.append(date)
        return files

    @classmethod
    def get_case_name(cls, test_case):
        """收集测试用例名称"""
        name = test_case['name'].split('[')
        case_name = name[1][:-1]
        return case_name

    @classmethod
    def get_parameters(cls, test_case):
        """获取allure报告中的parameters参数内容"""
        parameters = test_case['parameters'][0]['value']
        return ast.literal_eval(parameters)

    @classmethod
    def get_test_stage(cls, test_case):
        """获取allure报告中请求后的数据"""
        test_stage= test_case['testStage']['steps']
        return test_stage

    def get_case_url(self, test_case):
        """获取测试用例的url"""
        # 判断用例步骤中的数据是否异常
        if test_case['testStage']['status'] == 'broken':
            # 如果异常状态下，获取请求前的数据
            _url = self.get_parameters(test_case)['url']
        else:
            # 获取请求步骤数据，涉及到依赖会获取多组，取最后一组数据
            _url = self.get_test_stage(test_case)[-7]['name'][7:]
        return _url

    def get_method(self, test_case):
        """获取用例中的请求方式"""
        if test_case['testStage']['status'] == 'broken':
            _method = self.get_parameters(test_case)['method']
        else:
            _method = self.get_test_stage(test_case)[-6]['name'][6:]
        return _method

    def get_headers(self, test_case):
        """获取用例请求头"""
        if test_case['testStage']['status'] == 'broken':
            _headers = self.get_parameters(test_case)['headers']
        else:
            _headers_attachment = self.get_test_stage(test_case)[-5]['attachments'][0]['source']
            path = ensure_path_sep("\\report\\html\\data\\attachments\\" + _headers_attachment)
            with open(path, 'r', encoding='utf-8') as file:
                _headers = json.load(file)
        return _headers

    def  get_request_type(self, test_case):
        """获取用例的请求类型"""
        request_type = self.get_parameters(test_case)['requestType']
        return request_type

    def get_case_data(self, test_case):
        """获取用例内容"""
        if test_case['testStage']['status'] == 'broken':
            _case_data = self.get_parameters(test_case)['data']
        else:
            _case_data_attachments = self.get_test_stage(test_case)[-4]['attachments'][0]['source']
            path = ensure_path_sep('\\report\\html\\data\\attachments\\' + _case_data_attachments)
            with open(path, 'r', encoding='utf-8') as file:
                _case_data = json.load(file)
        return _case_data

    def get_dependence_case(self, test_case):
        """获取依赖用例"""
        _dependence_case_data =  self.get_parameters(test_case)['dependence_case_data']
        return _dependence_case_data

    def get_sql(self, test_case):
        """获取sql数据"""
        sql = self.get_parameters(test_case)['sql']
        return sql
