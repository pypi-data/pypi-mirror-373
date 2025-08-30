"""
Email MCP Server - 自动化获取/更新邮件模板信息的MCP服务器
"""

__version__ = "0.1.0"

from .server import mcp, main
from .models import EmailTemplate, UpdateTemplateRequest, ReviewRules, ApiResponse
from .client import EmailSystemClient
from .rules import get_review_rules

__all__ = [
    'mcp',
    'main',
    'EmailTemplate',
    'UpdateTemplateRequest',
    'ReviewRules',
    'ApiResponse',
    'EmailSystemClient',
    'get_review_rules'
]