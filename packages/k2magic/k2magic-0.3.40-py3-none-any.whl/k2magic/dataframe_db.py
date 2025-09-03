import logging
import re
from typing import Union

import pandas as pd
from sqlalchemy import create_engine, Table, MetaData, text, Column, Integer, Float, String, select, make_url, modifier, \
    ColumnElement, and_, literal, URL
from sqlalchemy.dialects import registry
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from k2magic.dataframe_db_exception import DataFrameDBException


class DataFrameDB:
    r"""
    DataFrameDB 是使用 SQLAlchemy 和 Pandas 实现的工具类，提供基于 DataFrame 的数据库操作，兼容多种数据库。

    使用前需要安装相应的数据库的驱动，例如 pymysql、psycopg2等。各种数据库的连接字符串
    格式可参考 https://docs.sqlalchemy.org/en/20/dialects/ ，常见数据库的格式::

        - postgresql+psycopg2://username:password@hostname/database_name
        - mysql+pymysql://username:password@hostname/database_name
        - mssql+pymssql://username:password@hostname:port/database_name
        - oracle+cx_oracle://username:password@hostname:port/database_name

    Examples
    --------
    假设关系表table1的结构如下::

        CREATE TABLE table1 (
            k_device VARCHAR(255) PRIMARY KEY,
            col1 FLOAT,
            col2 FLOAT,
            col3 FLOAT
        );

    对关系表table1进行增删改查操作的示例代码::

        >>> import pandas as pd
        >>> from k2magic.dataframe_db import DataFrameDB
        >>> db = DataFrameDB('postgresql+psycopg2://...')
        >>> df = db.select('table1', condition='col1 > 1')
        >>> df = db.select('table1', limit=3, order_by=['k_device DESC'])
        >>> data = {'k_device': ['a', 'b', 'c'], 'col1': [1, 2, 3], 'col2': [4, 5, 6]}
        >>> df = pd.DataFrame(data)
        >>> db.delete('table1')
        >>> db.insert('table1', df)
        >>> db.update('table1', df, index_keys=['k_device'])
        >>> db.upsert('table1', df, index_keys=['k_device'])

    """

    def __init__(self, db_url:Union[str, URL], schema=None, debug=False):
        """
        初始化 DataFrameDB 类。

        不同类型的数据库只要修改构造方法里的连接字符串，其余的CRUD代码都不需要修改。

        Parameters:
        -----------
        db_url : str | URL
            数据库连接 URL。
        schema : str
            可选的schema名称，如果指定，会作为表名的默认前缀
        """
        registry.register("k2assets.rest", "k2magic.dialect.calcite_dialect", "CalciteDialect")
        registry.register("rdb", "k2magic.dialect.rdb_dialect", "RdbDialect")
        # registry.register("repo", "k2magic.dialect.repo_dialect", "RepoDialect")
        # registry.register("postgresql", "k2magic.dialect.k2a_storage_dialect", "PostgresqlStorageDialect")

        db_url_obj = make_url(db_url)

        self.schema = schema
        self.engine = create_engine(db_url_obj, echo=debug)
        self.Session = sessionmaker(bind=self.engine)
        self.metadata = MetaData(schema=self.schema)
        self.debug = debug

        # 日志配置
        self.logger = logging.getLogger(self.__class__.__name__)
        if self.debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        # 例如taos的dialect没有实现get_table_names函数，所以用try
        try:
            self.metadata.reflect(bind=self.engine)
        except NotImplementedError as e:
            self.logger.error(e)

    def select(self, table_name: str, columns: list = None, condition: str = None,
               limit: int = None, order_by: list = None):
        """
        查询指定表中的数据，并返回 DataFrame。

        Parameters:
        -----------
        table_name : str
            关系表名。
        columns : list, optional
            要查询的列的字符串列表。如果未指定，将查询所有列。
        condition : str, optional
            查询条件，字符串格式，例如 'col1 > 10'。
        limit : int, optional
            查询结果的最大行数
        order_by : list, optional
            排序条件，例如 'k_device DESC'

        Returns:
        --------
        pandas.DataFrame
            查询结果。

        Raises:
        -------
        DataFrameDBException
            在操作数据库时发生错误。
        """
        # 若没有指定schema前缀则添加self.schema前缀
        if (self.schema is not None) and ('.' not in table_name):
            table_name = f"{self.schema}.{table_name}"

        if table_name in self.metadata.tables:
            table = self.metadata.tables[table_name]
        else:
            raise DataFrameDBException(f"Table '{table_name}' does not exist")

        try:
            with self.engine.connect() as conn:
                query = table.select()
                if columns:
                    query = query.with_only_columns(*(table.c[col] for col in columns))
                if condition:
                    query = query.where(text(condition))

                # if group_by:
                #     query = query.group_by(*[text(col) for col in group_by])
                if order_by:
                    query = query.order_by(*[text(col) for col in order_by])
                if limit:
                    query = query.limit(limit)

                result = conn.execute(query)
                return pd.DataFrame(result.fetchall(), columns=result.keys())
        except SQLAlchemyError as e:
            raise DataFrameDBException(
                "Failed to query records due to a database error.",
                original_exception=e
            )

    def sql_select(self, sql_query: str) -> pd.DataFrame:
        """
        ** 注意：仅当其他方法无法满足需求时，才使用此方法作为兜底，此函数的性能和数据库兼容性无法保证。 **

        执行指定的 SELECT 语句，并将结果作为 DataFrame 返回。

        Parameters:
        -----------
        sql_query : str
            要执行的 SELECT 语句。

        Returns:
        --------
        pd.DataFrame
            查询结果作为 DataFrame 返回。

        Raises:
        -------
        DataFrameDbException
            在执行 SQL 语句时发生错误。
        """
        if not sql_query.strip().lower().startswith('select'):
            raise DataFrameDBException("要执行的SQL语句必须以select开头")

        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql_query))
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
            return df
        except SQLAlchemyError as e:
            raise DataFrameDBException(
                "Failed to execute select query due to a database error.",
                original_exception=e
            )

    def insert(self, table_name: str, df: pd.DataFrame):
        """
        将 DataFrame 插入指定的关系表中，若包含主键已存在的数据则回滚并抛出异常。

        Parameters:
        -----------
        table_name : str
            关系表名。
        df : pandas.DataFrame
            要插入的数据。df中的数据列要在关系表中也存在且数据类型兼容。

        Raises:
        -------
        DataFrameDBException
            在操作数据库时发生错误。
        """

        # 若没有指定schema前缀则添加self.schema前缀
        if (self.schema is not None) and ('.' not in table_name):
            table_name = f"{self.schema}.{table_name}"

        if table_name in self.metadata.tables:
            table = self.metadata.tables[table_name]
        else:
            raise DataFrameDBException(f"Table '{table_name}' does not exist")

        batch_size = 100  # 每批插入的行数

        try:
            with self.engine.begin() as conn:  # 使用 begin() 方法确保事务处理
                for start in range(0, len(df), batch_size):
                    batch_df = df.iloc[start:start + batch_size]
                    # to_sql对于有schema情况的table_name是否需要带schema前缀，与conn.execute方式不统一
                    # batch_df.to_sql(table_name, conn, if_exists='append', index=False)
                    conn.execute(table.insert(), batch_df.to_dict(orient='records'))
        except SQLAlchemyError as e:
            raise DataFrameDBException(
                "Failed to insert records due to a database error.",
                original_exception=e
            )

    def delete(self, table_name: str, condition: str = None):
        """
        根据条件删除指定表中的数据。

        Parameters:
        -----------
        table_name : str
            关系表名。
        condition : str, optional
            删除条件，字符串格式，例如 'col1 > 10'。如果未指定条件，将删除整个表中的所有数据。

        Raises:
        -------
        DataFrameDBException
            在操作数据库时发生错误。
        """

        # 若没有指定schema前缀则添加self.schema前缀
        if (self.schema is not None) and ('.' not in table_name):
            table_name = f"{self.schema}.{table_name}"

        if table_name in self.metadata.tables:
            table = self.metadata.tables[table_name]
        else:
            raise DataFrameDBException(f"Table '{table_name}' does not exist")

        try:
            with self.engine.begin() as conn:  # 使用 begin() 方法确保事务处理
                if condition:
                    delete_query = table.delete().where(text(condition))
                else:
                    delete_query = table.delete()
                conn.execute(delete_query)
        except SQLAlchemyError as e:
            raise DataFrameDBException(
                "Failed to delete records due to a database error.",
                original_exception=e
            )

    def update(self, table_name: str, df: pd.DataFrame, index_keys: list):
        """
        根据条件更新指定表中的数据，若部分记录更新失败则回滚整个操作。

        Parameters:
        -----------
        table_name : str
            关系表名。
        df : pandas.DataFrame
            包含新值的数据。
        index_keys : list
            用于构建 WHERE 条件的列名。

        Raises:
        -------
        DataFrameDBException
            在操作数据库时发生错误。
        """
        # 若没有指定schema前缀则添加self.schema前缀
        if (self.schema is not None) and ('.' not in table_name):
            table_name = f"{self.schema}.{table_name}"

        if table_name in self.metadata.tables:
            table = self.metadata.tables[table_name]
        else:
            raise DataFrameDBException(f"Table '{table_name}' does not exist")

        try:
            with self.engine.begin() as conn:  # 使用 begin() 方法确保事务处理
                for _, row in df.iterrows():
                    # 构建 WHERE 条件
                    condition = ' AND '.join([f"{key} = :cond_{key}" for key in index_keys])
                    condition_params = {f"cond_{key}": row[key] for key in index_keys}

                    # 构建 SET 值
                    new_values = {col: row[col] for col in df.columns if col not in index_keys}
                    update_query = table.update().where(text(condition)).values(new_values)

                    conn.execute(update_query, condition_params)
        except SQLAlchemyError as e:
            raise DataFrameDBException(
                "Failed to update records due to a database error.",
                original_exception=e
            )

    def upsert(self, table_name: str, df: pd.DataFrame, index_keys: list):
        """
        执行 UPSERT 操作（插入或更新）。

        Parameters:
        -----------
        table_name : str
            关系表名。
        df : pandas.DataFrame
            要插入或更新的数据。
        index_keys : list
            用于构建 WHERE 条件的列名（作为唯一键）。

        Raises:
        -------
        DataFrameDbException
            在操作数据库时发生错误。
        """
        # 若没有指定schema前缀则添加self.schema前缀
        if (self.schema is not None) and ('.' not in table_name):
            table_name = f"{self.schema}.{table_name}"

        if table_name in self.metadata.tables:
            table = self.metadata.tables[table_name]
        else:
            raise DataFrameDBException(f"Table '{table_name}' does not exist")

        try:
            with self.engine.begin() as conn:  # 使用 begin() 方法确保事务处理
                for _, row in df.iterrows():
                    values = {col: row[col] for col in df.columns}

                    # col1 = :col1, col2 = :col2
                    update_clause = ', '.join([f"{col} = :{col}" for col in df.columns if col not in index_keys])

                    if self.engine.dialect.name == 'mysql':
                        insert_query = text(
                            f"""
                            INSERT INTO {table_name} ({', '.join(values.keys())})
                            VALUES ({', '.join([f':{key}' for key in values.keys()])})
                            ON DUPLICATE KEY UPDATE
                            {', '.join([f'{col}=VALUES({col})' for col in df.columns if col not in index_keys])}
                            """
                        )
                    elif self.engine.dialect.name == 'postgresql':
                        insert_query = text(
                            f"""
                            INSERT INTO {table_name} ({', '.join(values.keys())})
                            VALUES ({', '.join([f':{key}' for key in values.keys()])})
                            ON CONFLICT ({', '.join(index_keys)}) DO UPDATE SET
                            {', '.join([f'{col}=EXCLUDED.{col}' for col in df.columns if col not in index_keys])}
                            """
                        )
                    elif self.engine.dialect.name == 'oracle':
                        # Oracle的sql语句不能以分号结尾
                        insert_query = text(
                            f"""
                            MERGE INTO {table_name} t
                            USING (SELECT {', '.join([f":{col} AS {col}" for col in values.keys()])} FROM dual) s
                            ON ({' AND '.join([f't.{key} = s.{key}' for key in index_keys])})
                            WHEN MATCHED THEN UPDATE SET {', '.join([f't.{key} = s.{key}' for key in values.keys() if key not in index_keys])}
                            WHEN NOT MATCHED THEN INSERT ({', '.join(values.keys())}) VALUES ({', '.join([f's.{key}' for key in values.keys()])})
                            """
                        )

                    elif self.engine.dialect.name == 'mssql':
                        # SqlServer的sql语句需要以分号结尾
                        insert_query = text(
                            f"""
                            MERGE INTO {table_name} AS t
                            USING (SELECT :{', :'.join(values.keys())}) AS s ({', '.join(values.keys())})
                            ON ({' AND '.join([f't.{key} = s.{key}' for key in index_keys])})
                            WHEN MATCHED THEN UPDATE SET {update_clause}
                            WHEN NOT MATCHED THEN INSERT ({', '.join(values.keys())}) VALUES ({', '.join([f's.{key}' for key in values.keys()])});
                            """
                        )

                    else:
                        raise DataFrameDBException(f"Unsupported database dialect: {self.engine.dialect.name}")

                    conn.execute(insert_query, values)
        except SQLAlchemyError as e:
            raise DataFrameDBException(
                "Failed to perform upsert operation due to a database error.",
                original_exception=e
            )

    # def get_column(self, dtype, column_name):
    #     """根据 Pandas 列的数据类型返回适当的 SQLAlchemy 列类型"""
    #     if pd.api.types.is_integer_dtype(dtype):
    #         return Column(column_name, Integer)
    #     elif pd.api.types.is_float_dtype(dtype):
    #         return Column(column_name, Float)
    #     elif pd.api.types.is_string_dtype(dtype):
    #         return Column(column_name, String(255))  # Oracle要求指定字段长度
    #     else:
    #         raise ValueError(f"Unsupported data type: {dtype}")

    def create_table(self, df, table_name, primary_keys=None):
        """
        根据 DataFrame 创建一个新的表。

        Parameters:
        -----------
        df : pandas.DataFrame
            包含表结构和数据的 DataFrame。
        table_name : str
            要创建的表名。
        primary_keys : list, optional
            主键列名的列表。如果未指定，则没有主键。

        Raises:
        -------
        DataFrameDbException
            在创建表时发生错误。
        """
        # 若没有指定schema前缀则添加self.schema前缀
        if (self.schema is not None) and ('.' not in table_name):
            table_name = f"{self.schema}.{table_name}"

        if table_name in self.metadata.tables:
            raise DataFrameDBException(f"Table '{table_name}' already exists")

        if primary_keys is None:
            primary_keys = []

        try:
            columns = []
            for col_name, dtype in zip(df.columns, df.dtypes):
                if pd.api.types.is_integer_dtype(dtype):
                    col_type = Integer
                elif pd.api.types.is_float_dtype(dtype):
                    col_type = Float
                elif pd.api.types.is_string_dtype(dtype):
                    col_type = String(255)  # Oracle要求指定字段长度
                else:
                    raise ValueError(f"Unsupported data type: {dtype}")
                if primary_keys and col_name in primary_keys:
                    columns.append(Column(col_name, col_type, primary_key=True))
                else:
                    columns.append(Column(col_name, col_type))

            # 经验证这里需要指定不带schema前缀的table_name作为构造参数
            table = Table(table_name.split('.')[-1], self.metadata, *columns)
            self.metadata.create_all(self.engine)
        except SQLAlchemyError as e:
            # 捕获 SQLAlchemy 异常，并抛出自定义异常
            raise DataFrameDBException(f"An error occurred while creating the table: {str(e)}")

    def drop_table(self, table_name: str):
        """
        删除指定表。

        Parameters:
        -----------
        table_name : str
            要删除的关系表名。

        Raises:
        -------
        DataFrameDbException
            在删除表时发生错误。
        """
        # 若没有指定schema前缀则添加self.schema前缀
        if (self.schema is not None) and ('.' not in table_name):
            table_name = f"{self.schema}.{table_name}"

        try:
            with self.engine.begin() as conn:  # 使用 begin() 方法确保事务处理
                if table_name in self.metadata.tables:
                    table = self.metadata.tables[table_name]
                    self.metadata.drop_all(bind=self.engine, tables=[table])

                    # 强制更新metadata信息，以免后续创建同名表时报"表已存在"错误
                    # self.metadata = MetaData(schema=None)
                    self.metadata.clear()
                    self.metadata.reflect(bind=self.engine)
                else:
                    raise DataFrameDBException(f"Table {table_name} does not exist.")
        except SQLAlchemyError as e:
            raise DataFrameDBException(
                f"Failed to drop table {table_name} due to a database error.",
                original_exception=e
            )
