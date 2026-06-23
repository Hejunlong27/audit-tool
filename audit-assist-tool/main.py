# -*- coding: utf-8 -*-
# main.py
"""
审计日常工作协助工具 - 程序入口
"""
import os
import sys


def setup_environment():
    """初始化运行环境"""
    # 创建必要目录
    dirs = ['output', 'logs', 'data', 'templates/audit_reports', 'templates/working_papers']
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 初始化数据库
    from db.init_db import init_database
    init_database()

    # 配置日志
    from loguru import logger
    logger.add(
        'logs/audit_tool_{time:YYYY-MM-DD}.log',
        rotation='1 day',
        retention='30 days',
        level='INFO',
        encoding='utf-8'
    )


def main():
    """主函数"""
    setup_environment()

    from loguru import logger
    logger.info("审计日常工作协助工具启动中...")

    # 启动 GUI
    from ui.app import main as start_gui
    start_gui()


if __name__ == '__main__':
    main()
