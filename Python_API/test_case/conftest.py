import ast
import time

import allure
import pytest
import requests

from common.setting import ensure_path_sep
from utils.cache_control.cache_control import CacheHandler
from utils.logging_tool.log_control import INFO, ERROR, WARNING
from utils.other_tools.allure_data.allure_tools import allure_step_no, allure_step
from utils.other_tools.modles import TestCase
from utils.read_files_tools.clean_files import del_file
from utils.read_files_tools.regular_control import cache_regular


@pytest.fixture(scope='session', autouse=False)
def clear_report():
    """手动删除报告"""
    del_file(ensure_path_sep('\\report'))


@pytest.fixture(scope='session', autouse=True)
def work_login_init():
    """获取登录的token"""
    url = 'http://test.api.yiyouliao.com/rivers/web/account/login'
    data = {
        "accountName": "daji123",
        "password": "ce95d82ecc12df0b94137c6145b7a807"
    }
    headers = {'Content-Type': 'application/json'}
    """
    发送post请求
    url: 请求地址
    data: 请求的数据
    verify: 是否验证SSL证书，默认为True
    headers: HTTP请求头
    """
    res = requests.post(url=url, json=data, verify=True, headers=headers)
    login_token = res.json()['data']['token']
    CacheHandler.update_cache(cache_name='login_token', value=login_token)


def pytest_collection_modifyitems(items):
    """用例收集完成时，将收集到的item的name和node_id显示在控制台"""
    for item in items:
        item.name = item.name.encode('utf-8').decode('unicode_escape')
        item._nodeid = item.nodeid.encode('utf-8').decode('unicode_escape')
    appoint_items = []
    run_items = []
    for i in appoint_items:
        for item in items:
            module_item = item.name.split("[")[0]
            if i == module_item:
                run_items.append(item)
    for i in run_items:
        run_index = run_items.index(i)
        items_index = items.index(i)
        if run_index != items_index:
            n_data = items[run_index]
            run_index = items.index(n_data)
            items[items_index], items[run_index] = items[run_index], items[items_index]


def pytest_configure(config):
    config.addinivalue_line('markers', 'smoke')
    config.addinivalue_line('markers', '回归测试')


@pytest.fixture(scope='function', autouse=True)
def case_skip(in_data):
    """处理跳过用例"""
    in_data = TestCase(**in_data)
    if ast.literal_eval(cache_regular(str(in_data.is_run))) is False:
        allure.dynamic.title(in_data.detail)
        allure_step_no(f'请求URL:{in_data.is_run}')
        allure_step_no(f'请求方式:{in_data.method}')
        allure_step('请求头:', in_data.headers)
        allure_step('请求数据:', in_data.data)
        allure_step('依赖数据:', in_data.dependence_case_data)
        allure_step('预期数据：', in_data.assert_data)
        pytest.skip()


def pytest_terminal_summary(terminalreporter):
    """收集测试结果"""
    _PASSED = len([i for i in terminalreporter.stats.get('passed', []) if i.when != 'teardown'])
    _ERROR = len([i for i in terminalreporter.stats.get('error', []) if i.when != 'teardown'])
    _FAILED = len([i for i in terminalreporter.stats.get('failed', []) if i.when != 'teardown'])
    _SKIPPED = len([i for i in terminalreporter.stats.get('skipped', []) if i.when != 'teardown'])
    _TOTAL = terminalreporter._numcollected
    _TIMES = time.time() - terminalreporter._sessionstarttime
    INFO.logger.error(f"用例总数: {_TOTAL}")
    INFO.logger.error(f"异常用例数: {_ERROR}")
    ERROR.logger.error(f"失败用例数: {_FAILED}")
    WARNING.logger.warning(f"跳过用例数: {_SKIPPED}")
    INFO.logger.info("用例执行时长: %.2f" % _TIMES + " s")
    try:
        _RATE = _PASSED / _TOTAL * 100
        INFO.logger.info('用例成功率: %.2f' % _RATE + '%')
    except ZeroDivisionError:
        INFO.logger.info('用例成功率: 0.00%')