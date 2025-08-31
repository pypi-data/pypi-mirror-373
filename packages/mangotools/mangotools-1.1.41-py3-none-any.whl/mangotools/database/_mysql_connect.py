# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2023-09-09 23:17
# @Author : 毛鹏
import pymysql
from pymysql.err import InternalError, OperationalError, ProgrammingError
from pymysql.cursors import DictCursor

from ..exceptions import MangoToolsError
from ..exceptions.error_msg import ERROR_MSG_0001, ERROR_MSG_0033, ERROR_MSG_0035, ERROR_MSG_0034
from ..models import MysqlConingModel


class MysqlConnect:

    def __init__(self, mysql_config: MysqlConingModel, is_c: bool = True, is_rud: bool = False):
        self.is_c = is_c
        self.is_rud = is_rud
        try:
            self.connection = pymysql.connect(
                host=mysql_config.host,
                port=mysql_config.port,
                user=mysql_config.user,
                password=mysql_config.password,
                database=mysql_config.database,
                autocommit=True,
                cursorclass=DictCursor
            )
        except OperationalError:
            raise MangoToolsError(*ERROR_MSG_0001)
        except InternalError:
            raise MangoToolsError(*ERROR_MSG_0033, value=(mysql_config.database,))

    def __del__(self):
        if hasattr(self, 'connection') and self.connection:
            self.close()

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def condition_execute(self, sql: str) -> list[dict] | list | int | None:
        if sql is None or sql == '':
            return None
        sql_upper = sql.strip().upper()
        is_select = (sql_upper.startswith(('SELECT', 'WITH')) or
                     'SELECT' in sql_upper.split(None, 1)[0])

        if is_select:
            if self.is_c:
                return self.execute(sql)
        else:
            if self.is_rud:
                return self.execute(sql)

    def execute(self, sql) -> list[dict] | int | list:
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(sql)
                sql_upper = sql.strip().upper()
                is_select = (sql_upper.startswith(('SELECT', 'WITH')) or
                             'SELECT' in sql_upper.split(None, 1)[0])

                if is_select:
                    return cursor.fetchall()
                else:
                    result = cursor.rowcount
                    self.connection.commit()
                    return result

            except ProgrammingError:
                raise MangoToolsError(*ERROR_MSG_0034, value=(sql,))
            except InternalError:
                raise MangoToolsError(*ERROR_MSG_0035)
            except OperationalError:
                raise MangoToolsError(*ERROR_MSG_0034, value=(sql,))