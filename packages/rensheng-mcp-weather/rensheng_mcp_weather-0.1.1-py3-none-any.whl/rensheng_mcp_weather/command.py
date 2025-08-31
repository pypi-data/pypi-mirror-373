# 从mcp.server.fastmcp模块导入FastMCP类
from mcp.server.fastmcp import FastMCP

# 创建一个MCP服务器实例，名称为"Demo"
mcp = FastMCP("Demo")


# 添加一个加法工具
@mcp.tool()
# 定义加法函数，接收两个整数参数a和b，返回它们的和
def add(a: int, b: int) -> int:
    """Add two numbers"""
    # 返回a和b的和
    return a + b


# 添加一个动态问候资源
@mcp.resource("greeting://{name}")
# 定义获取问候语的函数，接收一个字符串参数name，返回个性化问候语
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    # 返回格式化后的问候语
    return f"Hello, {name}!"


# 添加一个提示（prompt）工具
@mcp.prompt()
# 定义问候用户的函数，接收name和style参数，style有默认值"friendly"
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate a greeting prompt"""
    # 定义不同风格的问候语模板
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }

    # 根据style选择对应的模板，默认使用"friendly"，并返回格式化后的提示语
    return f"{styles.get(style, styles['friendly'])} for someone named {name}."


# 定义主函数
def main():
    mcp.run(transport="stdio")


# 如果当前模块是主程序入口，则执行main函数
if __name__ == "__main__":
    main()
