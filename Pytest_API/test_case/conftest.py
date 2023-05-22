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
        "accountName": 'daji123',
        "password": 'ce95d82ecc12df0b94137c6145b7a807'
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
    # 提取token
    login_token = res.json()['data']['token']
    # 存入缓存
    CacheHandler.update_cache(cache_name='login_token', value=login_token)


def pytest_collection_modifyitems(items):
    """用例收集完成时，将收集到的item的name和node_id显示在控制台"""
    # 遍历用例
    for item in items:
        # 对用例进行编码和解码，用于处理用例中的特殊字符，保证正确性
        item.name = item.name.encode('utf-8').decode('unicode_escape')
        item._nodeid = item.nodeid.encode('utf-8').decode('unicode_escape')
    # 期望用例执行的顺序
    appoint_items = ['test_login']
    # 存储需要执行的测试用例
    run_items = []
    # 遍历列表
    for i in appoint_items:
        # 遍历用例
        for item in items:
            # 提取模块名
            module_item = item.name.split("[")[0]
            # 判断模块是否在列表中
            if i == module_item:
                # 添加进列表
                run_items.append(item)
    # 遍历列表
    for i in run_items:
        # 获取下表索引
        run_index = run_items.index(i)
        items_index = items.index(i)
        # 判断索引是否相等
        if run_index != items_index:
            # 不相等则交换用例位置
            n_data = items[run_index]
            run_index = items.index(n_data)
            items[items_index], items[run_index] = items[run_index], items[items_index]


def pytest_configure(config):
    """添加自定义标记"""
    config.addinivalue_line('markers', 'smoke')
    config.addinivalue_line('markers', '回归测试')


# 每个测试用例函数执行前自动执行
@pytest.fixture(scope='function', autouse=True)
def case_skip(in_data):
    """处理跳过用例"""
    # 获取用例数据
    in_data = TestCase(**in_data)
    # 判断用例是否设置跳过
    if ast.literal_eval(cache_regular(str(in_data.is_run))) is False:
        """使用allure动态生成测试报告"""
        # 生成标题
        allure.dynamic.title(in_data.detail)
        # 添加测试步骤
        allure_step_no(f'请求URL:{in_data.is_run}')
        allure_step_no(f'请求方式:{in_data.method}')
        allure_step('请求头:', in_data.headers)
        allure_step('请求数据:', in_data.data)
        allure_step('依赖数据:', in_data.dependence_case_data)
        allure_step('预期数据：', in_data.assert_data)
        # 跳过用例
        pytest.skip()


def pytest_terminal_summary(terminalreporter):
    """收集测试结果"""
    # 统计测试通过的用例数
    _PASSED = len([i for i in terminalreporter.stats.get('passed', []) if i.when != 'teardown'])
    # 统计测试异常的用例数
    _ERROR = len([i for i in terminalreporter.stats.get('error', []) if i.when != 'teardown'])
    # 统计测试失败的用例数
    _FAILED = len([i for i in terminalreporter.stats.get('failed', []) if i.when != 'teardown'])
    # 统计测试跳过的用例
    _SKIPPED = len([i for i in terminalreporter.stats.get('skipped', []) if i.when != 'teardown'])
    # 统计测试用例数
    _TOTAL = terminalreporter._numcollected
    # 统计测试用例执行时间
    _TIMES = time.time() - terminalreporter._sessionstarttime
    # 记录日志
    INFO.logger.info(f"用例总数: {_TOTAL}")
    INFO.logger.info(f"异常用例数: {_ERROR}")
    ERROR.logger.error(f"失败用例数: {_FAILED}")
    WARNING.logger.warning(f"跳过用例数: {_SKIPPED}")
    INFO.logger.info("用例执行时长: %.2f" % _TIMES + " s")
    try:
        # 计算用例成功率
        _RATE = _PASSED / _TOTAL * 100
        INFO.logger.info('用例成功率: %.2f' % _RATE + '%')
    except ZeroDivisionError:
        INFO.logger.info('用例成功率: 0.00%')