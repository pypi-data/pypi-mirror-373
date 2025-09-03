# 项目说明

本项目为 MCP MySQL Server，提供数据库知识和数据查询能力。

- 主逻辑文件：`mcp_mysql/server.py`
- 示例知识文件：`knowledge.txt`
- 测试用例：`tests/test_server.py`

## 安装依赖
```cmd
pip install pymysql
```

## 运行方式

### 方法1：使用Python模块方式（推荐）
```bash
python -m mcp_mysql
```

### 方法2：使用安装后的命令
```bash
mcp-mysql
```

### 方法3：直接运行server.py
```bash
python mcp_mysql/server.py
```

## 服务配置（Server config）

服务通过环境变量进行数据库连接配置（仅环境变量）。

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| DB_USER  | 数据库用户名 | readonly_user |
| DB_PASS  | 数据库密码   | readonly_pass |
| DB_HOST  | 数据库主机   | localhost |
| DB_PORT  | 数据库端口   | 3306 |
| DB_NAME  | 数据库名称   | mcp |

示例：
```cmd
set DB_USER=readonly_user
set DB_PASS=readonly_pass

set DB_HOST=127.0.0.1
set DB_PORT=3306
set DB_NAME=mcp
python -m mcp_mysql
```