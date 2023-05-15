from common.setting import ensure_path_sep
from utils.other_tools.modles import Config
from utils.read_files_tools.yaml_control import GetYamlData


# 获取yaml文件中的数据
_data = GetYamlData(ensure_path_sep('\\common\\config.yaml')).get_yaml_data()
config = Config(**_data)