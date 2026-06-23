# -*- coding: utf-8 -*-
# biz/file_manager.py
"""
文件管理器
批量文件整理、重命名、全文检索
"""
import os
import re
import hashlib
from typing import Optional
from loguru import logger

from core.base import ProcessResult


class FileManager:
    """文件管理器"""

    def batch_rename(
        self,
        directory: str,
        pattern: str,
        replacement: str,
        extensions: tuple = None
    ) -> ProcessResult:
        """
        批量重命名文件

        Args:
            directory: 目标目录
            pattern: 正则匹配模式
            replacement: 替换字符串
            extensions: 文件扩展名过滤
        """
        result = ProcessResult()
        extensions = extensions or ('.pdf', '.docx', '.xlsx', '.jpg', '.png')
        renamed = []

        for filename in os.listdir(directory):
            if not filename.lower().endswith(extensions):
                continue

            new_name = re.sub(pattern, replacement, filename)
            if new_name != filename:
                old_path = os.path.join(directory, filename)
                new_path = os.path.join(directory, new_name)
                os.rename(old_path, new_path)
                renamed.append({'old': filename, 'new': new_name})

        result.data = renamed
        result.message = f"重命名 {len(renamed)} 个文件"
        return result

    def find_duplicates(self, directory: str) -> ProcessResult:
        """查找重复文件（基于 MD5 哈希）"""
        result = ProcessResult()
        hash_map = {}
        duplicates = []

        for root, dirs, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    if file_hash in hash_map:
                        duplicates.append({
                            'file1': hash_map[file_hash],
                            'file2': filepath
                        })
                    else:
                        hash_map[file_hash] = filepath
                except (IOError, PermissionError):
                    continue

        result.data = duplicates
        result.message = f"发现 {len(duplicates)} 组重复文件"
        return result

    def organize_files(
        self,
        source_dir: str,
        rules: list[dict]
    ) -> ProcessResult:
        """
        按规则整理文件到子目录

        Args:
            source_dir: 源目录
            rules: 整理规则列表 [{"pattern": "regex", "folder": "target_folder"}]
        """
        result = ProcessResult()
        moved = []

        for filename in os.listdir(source_dir):
            filepath = os.path.join(source_dir, filename)
            if os.path.isfile(filepath):
                for rule in rules:
                    if re.search(rule['pattern'], filename):
                        target_dir = os.path.join(source_dir, rule['folder'])
                        os.makedirs(target_dir, exist_ok=True)
                        target_path = os.path.join(target_dir, filename)
                        os.rename(filepath, target_path)
                        moved.append({'file': filename, 'to': rule['folder']})
                        break

        result.data = moved
        result.message = f"整理 {len(moved)} 个文件"
        return result
