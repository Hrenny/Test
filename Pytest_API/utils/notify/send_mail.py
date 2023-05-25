import smtplib
from email.mime.text import MIMEText
from utils import config
from utils.other_tools.allure_data.allure_report_data import AllureFileClean, TestMetrics


class SendEmail:

    def __init__(self, metrics: TestMetrics):
        # 用例执行完成的数据
        self.metrics = metrics
        self.allure_data = AllureFileClean()
        # 失败用例数据
        self.CaseDetail = self.allure_data.get_failed_cases_detail()

    @classmethod
    def send_mail(cls, user_list, sub, content):
        """
        发送配置
        :param user_list: 发件人邮箱
        :param sub: 邮件标题
        :param content: 发送内容
        :return:
        """
        # 获取发件人邮箱
        user = config.email.send_user
        # 创建对象，保存邮件内容
        message = MIMEText(content)
        # 设置邮件主题
        message['Subject'] = sub
        # 设置发件人
        message['From'] = user
        # 设置收件人
        message['To'] = ','.join(user_list)
        # 创建对象，连接邮件服务器
        server = smtplib.SMTP_SSL(config.email.email_host, 465)
        # 登录邮箱
        server.login(config.email.send_user, config.email.stamp_key)
        # 发送邮件
        server.sendmail(user, user_list, message.as_string())
        # 关闭连接
        server.quit()

    def error_mail(self, error_message):
        """
        执行异常邮件通知
        :param error_message: 报错信息
        :return:
        """
        # 获取收件人列表
        email = config.email.send_list
        # 将收件人列表进行分割转换为列表
        user_list = email.split(',')
        # 设置邮件主题
        sub = config.project_name + '接口自动化执行异常通知'
        # 设置邮箱内容
        content = f'自动化测试执行完毕，程序发现异常，请悉知。报错信息如下：\n{error_message}'
        # 发送邮件
        self.send_mail(user_list, sub, content)

    def send_main(self):
        """发送邮件"""
        # 获取收件人列表
        email = config.email.send_list
        # 将收件人列表进行分割转换为列表
        user_list = email.split(',')
        # 设置邮件主题
        sub = config.project_name + '接口自动化报告'
        # 设置邮箱内容
        content = f"""
        自动化用例执行完成，执行结果如下：
        用例运行总数：{self.metrics.total}个
        通过用例个数：{self.metrics.passed}个
        失败用例个数：{self.metrics.failed}个
        异常用例个数：{self.metrics.broken}个
        跳过用例个数：{self.metrics.skipped}个
        成  功  率：{self.metrics.pass_rate}%
        {self.allure_data.get_failed_cases_detail()}
        """
        # 发送邮件
        self.send_mail(user_list, sub, content)