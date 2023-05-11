import allure
import pytest
from utils.assertion.assert_control import Assert
from utils.read_files_tools.get_yaml_data_analysis import GetTestCase
from utils.read_files_tools.regular_control import regular
from utils.requests_tool.request_control import RequestControl
from utils.requests_tool.teardown_control import TearDownHandler

case_id = ['login_01']
TestData = GetTestCase.case_data(case_id)
re_data = regular(str(TestData))


@allure.epic('百川接口')
@allure.feature('登录模块')
class TestLogin:
    @allure.story('登录')
    @pytest.mark.parametrize('in_data', eval(re_data), ids=[i['detail'] for i in TestData])
    def test_login(self, in_data, case_skip):
        res = RequestControl(in_data).http_request()
        TearDownHandler(res).teardown_handle()
        Assert(assert_data=in_data['assert_data'],
               sql_data=res.sql_data,
               request_data=res.body,
               response_data=res.response_data,
               status_code=res.status_code).assert_type_handle()


if __name__ == '__main__':
    pytest.main(['test_login.py', '-s', '-W', 'ignore:Module already imported:pytest.PytestWaring'])