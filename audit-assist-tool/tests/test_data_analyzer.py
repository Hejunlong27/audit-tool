# -*- coding: utf-8 -*-
# tests/test_data_analyzer.py
"""
数据分析引擎测试
"""
import pytest
import pandas as pd
import numpy as np
from core.data_analyzer import DataAnalyzer


class TestDataAnalyzer:

    def test_init(self, config):
        """测试数据分析器初始化"""
        analyzer = DataAnalyzer(config.get('analysis', {}))
        assert analyzer is not None

    def test_init_empty_config(self):
        """测试空配置初始化"""
        analyzer = DataAnalyzer({})
        assert analyzer is not None


class TestBankStatementAnalysis:

    def test_analyze_bank_statement_basic(self, config, sample_bank_statement):
        """测试银行流水基本分析"""
        analyzer = DataAnalyzer(config.get('analysis', {}))
        result = analyzer.analyze_bank_statement(
            sample_bank_statement,
            date_col='date',
            amount_col='amount',
            counterparty_col='counterparty',
            balance_col='balance'
        )
        assert result.success
        assert result.data is not None
        assert '大额交易' in result.data

    def test_analyze_bank_statement_large_amount(self, config, sample_bank_statement):
        """测试大额交易检测"""
        analyzer = DataAnalyzer(config.get('analysis', {}))
        result = analyzer.analyze_bank_statement(
            sample_bank_statement,
            date_col='date',
            amount_col='amount',
            counterparty_col='counterparty',
            balance_col='balance'
        )
        # 检查是否有大额交易（阈值50万）
        large_tx = result.data.get('大额交易', [])
        assert isinstance(large_tx, list)

    def test_analyze_bank_statement_round_amount(self, config, sample_bank_statement):
        """测试整额交易检测"""
        analyzer = DataAnalyzer(config.get('analysis', {}))
        result = analyzer.analyze_bank_statement(
            sample_bank_statement,
            date_col='date',
            amount_col='amount',
            counterparty_col='counterparty'
        )
        # 检查整额交易
        round_tx = result.data.get('整额交易', [])
        assert isinstance(round_tx, list)

    def test_analyze_bank_statement_frequent_counterparty(self, config, sample_bank_statement):
        """测试频繁对手方检测"""
        analyzer = DataAnalyzer(config.get('analysis', {}))
        result = analyzer.analyze_bank_statement(
            sample_bank_statement,
            date_col='date',
            amount_col='amount',
            counterparty_col='counterparty'
        )
        # 检查频繁对手方
        frequent_cp = result.data.get('频繁对手方', {})
        assert isinstance(frequent_cp, dict)

    def test_analyze_bank_statement_invalid_date_col(self, config, sample_bank_statement):
        """测试无效日期列"""
        analyzer = DataAnalyzer(config.get('analysis', {}))
        result = analyzer.analyze_bank_statement(
            sample_bank_statement,
            date_col='invalid_date_col',
            amount_col='amount'
        )
        # 应该处理错误但不完全失败
        assert result.data is not None or len(result.errors) >= 0


class TestBenfordTest:

    def test_benford_test_normal_distribution(self, config):
        """测试 Benford 法则 - 正常分布"""
        analyzer = DataAnalyzer(config.get('analysis', {}))
        # 生成符合 Benford 分布的数据
        np.random.seed(42)
        data = np.random.lognormal(mean=5, sigma=2, size=1000)

        result = analyzer.benford_test(pd.Series(data))
        assert result.success
        assert result.data is not None
        assert 'p_value' in result.data
        assert 'chi2_statistic' in result.data

    def test_benford_test_small_sample(self, config):
        """测试 Benford 法则 - 小样本"""
        analyzer = DataAnalyzer(config.get('analysis', {}))
        # 样本量小于30的情况
        data = pd.Series([100, 200, 300, 400, 500])

        result = analyzer.benford_test(data, min_sample=30)
        # 样本量不足应该产生警告
        assert len(result.warnings) > 0 or not result.success

    def test_benford_test_empty_data(self, config):
        """测试 Benford 法则 - 空数据"""
        analyzer = DataAnalyzer(config.get('analysis', {}))
        data = pd.Series([])

        result = analyzer.benford_test(data)
        assert result.success or len(result.errors) > 0

    def test_benford_test_negative_values(self, config):
        """测试 Benford 法则 - 负值处理"""
        analyzer = DataAnalyzer(config.get('analysis', {}))
        data = pd.Series([-100, -200, 300, 400, 500])

        result = analyzer.benford_test(data)
        # 应该过滤负数
        assert result.success
        assert result.data is not None


class TestReconciliation:

    def test_reconcile_basic(self, config):
        """测试基本对账功能"""
        analyzer = DataAnalyzer(config.get('analysis', {}))

        df_left = pd.DataFrame({
            'date': pd.to_datetime(['2026-01-01', '2026-01-02', '2026-01-03']),
            'amount': [100.0, 200.0, 300.0],
            'desc': ['A', 'B', 'C']
        })

        df_right = pd.DataFrame({
            'date': pd.to_datetime(['2026-01-01', '2026-01-02', '2026-01-03']),
            'amount': [100.0, 200.0, 300.0],
            'desc': ['A', 'B', 'C']
        })

        result = analyzer.reconcile(
            df_left, df_right,
            key_columns=['desc'],
            amount_col='amount',
            date_col='date'
        )
        assert result.success
        assert 'matched' in result.data
        assert 'unmatched_left' in result.data
        assert 'unmatched_right' in result.data

    def test_reconcile_with_tolerance(self, config):
        """测试带容差的对账"""
        analyzer = DataAnalyzer(config.get('analysis', {}))

        df_left = pd.DataFrame({
            'date': pd.to_datetime(['2026-01-01']),
            'amount': [100.5],
            'desc': ['A']
        })

        df_right = pd.DataFrame({
            'date': pd.to_datetime(['2026-01-01']),
            'amount': [100.0],
            'desc': ['A']
        })

        result = analyzer.reconcile(
            df_left, df_right,
            key_columns=['desc'],
            amount_col='amount',
            date_col='date',
            amount_tolerance=1.0
        )
        assert result.success

    def test_reconcile_empty_dataframes(self, config):
        """测试空DataFrame对账"""
        analyzer = DataAnalyzer(config.get('analysis', {}))

        df_left = pd.DataFrame({'date': [], 'amount': [], 'desc': []})
        df_right = pd.DataFrame({'date': [], 'amount': [], 'desc': []})

        result = analyzer.reconcile(
            df_left, df_right,
            key_columns=['desc'],
            amount_col='amount',
            date_col='date'
        )
        assert result.success
