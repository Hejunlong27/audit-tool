# -*- coding: utf-8 -*-
# biz/analysis_service.py
"""
数据分析服务
"""
import os
import pandas as pd
from loguru import logger

from core.data_analyzer import DataAnalyzer
from core.base import ProcessResult


class AnalysisService:
    """数据分析服务"""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.analyzer = DataAnalyzer(config.get('analysis', {}))

    def load_data(self, file_path: str, **kwargs) -> pd.DataFrame:
        """加载数据文件（Excel/CSV）"""
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ('.xlsx', '.xls'):
            return pd.read_excel(file_path, **kwargs)
        elif ext == '.csv':
            return pd.read_csv(file_path, encoding='utf-8', **kwargs)
        else:
            raise ValueError(f"不支持的文件格式: {ext}")

    def analyze_bank_statement(self, file_path: str, **kwargs) -> ProcessResult:
        """分析银行流水"""
        df = self.load_data(file_path)
        return self.analyzer.analyze_bank_statement(df, **kwargs)

    def benford_test(self, file_path: str, amount_col: str = 'amount') -> ProcessResult:
        """Benford 法则检验"""
        df = self.load_data(file_path)
        return self.analyzer.benford_test(df[amount_col])

    def reconcile(
        self,
        left_path: str,
        right_path: str,
        key_columns: list,
        amount_col: str,
        date_col: str
    ) -> ProcessResult:
        """多源对账"""
        df_left = self.load_data(left_path)
        df_right = self.load_data(right_path)
        return self.analyzer.reconcile(
            df_left, df_right, key_columns, amount_col, date_col
        )
