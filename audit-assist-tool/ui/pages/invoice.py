# -*- coding: utf-8 -*-
"""
发票处理页面
"""
from nicegui import ui
import os

from biz.invoice_service import InvoiceService


def create_invoice_page():
    """创建发票处理页面"""
    service = InvoiceService()

    ui.label('发票智能处理').classes('text-2xl font-bold')

    with ui.card().classes('w-full p-6'):
        ui.label('上传发票图片或 PDF，自动识别票面信息').classes('mb-4')

        upload = ui.upload(
            label='选择发票文件（支持多选）',
            auto_upload=True,
            on_upload=lambda e: handle_invoice(e, service)
        ).props('accept=.png,.jpg,.jpeg,.pdf multiple').classes('w-full')

        invoice_table = ui.table(
            columns=[
                {'name': 'file', 'label': '文件名', 'field': 'file'},
                {'name': 'code', 'label': '发票代码', 'field': 'code'},
                {'name': 'number', 'label': '发票号码', 'field': 'number'},
                {'name': 'amount', 'label': '金额', 'field': 'amount'},
                {'name': 'seller', 'label': '销售方', 'field': 'seller'},
                {'name': 'duplicate', 'label': '是否重复', 'field': 'duplicate'},
            ],
            rows=[].classes('w-full mt-4')
        )

        ui.button('导出 Excel', on_click=lambda: ui.notify('请先上传发票', 'warning'))


async def handle_invoice(e, service):
    """处理发票识别"""
    content = e.content.read()
    input_path = f'/tmp/{e.name}'
    with open(input_path, 'wb') as f:
        f.write(content)

    result = service.recognize_single(input_path)
    if result.success and result.data:
        fields = result.data.get('fields', {})
        ui.notify(
            f"识别完成: 发票号码 {fields.get('invoice_number', 'N/A')}",
            type='positive' if not result.data.get('is_duplicate') else 'warning'
        )
