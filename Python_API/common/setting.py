import os


def root_path():
    """获取根路径"""
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return path


def ensure_path_sep(path):
    """兼容windowns和Linux不同环境的操作系统路径"""
    if '/' in path:
        path = os.sep.join(path.split('/'))
    if '\\' in path:
        path = os.sep.join(path.split('\\'))
    return root_path() + path