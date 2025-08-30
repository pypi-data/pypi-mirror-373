import os
import json
import logging
from typing import Optional, Dict, Any
from mcp.server.fastmcp import FastMCP

from .client import EmailSystemClient
from .models import EmailTemplate, UpdateTemplateRequest, ReviewRules, ApiResponse
from .rules import get_review_rules

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 从环境变量获取配置
BASE_URL = os.getenv('EMAIL_SYSTEM_URL', 'https://admin.techscience-mail.com')
USERNAME = os.getenv('EMAIL_SYSTEM_USERNAME', '')
PASSWORD = os.getenv('EMAIL_SYSTEM_PASSWORD', '')

# 创建MCP服务器
mcp = FastMCP("email-mcp-server")

# 创建全局客户端实例
email_client = None


def get_client() -> EmailSystemClient:
    """获取或创建邮件系统客户端"""
    global email_client
    if email_client is None:
        if not USERNAME or not PASSWORD:
            raise ValueError("请设置EMAIL_SYSTEM_USERNAME和EMAIL_SYSTEM_PASSWORD环境变量")
        email_client = EmailSystemClient(BASE_URL, USERNAME, PASSWORD)
    return email_client


@mcp.tool()
def get_email_template_info(id: int) -> EmailTemplate:
    """
    获取邮件模板信息
    
    Args:
        id: 邮件模板ID，例如 1345、2133、2344
    
    Returns:
        邮件模板的详细信息
    """
    try:
        client = get_client()
        template_data = client.get_template(id)
        
        if template_data:
            # 转换为EmailTemplate模型
            return EmailTemplate(**template_data)
        else:
            raise ValueError(f"无法获取模板ID {id} 的信息")
            
    except Exception as e:
        logger.error(f"获取模板信息失败: {e}")
        raise


@mcp.tool()
def update_email_template_status(
    email_template_id: int,
    subject: str,
    text_body: str,
    html_body: str,
    is_public: int = 0,
    remark: Optional[str] = None,
    status: int = 1
) -> ApiResponse:
    """
    更新邮件模板状态
    
    Args:
        email_template_id: 邮件模板ID
        subject: 邮件标题
        text_body: 邮件正文（纯文本，支持{{变量}}）
        html_body: 邮件正文（HTML格式，支持{{变量}}）
        is_public: 是否公开（0=否，1=是），默认0
        remark: 备注信息，可选
        status: 模板状态（1=审核通过，0=审核不通过），默认1
    
    Returns:
        审核成功或失败的说明信息
    """
    try:
        client = get_client()
        
        # 准备更新数据
        update_data = {
            'email_template_id': str(email_template_id),
            'subject': subject,
            'text_body': text_body,
            'html_body': html_body,
            'is_public': str(is_public),
            'status': str(status)
        }
        
        if remark:
            update_data['remark'] = remark
        
        # 执行更新
        success = client.update_template(update_data)
        
        if success:
            return ApiResponse(ok="Update email template successfully.")
        else:
            return ApiResponse(error="Failed to update email template.")
            
    except Exception as e:
        logger.error(f"更新模板失败: {e}")
        return ApiResponse(error=str(e))


@mcp.tool()
def fetch_review_rules() -> ReviewRules:
    """
    获取审核规则
    
    Returns:
        结构化的审核规则，包括可用变量和规则说明
    """
    try:
        return get_review_rules()
    except Exception as e:
        logger.error(f"获取审核规则失败: {e}")
        raise


def main():
    """主函数"""
    import asyncio
    
    # 检查环境变量
    if not USERNAME or not PASSWORD:
        logger.warning("未设置EMAIL_SYSTEM_USERNAME或EMAIL_SYSTEM_PASSWORD环境变量")
        logger.warning("使用默认测试账号（仅用于开发测试）")
    
    # 运行MCP服务器
    asyncio.run(mcp.run())


if __name__ == "__main__":
    main()