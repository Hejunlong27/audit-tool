# -*- coding: utf-8 -*-
"""
合同解析器
从合同 PDF/Word 中提取关键条款，进行风险评分
"""
import os
import re
from typing import Optional
import pandas as pd
from loguru import logger

from core.base import BaseProcessor, ProcessResult


class ContractParser(BaseProcessor):
    """合同解析器"""

    # 条款模式正则
    CLAUSE_PATTERNS = {
        '合同主体': r'(甲方|乙方|委托方|受托方|买方|卖方|出租方|承租方)[：:]?\s*(.+?)(?:\n|$)',
        '合同金额': r'(?:合同总金额|合同价款|合同价格|总价)[：:]?\s*[¥￥]?\s*([\d,.]+\s*(?:万|元)?)',
        '付款条件': r'(?:付款方式|付款条件|结算方式|支付方式)[：:]?\s*(.+?)(?:\n\n|\n第|\n\d+\.|$)',
        '违约责任': r'(?:违约责任|违约条款|违约金)[：:]?\s*(.+?)(?:\n\n|\n第|\n\d+\.|$)',
        '保密条款': r'(?:保密[条款义务]|保密责任)[：:]?\s*(.+?)(?:\n\n|\n第|\n\d+\.|$)',
        '争议解决': r'(?:争议解决|争议处理|管辖法院|仲裁)[：:]?\s*(.+?)(?:\n\n|\n第|\n\d+\.|$)',
        '合同期限': r'(?:合同期限|合同有效期|合同期限为|有效期)[：:]?\s*(.+?)(?:\n|$)',
        '不可抗力': r'(?:不可抗力)[：:]?\s*(.+?)(?:\n\n|\n第|\n\d+\.|$)',
    }

    def _extract_text(self, file_path: str) -> str:
        """从 PDF 或 Word 文件中提取文本"""
        ext = os.path.splitext(file_path)[1].lower()

        if ext == '.pdf':
            import pdfplumber
            text = ''
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + '\n'
            return text

        elif ext in ('.docx', '.doc'):
            from docx import Document
            doc = Document(file_path)
            return '\n'.join([p.text for p in doc.paragraphs])

        elif ext in ('.txt',):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()

        return ''

    def _extract_clauses(self, text: str) -> dict:
        """提取合同条款"""
        clauses = {}

        for clause_type, pattern in self.CLAUSE_PATTERNS.items():
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                clauses[clause_type] = [m.strip() for m in matches if m.strip()]

        return clauses

    def _assess_risk(self, clauses: dict) -> list[dict]:
        """评估条款风险"""
        risk_keywords = self.config.get('risk_keywords', [
            '不可撤销', '无条件承担', '无限连带责任',
            '单方面解约', '自动续期'
        ])

        risks = []
        all_text = '\n'.join(
            '\n'.join(items) for items in clauses.values()
        )

        for keyword in risk_keywords:
            if keyword in all_text:
                # 找到包含关键词的条款
                for clause_type, items in clauses.items():
                    for item in items:
                        if keyword in item:
                            risks.append({
                                'clause_type': clause_type,
                                'risk_keyword': keyword,
                                'clause_text': item[:200],
                                'severity': 'high' if keyword in ('无限连带责任', '不可撤销') else 'medium'
                            })

        return risks

    def _extract_dates(self, text: str) -> dict:
        """提取合同日期信息"""
        dates = {}

        # 签订日期
        sign_match = re.search(r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', text)
        if sign_match:
            dates['sign_date'] = f"{sign_match.group(1)}-{sign_match.group(2):0>2}-{sign_match.group(3):0>2}"

        # 有效期
        period_match = re.search(
            r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日\s*(?:至|到|至-)\s*(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日',
            text
        )
        if period_match:
            dates['start_date'] = f"{period_match.group(1)}-{period_match.group(2):0>2}-{period_match.group(3):0>2}"
            dates['end_date'] = f"{period_match.group(4)}-{period_match.group(5):0>2}-{period_match.group(6):0>2}"

        return dates

    def process(self, file_path: str) -> ProcessResult:
        """解析合同文件"""
        result = ProcessResult()

        if not self._validate_input(file_path):
            result.add_error(f"文件不存在: {file_path}")
            return result

        try:
            text = self._extract_text(file_path)
            if not text.strip():
                result.add_error("文件内容为空")
                return result

            clauses = self._extract_clauses(text)
            risks = self._assess_risk(clauses)
            dates = self._extract_dates(text)

            result.data = {
                'file_path': file_path,
                'clauses': clauses,
                'risks': risks,
                'dates': dates,
                'total_clauses': sum(len(v) for v in clauses.values()),
                'total_risks': len(risks)
            }
            result.message = f"合同解析完成: {result.data['total_clauses']} 个条款, {len(risks)} 个风险点"

        except Exception as e:
            result.add_error(f"合同解析失败: {str(e)}")
            logger.exception(e)

        return result
