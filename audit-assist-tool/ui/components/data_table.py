# -*- coding: utf-8 -*-
"""
数据表格组件
"""
from nicegui import ui


class DataTable:
    """数据表格组件"""

    def __init__(self, columns: list[dict], rows: list[dict] = None):
        self.columns = columns
        self.rows = rows or []

    def render(self):
        """渲染表格"""
        return ui.table(
            columns=self.columns,
            rows=self.rows
        ).classes('w-full')

    def add_row(self, row: dict):
        """添加行"""
        self.rows.append(row)
