import os

import pytest

from utils.logging_tool.log_control import INFO


def run():
    INFO.logger.info('开始执行{}项目'.format())
    pytest.main(['-s', '-W', 'ignore:Module already imported:pytest.PytestWaring', '--alluredir', './report/tmp', '--clean-alluredir'])
    os.system(r'allure generate ./report/tmp -o ./report/html --clean')


if __name__ == '__main__':
    run()