from utils.logging_tool.log_control import ERROR


def execution_duration(number):
    """��װͳ�ƺ���ִ��ʱ��"""
    def decorator(func):
        def swapper(*args, **kwargs):
            res = func(*args, **kwargs)
            run_time = res.res_time
            # ����ʱ������׼������ʱ�����number,��ӡ�������ƺ��������ʱ��
            if run_time > number:
                ERROR.logger.error(
                    "\n==============================================\n"
                    "��������ִ��ʱ��ϳ������ע.\n"
                    "��������ʱ��: %s ms\n"
                    "���������������: %s\n"
                    "================================================="
                    , run_time, res)
            return res
        return swapper
    return decorator