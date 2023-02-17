import smtplib
from email.mime.text import MIMEText
from utils.other_tools.allure_data.allure_report_data import TestMetrics, AllureFileClean
from utils import config


class SendEmail:
    """发送邮箱"""
    def __init__(self, metrics: TestMetrics):
        self.metics = metrics
        self.allure_data = AllureFileClean()
        self.CaseDetail = self.allure_data.get_failed_cases_detail()

    @classmethod
    def send_mail(cls, user_list: list, sub, content: str) -> None:
        """
        :param user_list: 发件人邮箱
        :param sub:
        :param content: 发送内容
        :return:
        """
        user = "Hrenny" + "<" + config.email.send_user + ">"
        message = MIMEText(content, _subtype='plain', _charset='utf-8')
        message['Subject'] = sub
        message['From'] = user
        message['To'] = ";".join(user_list)
        server = smtplib.SMTP()
        server.connect(config.email.email_host)
        server.login(config.email.send_user, config.email.stamp_key)
        server.sendmail(user, user_list, message.as_string())
        server.close()

    def error_mail(self, error_message: str) -> None:
        """
        执行异常邮件通知
        :param error_message: 报错信息
        :return:
        """
        email = config.email.send_list
        user_list = email.split(',')
        sub = config.project_name + '接口自动化执行异常通知'
        content = f"自动化测试执行完毕，程序中发现异常，请须知。报错信息如下：\n{error_message}"
        self.send_mail(user_list, sub, content)

    def send_main(self) -> None:
        """发送邮件"""
        email = config.email.send_list
        user_list = email.split(',')
        sub = config.project_name + '接口自动化报告'
        content = f"""
        各位同事，大家好：
                自动化用例执行完成，执行结果如下：
                用例运行总数：{self.metics.total}个
                通过用例个数：{self.metics.passed}个
                失败用例个数：{self.metics.failed}个
                异常用例个数：{self.metics.broken}个
                跳过用例个数：{self.metics.skipped}个
                成 功 率：{self.metics.pass_rate} %
        {self.allure_data.get_failed_cases_detail()}
                """
        self.send_mail(user_list, sub, content)


if __name__ == '__main__':
    SendEmail(AllureFileClean().get_case_count()).send_mail()