# -*- coding: utf-8 -*-
"""
效率工具页面
"""
from nicegui import ui

from biz.file_manager import FileManager


def create_utils_page():
    """创建效率工具页面"""
    manager = FileManager()

    ui.label('效率工具集').classes('text-2xl font-bold')

    with ui.tabs().classes('w-full'):
        with ui.tab('文件整理'):
            with ui.card().classes('w-full p-6'):
                dir_input = ui.input('文件夹路径', placeholder='/path/to/files')
                pattern_input = ui.input('重命名模式（正则）', value=r'(.*)')
                replace_input = ui.input('替换为', value=r'\1')

                ui.button('执行重命名', on_click=lambda: ui.notify('功能开发中', 'info'))
                ui.button('查找重复文件', on_click=lambda: ui.notify('功能开发中', 'info'))

        with ui.tab('全文检索'):
            with ui.card().classes('w-full p-6'):
                ui.label('对审计项目文件建立全文索引').classes('mb-4')
                ui.button('建立索引', on_click=lambda: ui.notify('功能开发中', 'info'))

        with ui.tab('数据清洗'):
            with ui.card().classes('w-full p-6'):
                ui.label('多源数据导入与标准化').classes('mb-4')
                ui.button('导入数据', on_click=lambda: ui.notify('功能开发中', 'info'))

        with ui.tab('任务管理'):
            with ui.card().classes('w-full p-6'):
                ui.label('审计项目任务跟踪').classes('mb-4')
                ui.button('新建任务', on_click=lambda: ui.notify('功能开发中', 'info'))
