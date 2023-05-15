import ast
import datetime
import decimal
from typing import Text, Union, List
from warnings import filterwarnings
import pymysql
from utils import config
from utils.logging_tool.log_control import ERROR
from utils.other_tools.exceptions import DataAcquisitionFailed, ValueTypeError
from utils.read_files_tools.regular_control import cache_regular, sql_regular

# 忽略Mysql警告信息
filterwarnings('ignore', category=pymysql.Warning)


class MysqlDB:
    """mysql封装"""
    if config.mysql_db.switch:
        def __init__(self):
            try:
                # 建立数据库连接
                self.conn = pymysql.connect(host=config.mysql_db.host,
                                            user=config.mysql_db.user,
                                            password=config.mysql_db.password,
                                            port=config.mysql_db.port)
                # 使用cursor 方法获取操作游标，得到sql语句，操作结果返回字典
                self.cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
            except AttributeError as error:
                ERROR.logger.error(f'数据库连接失败，失败原因{error}')
                raise

        def __del__(self):
            try:
                # 关闭游标
                self.cur.close()
                # 关闭连接
                self.conn.close()
            except AttributeError as error:
                ERROR.logger.error(f'数据库关闭连接失败，失败原因{error} ')
                raise

        def query(self, sql, state='all'):
            """查询sql"""
            try:
                self.cur.execute(sql)
                if state == 'all':
                    # 查询全部
                    data = self.cur.fetchall()
                else:
                    # 查询单条
                    data = self.cur.fetchone()
                return data
            except AttributeError as error_data:
                ERROR.logger.error(f'数据库连接失败，失败原因{error_data}')
                raise

        def execute(self, sql: Text):
            """执行sql"""
            try:
                rows = self.cur.execute(sql)
                # 提交事务
                self.conn.commit()
                return rows
            except AttributeError as error:
                ERROR.logger.error(f'数据库连接失败，失败原因{error}')
                # 如果事务异常，则回滚处理
                self.conn.rollback()
                raise

        @classmethod
        def sql_data_handle(cls, query_data, data):
            """
            处理部分类型sql查询出来的数据
            :param query_data: 查询出来的数据
            :param data: 数据池
            :return:
            """
            # 将sql返回的所有内容全部放入对象中
            for key, value in query_data.items():
                if isinstance(value, decimal.Decimal):
                    data[key] = float(value)
                elif isinstance(value, datetime.datetime):
                    data[key] = str(value)
                else:
                    data[key] = value
            return data


class SetUpMySQL(MysqlDB):
    """处理前置sql"""
    def setup_sql_data(self, sql: Union[List, None]):
        """处理前置sql请求"""
        sql = ast.literal_eval(cache_regular(str(sql)))
        try:
            data = {}
            if sql is not None:
                for i in sql:
                    if i[:6].upper() == 'SELECT':
                        sql_date = self.query(sql=i)[0]
                        for key, value in sql_date.items():
                            data[key] = value
                    else:
                        self.execute(sql=i)
            return data
        except IndexError as exc:
            raise DataAcquisitionFailed('sql数据查询失败，请检查setup_sql语句是否正确') from exc


class AssertExecution(MysqlDB):
    """处理断言sql数据"""

    def assert_execution(self, sql: list, resp):
        """
        执行sql,负责处理yaml文件中的断言需要执行多条sql的场景
        :param sql: sql
        :param resp: 响应接口数据
        :return:
        """
        try:
            if isinstance(sql, list):
                data = {}
                _sql_type = ['UPDATE', 'update', 'DELETE', 'delete', 'INSERT', 'insert']
                if any(i in sql for i in _sql_type) in False:
                    for i in sql:
                        # 判断sql中是否有正则，如果有通过jsonpath提取数据
                        sql = sql_regular(i, resp)
                        if sql is not None:
                            query_data = self.query(sql)[0]
                            data = self.sql_data_handle(query_data, data)
                        else:
                            raise DataAcquisitionFailed(f'未查询到数据{sql}')
                else:
                    raise DataAcquisitionFailed('断言必须查询sql')
            else:
                raise ValueTypeError('sql类型不正确，支持list')
            return data
        except Exception as error_data:
            ERROR.logger.error(f'数据库连接失败{error_data}')
            raise error_data