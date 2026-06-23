# -*- coding: utf-8 -*-
# biz/working_paper.py
"""
工作底稿管理
"""
import os
from loguru import logger

from db.init_db import get_connection
from core.base import ProcessResult


class WorkingPaperManager:
    """工作底稿管理"""

    def __init__(self, config: dict = None):
        self.config = config or {}

    def create_project(self, name: str, client_name: str, audit_period: str) -> ProcessResult:
        """创建审计项目"""
        result = ProcessResult()
        try:
            conn = get_connection()
            cursor = conn.execute(
                'INSERT INTO audit_projects (name, client_name, audit_period) VALUES (?, ?, ?)',
                (name, client_name, audit_period)
            )
            conn.commit()
            project_id = cursor.lastrowid
            conn.close()

            result.data = {'project_id': project_id, 'name': name}
            result.message = f"项目创建成功: {name} (ID: {project_id})"
        except Exception as e:
            result.add_error(f"项目创建失败: {str(e)}")
        return result

    def generate_paper_number(
        self,
        project_id: int,
        category: str,
        sequence: int,
        sub_sequence: int = 0
    ) -> str:
        """
        生成底稿编号

        Args:
            project_id: 项目 ID
            category: 科目类别（如"资产类"）
            sequence: 主序号
            sub_sequence: 子序号
        """
        prefix_map = self.config.get('numbering', {}).get('prefix_map', {
            '资产类': 'A', '负债类': 'L', '所有者权益类': 'E',
            '收入类': 'I', '费用类': 'F', '现金流量类': 'C'
        })
        separator = self.config.get('numbering', {}).get('separator', '-')

        prefix = prefix_map.get(category, 'X')
        if sub_sequence > 0:
            return f"{prefix}{separator}{sequence}{separator}{sub_sequence}"
        return f"{prefix}{separator}{sequence}"

    def list_projects(self) -> ProcessResult:
        """列出所有项目"""
        result = ProcessResult()
        try:
            conn = get_connection()
            rows = conn.execute(
                'SELECT * FROM audit_projects ORDER BY created_at DESC'
            ).fetchall()
            conn.close()

            result.data = [dict(row) for row in rows]
            result.message = f"共 {len(rows)} 个项目"
        except Exception as e:
            result.add_error(f"查询失败: {str(e)}")
        return result

    def list_papers(self, project_id: int) -> ProcessResult:
        """列出项目的所有底稿"""
        result = ProcessResult()
        try:
            conn = get_connection()
            rows = conn.execute(
                'SELECT * FROM working_papers WHERE project_id = ? ORDER BY paper_number',
                (project_id,)
            ).fetchall()
            conn.close()

            result.data = [dict(row) for row in rows]
            result.message = f"共 {len(rows)} 张底稿"
        except Exception as e:
            result.add_error(f"查询失败: {str(e)}")
        return result
