from mcp.server.fastmcp import FastMCP

mcp = FastMCP("天气查询服务")
@mcp.tool()
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    # 实际开发中需调用天气API（此处模拟数据）
    return f"{city}今日晴，28℃"

def run():
    mcp.run(transport='stdio')  # 本地调试模式

if __name__ == '__main__':
   run()