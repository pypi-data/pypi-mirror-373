from lark_helper.constants.message import MessageType, ReceiveIdType
from lark_helper.models.message import TextMessageContent
from lark_helper.token_manager import TenantAccessTokenManager
from lark_helper.v1.message import send_message
from mcp.server.fastmcp import FastMCP

from lark_helper_mcp.config import config

# Create an MCP server
mcp = FastMCP("Demo")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.tool()
def send_text_message(receive_id: str, receive_id_type: str, text_content: str):
    """
    向指定飞书用户或者群聊发送文本消息
    Args:
        receive_id: 接收者ID
        receive_id_type: 接收者ID类型，支持user_id, open_id, chat_id
        text_content: 文本内容
    """
    token_manager = TenantAccessTokenManager(config.lark_app_id, config.lark_app_secret)
    receive_id_type_enum = ReceiveIdType(receive_id_type)
    send_message(
        token_manager,
        receive_id,
        receive_id_type_enum,
        MessageType.TEXT,
        TextMessageContent(text=text_content).json_str(),
    )
    return "success"


def main():
    print("Hello from lark-helper-mcp!")

    # 验证必需的环境变量
    try:
        config.ensure_required_config()
        print("✓ 环境变量配置验证通过")
    except ValueError as e:
        print(f"❌ {e}")
        print("\n请设置以下环境变量：")
        print("export LARK_APP_ID=your_app_id")
        print("export LARK_APP_SECRET=your_app_secret")
        return

    mcp.run()


if __name__ == "__main__":
    main()
