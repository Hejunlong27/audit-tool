# -*- coding: utf-8 -*-
"""
数据分析引擎
支持银行流水分析、Benford 法则检验、异常检测、多源对账
"""
import os
from typing import Optional
import pandas as pd
import numpy as np
from scipy import stats
from loguru import logger

from core.base import BaseProcessor, ProcessResult


class DataAnalyzer(BaseProcessor):
    """数据分析引擎"""

    def process(self, data: Any = None, **kwargs) -> ProcessResult:
        """
        通用处理入口

        Args:
            data: 输入数据（DataFrame 或文件路径）
            **kwargs: 其他参数

        Returns:
            ProcessResult
        """
        result = ProcessResult()

        # 根据数据类型自动选择分析方法
        if isinstance(data, pd.DataFrame):
            # 如果是 DataFrame，尝试进行银行流水分析
            return self.analyze_bank_statement(data, **kwargs)
        elif isinstance(data, str) and os.path.isfile(data):
            # 如果是文件路径，加载后分析
            ext = os.path.splitext(data)[1].lower()
            if ext in ('.xlsx', '.xls', '.csv'):
                df = pd.read_excel(data) if ext in ('.xlsx', '.xls') else pd.read_csv(data)
                return self.analyze_bank_statement(df, **kwargs)

        result.add_warning("DataAnalyzer.process() 建议直接调用具体方法")
        return result

    def analyze_bank_statement(
        self,
        df: pd.DataFrame,
        date_col: str = 'date',
        amount_col: str = 'amount',
        counterparty_col: str = 'counterparty',
        balance_col: str = 'balance',
        config: dict = None
    ) -> ProcessResult:
        """
        银行流水异常分析

        Args:
            df: 银行流水 DataFrame
            date_col: 日期列名
            amount_col: 金额列名
            counterparty_col: 对手方列名
            balance_col: 余额列名
            config: 分析配置
        """
        result = ProcessResult()
        config = config or self.config.get('bank_statement', {})
        anomalies = {}

        try:
            # 确保日期列为 datetime 类型
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            df[amount_col] = pd.to_numeric(df[amount_col], errors='coerce')

            # 1. 大额交易
            threshold = config.get('large_amount_threshold', 500000)
            large_tx = df[df[amount_col].abs() >= threshold]
            anomalies['大额交易'] = large_tx.to_dict('records')
            logger.info(f"大额交易: {len(large_tx)} 笔 (阈值: {threshold})")

            # 2. 整额交易
            round_tx = df[df[amount_col].abs() % 10000 == 0]
            anomalies['整额交易'] = round_tx.to_dict('records')
            logger.info(f"整额交易: {len(round_tx)} 笔")

            # 3. 非工作时间交易
            if counterparty_col in df.columns:
                off_hours = config.get('off_hours', {'start': '22:00', 'end': '06:00'})
                start_h = int(off_hours['start'].split(':')[0])
                end_h = int(off_hours['end'].split(':')[0])

                hours = df[date_col].dt.hour
                if start_h > end_h:  # 跨午夜
                    off_time_tx = df[(hours >= start_h) | (hours < end_h)]
                else:
                    off_time_tx = df[(hours >= start_h) & (hours < end_h)]

                # 排除周末
                off_time_tx = off_time_tx[off_time_tx[date_col].dt.dayofweek < 5]
                anomalies['非工作时间交易'] = off_time_tx.to_dict('records')
                logger.info(f"非工作时间交易: {len(off_time_tx)} 笔")

            # 4. 频繁对手方
            if counterparty_col in df.columns:
                freq_threshold = config.get('frequent_counterparty_threshold', 10)
                counterparty_counts = df[counterparty_col].value_counts()
                frequent = counterparty_counts[counterparty_counts >= freq_threshold]
                anomalies['频繁对手方'] = frequent.to_dict()
                logger.info(f"频繁对手方: {len(frequent)} 个 (阈值: {freq_threshold})")

            # 5. 余额异常波动
            if balance_col in df.columns:
                df[balance_col] = pd.to_numeric(df[balance_col], errors='coerce')
                std_multiple = config.get('balance_anomaly_std_multiple', 3)
                daily_change = df[balance_col].diff().abs()
                mean_change = daily_change.mean()
                std_change = daily_change.std()
                threshold_val = mean_change + std_multiple * std_change
                balance_anomaly = df[daily_change > threshold_val]
                anomalies['余额异常波动'] = balance_anomaly.to_dict('records')
                logger.info(f"余额异常波动: {len(balance_anomaly)} 笔")

            # 6. 拆分交易检测
            if counterparty_col in df.columns:
                window_hours = config.get('split_transaction_window', 24)
                split_threshold = config.get('split_transaction_threshold', 500000)
                df_sorted = df.sort_values(date_col)
                df_sorted['time_group'] = df_sorted[date_col].dt.floor(f'{window_hours}h')

                grouped = df_sorted.groupby([counterparty_col, 'time_group'])[amount_col].agg(['sum', 'count'])
                split_suspects = grouped[(grouped['sum'].abs() >= split_threshold) & (grouped['count'] > 1)]
                anomalies['疑似拆分交易'] = split_suspects.reset_index().to_dict('records')
                logger.info(f"疑似拆分交易: {len(split_suspects)} 组")

            result.data = anomalies
            total_anomalies = sum(len(v) for v in anomalies.values() if isinstance(v, list))
            result.message = f"分析完成，发现 {total_anomalies} 条异常记录"

        except Exception as e:
            result.add_error(f"银行流水分析失败: {str(e)}")
            logger.exception(e)

        return result

    def benford_test(
        self,
        data: pd.Series,
        alpha: float = 0.05,
        min_sample: int = 30
    ) -> ProcessResult:
        """
        Benford 法则检验

        Args:
            data: 数值序列（如金额列）
            alpha: 显著性水平
            min_sample: 最小样本量

        Returns:
            包含首位数字分布、卡方检验结果、p 值
        """
        result = ProcessResult()

        try:
            # 过滤正数
            values = data[data > 0].dropna()
            if len(values) < min_sample:
                result.add_warning(f"样本量不足 ({len(values)} < {min_sample})，结果可能不可靠")

            # 提取首位数字（过滤0和非数字）
            first_digits = values.astype(str).str[0]
            first_digits = first_digits[first_digits.str.match(r'^[1-9]$')].astype(int)
            observed = first_digits.value_counts().sort_index()

            # 确保包含 1-9
            for d in range(1, 10):
                if d not in observed.index:
                    observed[d] = 0
            observed = observed.sort_index()

            # 理论分布
            theoretical = pd.Series({
                1: 0.301, 2: 0.176, 3: 0.125, 4: 0.097,
                5: 0.079, 6: 0.067, 7: 0.058, 8: 0.051, 9: 0.046
            })

            # 使用观测值的实际总数来计算期望频数
            total_observed = len(first_digits)
            expected_counts = theoretical * total_observed

            # 卡方检验（归一化以确保总和相等）
            observed_normalized = observed.values / observed.values.sum()
            expected_normalized = expected_counts.values / expected_counts.values.sum()
            chi2, p_value = stats.chisquare(observed_normalized, f_exp=expected_normalized)

            is_anomaly = p_value < alpha

            result.data = {
                'observed': observed.to_dict(),
                'expected': (expected_counts).to_dict(),
                'chi2_statistic': float(chi2),
                'p_value': float(p_value),
                'alpha': alpha,
                'is_anomaly': is_anomaly,
                'sample_size': len(values),
                'conclusion': '偏离 Benford 分布，可能存在异常' if is_anomaly else '符合 Benford 分布'
            }
            result.message = f"Benford 检验: p={p_value:.4f}, {'异常' if is_anomaly else '正常'}"
            logger.info(result.message)

        except Exception as e:
            result.add_error(f"Benford 法则检验失败: {str(e)}")
            logger.exception(e)

        return result

    def reconcile(
        self,
        df_left: pd.DataFrame,
        df_right: pd.DataFrame,
        key_columns: list,
        amount_col: str,
        date_col: str,
        date_tolerance_days: int = 3,
        amount_tolerance: float = 1.0
    ) -> ProcessResult:
        """
        多源数据对账

        Args:
            df_left: 左表（如银行流水）
            df_right: 右表（如企业账簿）
            key_columns: 匹配关键字段列表
            amount_col: 金额列名
            date_col: 日期列名
            date_tolerance_days: 日期容差（天）
            amount_tolerance: 金额容差
        """
        result = ProcessResult()

        try:
            df_left[date_col] = pd.to_datetime(df_left[date_col], errors='coerce')
            df_right[date_col] = pd.to_datetime(df_right[date_col], errors='coerce')
            df_left[amount_col] = pd.to_numeric(df_left[amount_col], errors='coerce')
            df_right[amount_col] = pd.to_numeric(df_right[amount_col], errors='coerce')

            matched = []
            unmatched_left = []
            unmatched_right = []

            used_right_indices = set()

            for _, left_row in df_left.iterrows():
                found = False
                for j, right_row in df_right.iterrows():
                    if j in used_right_indices:
                        continue

                    # 金额匹配（容差内）
                    amount_diff = abs(left_row[amount_col] - right_row[amount_col])
                    if amount_diff > amount_tolerance:
                        continue

                    # 日期匹配（容差内）
                    date_diff = abs((left_row[date_col] - right_row[date_col]).days)
                    if date_diff > date_tolerance_days:
                        continue

                    matched.append({
                        'left': left_row.to_dict(),
                        'right': right_row.to_dict(),
                        'amount_diff': amount_diff,
                        'date_diff_days': date_diff
                    })
                    used_right_indices.add(j)
                    found = True
                    break

                if not found:
                    unmatched_left.append(left_row.to_dict())

            for j, right_row in df_right.iterrows():
                if j not in used_right_indices:
                    unmatched_right.append(right_row.to_dict())

            result.data = {
                'matched': matched,
                'unmatched_left': unmatched_left,
                'unmatched_right': unmatched_right,
                'match_rate': len(matched) / len(df_left) if len(df_left) > 0 else 0
            }
            result.message = f"对账完成: 匹配 {len(matched)}, 左表未达 {len(unmatched_left)}, 右表未达 {len(unmatched_right)}"

        except Exception as e:
            result.add_error(f"对账失败: {str(e)}")
            logger.exception(e)

        return result
