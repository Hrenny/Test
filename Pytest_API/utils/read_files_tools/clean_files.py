import os


def del_file(path):
    """删除目录下的文件"""
    # 获取路径下的所有文件和文件夹
    list_path = os.listdir(path)
    for i in list_path:
        # 拼接路径
        c_path = os.path.join(path, i)
        # 判断是否文件夹
        if os.path.isdir(c_path):
            # 删除文件夹下的所有文件和文件夹
            del_file(c_path)
        else:
            # 删除文件
            os.remove(c_path)