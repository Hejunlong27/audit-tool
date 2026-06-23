# -*- coding: utf-8 -*-
"""
数据分析页面
"""
from nicegui import ui
import os

from biz.analysis_service import AnalysisService


def create_analysis_page():
    """创建数据分析页面"""
    service = AnalysisService()

    ui.label('数据分析引擎').classes('text-2xl font-bold')

    with ui.tabs().classes('w-full') as tabs:
        with ui.tab('银行流水分析'):
            with ui.card().classes('w-full p-6'):
                ui.label('上传银行流水文件（Excel/CSV），自动执行异常检测').classes('mb-4')

                upload = ui.upload(
                    label='选择银行流水文件',
                    auto_upload=True,
                    on_upload=lambda e: handle_bank_analysis(e, service)
                ).props('accept=.xlsx,.xls,.csv').classes('w-full')

                analysis_result = ui.expansion('分析结果', value=True).classes('w-full mt-4')
                with analysis_result:
                    result_table = ui.table(
                        columns=[
                            {'name': 'type', 'label': '异常类型', 'field': 'type'},
                            {'name': 'count', 'label': '数量', 'field': 'count'},
                        ],
                        rows=[].classes('w-full')
                    )

        with ui.tab('Benford 法则'):
            with ui.card().classes('w-full p-6'):
                ui.label('对金额数据进行 Benford 法则检验，检测异常分布').classes('mb-4')

                upload = ui.upload(
                    label='选择数据文件',
                    auto_upload=True,
                    on_upload=lambda e: handle_benford(e, service)
                ).props('accept=.xlsx,.xls,.csv').classes('w-full')

                benford_result = ui.label('').classes('mt-4')

        with ui.tab('多源对账'):
            with ui.card().classes('w-full p-6'):
                ui.label('上传两份文件进行自动对账').classes('mb-4')

                upload_left = ui.upload(
                    label='左表（如银行流水）',
                    auto_upload=True
                ).props('accept=.xlsx,.xls,.csv').classes('w-full mb-2')

                upload_right = ui.upload(
                    label='右表（如企业账簿）',
                    auto_upload=True
                ).props('accept=.xlsx,.xls,.csv').classes('w-full')

                ui.button('开始对账', on_click=lambda: ui.notify('请上传两份文件', 'warning'))


async def handle_bank_analysis(e, service):
    """处理银行流水分析"""
    content = e.content.read()
    input_path = f'/tmp/{e.name}'
    with open(input_path, 'wb') as f:
        f.write(content)

    result = service.analyze_bank_statement(input_path)
    if result.success and result.data:
        rows = [
            {'type': k, 'count': len(v) if isinstance(v, list) else v}
            for k, v in result.data.items()
        ]
        ui.notify(result.message, type='positive')


async def handle_benford(e, service):
    """处理 Benford 法则检验"""
    content = e.content.read()
    input_path = f'/tmp/{e.name}'
    with open(input_path, 'wb') as f:
        f.write(content)

    result = service.benford_test(input_path)
    if result.success and result.data:
        msg = f"p值: {result.data['p_value']:.4f} - {result.data['conclusion']}"
        ui.notify(msg, type='warning' if result.data.get('is_anomaly') else 'positive')
