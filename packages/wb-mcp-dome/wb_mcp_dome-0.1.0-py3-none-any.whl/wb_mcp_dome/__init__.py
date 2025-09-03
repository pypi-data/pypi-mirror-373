from mcp.server.fastmcp import FastMCP
import uvicorn

# 创建MCP服务器
mcp = FastMCP("Calculator")


# 四则运算工具
@mcp.tool()
def calculate(a: float, b: float, operation: str) -> float:
    """执行四则运算
    Args:
        a: 第一个数字
        b: 第二个数字
        operation: 运算符 '+', '-', '*', '/'
    Returns:
        运算结果
    """
    if operation == '+':
        return a + b
    elif operation == '-':
        return a - b
    elif operation == '*':
        return a * b
    elif operation == '/':
        if b == 0:
            raise ValueError("不能除以零")
        return a / b
    else:
        raise ValueError("无效运算符，请使用: '+', '-', '*', '/'")


# 动态问候资源
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """获取个性化问候"""
    return f"Hello, {name}!"





def main() -> None:
    mcp.run(transport="stdio")
