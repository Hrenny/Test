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
            # 已只读的方式打开文件
            data = open(self.file_dir, 'r', encoding='utf-8')
            # 解析yaml文件中的数据
            res = yaml.load(data, Loader=yaml.FullLoader)
        else:
            raise FileNotFoundError('文件路径不存在')
        return res

    def write_yaml_data(self, key: str, value):
        """更改yaml文件中的值，并保留注释内容"""
        # 已只读的方式打开文件
        with open(self.file_dir, 'r', encoding='utf-8') as file:
            lines = []
            # 读取文件中所有行，返回列表，进行遍历
            for line in file.readlines():
                if line != '\n':
                    # 添加到列表中
                    lines.append(line)
            # 关闭文件
            file.close()
        # 已写的方式打开文件
        with open(self.file_dir, 'w', encoding='utf-8') as file:
            flag = 0
            # 遍历列表
            for line in lines:
                # 分割字符串，取key值
                left_str = line.split(":")[0]
                # 判断文件中是否存在key，并且没有被注释
                if key == left_str.lstrip() and '#' not in line:
                    # 替换key的value值
                    newline = f'{left_str}: {value}'
                    line = newline
                    # 写入文件
                    file.write(f'{line}\n')
                    flag = 1
                else:
                    # 写入文件
                    file.write(f'{line}')
            # 关闭文件
            file.close()
            return flag


class GetCaseData(GetYamlData):
    """获取测试用例中的数据"""
    def get_different_formats_yaml_data(self):
        """获取兼容不同格式的yaml数据"""
        res_list = []
        # 遍历yaml文件中的数据
        for i in self.get_yaml_data():
            # 添加到列表
            res_list.append(i)
        return res_list

    def get_yaml_case_data(self):
        """获取测试用例数据，转换成指定数据格式"""
        # 获取yaml文件中的数据
        _yaml_data = self.get_yaml_data()
        # 正则处理yaml文件中的数据
        re_data = regular(str(_yaml_data))
        # 将字符串转换成对应的数据类型
        return ast.literal_eval(re_data)