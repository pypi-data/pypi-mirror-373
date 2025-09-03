import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from mcp_mysql.server import mcp, query_mysql, read_knowledge, list_tables, describe_table, query_table
# 测试知识文件读取资源
def test_read_knowledge():
    # 直接调用被装饰的资源函数
    result = read_knowledge()
    assert isinstance(result, str)
    assert "张镇孙" in result
    print(result)

# 测试数据库连接（需保证数据库可访问）
def test_query_mysql():
    try:
        tables = query_mysql("SHOW TABLES")
        assert isinstance(tables, list)
    except Exception as e:
        pytest.skip(f"数据库连接失败: {e}")

# 测试MCP资源列出表
@pytest.mark.asyncio
async def test_list_tables():
    tables = await list_tables()
    assert isinstance(tables, list)

# 测试describe_table工具
@pytest.mark.asyncio
async def test_describe_table():
    tables = await list_tables()
    if tables:
        table_name = tables[0]["name"]
        desc = await describe_table(table_name)
        assert "结构" in desc or "不存在" in desc
    else:
        pytest.skip("无表可测试")

# 测试query_table工具
@pytest.mark.asyncio
async def test_query_table():
    tables = await list_tables()
    if tables:
        table_name = tables[0]["name"]
        result = await query_table(table_name, limit=1)
        assert "查询" in result or "没有找到数据" in result
    else:
        pytest.skip("无表可测试")
