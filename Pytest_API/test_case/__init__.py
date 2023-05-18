from common.setting import ensure_path_sep
from utils.read_files_tools.get_all_files_path import get_all_files
from utils.read_files_tools.get_yaml_data_analysis import CaseData
from utils.cache_control.cache_control import _cache_config, CacheHandler


def write_case_process():
    """获取所有用例，写入用例池"""
    # 遍历拿到所有存放用例的文件路径
    for i in get_all_files(file_path=ensure_path_sep('\\data'), yaml_data_switch=True):
        # 处理用例数据，获取测试用例列表
        case_process = CaseData(i).case_process(case_id_switch=True)
        # 判断列表不为空
        if case_process is not None:
            # 遍历列表中的用例
            for case in case_process:
                # 遍历用例中的数据
                for k, v in case.items():
                    # 判断case_id是否存在
                    case_id_exit = k in _cache_config.keys()
                    # 如果case_id 不存在，则将用例写入缓存池中
                    if case_id_exit is False:
                        # 将用例数据添加到缓存中
                        CacheHandler.update_cache(cache_name=k, value=v)
                    elif case_id_exit is True:
                        raise ValueError(f'case_id: {k} 存在重复项， 请修改case_id\n'
                                         f'文件路径：{i}')


write_case_process()