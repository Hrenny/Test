"""缓存文件处理"""
import os
from typing import Any, Text, Union
from common.setting import ensure_path_sep
from utils.other_tools.exceptions import ValueNotFoundError


class Cache:
    """设置读取缓存"""
    def __init__(self, filename: Union[Text, None]) -> None:
        # 如果filename不为空，则操作指定文件内容
        if filename:
            self.path = ensure_path_sep('\\cache' + filename)
        # 如果filename为None，则操作所有文件内容
        else:
            self.path = ensure_path_sep('\\cache')

    def set_cache(self, key: Text, value: Any) -> None:
        """设置缓存，只支持设置单字典类型缓存数据，缓存文件如存在，则替换之前的缓存内容"""
        with open(self.path, 'w', encoding='utf-8') as file:
            file.write(str({key: value}))

    def set_caches(self, value: Any) -> None:
        """设置多组缓存数据"""
        with open(self.path, 'w', encoding='utf-8') as file:
            file.write(str(value))

    def get_cache(self) -> Any:
        """获取缓存数据"""
        try:
            with open(self.path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            pass

    def clean_cache(self) -> None:
        """删除缓存文件"""
        if not os.path.exists(self.path):
            raise FileNotFoundError(f'您要删除的缓存文件不存在{self.path}')
        os.remove(self.path)

    @classmethod
    def clean_all_cache(cls) -> None:
        """清楚所有缓存文件"""
        cache_path = ensure_path_sep('\\cache')
        # 列出目录下所有文件，生成的一个list
        list_dir = os.listdir(cache_path)
        for i in list_dir:
            # 循环删除文件夹下的所有内容
            os.remove(cache_path + i)

_cache_config = {}


class CacheHandler:
    @staticmethod
    def get_cache(cache_date):
        try:
            return _cache_config[cache_date]
        except KeyError:
            raise ValueNotFoundError(f'{cache_date}的缓存数据未找到，请检查是否将该数据存入缓存中')

    @staticmethod
    def update_cache(*, cache_name, value):
        _cache_config[cache_name] = value