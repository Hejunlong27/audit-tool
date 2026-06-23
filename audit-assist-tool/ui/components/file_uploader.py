# -*- coding: utf-8 -*-
"""
文件上传组件
"""
from nicegui import ui, events


class FileUploader:
    """文件上传组件"""

    def __init__(self, accept: str = '.pdf,.xlsx,.csv', multiple: bool = False):
        self.accept = accept
        self.multiple = multiple
        self.uploaded_files = []

    def render(self):
        """渲染上传组件"""
        upload = ui.upload(
            label='选择文件',
            auto_upload=True,
            on_upload=self._on_upload
        ).props(f'accept={self.accept} {"multiple" if self.multiple else ""}')

        return upload

    def _on_upload(self, e: events.UploadEventArguments):
        import tempfile
        import os

        content = e.content.read()
        path = os.path.join(tempfile.gettempdir(), e.name)
        with open(path, 'wb') as f:
            f.write(content)
        self.uploaded_files.append(path)
