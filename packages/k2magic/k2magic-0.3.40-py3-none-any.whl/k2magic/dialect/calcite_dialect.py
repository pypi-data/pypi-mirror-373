import time
from typing import Any, Optional

import requests
from sqlalchemy import Connection, ResultProxy, Integer, Float, String, Boolean, BINARY
from sqlalchemy.engine.default import DefaultDialect


class CalciteDialect(DefaultDialect):
    """
    SQLAlchemy的插件，用于让SQLAlchemy能够访问K2Assets Calcite数据库接口（REST API）。
    这样k2magic sdk可以让分析师用相同的python语法，直接访问oracle等数据库（读写），也可以访问k2a里的repo数据（只读）。
    """
    name = 'calcite'
    driver = 'rest'

    @classmethod
    def dbapi(cls):
        return MockDBAPI()

    def create_connect_args(self, url):
        host = url.host
        port = url.port or 8765
        return [], {
            'host': host,
            'port': port
        }

    def get_table_names(self, connection, schema=None, **kw):
        # 获取所有表名
        calcite_connection = connection.connection  # 获取底层的 CalciteConnection 对象
        payload = {
            'request': 'getTables',
            'connectionId': calcite_connection.connection_id,
            'catalog': None,
            'schemaPattern': schema,
            'tableNamePattern': '%',
            'typeList': ['TABLE']
        }
        response = calcite_connection.session.post(
            calcite_connection.base_url,
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        # [null,"k2repo","my_repo","TABLE",null,null]
        tables = [table[2] for table in response.json()['firstFrame']['rows']]
        return tables

    def get_columns(self, connection, table_name, schema=None, **kw):
        # 获取指定表的列信息
        calcite_connection = connection.connection  # 获取底层的 CalciteConnection 对象
        payload = {
            'request': 'getColumns',
            'connectionId': calcite_connection.connection_id,
            'catalog': None,
            'schemaPattern': schema,
            'tableNamePattern': table_name,
            'columnNamePattern': '%'
        }
        response = calcite_connection.session.post(
            calcite_connection.base_url,
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        columns = []
        for col in response.json()['firstFrame']['rows']:
            dtype = col[4]
            if dtype == 16:  # BOOLEAN NOT NULL
                col_type = Boolean
            elif dtype == 4:  # INTEGER NOT NULL
                col_type = Integer
            elif dtype == 5:  # SMALLINT NOT NULL
                col_type = Integer
            elif dtype == -5:  # BIGINT NOT NULL
                col_type = Integer
            elif dtype == 93:  # TIMESTAMP NOT NULL
                col_type = Integer
            elif dtype == 3:  # DECIMAL NOT NULL
                col_type = Float
            elif dtype == 8:  # DOUBLE NOT NULL
                col_type = Float
            elif dtype == 12:  # VARCHAR NOT NULL
                col_type = String(255)  # Oracle要求指定字段长度
            elif dtype == -2:  # BINARY
                col_type = BINARY(65535)
            else:
                raise ValueError(f"Unsupported data type: {dtype}")
            # [None, 'csvSchema', 'hello1', 'ts', 12, 'VARCHAR NOT NULL', -1, None, None, 10, 0, None, None, None, None, -1, 1, 'NO', None, None, None, None, '', '']
            column_info = {
                'name': col[3],
                'type': col_type,
                'nullable': col[10] == 1
            }
            columns.append(column_info)
        return columns

    def get_pk_constraint(self, connection, table_name, schema=None, **kw):
        return None

    def get_foreign_keys(self, connection, table_name, schema=None, **kw):
        return []

    def get_indexes(self, connection, table_name, schema=None, **kw):
        return []

    def has_table(self, connection: Connection, table_name: str, schema: Optional[str] = None, **kw: Any):
        return True


class MockDBAPI:
    paramstyle = "pyformat"

    def connect(self, *args, **kwargs):
        return CalciteConnection(*args, **kwargs)

    class Error(Exception):
        pass

    class OperationalError(Error):
        pass


class CalciteConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.session = requests.Session()
        self.base_url = f'http://{host}:{port}/'
        self.connection_id = self._open_connection()

    def _open_connection(self):
        connection_id = f"{time.time()}";
        payload = {
            'request': 'openConnection',
            "connectionId": connection_id
        }
        response = self.session.post(
            f'{self.base_url}avatica',
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        return connection_id

    def cursor(self):
        return CalciteCursor(self)

    def close(self):
        payload = {
            'request': 'closeConnection',
            'connectionId': self.connection_id
        }
        self.session.post(
            f'{self.base_url}avatica',
            json=payload,
            headers={'Content-Type': 'application/json'}
        )

    def commit(self):
        # 假设 commit 不做实际操作
        pass

    def rollback(self):
        # 假设 rollback 不做实际操作
        pass


class CalciteCursor:
    def __init__(self, connection):
        self.connection = connection
        self.statement_id = self._create_statement()
        self.result = None
        self.row_iter = iter([])
        self.description = None  # 初始化 description 属性

    def _create_statement(self):
        payload = {
            'request': 'createStatement',
            'connectionId': self.connection.connection_id
        }
        response = self.connection.session.post(
            f'{self.connection.base_url}avatica',
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        return response.json()['statementId']

    def execute(self, query, parameters=None):
        if parameters:
            if isinstance(parameters, tuple):
                query = query % tuple(parameters)
            elif isinstance(parameters, dict):
                query = query % dict(parameters)
            else:
                raise ValueError("Parameters must be a tuple or a dict")

        # 目前：
        # calcite对接的是k2a的repo-data rest接口，后者不是分批返回的，因此这里也无需分批遍历。
        # 即对rest接口返回的结果，直接将所有结果放在firstFrame里返回（maxRowsInFirstFrame参数），实现比较方便。
        #
        # 未来：
        # calcite可能改为对接k2a的storage sdk接口以适应大量数据返回的场景，届时这里的实现需要修改，避免内存溢出。
        # 如果是其他接口，需要分批请求。例子见：https://calcite.apache.org/avatica/docs/protocol_testing.html
        payload = {
            'request': 'prepareAndExecute',
            'connectionId': self.connection.connection_id,
            'statementId': self.statement_id,
            'sql': query,
            'maxRowsInFirstFrame': -1,  # 此参数在avatica接口文档中没有写，但需要指定-1，否则默认是0
            'maxRowCount': -1
        }
        response = self.connection.session.post(
            f'{self.connection.base_url}avatica',
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        self.result = response.json()
        self.row_iter = iter(self.result['results'][0]['firstFrame']['rows'])
        self.description = [(col['columnName'], None, None, None, None, None, None) for col in
                            self.result['results'][0]['signature']['columns']]

    def executemany(self, query, param_list):
        for parameters in param_list:
            self.execute(query, parameters)

    def fetchone(self):
        try:
            return next(self.row_iter)
        except StopIteration:
            return None

    # 要获取全部结果，正常应该循环调用fetch方法进行遍历
    # 这里直接转换为list是因为进行第一次请求时，将所有结果返回到了firstFrame里（假设结果较小）
    def fetchall(self):
        return list(self.row_iter)

    def close(self):
        payload = {
            'request': 'closeStatement',
            'connectionId': self.connection.connection_id,
            'statementId': self.statement_id
        }
        self.connection.session.post(
            f'{self.connection.base_url}avatica',
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
