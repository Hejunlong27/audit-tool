# -*- coding: utf-8 -*-
"""
格式转换页面
PDF 转 Excel / PDF 转 Word / OCR 识别
"""
from nicegui import ui, events
import os

from biz.convert_service import ConvertService


def create_convert_page():
    """创建格式转换页面"""
    service = ConvertService()

    ui.label('智能格式转换').classes('text-2xl font-bold')
    ui.label('支持 PDF 转 Excel、PDF 转 Word、扫描件 OCR 识别').classes('text-gray-500')

    # 功能选项卡
    with ui.tabs().classes('w-full') as tabs:
        with ui.tab('PDF 转 Excel'):
            with ui.card().classes('w-full p-6'):
                ui.label('上传 PDF 文件，自动提取表格数据并导出为 Excel').classes('mb-4')

                upload = ui.upload(
                    label='选择 PDF 文件',
                    auto_upload=True,
                    on_upload=lambda e: handle_pdf_to_excel(e, service)
                ).props('accept=.pdf').classes('w-full')

                result_label = ui.label('').classes('mt-4')

        with ui.tab('PDF 转 Word'):
            with ui.card().classes('w-full p-6'):
                ui.label('将 PDF 文档转换为可编辑的 Word 文件').classes('mb-4')

                upload = ui.upload(
                    label='选择 PDF 文件',
                    auto_upload=True,
                    on_upload=lambda e: handle_pdf_to_word(e, service)
                ).props('accept=.pdf').classes('w-full')

                result_label = ui.label('').classes('mt-4')

        with ui.tab('OCR 识别'):
            with ui.card().classes('w-full p-6'):
                ui.label('对扫描件图片/PDF 进行文字识别').classes('mb-4')

                upload = ui.upload(
                    label='选择图片或 PDF',
                    auto_upload=True,
                    on_upload=lambda e: handle_ocr(e, service)
                ).props('accept=.png,.jpg,.jpeg,.bmp,.pdf').classes('w-full')

                ocr_result = ui.textarea('').classes('w-full mt-4').props('rows=10 readonly')

        with ui.tab('批量处理'):
            with ui.card().classes('w-full p-6'):
                ui.label('批量转换整个文件夹的 PDF 文件').classes('mb-4')

                dir_input = ui.input('输入文件夹路径', placeholder='/path/to/pdf/files')
                ui.button('开始批量转换', on_click=lambda: handle_batch(dir_input.value, service))

                batch_result = ui.label('').classes('mt-4')


async def handle_pdf_to_excel(e: events.UploadEventArguments, service):
    """处理 PDF 转 Excel"""
    content = e.content.read()
    input_path = f'/tmp/{e.name}'
    output_path = f'./output/{os.path.splitext(e.name)[0]}.xlsx'

    with open(input_path, 'wb') as f:
        f.write(content)

    result = service.pdf_to_excel(input_path, output_path)
    ui.notify(result.message, type='positive' if result.success else 'negative')


async def handle_pdf_to_word(e: events.UploadEventArguments, service):
    """处理 PDF 转 Word"""
    content = e.content.read()
    input_path = f'/tmp/{e.name}'
    output_path = f'./output/{os.path.splitext(e.name)[0]}.docx'

    with open(input_path, 'wb') as f:
        f.write(content)

    result = service.pdf_to_word(input_path, output_path)
    ui.notify(result.message, type='positive' if result.success else 'negative')


async def handle_ocr(e: events.UploadEventArguments, service):
    """处理 OCR 识别"""
    content = e.content.read()
    input_path = f'/tmp/{e.name}'

    with open(input_path, 'wb') as f:
        f.write(content)

    result = service.ocr_recognize(input_path)
    if result.success and result.data:
        ocr_text = result.data.get('full_text', '')
        # 更新文本框内容
        ui.notify(f"OCR 识别完成: {len(result.data.get('text_lines', []))} 行文本", type='positive')


async def handle_batch(dir_path: str, service):
    """处理批量转换"""
    if not dir_path or not os.path.isdir(dir_path):
        ui.notify('请输入有效的文件夹路径', type='negative')
        return

    result = service.batch_pdf_to_excel(dir_path, './output/')
    ui.notify(result.message, type='positive' if result.success else 'negative')
