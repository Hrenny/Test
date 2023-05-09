import json

import allure

from utils.other_tools.modles import AllureAttachmentType


def allure_step(step: str, var: str):
    """
    :param step: ���輰��������
    :param var: ��������
    :return:
    """
    with allure.step(step):
        allure.attach(
            json.dump(
                str(var),
                ensure_ascii=False,
                indent=4),
            step, allure.attachment_type.JSON)


def allure_attach(source: str, name: str, extension: str):
    """
    allure�����ϴ�������ͼƬ��excel
    :param source: �ļ�·��
    :param name: ��������
    :param extension: ������չ����
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
    �޸����Ĳ�������
    :param step: ��������
    :return:
    """
    with allure.step(step):
        pass