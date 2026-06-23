"""
数据库初始化脚本
"""
import sqlite3
import os
from loguru import logger


def get_db_path() -> str:
    """获取数据库文件路径"""
    db_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, 'audit_tool.db')


def init_database(db_path: str = None) -> sqlite3.Connection:
    """初始化数据库，创建表结构"""
    if db_path is None:
        db_path = get_db_path()

    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    with open(schema_path, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())

    conn.commit()
    logger.info(f"数据库初始化完成: {db_path}")
    return conn


def get_connection(db_path: str = None) -> sqlite3.Connection:
    """获取数据库连接"""
    if db_path is None:
        db_path = get_db_path()

    if not os.path.exists(db_path):
        return init_database(db_path)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


if __name__ == '__main__':
    init_database()
    print("数据库初始化完成")