import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from contextlib import contextmanager
import threading
import time
from enum import Enum
import pandas as pd

import pymysql
from pymysql import Connection, cursors
from pymysql.err import MySQLError

# ==============================
# 可配置数据库连接参数
# ==============================
# 测试环境
# DB_CONFIG = {
#     "db_type": "mysql",
#     "host": "172.27.88.56",
#     "port": 3306,
#     "database": "ep_schema",
#     "username": "root",
#     "password": "root",
#     "pool_size": 10,
# }
# 生产环境
DB_CONFIG = {
    "db_type": "mysql",
    "host": "172.27.88.56",
    "port": 4310,
    "database": "ep_schema",
    "username": "root",
    "password": "UZQZ7Vc6p!FE",
    "pool_size": 10,
}

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DBType(Enum):
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"


class ExecutionMode(Enum):
    READ = "read"
    WRITE = "write"
    SCHEMA = "schema"


class DBConnection:
    """数据库连接池管理类（内部使用）"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_type = DBType(config["db_type"])
        self.host = config["host"]
        self.port = config["port"]
        self.database = config["database"]
        self.username = config["username"]
        self.password = config["password"]
        self.pool_size = config.get("pool_size", 5)
        self.conn_params = {k: v for k, v in config.items() if k not in [
            "db_type", "host", "port", "database", "username", "password", "pool_size"
        ]}

        self._connection_pool = []
        self._lock = threading.Lock()
        self._initialize_pool()

    def _initialize_pool(self):
        """初始化连接池"""
        for _ in range(self.pool_size):
            conn = self._create_connection()
            if conn:
                with self._lock:
                    self._connection_pool.append(conn)
            else:
                logger.warning("Failed to initialize one connection in pool.")

    def _create_connection(self) -> Optional[Connection]:
        """创建新数据库连接"""
        try:
            if self.db_type == DBType.MYSQL:
                conn = pymysql.connect(
                    host=self.host,
                    port=self.port,
                    user=self.username,
                    password=self.password,
                    database=self.database,
                    **self.conn_params
                )
                return conn
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
        except Exception as e:
            logger.error(f"Failed to create database connection: {e}")
            return None

    @contextmanager
    def get_connection(self) -> Connection:
        """从连接池获取连接（上下文管理器）"""
        conn = None
        try:
            with self._lock:
                conn = self._connection_pool.pop() if self._connection_pool else None

            if conn is None:
                conn = self._create_connection()
                if conn is None:
                    raise Exception("Failed to create or get a database connection.")

            yield conn

            # 归还连接
            with self._lock:
                if len(self._connection_pool) < self.pool_size:
                    self._connection_pool.append(conn)
                else:
                    conn.close()
        except Exception as e:
            logger.error(f"Error in get_connection: {e}")
            if conn:
                conn.close()
            raise

    def execute_sql(
            self,
            sql: str,
            params: Optional[Union[Tuple, List, Dict]] = None,
            mode: ExecutionMode = ExecutionMode.READ,
            fetch: bool = True
    ) -> Union[int, List[Dict[str, Any]], None]:
        """执行SQL语句"""
        start_time = time.time()
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursors.DictCursor) as cursor:
                    cursor.execute(sql, params)

                    if mode == ExecutionMode.READ and fetch:
                        result = cursor.fetchall()
                    elif mode == ExecutionMode.WRITE:
                        result = cursor.rowcount
                        conn.commit()
                    else:
                        result = None
                        if mode != ExecutionMode.SCHEMA:
                            conn.commit()

                    execution_time = time.time() - start_time
                    logger.info(
                        f"SQL executed in {execution_time:.3f}s: {sql[:100]}{'...' if len(sql) > 100 else ''}")
                    return result

        except MySQLError as e:
            logger.error(f"Database error executing SQL: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error executing SQL: {e}")
            raise

    def call_procedure(self, proc_name: str, params: Optional[List] = None) -> List:
        """调用存储过程"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.callproc(proc_name, params or [])
                    result = cursor.fetchall()
                    conn.commit()
                    return result
        except Exception as e:
            logger.error(f"Error calling procedure {proc_name}: {e}")
            raise

    def close_all(self):
        """关闭所有连接"""
        with self._lock:
            for conn in self._connection_pool:
                try:
                    conn.close()
                except Exception as e:
                    logger.warning(f"Error closing connection: {e}")
            self._connection_pool.clear()


class DBHandler:
    """
    数据库操作SDK主类（算法团队通过类方法直接调用）
    示例：DBHandler.query("SELECT * FROM table")
    """

    # 类变量：存储全局唯一的 DBConnection 实例
    _db_conn: Optional[DBConnection] = None
    _init_lock = threading.Lock()

    @classmethod
    def connect(cls, config: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化数据库连接（SDK入口）

        Args:
            config: 数据库配置。若为None，则使用全局DB_CONFIG
        """
        if cls._db_conn is not None:
            return  # 已初始化

        with cls._init_lock:
            if cls._db_conn is not None:
                return

            effective_config = config or DB_CONFIG
            cls._db_conn = DBConnection(effective_config)
            logger.info("DBHandler initialized successfully.")

    @classmethod
    def _ensure_connected(cls):
        """确保已连接，否则初始化"""
        if cls._db_conn is None:
            cls.connect()

    @classmethod
    def query(cls, sql: str, params: Optional[Union[Tuple, List, Dict]] = None) -> List[Dict[str, Any]]:
        """
        执行查询并返回字典列表

        Args:
            sql: 查询SQL
            params: 参数

        Returns:
            查询结果（每行为一个字典）
        """
        cls._ensure_connected()
        return cls._db_conn.execute_sql(sql, params, ExecutionMode.READ, fetch=True)

    @classmethod
    def query_to_dataframe(cls, sql: str, params: Optional[Union[Tuple, List, Dict]] = None) -> pd.DataFrame:
        """
        执行查询并返回Pandas DataFrame

        Args:
            sql: 查询SQL
            params: 参数

        Returns:
            DataFrame
        """
        results = cls.query(sql, params)
        return pd.DataFrame(results)


    @classmethod
    def close_all(cls) -> None:
        """
        关闭所有数据库连接（程序退出时调用）
        """
        if cls._db_conn:
            cls._db_conn.close_all()
            cls._db_conn = None
            logger.info("All database connections closed.")


# ==============================
# 使用示例（算法团队可复制使用）
# ==============================
if __name__ == "__main__":
    # 初始化连接（自动读取 DB_CONFIG）
    DBHandler.connect()

    try:
        # 查询示例
        results = DBHandler.query("SELECT * FROM history_dd_dayahead_posinegarequirement LIMIT 5")
        print("Query results:", results)

        # 查询到 DataFrame
        df = DBHandler.query_to_dataframe("SELECT * FROM history_dd_dayahead_posinegarequirement LIMIT 10")
        print("DataFrame shape:", df.shape)
        print("Columns:", df.columns.tolist())

    except Exception as e:
        print(f"Database operation failed: {e}")

    finally:
        # 程序结束时关闭连接
        DBHandler.close_all()