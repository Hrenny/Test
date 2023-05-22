import smtplib
from email.mime.text import MIMEText
from utils import config
from utils.other_tools.allure_data.allure_report_data import AllureFileClean, TestMetrics


class SendEmail:

    def __init__(self, metrics: TestMetrics):
        self.metrics = metrics
        self.allure_data = AllureFileClean()
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
        user = config.email.send_user
        message = MIMEText(content)
        message['Subject'] = sub
        message['From'] = user
        message['To'] = ','.join(user_list)
        server = smtplib.SMTP_SSL(config.email.email_host, 465)
        server.login(config.email.send_user, config.email.stamp_key)
        server.sendmail(user, user_list, message.as_string())
        server.quit()

    def error_mail(self, error_message):
        """
        执行异常邮件通知
        :param error_message: 报错信息
        :return:
        """
        email = config.email.send_list
        user_list = email.split(',')
        sub = config.project_name + '接口自动化执行异常通知'
        content = f'自动化测试执行完毕，程序发现异常，请悉知。报错信息如下：\n{error_message}'
        self.send_mail(user_list, sub, content)

    def send_main(self):
        """发送邮件"""
        email = config.email.send_list
        user_list = email.split(',')
        sub = config.project_name + '接口自动化报告'
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
        self.send_mail(user_list, sub, content)


if __name__ == '__main__':
    SendEmail(AllureFileClean().get_case_count()).send_main()