import sqlite3
from typing import Union


class SQLiteConnect:

    def __init__(self, database_path: str):
        self.conn = None
        self.conn = sqlite3.connect(database_path)
        self.cursor = self.conn.cursor()

    def execute(self, sql: str, data: tuple | None = None) -> Union[list[dict], int]:
        if data:
            self.cursor.execute(sql, data)
        else:
            self.cursor.execute(sql)
        if sql.strip().split()[0].upper() == 'SELECT':
            rows = self.cursor.fetchall()
            column_names = [description[0] for description in self.cursor.description]
            result_list = [dict(zip(column_names, row)) for row in rows]
            return result_list
        elif sql.strip().split()[0].upper() in ['INSERT', 'UPDATE']:
            self.conn.commit()
            return self.cursor.rowcount
        elif sql.strip().split()[0].upper() == 'DELETE':
            self.conn.commit()
            return self.cursor.rowcount
        elif sql.strip().split()[0].upper() == 'CREATE':
            self.conn.commit()
            return self.cursor.rowcount
        else:
            self.conn.commit()
            return self.cursor.rowcount

    def close_connection(self) -> None:
        if self.conn:
            self.conn.close()

    def __del__(self):
        if self.conn:
            self.conn.close()
