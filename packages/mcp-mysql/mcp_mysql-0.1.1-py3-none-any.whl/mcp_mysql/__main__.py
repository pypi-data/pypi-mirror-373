"""
MCP MySQL Server 主入口点
当运行 python -m mcp_mysql 时，此文件会被执行
"""

import logging
from .server import mcp

def main():
    """主函数入口点"""
    logging.basicConfig(level=logging.INFO)
    logging.info("MCP MySQL Server 启动中...")
    
    try:
        # 启动MCP服务器（stdio模式）
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logging.info("服务器被用户中断")
    except Exception as e:
        logging.error(f"服务器启动失败: {e}")
        raise

if __name__ == "__main__":
    main() 