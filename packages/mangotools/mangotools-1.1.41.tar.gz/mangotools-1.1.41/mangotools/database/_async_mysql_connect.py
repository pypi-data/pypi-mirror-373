# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2023-09-09 23:17
# @Author : 毛鹏
import aiomysql
from aiomysql import OperationalError, InternalError, ProgrammingError

from ..exceptions import MangoToolsError
from ..exceptions.error_msg import ERROR_MSG_0001, ERROR_MSG_0033, ERROR_MSG_0035, ERROR_MSG_0034
from ..models import MysqlConingModel


class AsyncMysqlConnect:
    """异步MySQL连接池工具类"""

    def __init__(self, mysql_config: MysqlConingModel, is_c: bool = True, is_rud: bool = False):
        self.is_c = is_c
        self.is_rud = is_rud
        self.mysql_config = mysql_config
        self.pool = None

    async def initialize(self):
        """初始化连接池（需显式调用）"""
        try:
            self.pool = await aiomysql.create_pool(
                host=self.mysql_config.host,
                port=self.mysql_config.port,
                user=self.mysql_config.user,
                password=self.mysql_config.password,
                db=self.mysql_config.database,
                autocommit=True,
                minsize=1,
                maxsize=50  # 可根据并发需求调整
            )
        except OperationalError:
            raise MangoToolsError(*ERROR_MSG_0001)
        except InternalError:
            raise MangoToolsError(*ERROR_MSG_0033, value=(self.mysql_config.database,))

    async def close(self):
        """关闭连接池"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            self.pool = None

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def condition_execute(self, sql: str) -> list[dict] | list | int | None:
        """条件执行SQL（根据is_c/is_rud判断是否执行）"""
        if sql is None or sql == '':
            return None
        if sql.strip().upper().startswith('SELECT'):
            if self.is_c:
                return await self.execute(sql)
        else:
            if self.is_rud:
                return await self.execute(sql)

    async def execute(self, sql: str) -> list[dict] | int:
        """执行SQL并返回结果"""
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                try:
                    await cursor.execute(sql)
                except ProgrammingError:
                    raise MangoToolsError(*ERROR_MSG_0034, value=(sql,))
                except InternalError:
                    raise MangoToolsError(*ERROR_MSG_0035)
                except OperationalError:
                    raise MangoToolsError(*ERROR_MSG_0034, value=(sql,))

                if sql.strip().upper().startswith('SELECT'):
                    return await cursor.fetchall()
                else:
                    await conn.commit()
                    return cursor.rowcount
