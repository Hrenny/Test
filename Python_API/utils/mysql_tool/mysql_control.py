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

# ����Mysql������Ϣ
filterwarnings('ignore', category=pymysql.Warning)


class MysqlDB:
    """mysql��װ"""
    if config.mysql_db.switch:
        def __init__(self):
            try:
                # �������ݿ�����
                self.conn = pymysql.connect(host=config.mysql_db.host,
                                            user=config.mysql_db.user,
                                            password=config.mysql_db.password,
                                            port=config.mysql_db.port)
                # ʹ��cursor ������ȡ�����α꣬�õ�sql��䣬������������ֵ�
                self.cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
            except AttributeError as error:
                ERROR.logger.error(f'���ݿ�����ʧ�ܣ�ʧ��ԭ��{error}')
                raise

        def __del__(self):
            try:
                # �ر��α�
                self.cur.close()
                # �ر�����
                self.conn.close()
            except AttributeError as error:
                ERROR.logger.error(f'���ݿ�ر�����ʧ�ܣ�ʧ��ԭ��{error} ')
                raise

        def query(self, sql, state='all'):
            """��ѯsql"""
            try:
                self.cur.execute(sql)
                if state == 'all':
                    # ��ѯȫ��
                    data = self.cur.fetchall()
                else:
                    # ��ѯ����
                    data = self.cur.fetchone()
                return data
            except AttributeError as error_data:
                ERROR.logger.error(f'���ݿ�����ʧ�ܣ�ʧ��ԭ��{error_data}')
                raise

        def execute(self, sql: Text):
            """ִ��sql"""
            try:
                rows = self.cur.execute(sql)
                # �ύ����
                self.conn.commit()
                return rows
            except AttributeError as error:
                ERROR.logger.error(f'���ݿ�����ʧ�ܣ�ʧ��ԭ��{error}')
                # ��������쳣����ع�����
                self.conn.rollback()
                raise

        @classmethod
        def sql_data_handle(cls, query_data, data):
            """
            ����������sql��ѯ����������
            :param query_data: ��ѯ����������
            :param data: ���ݳ�
            :return:
            """
            # ��sql���ص���������ȫ�����������
            for key, value in query_data.items():
                if isinstance(value, decimal.Decimal):
                    data[key] = float(value)
                elif isinstance(value, datetime.datetime):
                    data[key] = str(value)
                else:
                    data[key] = value
            return data


class SetUpMySQL(MysqlDB):
    """����ǰ��sql"""
    def setup_sql_data(self, sql: Union[List, None]):
        """����ǰ��sql����"""
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
            raise DataAcquisitionFailed('sql���ݲ�ѯʧ�ܣ�����setup_sql����Ƿ���ȷ') from exc


class AssertExecution(MysqlDB):
    """�������sql����"""

    def assert_execution(self, sql: list, resp):
        """
        ִ��sql,������yaml�ļ��еĶ�����Ҫִ�ж���sql�ĳ���
        :param sql: sql
        :param resp: ��Ӧ�ӿ�����
        :return:
        """
        try:
            if isinstance(sql, list):
                data = {}
                _sql_type = ['UPDATE', 'update', 'DELETE', 'delete', 'INSERT', 'insert']
                if any(i in sql for i in _sql_type) in False:
                    for i in sql:
                        # �ж�sql���Ƿ������������ͨ��jsonpath��ȡ����
                        sql = sql_regular(i, resp)
                        if sql is not None:
                            query_data = self.query(sql)[0]
                            data = self.sql_data_handle(query_data, data)
                        else:
                            raise DataAcquisitionFailed(f'δ��ѯ������{sql}')
                else:
                    raise DataAcquisitionFailed('���Ա����ѯsql')
            else:
                raise ValueTypeError('sql���Ͳ���ȷ��֧��list')
            return data
        except Exception as error_data:
            ERROR.logger.error(f'���ݿ�����ʧ��{error_data}')
            raise error_data