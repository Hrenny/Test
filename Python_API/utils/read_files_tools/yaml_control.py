import ast
import os.path

import yaml

from utils.read_files_tools.regular_control import regular


class GetYamlData:
    """获取yaml文件中的数据"""
    def __init__(self, file_dir):
        self.file_dir = str(file_dir)

    def get_yaml_data(self):
        """获取yaml中的数据"""
        # 判断文件是否存在
        if os.path.exists(self.file_dir):
            data = open(self.file_dir, 'r', encoding='utf-8')
            res = yaml.load(data, Loader=yaml.FullLoader)
        else:
            raise FileNotFoundError('文件路径不存在')
        return res

    def write_yaml_data(self, key: str, value):
        """更改yaml文件中的值，并保留注释内容"""
        with open(self.file_dir, 'r', encoding='utf-8') as file:
            lines = []
            for line in file.readlines():
                if line != '\n':
                    lines.append(line)
            file.close()
        with open(self.file_dir, 'w', encoding='utf-8') as file:
            flag = 0
            for line in lines:
                left_str = line.split(":")[0]
                if key == left_str.lstrip() and '#' not in line:
                    newline = f'{left_str}: {value}'
                    line = newline
                    file.write(f'{line}\n')
                    flag = 1
                else:
                    file.write(f'{line}')
            file.close()
            return flag


class GetCaseData(GetYamlData):
    """获取测试用例中的数据"""
    def get_different_formats_yaml_data(self):
        """获取兼容不同格式的yaml数据"""
        res_list = []
        for i in self.get_yaml_data():
            res_list.append(i)
        return res_list

    def get_yaml_case_data(self):
        """获取测试用例数据，转换成指定数据格式"""
        _yaml_data = self.get_yaml_data()
        # 正则处理yaml文件中的数据
        re_data = regular(str(_yaml_data))
        return ast.literal_eval(re_data)