# -*- coding: utf-8 -*-
# tests/conftest.py
"""
pytest 公共 fixtures
"""
import os
import pytest
import pandas as pd


@pytest.fixture
def sample_pdf_path():
    """示例 PDF 文件路径"""
    return os.path.join(os.path.dirname(__file__), 'fixtures', 'sample.pdf')


@pytest.fixture
def sample_invoice_path():
    """示例发票图片路径"""
    return os.path.join(os.path.dirname(__file__), 'fixtures', 'sample_invoice.jpg')


@pytest.fixture
def sample_bank_statement():
    """示例银行流水 DataFrame"""
    return pd.DataFrame({
        'date': pd.date_range('2026-01-01', periods=100, freq='h'),
        'amount': [100.0, -500.0, 1000000.0, 200.0, -300.0] * 20,
        'counterparty': ['公司A', '公司B', '公司C', '公司A', '公司D'] * 20,
        'balance': [50000.0 + i * 100 for i in range(100)],
        'summary': ['转账', '收款', '付款', '手续费', '存款'] * 20
    })


@pytest.fixture
def config():
    """测试配置"""
    return {
        'pdf_extract': {'ocr_fallback': False},
        'ocr': {'use_gpu': False, 'lang': 'ch'},
        'analysis': {
            'bank_statement': {
                'large_amount_threshold': 500000,
                'off_hours': {'start': '22:00', 'end': '06:00'}
            }
        }
    }
