import re
import time
from sqlalchemy.engine.default import DefaultDialect
from sqlalchemy.engine.interfaces import DBAPICursor, DBAPIConnection

from ysdb.ysdbLib import RdbClient, HisQuery


class RdbDialect(DefaultDialect):
    name = 'rdb'
    driver = 'rdb'

    @classmethod
    def dbapi(cls):
        return MockDBAPI()

    # def do_execute(self, cursor, statement, parameters, context=None):
    #     cursor.execute(statement, parameters)


class MockDBAPI():
    paramstyle = "pyformat"

    def connect(self, *args, **kwargs):
        return MockConnection()

    class Error(Exception):
        pass

    class OperationalError(Error):
        pass


class MockConnection(DBAPIConnection):
    def __init__(self):
        self.client = RdbClient()
        self.client.connect("192.168.130.13", 30221)

    def rollback(self):
        pass

    def cursor(self):
        return MockCursor(self)

    def close(self):
        self.client.disconnect()


class MockCursor():
    def __init__(self, connection):
        self.connection: MockConnection = connection
        self.statement_id = self._create_statement()
        self.result = None
        self.row_iter = iter([])

    def _create_statement(self):
        return 1

    def execute(self, query, parameters=None):
        startTm = int(time.time()) - 500000
        endTm = int(time.time())

        # 解析 SQL 查询以提取列名
        match = re.search(r'SELECT\s+(.*?)\s+FROM', query, re.IGNORECASE | re.DOTALL)
        if match:
            columns_str = match.group(1)
            # 处理列名，可能包括别名、函数等
            self.column_names = [col.strip() for col in columns_str.split(',')]
            print("Extracted columns:", self.column_names)
        else:
            self.column_names = []
            print("No columns found or not a SELECT statement")
        hisQueries = [HisQuery(0, 1, b'', startTm, 0, endTm, 0, 0, 0) for column in self.column_names]
        retHisDatas = self.connection.client.readPointHisDatas(hisQueries)
        self.result = [item for item in retHisDatas]
        print(self.result)
        self.row_iter = iter(self.result)
        self.description = [('col1', None, None, None, None, None, None)]
        # pass

    def fetchall(self):
        return list(self.row_iter)

    def close(self):
        pass

    def executemany(self, query, param_list):
        pass

    def fetchone(self):
        pass
