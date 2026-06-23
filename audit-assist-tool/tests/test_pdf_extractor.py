# -*- coding: utf-8 -*-
# tests/test_pdf_extractor.py
"""
PDF 表格提取器测试
"""
import pytest
import pandas as pd
from core.pdf_extractor import PDFTableExtractor


class TestPDFTableExtractor:

    def test_init(self, config):
        extractor = PDFTableExtractor(config.get('pdf_extract'))
        assert extractor is not None

    def test_detect_page_type_lined(self, config):
        """测试有线框页面检测"""
        extractor = PDFTableExtractor(config.get('pdf_extract'))
        # 需要准备测试 PDF
        # page_type = extractor._detect_page_type('tests/fixtures/lined_table.pdf')
        # assert page_type == 'lined'
        pass

    def test_process_invalid_file(self, config):
        """测试无效文件路径"""
        extractor = PDFTableExtractor(config.get('pdf_extract'))
        result = extractor.process('/nonexistent/file.pdf')
        assert not result.success
        assert len(result.errors) > 0

    def test_benford_theoretical_distribution(self, config):
        """测试 Benford 理论分布"""
        from core.data_analyzer import DataAnalyzer
        analyzer = DataAnalyzer(config.get('analysis', {}))

        # 生成符合 Benford 分布的数据
        import numpy as np
        np.random.seed(42)
        data = np.random.lognormal(mean=5, sigma=2, size=1000)

        result = analyzer.benford_test(pd.Series(data))
        assert result.success
        assert result.data is not None
        assert 'p_value' in result.data
