# -*- coding: utf-8 -*-
"""
发票识别器
OCR 识别 + 正则模板提取 + 查重检测
"""
import os
import re
import yaml
from typing import Optional
from loguru import logger

from core.base import BaseProcessor, ProcessResult
from core.ocr_engine import OCREngine


class InvoiceRecognizer(BaseProcessor):
    """发票识别器"""

    def __init__(self, config: dict = None):
        super().__init__(config)
        self.ocr_engine = OCREngine(config.get('ocr', {}))
        self.templates = self._load_templates()

    def _load_templates(self) -> dict:
        """加载发票识别模板"""
        template_path = os.path.join(
            os.path.dirname(__file__), '..', 'config', 'rules', 'invoice.yaml'
        )
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f).get('templates', {})
        return {}

    def _extract_fields(self, text_lines: list[str], invoice_type: str = None) -> dict:
        """从 OCR 文本中提取发票字段"""
        fields = {}

        # 确定使用哪个模板
        templates_to_try = []
        if invoice_type and invoice_type in self.templates:
            templates_to_try.append(self.templates[invoice_type])
        else:
            templates_to_try = list(self.templates.values())

        full_text = '\n'.join(text_lines)

        for template in templates_to_try:
            field_patterns = template.get('field_patterns', {})
            for field_name, pattern_config in field_patterns.items():
                if field_name in fields:
                    continue

                regex = pattern_config['regex']
                group = pattern_config.get('group', 1)
                fmt = pattern_config.get('format', None)

                match = re.search(regex, full_text)
                if match:
                    if group == 'all':
                        value = match.group(0)
                        if fmt:
                            try:
                                value = fmt.format(*match.groups())
                            except (IndexError, KeyError):
                                value = match.group(0)
                    else:
                        value = match.group(group)

                    # 金额字段清理
                    if field_name in ('amount', 'tax', 'total'):
                        try:
                            value = float(str(value).replace(',', ''))
                        except ValueError:
                            value = None

                    fields[field_name] = value

        return fields

    def process(self, image_path: str, project_name: str = '') -> ProcessResult:
        """
        识别单张发票

        Args:
            image_path: 发票图片路径
            project_name: 所属项目名称
        """
        result = ProcessResult()

        # Step 1: OCR 识别
        ocr_result = self.ocr_engine.process(image_path)
        if not ocr_result.success:
            return ocr_result

        text_lines = ocr_result.data['text_lines']

        # Step 2: 正则提取字段
        fields = self._extract_fields(text_lines)

        if not fields:
            result.add_warning("未能提取到任何发票字段")
            result.data = {'fields': {}, 'is_duplicate': False}
            return result

        # Step 3: 查重检测
        fingerprint = self._generate_fingerprint(fields)
        is_duplicate = self._check_duplicate(fingerprint)

        if is_duplicate:
            result.add_warning(f"疑似重复发票: {fingerprint}")

        result.data = {
            'fields': fields,
            'fingerprint': fingerprint,
            'is_duplicate': is_duplicate,
            'file_path': image_path,
            'project_name': project_name
        }
        result.message = f"发票识别完成: 提取 {len(fields)} 个字段" + (" [疑似重复]" if is_duplicate else "")

        return result

    def batch_process(self, image_dir: str, project_name: str = '') -> ProcessResult:
        """批量识别目录下的发票"""
        result = ProcessResult()
        results = []

        image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.pdf')
        files = [f for f in os.listdir(image_dir)
                 if f.lower().endswith(image_extensions)]

        for i, filename in enumerate(files):
            file_path = os.path.join(image_dir, filename)
            sub_result = self.process(file_path, project_name)
            results.append(sub_result.data)
            logger.info(f"[{i+1}/{len(files)}] {filename}: {sub_result.message}")

        success_count = sum(1 for r in results if r.get('fields'))
        result.data = results
        result.message = f"批量识别完成: {success_count}/{len(files)} 成功提取"
        return result

    def _generate_fingerprint(self, fields: dict) -> str:
        """生成发票指纹（用于查重）"""
        parts = [
            str(fields.get('invoice_code', '')),
            str(fields.get('invoice_number', '')),
            str(fields.get('amount', ''))
        ]
        return '_'.join(parts)

    def _check_duplicate(self, fingerprint: str) -> bool:
        """检查是否为重复发票"""
        try:
            from db.init_db import get_connection
            conn = get_connection()
            cursor = conn.execute(
                'SELECT id FROM invoice_fingerprints WHERE fingerprint = ?',
                (fingerprint,)
            )
            exists = cursor.fetchone() is not None
            conn.close()
            return exists
        except Exception:
            return False
