# XeSQL MCP Server

A high-performance **Model Context Protocol (MCP) server** that enables secure and efficient interaction with MySQL-compatible databases including MySQL, MariaDB, TiDB, OceanBase, AWS RDS, and Aurora MySQL.

## ✨ Key Highlights

- **🏗️ Professional Architecture**: Modular design with singleton patterns and clean separation of concerns
- **⚡ High Performance**: Full async/await implementation with intelligent connection pooling
- **🛡️ Enterprise Security**: Multi-layer security with parameter validation and sensitive data protection
- **🔧 Universal Compatibility**: Support for 6+ MySQL-compatible database systems
- **📊 Production Ready**: Comprehensive logging, error handling, and resource management
- **🎯 MCP Standard**: Built on FastMCP framework with complete MCP protocol compliance

## 🚀 Core Features

### **MCP Protocol Implementation**
- **Standard Tools & Resources**: Complete MCP tool and resource definitions
- **FastMCP Framework**: Built on robust FastMCP foundation for reliability
- **Async Communication**: Non-blocking MCP message handling

### **Database Operation Tools**
- **Universal SQL Execution**: Execute any SQL statement with intelligent type detection
- **Table Structure Analysis**: Comprehensive table metadata and schema information
- **Test Data Generation**: Automated test data creation with customizable parameters
- **Query Optimization**: Smart result handling for different SQL operation types

### **Advanced Architecture**
- **Singleton Connection Pool**: Efficient resource management with automatic cleanup
- **Smart Configuration**: Multi-instance support with environment variable override
- **Async-First Design**: Built from ground up for asynchronous operations
- **Modular Structure**: Clean separation of tools, resources, utilities, and configuration

## 📋 Prerequisites

- Python >= 3.12
- XeSQL/MySQL/MariaDB/TiDB/OceanBase database instance
- Network access to database server

## 🛠️ Installation

### 1. Install from PyPI (Recommended)
```bash
pip install xesql-mcp-server
```

### 2. Configure database connection

Edit `dbconfig.json` with your database credentials:

```json
{
    "dbPoolSize": 5,
    "dbMaxOverflow": 10,
    "dbPoolTimeout": 30,
    "dbType-Comment": "The database currently in use,such as XeSQL/MySQL/MariaDB/UbiSQL OceanBase/RDS/Aurora MySQL DataBases",
    "dbList": [
        {   "dbInstanceId": "xesql_1",
            "dbHost": "localhost",
            "dbPort": 2281,
            "dbDatabase": "xesql_db",
            "dbUsername": "root",
            "dbPassword": "123456",
            "dbType": "XeSQL",
            "dbVersion": "V2.0.0",
            "dbActive": true
        },
        {   "dbInstanceId": "mysql_2",
            "dbHost": "localhost",
            "dbPort": 3306,
            "dbDatabase": "mysql_db",
            "dbUsername": "root",
            "dbPassword": "123456",
            "dbType": "MySQL",
            "dbVersion": "8.0",
            "dbActive": false
        },
        {   "dbInstanceId": "tidb_3",
            "dbHost": "localhost",
            "dbPort": 4000,
            "dbDatabase": "tidb_db",
            "dbUsername": "root",
            "dbPassword": "123456",
            "dbType": "UbiSQL",
            "dbVersion": "8.5.3",
            "dbActive": false
        }
    ],
    "logPath": "/path/to/logs",
    "logLevel": "info"
}
# dbType
Oceanbase Instance is in MySQL/MariaDB/TiDB OceanBase/RDS/Aurora MySQL DataBases.
# dbActive
Only database instances with dbActive set to true in the dbList configuration list are available. 
# logPath
MCP server log is stored in /path/to/logs/mcp_server.log.
# logLevel
TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL
```

### 3. Configure MCP Client

Add to your MCP client configuration file:

```json
{
  "mcpServers": {
    "xesql-mcp-client": {
      "command": "xesql-mcp-server",
      "env": {
        "config_file": "/path/to/your/dbconfig.json"
      },
      "disabled": false
    }
  }
}
```

**Note**: Replace `/path/to/your/dbconfig.json` with the actual path to your configuration file.

### 4. Clone the repository (Development Mode)
```bash
git clone https://github.com/j00131120/mcp_database_server.git
cd mcp_database_server/xesql_mcp_server
# Import project into your IDE
```

### 5. Configure MCP Client for Development
```json
{
  "mcpServers": {
    "xesql-mcp-server": {
      "command": "/bin/uv",
      "args": ["run", "src/server.py"],
      "cwd": "/path/to/your/project",
      "env": {
        "config_file": "/path/to/your/dbconfig.json"
      },
      "disabled": false,
      "autoApprove": ["describe_table", "sql_exec", "generate_demo_data"]
    }
  }
}

# command
uv absolute path
# cwd
project absolute path
# config_file
dbconfig.json file path
```