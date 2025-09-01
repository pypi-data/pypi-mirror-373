# Lark Helper MCP Server

一个用于 [Lark (飞书)](https://www.larksuite.com/) 集成的 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 服务器。

## 功能特性

- 🚀 基于 FastMCP 构建的高性能 MCP 服务器
- 📱 支持向飞书用户和群聊发送文本消息
- 🔐 安全的环境变量配置管理
- 🛠 支持多种安装和运行方式

## 环境要求

- Python 3.12+
- 有效的飞书应用凭据（App ID 和 App Secret）

## 安装

### 方法一：使用 uvx（推荐）

```bash
# 临时运行
uvx lark-helper-mcp

# 或永久安装
uv tool install lark-helper-mcp
```

### 方法二：使用 pip

```bash
pip install lark-helper-mcp
```

### 方法三：开发安装

```bash
git clone <repository-url>
cd lark-helper-mcp
uv sync
uv run python main.py
```

## 配置

在运行之前，需要设置以下环境变量：

```bash
export LARK_APP_ID=your_app_id_here
export LARK_APP_SECRET=your_app_secret_here
```

或者创建 `.env` 文件：

```env
LARK_APP_ID=your_app_id_here
LARK_APP_SECRET=your_app_secret_here
```

### 获取飞书应用凭据

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建一个新的应用或选择现有应用
3. 在应用详情页面获取 App ID 和 App Secret
4. 确保应用有发送消息的权限

## 使用方法

### 作为独立服务器运行

```bash
# 使用 uvx
uvx lark-helper-mcp

# 或使用已安装的命令
lark-helper-mcp

# 或使用 Python 模块
python -m lark_helper_mcp
```

### 在 Claude Desktop 中使用

在 Claude Desktop 的配置文件中添加：

```json
{
  "mcpServers": {
    "lark-helper": {
      "command": "uvx",
      "args": ["lark-helper-mcp"],
      "env": {
        "LARK_APP_ID": "your_app_id_here",
        "LARK_APP_SECRET": "your_app_secret_here"
      }
    }
  }
}
```

## 可用工具

### `send_text_message`

向指定的飞书用户或群聊发送文本消息。

**参数：**
- `receive_id` (string): 接收者 ID
- `receive_id_type` (string): 接收者 ID 类型，支持：
  - `user_id`: 用户 ID
  - `open_id`: Open ID
  - `chat_id`: 群聊 ID
- `text_content` (string): 要发送的文本内容

**示例使用：**
```python
# 发送消息给用户
send_text_message(
    receive_id="user123", 
    receive_id_type="user_id", 
    text_content="Hello from MCP!"
)

# 发送消息到群聊
send_text_message(
    receive_id="oc_chat456", 
    receive_id_type="chat_id", 
    text_content="团队通知：会议将在10分钟后开始"
)
```

## 开发

### 环境设置

```bash
# 克隆仓库
git clone <repository-url>
cd lark-helper-mcp

# 创建虚拟环境并安装依赖
uv venv
uv sync

# 运行开发服务器
uv run python main.py
```

### 代码质量检查

```bash
# 运行 linter
ruff check

# 格式化代码
ruff format
```

### 构建和发布

```bash
# 构建包
uv build

# 发布到 PyPI（需要配置 PyPI 凭据）
twine upload dist/*
```

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 支持

如有问题，请在 [GitHub Issues](https://github.com/philoveritas/lark-helper-mcp/issues) 中提出。