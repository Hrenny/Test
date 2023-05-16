import json

import allure

from utils.other_tools.modles import AllureAttachmentType


def allure_step(step: str, var: str):
    """
    在allure报告中添加步骤和附件
    :param step: 步骤及附件名称
    :param var: 附件内容
    :return:
    """
    # 用例步骤
    with allure.step(step):
        """
        添加附件
        json.dumps()将数据转换为json字符串
        ensure_ascii=False表示允许在JSON字符串中使用非ASCII字符；
        indent=4表示使用4个空格进行缩进
        allure.attachment_type.JSON表示将附件添加为JSON格式的附件
        """
        allure.attach(
            json.dumps(
                str(var),
                ensure_ascii=False,
                indent=4),
            step, allure.attachment_type.JSON)


def allure_attach(source: str, name: str, extension: str):
    """
    allure报告上传附件、图片、excel
    :param source: 文件路径
    :param name: 附件名称
    :param extension: 附件扩展名称
    :return:
    """
    _name = name.split('.')[-1].upper()
    _attachment_type = getattr(AllureAttachmentType, _name, None)
    allure.attach.file(
        source=source,
        name=name,
        attachment_type=_attachment_type if _attachment_type is None else _attachment_type.value,
        extension=extension
    )


def allure_step_no(step: str):
    """
    无附件的操作步骤
    :param step: 操作名称
    :return:
    """
    with allure.step(step):
        pass