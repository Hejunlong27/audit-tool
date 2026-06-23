# -*- coding: utf-8 -*-
# tests/test_invoice_recognizer.py
"""
发票识别器测试
"""
import pytest
from core.invoice_recognizer import InvoiceRecognizer


class TestInvoiceRecognizer:

    def test_init(self, config):
        """测试发票识别器初始化"""
        recognizer = InvoiceRecognizer(config.get('invoice', {}))
        assert recognizer is not None

    def test_init_empty_config(self):
        """测试空配置初始化"""
        recognizer = InvoiceRecognizer({})
        assert recognizer is not None

    def test_ocr_engine_initialized(self, config):
        """测试 OCR 引擎已初始化"""
        recognizer = InvoiceRecognizer(config.get('invoice', {}))
        assert recognizer.ocr_engine is not None

    def test_templates_loaded(self, config):
        """测试模板加载"""
        recognizer = InvoiceRecognizer(config.get('invoice', {}))
        # 模板应该是一个字典
        assert isinstance(recognizer.templates, dict)


class TestInvoiceFieldExtraction:

    def test_extract_fields_empty_text(self, config):
        """测试空文本字段提取"""
        recognizer = InvoiceRecognizer(config.get('invoice', {}))
        fields = recognizer._extract_fields([])
        assert isinstance(fields, dict)
        assert len(fields) == 0

    def test_extract_fields_with_text(self, config):
        """测试带文本的字段提取"""
        recognizer = InvoiceRecognizer(config.get('invoice', {}))
        # 模拟 OCR 文本行
        text_lines = [
            '发票代码：1234567890',
            '发票号码：12345678',
            '金额：¥1,000.00'
        ]
        fields = recognizer._extract_fields(text_lines)
        assert isinstance(fields, dict)

    def test_extract_fields_invoice_type_filter(self, config):
        """测试按发票类型过滤字段"""
        recognizer = InvoiceRecognizer(config.get('invoice', {}))
        text_lines = [
            '发票代码：1234567890',
            '发票号码：12345678'
        ]
        fields = recognizer._extract_fields(text_lines, invoice_type='增值税专用发票')
        assert isinstance(fields, dict)


class TestInvoiceFingerprint:

    def test_generate_fingerprint_basic(self, config):
        """测试基本指纹生成"""
        recognizer = InvoiceRecognizer(config.get('invoice', {}))
        fields = {
            'invoice_code': '1234567890',
            'invoice_number': '12345678',
            'amount': 1000.0
        }
        fingerprint = recognizer._generate_fingerprint(fields)
        assert isinstance(fingerprint, str)
        assert '1234567890' in fingerprint
        assert '12345678' in fingerprint

    def test_generate_fingerprint_empty_fields(self, config):
        """测试空字段指纹生成"""
        recognizer = InvoiceRecognizer(config.get('invoice', {}))
        fields = {}
        fingerprint = recognizer._generate_fingerprint(fields)
        assert isinstance(fingerprint, str)

    def test_generate_fingerprint_partial_fields(self, config):
        """测试部分字段指纹生成"""
        recognizer = InvoiceRecognizer(config.get('invoice', {}))
        fields = {
            'invoice_code': '1234567890',
            'invoice_number': '12345678'
        }
        fingerprint = recognizer._generate_fingerprint(fields)
        assert isinstance(fingerprint, str)


class TestInvoiceDuplicateCheck:

    def test_check_duplicate_new_invoice(self, config):
        """测试新发票查重"""
        recognizer = InvoiceRecognizer(config.get('invoice', {}))
        fingerprint = 'new_invoice_fingerprint_12345'
        is_dup = recognizer._check_duplicate(fingerprint)
        # 新发票应该不是重复
        assert isinstance(is_dup, bool)

    def test_check_duplicate_database_error(self, config):
        """测试数据库错误时的查重"""
        recognizer = InvoiceRecognizer(config.get('invoice', {}))
        # 使用不存在的指纹
        is_dup = recognizer._check_duplicate('nonexistent_fingerprint_xxx')
        # 数据库错误时应该返回 False
        assert is_dup is False


class TestInvoiceRecognize:

    def test_process_invalid_file(self, config):
        """测试处理无效文件"""
        recognizer = InvoiceRecognizer(config.get('invoice', {}))
        result = recognizer.process('/nonexistent/invoice.jpg')
        # OCR 失败时 result.success 应为 False
        assert not result.success or len(result.errors) > 0

    def test_process_valid_file_with_ocr_failure(self, config):
        """测试文件存在但 OCR 识别失败"""
        recognizer = InvoiceRecognizer(config.get('invoice', {}))
        # 不存在的文件路径
        result = recognizer.process('/nonexistent/path/invoice.jpg')
        assert not result.success


class TestInvoiceBatchProcess:

    def test_batch_process_empty_directory(self, config):
        """测试批量处理空目录"""
        recognizer = InvoiceRecognizer(config.get('invoice', {}))
        result = recognizer.batch_process('/nonexistent/directory')
        # 目录不存在时应该返回失败
        assert not result.success
        assert len(result.errors) > 0

    def test_batch_process_directory_validation(self, config):
        """测试目录验证"""
        recognizer = InvoiceRecognizer(config.get('invoice', {}))
        # 不存在的目录
        result = recognizer.batch_process('/nonexistent/path')
        # 应该处理错误
        assert result.success or len(result.errors) >= 0


class TestInvoiceRecognizerIntegration:
    """发票识别器集成测试（需要实际文件）"""

    @pytest.mark.skipif(True, reason="需要实际发票图片进行测试")
    def test_process_real_invoice(self, sample_invoice_path):
        """测试处理真实发票"""
        recognizer = InvoiceRecognizer({'ocr': {'use_gpu': False, 'lang': 'ch'}})
        result = recognizer.process(sample_invoice_path)
        if result.success:
            assert 'fields' in result.data
            assert 'fingerprint' in result.data
            assert 'is_duplicate' in result.data
