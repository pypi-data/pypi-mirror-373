from mcp.server.fastmcp import FastMCP
from datetime import datetime

mcp = FastMCP(name="查询服务器信息MCP",host="0.0.0.0",port=8123)

# 使用@mcp.tool装饰器定义MCP工具
@mcp.tool(
    name="get_system_time",
    description="获取当前系统的时间和日期"
)
async def get_system_time():
    """获取当前系统时间的工具函数"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "status": "success",
        "data": {
            "system_time": current_time
        },
        "message": "当前系统时间获取成功"
    }
    
    
# 系统版本信息查询工具
import platform

@mcp.tool(
    name="get_system_info",
    description="获取当前系统的版本和相关信息"
)
async def get_system_info():
    """获取系统版本信息的工具函数"""
    system_info = {
        "system": platform.system(),  # 操作系统名称
        "node": platform.node(),      # 网络名称
        "release": platform.release(),# 操作系统版本
        "version": platform.version(),# 操作系统版本详情
        "machine": platform.machine(),# 硬件架构
        "processor": platform.processor()  # 处理器信息
    }
    
    return {
        "status": "success",
        "data": system_info,
        "message": "系统版本信息获取成功"
    }    

if __name__ == "__main__":
    mcp.run(transport="sse")

