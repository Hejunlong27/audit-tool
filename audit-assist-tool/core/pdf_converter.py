# -*- coding: utf-8 -*-
"""
PDF 转 Word 转换器
基于 pdf2docx 实现，支持批量处理
"""
import os
from typing import Optional
from loguru import logger

from core.base import BaseProcessor, ProcessResult


class PDFToWordConverter(BaseProcessor):
    """PDF 转 Word 转换器"""

    def process(
        self,
        pdf_path: str,
        output_path: str = None,
        start_page: int = 0,
        end_page: int = None
    ) -> ProcessResult:
        """
        将 PDF 转换为 Word 文档

        Args:
            pdf_path: PDF 文件路径
            output_path: 输出 Word 路径（默认与 PDF 同名 .docx）
            start_page: 起始页（0-indexed）
            end_page: 结束页（None 表示到最后一页）
        """
        result = ProcessResult()

        if not self._validate_input(pdf_path):
            result.add_error(f"PDF 文件不存在: {pdf_path}")
            return result

        try:
            from pdf2docx import Converter

            if output_path is None:
                output_path = os.path.splitext(pdf_path)[0] + '.docx'

            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

            cv = Converter(pdf_path)
            cv.convert(output_path, start=start_page, end=end_page)
            cv.close()

            file_size = os.path.getsize(output_path)
            result.data = {'output_path': output_path, 'file_size': file_size}
            result.message = f"PDF 转 Word 完成: {output_path} ({file_size/1024:.1f} KB)"
            logger.info(result.message)

        except ImportError:
            result.add_error("pdf2docx 未安装，请运行: pip install pdf2docx")
        except Exception as e:
            result.add_error(f"PDF 转 Word 失败: {str(e)}")
            logger.exception(e)

        return result

    def batch_convert(
        self,
        pdf_dir: str,
        output_dir: str = None,
        recursive: bool = False
    ) -> ProcessResult:
        """
        批量转换目录下的 PDF 文件

        Args:
            pdf_dir: PDF 文件所在目录
            output_dir: 输出目录（默认与 PDF 同目录）
            recursive: 是否递归子目录
        """
        result = ProcessResult()
        results = []

        if output_dir is None:
            output_dir = pdf_dir

        os.makedirs(output_dir, exist_ok=True)

        pattern = os.path.join(pdf_dir, '**/*.pdf') if recursive else os.path.join(pdf_dir, '*.pdf')
        pdf_files = [f for f in os.popen(f'find {pdf_dir} -name "*.pdf"').read().strip().split('\n') if f]

        if not pdf_files:
            result.message = "未找到 PDF 文件"
            return result

        for pdf_path in pdf_files:
            pdf_path = pdf_path.strip()
            if not pdf_path or not os.path.exists(pdf_path):
                continue

            rel_path = os.path.relpath(pdf_path, pdf_dir)
            out_path = os.path.join(output_dir, os.path.splitext(rel_path)[0] + '.docx')

            sub_result = self.process(pdf_path, out_path)
            results.append({
                'input': pdf_path,
                'output': out_path,
                'success': sub_result.success,
                'message': sub_result.message
            })

        success_count = sum(1 for r in results if r['success'])
        result.data = results
        result.message = f"批量转换完成: {success_count}/{len(results)} 成功"
        logger.info(result.message)

        return result
