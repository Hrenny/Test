import json

from common.setting import ensure_path_sep
from utils.other_tools.modles import TestMetrics
from utils.read_files_tools.get_all_files_path import get_all_files


class AllureFileClean:
    """allure报告数据清洗，提取业务需要的数据"""
    @classmethod
    def get_testcases(cls):
        """获取所有allure报告中执行用例的情况"""
        # 将所有数据都收集到files中
        files = []
        for i in get_all_files(ensure_path_sep('\\report\\html\\data\\test-cases')):
            with open(i, 'r', encoding='utf-8') as file:
                date = json.load(file)
                files.append(date)
        return files

    def get_failed_case(self):
        """获取所有失败的用例标题和用例代码路径"""
        error_case = []
        for i in self.get_testcases():
            if i['status'] == 'failed' or i['status'] == 'broken':
                error_case.append((i['name'], i['fillName']))
        return error_case

    def get_failed_cases_detail(self):
        """返回所有失败的测试用例相关数据"""
        date = self.get_failed_case()
        values = ''
        # 判断是否有失败内容
        if len(date) >= 1:
            values = '失败用例：\n'
            values += ' *******************\n'
            for i in date:
                values += '       ' + i[0] + ':' + i[1] + '\n'
        return values

    @classmethod
    def get_case_count(cls):
        """统计用例数量"""
        try:
            file_name = ensure_path_sep('\\report\\html\\widgets\\summary.json')
            with open(file_name, 'r', encoding='utf-8') as file:
                data = json.load(file)
            _case_count = data['statistic']
            _time = data['time']
            keep_keys = {'passed', 'failed', 'broken', 'skipped', 'total'}
            run_case_data = {k: v for k,  v in data['statistic'].items() if k in keep_keys}
            # 判断用例总数不为空
            if _case_count['total'] > 0:
                # 计算用例成功率
                run_case_data['pass_rate'] = round(
                    (_case_count['passed'] + _case_count['skipped']) / _case_count['total'] * 100, 2
                )
            else:
                run_case_data['pass_rate'] = 0.0
            # 收集用例运行时长
            run_case_data['time'] = _time if run_case_data['total'] == 0 else round(_time['duration'] / 1000, 2)
            return TestMetrics(**run_case_data)
        except FileNotFoundError as exc:
            raise FileNotFoundError('程序中检查到未生成allure报告') from exc