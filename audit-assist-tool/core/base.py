# -*- coding: utf-8 -*-
"""
处理器基类
所有核心处理器继承此基类，统一输入输出规范
"""
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional
from loguru import logger


@dataclass
class ProcessResult:
    """处理结果基类"""
    success: bool = True
    data: Any = None
    message: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def add_warning(self, msg: str):
        self.warnings.append(msg)
        logger.warning(msg)

    def add_error(self, msg: str):
        self.errors.append(msg)
        self.success = False
        logger.error(msg)


class BaseProcessor(ABC):
    """处理器基类"""

    def __init__(self, config: dict = None):
        self.config = config or {}

    @abstractmethod
    def process(self, *args, **kwargs) -> ProcessResult:
        """处理方法，子类必须实现"""
        pass

    def _validate_input(self, file_path: str) -> bool:
        """验证输入文件是否存在"""
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return False
        return True
