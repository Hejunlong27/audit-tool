# -*- coding: utf-8 -*-
"""
NiceGUI 主应用
审计日常工作协助工具的 Web 界面入口
"""
from nicegui import ui, app

from ui.pages.convert import create_convert_page
from ui.pages.analysis import create_analysis_page
from ui.pages.invoice import create_invoice_page
from ui.pages.contract import create_contract_page
from ui.pages.working_paper import create_working_paper_page
from ui.pages.utils import create_utils_page


@ui.page('/')

@ui.page('/convert')
def convert_page():
    create_convert_page()


@ui.page('/analysis')
def analysis_page():
    create_analysis_page()


@ui.page('/invoice')
def invoice_page():
    create_invoice_page()


@ui.page('/contract')
def contract_page():
    create_contract_page()


@ui.page('/working-paper')
def working_paper_page():
    create_working_paper_page()


@ui.page('/utils')
def utils_page():
    create_utils_page()


def create_main_layout():
    """创建主导航布局"""
    # 侧边导航
    with ui.column().classes('w-48 h-full p-4 bg-gray-50'):
        ui.label('审计协助工具').classes('text-lg font-bold mb-4')

        ui.button('格式转换', on_click=lambda: ui.navigate.to('/convert'))
        ui.button('数据分析', on_click=lambda: ui.navigate.to('/analysis'))
        ui.button('发票处理', on_click=lambda: ui.navigate.to('/invoice'))
        ui.button('合同审查', on_click=lambda: ui.navigate.to('/contract'))
        ui.button('底稿管理', on_click=lambda: ui.navigate.to('/working-paper'))
        ui.button('效率工具', on_click=lambda: ui.navigate.to('/utils'))

    # 主内容区域（由各页面自行填充）
    ui.space()


def main():
    """启动应用"""
    app.add_static_files('/output', './output')

    ui.run(
        title='审计日常工作协助工具',
        host='127.0.0.1',
        port=8080,
        reload=False,
        show=False
    )


if __name__ == '__main__':
    main()
