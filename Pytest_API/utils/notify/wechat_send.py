import requests

from utils import config
from utils.logging_tool.log_control import ERROR
from utils.other_tools.allure_data.allure_report_data import AllureFileClean
from utils.other_tools.exceptions import SendMessageError, ValueTypeError
from utils.other_tools.modles import TestMetrics
from utils.times_tool.time_control import now_time


class WeChatSend:
    def __init__(self, metrics: TestMetrics):
        # 执行完成后的用例数据
        self.metrics = metrics
        # 请求头信息
        self.headers = {'Content-Type': 'application/json'}

    def send_text(self, content, mentioned_mobile_list=None):
        """
        发送文本类型通知
        :param content: 文本内容
        :param mentioned_mobile_list: 手机号列表
        :return:
        """
        _data = {'msgtype': 'text', 'text': {'content': content, 'mentioned_list': None, 'mentioned_mobile_list': mentioned_mobile_list}}
        if mentioned_mobile_list is not None or isinstance(mentioned_mobile_list, list):
            if len(mentioned_mobile_list) >= 1:
                for i in mentioned_mobile_list:
                    if isinstance(i, str):
                        res = requests.post(url=config.wechat.webhook, json=_data, headers=self.headers)
                        if res.json()['errcode'] != 0:
                            ERROR.logger.error(res.json())
                            raise SendMessageError('企业微信发送信息失败')
                    else:
                        raise ValueTypeError('手机号必须是字符串类型')
        else:
            raise ValueTypeError('手机号列表必须是list类型')

    def send_markdown(self, content):
        """
        发送MarkDown类型消息
        :param content: 消息内容
        :return:
        """
        _data = {'msgtype': 'markdown', 'markdown': {'content': content}}
        res = requests.post(url=config.wechat.webhook, json=_data, headers=self.headers)
        if res.json()['errcode'] != 0:
            ERROR.logger.error(res.json())
            raise SendMessageError('企业微信消息发送失败')

    def _upload_file(self, file):
        """文件上传到临时媒体库"""
        key = config.wechat.webhook.split('key=')[1]
        url = f'https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={key}&type=file'
        data = {'file': open(file, 'rb')}
        res = requests.post(url, files=data).json()
        return res['media_id']

    def send_file_msg(self, file):
        """发送文件类型消息"""
        _data = {'msgtype': 'file', 'file': {'media_id': self._upload_file(file)}}
        res = requests.post(url=config.wechat.webhook, json=_data, headers=self.headers)
        if res.json()['errcode'] != 0:
            ERROR.logger.error(res.json())
            raise SendMessageError('企业微信消息发送失败')

    def send_wechat_notification(self):
        """发送企业微信通知"""
        text = f"""[{config.project_name}自动化通知]
                    >测试环境<font color=\"info\">TEST</font>
                    >测试负责人:@{config.tester_name}
                    >
                    > **执行结果**
                    ><font color=\"info\">成  功  率:{self.metrics.pass_rate}%</font>
                    >用例总数: <font color=\"info\">{self.metrics.total}个</font>
                    >成功用例数: <font color=\"info\">{self.metrics.passed}个</font>
                    >失败用例数:{self.metrics.failed}个
                    >异常用例数:{self.metrics.broken}个
                    >跳过用例数: <font color=\"warning\">{self.metrics.skipped}个</font>
                    >用例执行时长: <font color=\"warning\">{self.metrics.time}s</font>
                    >时间: <font color=\"comment\">{now_time()}</font>"""
        WeChatSend(AllureFileClean().get_case_count()).send_markdown(text)
