# -*- coding: utf-8 -*-
"""
底稿管理页面
"""
from nicegui import ui

from biz.working_paper import WorkingPaperManager


def create_working_paper_page():
    """创建底稿管理页面"""
    manager = WorkingPaperManager()

    ui.label('底稿与报告管理').classes('text-2xl font-bold')

    with ui.tabs().classes('w-full'):
        with ui.tab('项目管理'):
            with ui.card().classes('w-full p-6'):
                ui.button('新建项目', on_click=lambda: ui.notify('功能开发中', 'info'))

                project_table = ui.table(
                    columns=[
                        {'name': 'name', 'label': '项目名称', 'field': 'name'},
                        {'name': 'client', 'label': '客户', 'field': 'client_name'},
                        {'name': 'period', 'label': '审计期间', 'field': 'audit_period'},
                        {'name': 'status', 'label': '状态', 'field': 'status'},
                    ],
                    rows=[].classes('w-full mt-4')
                )

        with ui.tab('底稿列表'):
            with ui.card().classes('w-full p-6'):
                ui.label('选择项目后查看底稿列表').classes('text-gray-500')

        with ui.tab('报告生成'):
            with ui.card().classes('w-full p-6'):
                ui.label('基于模板生成审计报告').classes('mb-4')
                ui.button('生成报告', on_click=lambda: ui.notify('功能开发中', 'info'))
