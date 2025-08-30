from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class SensitiveWord(BaseModel):
    keyword: str
    category: str
    position: str


class EmailTemplate(BaseModel):
    id: int
    subject: str
    text_body: str
    html_body: str
    is_public: int = Field(default=0)
    user_id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    status: int = Field(default=1, description="0=审核不通过, 1=审核通过")
    remark: Optional[str] = None
    spanList: Optional[List[SensitiveWord]] = None


class UpdateTemplateRequest(BaseModel):
    email_template_id: int
    subject: str
    text_body: str
    html_body: str
    is_public: int = Field(default=0)
    remark: Optional[str] = None
    status: int = Field(default=1)


class ReviewRules(BaseModel):
    title_variables: List[str] = ["{{ Greeting }}"]
    body_variables: List[str] = [
        "{{ Salutation }}",
        "{{ Opening }}",
        "{{ ClosingPhrase }}",
        "{{ ClosingSalutation }}"
    ]
    other_variables: List[str] = [
        "{{ Email }}",
        "{{ First name }}",
        "{{ Middle name }}",
        "{{ Last name }}",
        "{{ Title }}",
        "{{ Affiliation }}",
        "{{ Roles }}",
        "{{ Note }}"
    ]
    rules: List[str] = [
        "邮件主体内容要放在{{ Opening }}和{{ ClosingPhrase }}中间",
        "最后{{ ClosingSalutation }}下面放落款",
        "所有的邮件变量都在上述规则中，用{{和}}包裹",
        "邮件模版的内容不能和邮件变量名重复",
        "邮件模板敏感词不能超过10个",
        "10个以内的敏感词不能同时包含涉及'政治、金钱、利益、暴力'等其中两种类型",
        "邮件模板的text正文和Html正文内容必须保持相同（不包括格式、Html标签、换行等特殊字符）",
        "邮件正文和变量之间语义不得冲突"
    ]


class ApiResponse(BaseModel):
    ok: Optional[str] = None
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None