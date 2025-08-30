# Email MCP Server

自动化获取/更新邮件模板信息的 MCP (Model Context Protocol) 服务器。

## 项目简介

Email MCP Server 是一个基于 Model Context Protocol (MCP) 的服务器实现，用于自动化管理邮件模板系统。它提供了三个核心工具，让 AI 助手（如 Claude）能够直接与邮件系统交互，实现邮件模板的获取、更新和审核规则查询。

## 功能特性

### 提供的 Tools

1. **get_email_template_info** - 获取邮件模板信息
   - 输入：模板ID（如 1345、2133、2344）
   - 输出：邮件模板的详细信息，包括标题、正文、状态、敏感词等

2. **update_email_template_status** - 更新邮件模板状态
   - 输入：模板ID和更新内容（支持全部字段）
   - 输出：更新成功或失败的状态信息

3. **fetch_review_rules** - 获取审核规则
   - 输入：无
   - 输出：结构化的审核规则，包括可用变量和规则说明

## 快速开始

### 安装
```bash
pip install email-mcp-server
```

### 在 Claude Desktop 中使用

配置文件位置：
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

添加配置：
```json
{
  "mcpServers": {
    "email-mcp-server": {
      "command": "python",
      "args": ["-m", "email_mcp_server.server"],
      "env": {
        "EMAIL_SYSTEM_URL": "https://system_url.com",
        "EMAIL_SYSTEM_USERNAME": "your_email@example.com",
        "EMAIL_SYSTEM_PASSWORD": "your_password"
      }
    }
  }
}
```

## 使用示例

### 在 Claude 中使用

```
请帮我获取邮件模板 1509 的信息
```

```
请更新邮件模板 1509 的状态为审核通过
```

```
请告诉我邮件模板的审核规则
```

## 审核规则说明

### 可用变量

#### 标题变量
- `{{ Greeting }}` - 问候语

#### 正文变量
- `{{ Salutation }}` - 称呼语（如：Dear Prof. xxx）
- `{{ Opening }}` - 开场白
- `{{ ClosingPhrase }}` - 结束寒暄语
- `{{ ClosingSalutation }}` - 结束称呼语

#### 其他变量
- `{{ Email }}` - 邮箱地址
- `{{ First name }}` - 名
- `{{ Middle name }}` - 中间名
- `{{ Last name }}` - 姓
- `{{ Title }}` - 职称
- `{{ Affiliation }}` - 单位/机构
- `{{ Roles }}` - 角色
- `{{ Note }}` - 备注

### 审核规则

1. 邮件主体内容要放在 `{{ Opening }}` 和 `{{ ClosingPhrase }}` 中间
2. 最后 `{{ ClosingSalutation }}` 下面放落款
3. 所有邮件变量必须用 `{{` 和 `}}` 包裹
4. 邮件模板内容不能和邮件变量名重复
5. 敏感词不能超过10个
6. 敏感词不能同时包含涉及"政治、金钱、利益、暴力"等其中两种类型
7. text正文和HTML正文的主体内容必须保持相同
8. 邮件正文和变量之间语义不得冲突

## 许可证

MIT License - 详见 [LICENSE](LINSE) 文件