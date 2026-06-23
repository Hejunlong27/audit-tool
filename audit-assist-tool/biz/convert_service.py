# -*- coding: utf-8 -*-
# biz/convert_service.py
"""
格式转换服务
调度核心处理层，提供统一的格式转换接口
"""
import os
from typing import Optional
from loguru import logger

from core.pdf_extractor import PDFTableExtractor
from core.pdf_converter import PDFToWordConverter
from core.pdf_merger import PDFMerger
from core.ocr_engine import OCREngine
from core.base import ProcessResult


class ConvertService:
    """格式转换服务"""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.extractor = PDFTableExtractor(config.get('pdf_extract', {}))
        self.converter = PDFToWordConverter()
        self.merger = PDFMerger()
        self.ocr = OCREngine(config.get('ocr', {}))

    def pdf_to_excel(
        self,
        pdf_path: str,
        output_path: str = None,
        strategy: str = 'auto'
    ) -> ProcessResult:
        """PDF 转 Excel"""
        if output_path is None:
            output_path = os.path.splitext(pdf_path)[0] + '.xlsx'
        return self.extractor.process(
            pdf_path,
            strategy=strategy,
            output_excel=output_path
        )

    def pdf_to_word(
        self,
        pdf_path: str,
        output_path: str = None
    ) -> ProcessResult:
        """PDF 转 Word"""
        return self.converter.process(pdf_path, output_path)

    def ocr_recognize(self, image_path: str) -> ProcessResult:
        """OCR 识别"""
        return self.ocr.process(image_path)

    def batch_pdf_to_excel(self, pdf_dir: str, output_dir: str = None) -> ProcessResult:
        """批量 PDF 转 Excel"""
        if output_dir is None:
            output_dir = pdf_dir

        results = []
        pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]

        for filename in pdf_files:
            pdf_path = os.path.join(pdf_dir, filename)
            out_path = os.path.join(output_dir, os.path.splitext(filename)[0] + '.xlsx')
            sub_result = self.pdf_to_excel(pdf_path, out_path)
            results.append({
                'file': filename,
                'success': sub_result.success,
                'message': sub_result.message
            })
            logger.info(f"[批量转换] {filename}: {sub_result.message}")

        result = ProcessResult()
        success_count = sum(1 for r in results if r['success'])
        result.data = results
        result.message = f"批量 PDF 转 Excel: {success_count}/{len(results)} 成功"
        return result
