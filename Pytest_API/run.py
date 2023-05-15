import os
import pytest
from utils import config
from utils.logging_tool.log_control import INFO


def run():
    # 在日志中添加信息
    INFO.logger.info("开始执行{}项目".format(config.project_name))
    """
    运行pytest测试用例并生成测报告
    -s:显示程序中的print/logging输出
    '-W', 'ignore:Module already imported:pytest.PytestWaring': 忽略pytest重复导入模块的警告信息
    '--alluredir', './report/tmp': 表示生成测试报告的目录
    '--clean-alluredir': 表示生成测试报告前清空测试报告目录
    """
    pytest.main(['-s', '-W', 'ignore:Module already imported:pytest.PytestWaring', '--alluredir', './report/tmp', '--clean-alluredir'])
    """
    将之前生成都测试报告文件转换成HTML格式，并输出到指定目录
    generate: 生成测试报告
    ./report/tmp: 测试报告文件所在的路径
    -o ./report/html: 将生成的HTML格式的测试报告输出到指定路径中
    --clean: 在生成测试报告前清空目录
    """
    os.system(r'allure generate ./report/tmp -o ./report/html --clean')


if __name__ == '__main__':
    run()