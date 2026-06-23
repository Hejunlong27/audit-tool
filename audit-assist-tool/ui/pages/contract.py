# -*- coding: utf-8 -*-
"""
合同审查页面
"""
from nicegui import ui

from biz.contract_service import ContractService


def create_contract_page():
    """创建合同审查页面"""
    service = ContractService()

    ui.label('合同审查辅助').classes('text-2xl font-bold')

    with ui.card().classes('w-full p-6'):
        ui.label('上传合同文件，自动提取关键条款并评估风险').classes('mb-4')

        upload = ui.upload(
            label='选择合同文件',
            auto_upload=True,
            on_upload=lambda e: handle_contract(e, service)
        ).props('accept=.pdf,.docx,.doc').classes('w-full')

        clauses_expansion = ui.expansion('提取的条款', value=True).classes('w-full mt-4')
        with clauses_expansion:
            clauses_content = ui.column().classes('w-full')

        risks_expansion = ui.expansion('风险点', value=True).classes('w-full mt-2')
        with risks_expansion:
            risks_content = ui.column().classes('w-full')


async def handle_contract(e, service):
    """处理合同审查"""
    content = e.content.read()
    input_path = f'/tmp/{e.name}'
    with open(input_path, 'wb') as f:
        f.write(content)

    result = service.review_contract(input_path)
    if result.success and result.data:
        clauses = result.data.get('clauses', {})
        risks = result.data.get('risks', [])
        ui.notify(result.message, type='positive' if not risks else 'warning')
