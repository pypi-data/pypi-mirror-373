from .models import ReviewRules


def get_review_rules() -> ReviewRules:
    """
    获取邮件模板审核规则
    """
    return ReviewRules(
        title_variables=["{{ Greeting }}"],
        body_variables=[
            "{{ Salutation }}",
            "{{ Opening }}",
            "{{ ClosingPhrase }}",
            "{{ ClosingSalutation }}"
        ],
        other_variables=[
            "{{ Email }}",
            "{{ First name }}",
            "{{ Middle name }}",
            "{{ Last name }}",
            "{{ Title }}",
            "{{ Affiliation }}",
            "{{ Roles }}",
            "{{ Note }}"
        ],
        rules=[
            "邮件主体内容要放在{{ Opening }}和{{ ClosingPhrase }}中间",
            "最后{{ ClosingSalutation }}下面放落款",
            "所有的邮件变量都在上述规则中，用{{和}}包裹",
            "邮件模版的内容不能和邮件变量名重复",
            "邮件模板敏感词不能超过10个",
            "10个以内的敏感词不能同时包含涉及'政治、金钱、利益、暴力'等其中两种类型",
            "邮件模板的text正文和Html正文内容必须保持相同（不包括格式、Html标签、换行等特殊字符）",
            "邮件正文和变量之间语义不得冲突"
        ]
    )