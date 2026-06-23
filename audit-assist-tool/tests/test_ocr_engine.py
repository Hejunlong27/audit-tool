# -*- coding: utf-8 -*-
# tests/test_ocr_engine.py
"""
OCR 识别引擎测试
"""
import pytest
from core.ocr_engine import OCREngine


class TestOCREngine:

    def test_init(self, config):
        """测试 OCR 引擎初始化"""
        ocr = OCREngine(config.get('ocr', {}))
        assert ocr is not None
        assert ocr._ocr is None  # 延迟加载，未初始化前为 None

    def test_init_with_gpu_disabled(self, config):
        """测试禁用 GPU 模式初始化"""
        ocr_config = {'use_gpu': False, 'lang': 'ch'}
        ocr = OCREngine(ocr_config)
        assert ocr is not None

    def test_init_with_lang_en(self, config):
        """测试英文语言模式初始化"""
        ocr_config = {'use_gpu': False, 'lang': 'en'}
        ocr = OCREngine(ocr_config)
        assert ocr is not None

    def test_init_with_lang_ch_en(self, config):
        """测试中英混合语言模式初始化"""
        ocr_config = {'use_gpu': False, 'lang': 'ch_en'}
        ocr = OCREngine(ocr_config)
        assert ocr is not None

    def test_process_invalid_file(self, config):
        """测试无效文件路径"""
        ocr = OCREngine(config.get('ocr', {}))
        result = ocr.process('/nonexistent/image.jpg')
        assert not result.success
        assert len(result.errors) > 0

    def test_validate_input_valid_path(self, config):
        """测试输入验证 - 有效路径检查"""
        ocr = OCREngine(config.get('ocr', {}))
        # 不存在的文件应该返回 False
        assert ocr._validate_input('/nonexistent/file.jpg') is False

    def test_validate_input_nonexistent(self, config):
        """测试输入验证 - 不存在的文件"""
        ocr = OCREngine(config.get('ocr', {}))
        assert ocr._validate_input('/path/to/nonexistent/file.jpg') is False

    def test_get_ocr_instance_lazy_load(self, config):
        """测试延迟加载机制"""
        ocr = OCREngine(config.get('ocr', {}))
        # 初始状态应为 None
        assert ocr._ocr is None

    def test_config_storage(self, config):
        """测试配置存储"""
        ocr_config = {'use_gpu': False, 'lang': 'ch', 'model_type': 'server'}
        ocr = OCREngine(ocr_config)
        assert ocr.config.get('use_gpu') is False
        assert ocr.config.get('lang') == 'ch'
        assert ocr.config.get('model_type') == 'server'


class TestOCREngineIntegration:
    """OCR 引擎集成测试（需要 PaddleOCR 依赖）"""

    def test_ocr_available(self):
        """测试 OCR 引擎是否可用"""
        try:
            from paddleocr import PaddleOCR
            assert True
        except ImportError:
            pytest.skip("PaddleOCR 未安装，跳过集成测试")

    @pytest.mark.skipif(True, reason="需要实际图片文件进行测试")
    def test_process_real_image(self, sample_invoice_path):
        """测试处理真实发票图片"""
        ocr = OCREngine({'use_gpu': False, 'lang': 'ch'})
        result = ocr.process(sample_invoice_path)
        if result.success:
            assert 'text_lines' in result.data
            assert 'full_text' in result.data
