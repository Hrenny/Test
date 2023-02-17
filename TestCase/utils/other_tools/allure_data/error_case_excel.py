import json
import shutil
import ast
import xlwings
from common.setting import ensure_path_sep
from utils.read_files_tools.get_all_files_path import get_all_files
from utils.notify.wechat_send import WeChatSend
from utils.other_tools.allure_data.allure_report_data import AllureFileClean


class ErrorTestCase:
    """收集错误的excel"""
    def __init__(self):
        self.test_case_path = ensure_path_sep('\\report\\html\\data\\test-case\\')

    def get_error_case_data(self):
        """收集所有失败用例数据"""
        path = get_all_files(self.test_case_path)
        files = []
        for i in path:
            with open(i, 'r', encoding='utf-8') as file:
                date = json.load(file)
                # 收集执行失败的用例数据
                if date['status'] == 'failed' or date['status'] == 'broken':
                    files.append(date)
            print(files)
            return files

    @classmethod
    def get_case_name(cls, test_case):
        """收集测试用例名称"""
        name = test_case['name'].split('[')
        case_name = name[1][:-1]
        return case_name

    @classmethod
    def get_parameters(cls, test_case):
        """获取allure报告中的parameters的参数内容，请求前的数据，用于兼容用例执行异常，未发送请求导致的情况"""
        parameters = test_case['parameters'][0]['value']
        return ast.literal_eval(parameters)

    @classmethod
    def get_test_stage(cls, test_case):
        """获取allure报告中请求后的数据"""
        test_stage = test_case['testStage']['steps']
        return test_stage

    def get_case_url(self, test_case):
        """获取测试用例的url"""
        # 判断用例步骤中的数据是否异常
        if test_case['testStage']['status'] == 'broken':
            # 如果异常状态下，则获取请求前的数据
            _url = self.get_parameters(test_case)['url']
        else:
            # 否则拿请求步骤的数据，因为如果设计到依赖，会获取多组，因此我们只取最后一组数据内容
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
        """获取用例中的请求头"""
        if test_case['testStage']['status'] == 'broken':
            _headers = self.get_parameters(test_case)['headers']
        else:
            # 如果用例请求成功，则从allure附件中获取请求头部信息
            _headers_attachment = self.get_test_stage(test_case)[-5]['attachments'][0]['source']
            path = ensure_path_sep("\\report\\html\\data\\attachments\\" + _headers_attachment)
            with open(path, 'r', encoding='utf-8') as file:
                _headers = json.load(file)
            return _headers

    def get_request_type(self, test_case):
        """获取用例的请求类型"""
        request_type = self.get_parameters(test_case)['requestType']
        return request_type