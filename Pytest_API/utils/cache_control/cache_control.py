import os
from typing import Text, Any, Union
from common.setting import ensure_path_sep
from utils.other_tools.exceptions import ValueNotFoundError


class Cache:
    """设置、读取缓存"""
    def __init__(self, filename: Union[Text, None]):
        # 如果filename不为空，则操作指定文件内容
        if filename:
            self.path = ensure_path_sep("\\cache" + filename)
        # 如果filename为空，则操作所有文件内容
        else:
            self.path = ensure_path_sep("\\cache")

    def set_cache(self, key: Text, value: Any):
        """设置单字典类型缓存数据，如文件存在，替换文件内容"""
        with open(self.path, 'w', encoding='utf-8') as file:
            file.write(str({key: value}))

    def set_caches(self, value: Any):
        """设置多组缓存"""
        # 已写的方式打开文件，写入数据
        with open(self.path, 'w', encoding='utf-8') as file:
            file.write(str(value))

    def get_cache(self):
        """获取缓存数据"""
        try:
            # 读取文件
            with open(self.path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            pass

    def clean_cache(self):
        """删除指定缓存文件"""
        # 判断路径下不存在文件
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"要删除的文件不存在{self.path}")
        # 删除文件
        os.remove(self.path)

    @classmethod  # 类方法
    def clean_all_cache(cls):
        """删除所有缓存文件"""
        # 获取文件路径
        cache_path = ensure_path_sep("\\cache")
        # 将目录下的所有文件生成一个列表
        list_dir = os.listdir(cache_path)
        # 遍历删除文件
        for i in list_dir:
            os.remove(cache_path + i)


_cache_config = {}


class CacheHandler:
    @staticmethod  # 静态方法
    def get_cache(cache_data):
        """从缓存中获取指定的缓存数据"""
        try:
            return _cache_config[cache_data]
        except KeyError:
            raise ValueNotFoundError(f"{cache_data}的缓存数据未找到，请检查是否将该数据存入缓存中")

    @staticmethod
    def update_cache(*, cache_name, value):
        """更新缓存中的名称和值"""
        _cache_config[cache_name] = value