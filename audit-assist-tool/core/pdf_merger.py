# -*- coding: utf-8 -*-
"""
PDF 合并与拆分
基于 PyMuPDF (fitz) 实现
"""
import os
from typing import List
from loguru import logger

from core.base import BaseProcessor, ProcessResult


class PDFMerger(BaseProcessor):
    """PDF 合并与拆分工具"""

    def merge(self, pdf_paths: List[str], output_path: str) -> ProcessResult:
        """合并多个 PDF 文件"""
        result = ProcessResult()

        import fitz

        merged_doc = fitz.open()
        for path in pdf_paths:
            if not os.path.exists(path):
                result.add_warning(f"文件不存在，已跳过: {path}")
                continue
            doc = fitz.open(path)
            merged_doc.insert_pdf(doc)
            doc.close()

        merged_doc.save(output_path)
        merged_doc.close()

        result.data = {'output_path': output_path, 'page_count': merged_doc.page_count}
        result.message = f"合并完成: {len(pdf_paths)} 个文件 -> {output_path}"
        logger.info(result.message)
        return result

    def split(self, pdf_path: str, output_dir: str, ranges: str = None) -> ProcessResult:
        """
        拆分 PDF 文件

        Args:
            pdf_path: PDF 文件路径
            output_dir: 输出目录
            ranges: 页码范围，如 "1-3,5,7-10"（1-indexed），None 表示逐页拆分
        """
        result = ProcessResult()
        import fitz

        doc = fitz.open(pdf_path)
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_files = []

        if ranges is None:
            # 逐页拆分
            for i in range(len(doc)):
                out_path = os.path.join(output_dir, f"{base_name}_page_{i+1}.pdf")
                new_doc = fitz.open()
                new_doc.insert_pdf(doc, from_page=i, to_page=i)
                new_doc.save(out_path)
                new_doc.close()
                output_files.append(out_path)
        else:
            # 按范围拆分
            parts = ranges.split(',')
            for part in parts:
                part = part.strip()
                if '-' in part:
                    start, end = part.split('-')
                    start, end = int(start) - 1, int(end) - 1
                else:
                    start = end = int(part) - 1

                out_path = os.path.join(output_dir, f"{base_name}_p{start+1}-{end+1}.pdf")
                new_doc = fitz.open()
                new_doc.insert_pdf(doc, from_page=start, to_page=end)
                new_doc.save(out_path)
                new_doc.close()
                output_files.append(out_path)

        doc.close()
        result.data = {'output_files': output_files}
        result.message = f"拆分完成: {len(output_files)} 个文件"
        return result
