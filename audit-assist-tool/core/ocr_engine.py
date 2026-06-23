# -*- coding: utf-8 -*-
"""
OCR 识别引擎
基于 PaddleOCR PP-OCRv5 实现，支持中文印刷体识别
"""
import os
from typing import Optional
from loguru import logger

from core.base import BaseProcessor, ProcessResult


class OCREngine(BaseProcessor):
    """OCR 识别引擎"""

    def __init__(self, config: dict = None):
        super().__init__(config)
        self._ocr = None

    def _get_ocr_instance(self):
        """延迟加载 PaddleOCR（模型加载耗时较长）"""
        if self._ocr is None:
            from paddleocr import PaddleOCR

            use_gpu = self.config.get('use_gpu', False)
            lang = self.config.get('lang', 'ch')

            self._ocr = PaddleOCR(
                use_angle_cls=True,
                lang=lang,
                use_gpu=use_gpu,
                show_log=False,
                # PP-OCRv5 server 模型精度更高
                ocr_version='PP-OCRv5'
            )
            logger.info(f"PaddleOCR 初始化完成 (lang={lang}, gpu={use_gpu})")

        return self._ocr

    def process(self, image_path: str) -> ProcessResult:
        """
        对图片进行 OCR 识别

        Returns:
            ProcessResult.data 包含:
            - text_lines: list[str] 识别到的文本行
            - text_blocks: list[dict] 含位置信息的文本块
            - full_text: str 全部文本拼接
        """
        result = ProcessResult()

        if not self._validate_input(image_path):
            result.add_error(f"图片文件不存在: {image_path}")
            return result

        try:
            ocr = self._get_ocr_instance()
            ocr_result = ocr.ocr(image_path, cls=True)

            if not ocr_result or not ocr_result[0]:
                result.add_warning("OCR 未识别到任何文字")
                result.data = {'text_lines': [], 'text_blocks': [], 'full_text': ''}
                return result

            text_lines = []
            text_blocks = []

            for line in ocr_result[0]:
                bbox, (text, confidence) = line[0], line[1]
                text_lines.append(text)
                text_blocks.append({
                    'text': text,
                    'confidence': confidence,
                    'bbox': bbox  # [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
                })

            full_text = '\n'.join(text_lines)

            result.data = {
                'text_lines': text_lines,
                'text_blocks': text_blocks,
                'full_text': full_text
            }
            result.message = f"OCR 识别完成: {len(text_lines)} 行文本"
            logger.info(result.message)

        except ImportError:
            result.add_error("PaddleOCR 未安装，请运行: pip install paddlepaddle paddleocr")
        except Exception as e:
            result.add_error(f"OCR 识别失败: {str(e)}")
            logger.exception(e)

        return result
