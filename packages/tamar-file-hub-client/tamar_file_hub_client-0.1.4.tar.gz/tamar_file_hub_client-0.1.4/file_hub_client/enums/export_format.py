"""
导出格式枚举
"""
from enum import Enum


class ExportFormat(Enum):
    """导出格式（用于自定义文件类型）"""
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    PPTX = "pptx"
    HTML = "html"
    MARKDOWN = "markdown"
    JSON = "json"
    CSV = "csv" 