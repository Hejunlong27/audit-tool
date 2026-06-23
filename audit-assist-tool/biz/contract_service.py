# -*- coding: utf-8 -*-
# biz/contract_service.py
"""
合同审查服务
"""
import os
from loguru import logger

from core.contract_parser import ContractParser
from core.base import ProcessResult


class ContractService:
    """合同审查服务"""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.parser = ContractParser(config.get('contract', {}))

    def review_contract(self, file_path: str) -> ProcessResult:
        """审查单个合同"""
        return self.parser.process(file_path)

    def batch_review(self, file_dir: str) -> ProcessResult:
        """批量审查合同"""
        result = ProcessResult()
        results = []

        extensions = ('.pdf', '.docx', '.doc', '.txt')
        files = [f for f in os.listdir(file_dir) if f.lower().endswith(extensions)]

        for filename in files:
            file_path = os.path.join(file_dir, filename)
            sub_result = self.parser.process(file_path)
            results.append(sub_result.data)
            logger.info(f"[合同审查] {filename}: {sub_result.message}")

        result.data = results
        total_risks = sum(r.get('total_risks', 0) for r in results)
        result.message = f"批量审查完成: {len(results)} 份合同, {total_risks} 个风险点"
        return result
