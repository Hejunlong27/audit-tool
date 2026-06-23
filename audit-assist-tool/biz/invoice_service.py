# -*- coding: utf-8 -*-
# biz/invoice_service.py
"""
发票处理服务
"""
import os
import pandas as pd
from loguru import logger

from core.invoice_recognizer import InvoiceRecognizer
from core.base import ProcessResult


class InvoiceService:
    """发票处理服务"""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.recognizer = InvoiceRecognizer(config.get('invoice', {}))

    def recognize_single(self, image_path: str, project_name: str = '') -> ProcessResult:
        """识别单张发票"""
        return self.recognizer.process(image_path, project_name)

    def recognize_batch(self, image_dir: str, project_name: str = '') -> ProcessResult:
        """批量识别发票"""
        return self.recognizer.batch_process(image_dir, project_name)

    def export_to_excel(self, results: list[dict], output_path: str) -> ProcessResult:
        """将识别结果导出为 Excel"""
        result = ProcessResult()

        try:
            rows = []
            for r in results:
                fields = r.get('fields', {})
                rows.append({
                    '文件名': os.path.basename(r.get('file_path', '')),
                    '发票类型': fields.get('invoice_type', ''),
                    '发票代码': fields.get('invoice_code', ''),
                    '发票号码': fields.get('invoice_number', ''),
                    '开票日期': fields.get('invoice_date', ''),
                    '金额': fields.get('amount', ''),
                    '税额': fields.get('tax', ''),
                    '价税合计': fields.get('total', ''),
                    '销售方': fields.get('seller', ''),
                    '购买方': fields.get('buyer', ''),
                    '是否重复': '是' if r.get('is_duplicate') else '否'
                })

            df = pd.DataFrame(rows)
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            df.to_excel(output_path, index=False)

            result.data = {'output_path': output_path, 'count': len(rows)}
            result.message = f"发票汇总导出完成: {output_path} ({len(rows)} 条)"

        except Exception as e:
            result.add_error(f"导出失败: {str(e)}")

        return result
