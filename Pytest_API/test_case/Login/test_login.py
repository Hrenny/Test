import allure
import pytest
from utils.assertion.assert_control import Assert
from utils.read_files_tools.get_yaml_data_analysis import GetTestCase
from utils.read_files_tools.regular_control import regular
from utils.requests_tool.request_control import RequestControl
from utils.requests_tool.teardown_control import TearDownHandler

case_id = ['login_01']
TestData = GetTestCase.case_data(case_id)
# 获取请求数据
re_data = regular(str(TestData))


@allure.epic('百川接口')  # 项目注解
@allure.feature('登录模块')  # 模块注解
class TestLogin:
    @allure.story('登录')  # 用例注解
    # 对测试用例进行参数化，in_data: 测试用例的参数，ids：用例的标识
    @pytest.mark.parametrize('in_data', eval(re_data), ids=[i['detail'] for i in TestData])
    def test_login(self, in_data, case_skip):
        # 获取响应数据
        res = RequestControl(in_data).http_request()
        # 处理响应结果
        TearDownHandler(res).teardown_handle()
        # 对响应结果进行断言
        Assert(assert_data=in_data['assert_data'],
               sql_data=res.sql_data,
               request_data=res.body,
               response_data=res.response_data,
               status_code=res.status_code).assert_type_handle()


if __name__ == '__main__':
    pytest.main(['test_login.py', '-s', '-W', 'ignore:Module already imported:pytest.PytestWaring'])