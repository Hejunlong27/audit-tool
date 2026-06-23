# -*- coding: utf-8 -*-
"""
PDF 表格提取器
支持三种策略：有线框表格(pdfplumber)、无线框表格(camelot stream)、扫描件(OCR)
自动检测页面类型并选择最优策略
"""
import os
import re
from typing import Optional
import pandas as pd
from dataclasses import dataclass
from loguru import logger

from core.base import BaseProcessor, ProcessResult


@dataclass
class TableExtractionResult:
    """表格提取结果"""
    tables: list[pd.DataFrame]
    page_numbers: list[int]
    strategy_used: str
    total_tables: int


class PDFTableExtractor(BaseProcessor):
    """PDF 表格提取器"""

    def __init__(self, config: dict = None):
        super().__init__(config)
        self.ocr_engine = None  # 延迟加载，避免启动时加载 PaddleOCR

    def _detect_page_type(self, pdf_path: str, page_num: int = 0) -> str:
        """
        检测 PDF 页面类型
        返回: 'lined' (有线框) / 'unlined' (无线框) / 'scanned' (扫描件)
        """
        import fitz  # PyMuPDF

        doc = fitz.open(pdf_path)
        page = doc[page_num]

        # 检测是否有图片覆盖（扫描件特征）
        images = page.get_images(full=True)
        text_length = len(page.get_text().strip())

        if len(images) > 0 and text_length < 50:
            doc.close()
            return 'scanned'

        # 检测线条/矩形数量（有线框特征）
        drawings = page.get_drawings()
        line_count = sum(1 for d in drawings if d['items'] and len(d['items']) > 0)

        doc.close()

        if line_count > 10:
            return 'lined'
        else:
            return 'unlined'

    def _extract_with_pdfplumber(self, pdf_path: str) -> list[pd.DataFrame]:
        """使用 pdfplumber 提取有线框表格"""
        import pdfplumber

        tables = []
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                page_tables = page.extract_tables()
                for table in page_tables:
                    if table and len(table) > 1:
                        df = pd.DataFrame(table[1:], columns=table[0])
                        df = df.dropna(how='all')
                        df = df.dropna(axis=1, how='all')
                        if not df.empty:
                            tables.append(df)
                            logger.info(f"pdfplumber 提取到表格: 第{i+1}页, {len(df)}行x{len(df.columns)}列")
        return tables

    def _extract_with_camelot(self, pdf_path: str) -> list[pd.DataFrame]:
        """使用 camelot stream 模式提取无线框表格"""
        try:
            import camelot
        except ImportError:
            logger.warning("camelot 未安装，跳过无线框表格提取")
            return []

        tables = []
        try:
            result = camelot.read_pdf(pdf_path, flavor='stream', pages='all')
            for i, table in enumerate(result._tables):
                df = table.df
                df = df.dropna(how='all')
                df = df.dropna(axis=1, how='all')
                if not df.empty:
                    # 清理列名中的空白
                    df.columns = [str(c).strip() for c in df.columns]
                    tables.append(df)
                    logger.info(f"camelot stream 提取到表格: 第{table.page}页, {len(df)}行x{len(df.columns)}列")
        except Exception as e:
            logger.error(f"camelot 提取失败: {e}")

        return tables

    def _extract_with_ocr(self, pdf_path: str) -> list[pd.DataFrame]:
        """使用 OCR 提取扫描件中的表格"""
        if self.ocr_engine is None:
            try:
                from core.ocr_engine import OCREngine
                self.ocr_engine = OCREngine(self.config.get('ocr', {}))
            except ImportError:
                logger.error("OCR 引擎不可用")
                return []

        # 将 PDF 转为图片后 OCR
        import fitz
        doc = fitz.open(pdf_path)
        tables = []

        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=300)
            img_path = f"/tmp/page_{i}.png"
            pix.save(img_path)

            result = self.ocr_engine.process(img_path)
            if result.success and result.data:
                # 将 OCR 文本尝试解析为表格
                text_lines = result.data.get('text_lines', [])
                # 简单的文本行转 DataFrame
                if text_lines:
                    df = pd.DataFrame([line.split('\t') for line in text_lines if line.strip()])
                    tables.append(df)
                    logger.info(f"OCR 提取到内容: 第{i+1}页")

            os.remove(img_path)

        doc.close()
        return tables

    def _merge_cross_page_tables(self, tables: list[pd.DataFrame]) -> list[pd.DataFrame]:
        """合并跨页表格（检测表头重复出现）"""
        if len(tables) < 2:
            return tables

        merged = [tables[0]]
        for i in range(1, len(tables)):
            current = tables[i]
            prev = merged[-1]

            # 检查当前表头是否与前一表相同
            if list(current.columns) == list(prev.columns):
                # 表头相同，尝试合并
                try:
                    merged_df = pd.concat([prev, current], ignore_index=True)
                    merged[-1] = merged_df
                    logger.info(f"合并跨页表格: 第{len(merged)}组")
                except Exception:
                    merged.append(current)
            else:
                merged.append(current)

        return merged

    def process(
        self,
        pdf_path: str,
        strategy: str = 'auto',
        merge_cross_page: bool = True,
        output_excel: str = None
    ) -> ProcessResult:
        """
        提取 PDF 中的表格

        Args:
            pdf_path: PDF 文件路径
            strategy: 提取策略 (auto/lined/unlined/scanned/pdfplumber/camelot/ocr)
            merge_cross_page: 是否合并跨页表格
            output_excel: 输出 Excel 路径（可选）

        Returns:
            ProcessResult 包含 TableExtractionResult
        """
        result = ProcessResult()

        if not self._validate_input(pdf_path):
            result.add_error(f"PDF 文件不存在: {pdf_path}")
            return result

        try:
            # 确定策略
            if strategy == 'auto':
                page_type = self._detect_page_type(pdf_path)
                logger.info(f"页面类型检测结果: {page_type}")

                if page_type == 'scanned':
                    tables = self._extract_with_ocr(pdf_path)
                    strategy_used = 'ocr'
                elif page_type == 'lined':
                    tables = self._extract_with_pdfplumber(pdf_path)
                    if not tables:
                        tables = self._extract_with_camelot(pdf_path)
                        strategy_used = 'camelot_stream'
                    else:
                        strategy_used = 'pdfplumber'
                else:
                    tables = self._extract_with_camelot(pdf_path)
                    if not tables:
                        tables = self._extract_with_pdfplumber(pdf_path)
                        strategy_used = 'pdfplumber'
                    else:
                        strategy_used = 'camelot_stream'
            elif strategy in ('pdfplumber', 'lined'):
                tables = self._extract_with_pdfplumber(pdf_path)
                strategy_used = 'pdfplumber'
            elif strategy in ('camelot', 'unlined'):
                tables = self._extract_with_camelot(pdf_path)
                strategy_used = 'camelot_stream'
            elif strategy == 'ocr':
                tables = self._extract_with_ocr(pdf_path)
                strategy_used = 'ocr'
            else:
                tables = self._extract_with_pdfplumber(pdf_path)
                strategy_used = 'pdfplumber'

            # OCR 降级
            if not tables and self.config.get('ocr_fallback', True) and strategy != 'ocr':
                result.add_warning("常规提取无结果，降级到 OCR 模式")
                tables = self._extract_with_ocr(pdf_path)
                if tables:
                    strategy_used = 'ocr_fallback'

            # 合并跨页表格
            if merge_cross_page and tables:
                tables = self._merge_cross_page_tables(tables)

            # 输出 Excel
            if output_excel and tables:
                os.makedirs(os.path.dirname(output_excel) or '.', exist_ok=True)
                with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                    for i, table in enumerate(tables):
                        sheet_name = f"Table_{i+1}"[:31]
                        table.to_excel(writer, sheet_name=sheet_name, index=False)
                logger.info(f"表格已导出到: {output_excel}")

            extraction_result = TableExtractionResult(
                tables=tables,
                page_numbers=list(range(len(tables))),
                strategy_used=strategy_used,
                total_tables=len(tables)
            )
            result.data = extraction_result
            result.message = f"成功提取 {len(tables)} 个表格，策略: {strategy_used}"

        except Exception as e:
            result.add_error(f"PDF 表格提取失败: {str(e)}")
            logger.exception(e)

        return result
