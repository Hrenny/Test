def jsonpath_replace(change_data, key_name, data_switch=None):
    """
    处理jsonpath请求
    :param change_data: 需要替换的json路径
    :param key_name: 需要替换的键名
    :param data_switch: 是否需要对data进行特殊处理
    :return:
    """
    _new_data = key_name + ''
    # 遍历列表
    for i in change_data:
        if i == '$':
            pass
        elif data_switch is not None and i == 'data':
            _new_data += '.data'
        # 判断元素为列表
        elif i[0] == '[' and i[-1] == ']':
            _new_data += '[' + i[1:-1] + ']'
        else:
            _new_data += '[' + '"' + i + '"' + ']'
    return _new_data