import os


def get_all_files(file_path, yaml_data_switch=False):
    """
    获取文件路径
    :param file_path: 目录路径
    :param yaml_data_switch: 是否过滤yaml文件
    :return:
    """
    # 存储目录中发现的所有文件路径
    filename = []
    # root：获取根目录路径  dirs：子目录名称 files：文件名称
    for root, dirs, files in os.walk(file_path):
        # 遍历文件名
        for _file_path in files:
            # 拼接路径
            path = os.path.join(root, _file_path)
            # 过滤yaml文件是否开启
            if yaml_data_switch:
                # 判断文件路径中是否包含yaml和yml
                if 'yaml' in path or '.yml' in path:
                    # 将yaml文件路径添加进列表
                    filename.append(path)
            else:
                # 所有文件路径添加进列表
                filename.append(path)
    return filename