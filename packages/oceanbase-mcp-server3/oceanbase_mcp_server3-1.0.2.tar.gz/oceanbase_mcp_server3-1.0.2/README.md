# OceanBase MCP Server

A Model Context Protocol (MCP) server that enables secure interaction with OceanBase databases. Supports both MySQL and Oracle compatibility modes with high-performance async operations.

## 🚀 Features

- **MCP Protocol Support**: Built on FastMCP framework with standard MCP tools and resources
- **Multi-Database Compatibility**: Support for OceanBase (MySQL/Oracle modes) 
- **Asynchronous Architecture**: Built with `aiomysql/oracledb` for high-performance database operations
- **Connection Pooling**: Efficient connection management with configurable pool settings
- **Security Features**: Query type restrictions, automatic LIMIT enforcement, and parameter validation
- **Comprehensive Tools**: SQL execution, table structure queries, and test data generation

## 📋 Prerequisites

- Python >= 3.12
- OceanBase database instance (MySQL or Oracle mode)
- Network access to database server

## 🛠️ Installation

### 1. Install from PyPI (Recommended)
```bash
pip install oceanbase-mcp-server3
```

### 2. Configure database connection

Edit `dbconfig.json` with your database credentials:

```json
{
    "dbPoolSize": 5,
    "dbMaxOverflow": 10,
    "dbPoolTimeout": 30,
    "dbType-Comment": "The database currently in use,such as OceanBase(Mysql/Oracle) DataBases",
    "dbList": [
        {   "dbInstanceId": "oceanbase_1",
            "dbHost": "localhost",
            "dbPort": 2881,
            "dbDatabase": "oceanbase_db",
            "dbUsername": "root",
            "dbPassword": "123456",
            "dbType": "oracle",
            "dbVersion": "V4.0.0",
            "dbActive": true
        },
        {   "dbInstanceId": "oceanbase_2",
            "dbHost": "localhost",
            "dbPort": 2881,
            "dbDatabase": "oceanbase_db",
            "dbUsername": "root",
            "dbPassword": "123456",
            "dbType": "mysql",
            "dbVersion": "V3.0.0",
            "dbActive": false
        }
    ],
    "logPath": "/path/to/logs",
    "logLevel": "info"
}
# dbType
Oceanbase Instance is in Oracle mode or Mysql mode.
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
    "oceanbase-mcp-client": {
      "command": "oceanbase-mcp-server3",
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
cd mcp_database_server/oceanbase_mcp_server
# Import project into your IDE
```

### 5. Configure MCP Client for Development
```json
{
  "mcpServers": {
    "oceanbase-mcp-client": {
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

## 🚀 Quick Start

### Start the MCP Server
```bash
# Using the installed package
oceanbase-mcp-server3

# Using fastmcp CLI (development mode)
fastmcp run src/server.py

# Using uv (development mode)
uv run src/server.py

# Or directly with Python
python src/server.py

# Using fastmcp debug
fastmcp dev src/server.py
```

### Using with MCP Clients
The server provides the following MCP tools and resources:

#### Tools
- `sql_exec`: Execute any SQL statement
- `describe_table`: Get table structure information
- `generate_demo_data`: Generate test data for tables

#### Resources
- `database://tables`: Database table metadata
- `database://config`: Database configuration information

## 📚 API Reference

### SQL Execution Tool
```python
await sql_exec("SELECT * FROM users WHERE age > 18")
```

**Parameters:**
- `sql` (str): SQL statement to execute

**Returns:**
- `success` (bool): Execution status
- `result`: Query results or affected rows
- `message` (str): Status description

### Table Structure Tool
```python
await describe_table("users")
```

**Parameters:**
- `table_name` (str): Table name (supports `database.table` format)

**Returns:**
- Table structure information including columns, types, and constraints

### Test Data Generation
```python
await generate_demo_data("users", ["name", "email"], 50)
```

**Parameters:**
- `table_name` (str): Target table name
- `columns_name` (List[str]): Column names to populate
- `num` (int): Number of test records to generate

## ⚙️ Configuration

### Database Configuration
The `dbconfig.json` file supports multiple database instances:

```json
{
    "dbPoolSize": 5,
    "dbMaxOverflow": 10,
    "dbPoolTimeout": 30,
    "dbType-Comment": "The database currently in use,such as OceanBase(Mysql/Oracle) DataBases",
    "dbList": [
        {   "dbInstanceId": "oceanbase_1",
            "dbHost": "localhost",
            "dbPort": 3306,
            "dbDatabase": "oceanbase_db",
            "dbUsername": "root",
            "dbPassword": "123456",
            "dbType": "oracle",
            "dbVersion": "V4.0.0",
            "dbActive": true   // Only one instance should be active
        },
        {   "dbInstanceId": "oceanbase_2",
            "dbHost": "localhost",
            "dbPort": 2881,
            "dbDatabase": "oceanbase_db",
            "dbUsername": "root",
            "dbPassword": "123456",
            "dbType": "mysql",
            "dbVersion": "V3.0.0",
            "dbActive": false   // other instances should be inactive
        }
    ],
    "logPath": "/path/to/logs",
    "logLevel": "info"
}
```

### Logging Configuration
- **Log Levels**: TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL
- **Log Rotation**: 10 MB per file, 7 days retention
- **Output**: Both stderr (for MCP) and file logging

## 🔒 Security Features

### Query Restrictions
- **Parameterized Queries**: All SQL queries use parameter binding to prevent SQL injection
- **Transaction Management**: Automatic commit/rollback for data integrity
- **Parameter Validation**: Input validation for all parameters

### Configuration Security
- **Password Hiding**: Sensitive information is masked in responses
- **Instance Isolation**: Only active database configuration is exposed
- **Environment Override**: Secure configuration file path management

## 🏗️ Architecture

### Project Structure
```
src/
├── server.py              # MCP server main entry point
├── utils/                 # Utility modules
│   ├── db_config.py       # Database configuration management
│   ├── db_pool.py         # Connection pool management
│   ├── db_operate.py      # Database operations
│   ├── logger_util.py     # Logging management
│   └── __init__.py        # Module initialization
├── resources/             # MCP resources
│   └── db_resources.py    # Database resources
└── tools/                 # MCP tools
    └── db_tool.py         # Database tools
```

### Key Components

#### Database Connection Pool
- **Singleton Pattern**: Ensures single pool instance
- **Async Management**: Non-blocking connection handling
- **Automatic Cleanup**: Connection release and pool management

#### Configuration Management
- **JSON-based**: Human-readable configuration format
- **Environment Override**: Flexible configuration management
- **Validation**: Required field validation and error handling

#### Logging System
- **Unified Interface**: Single logger instance across modules
- **Configurable Output**: File and console logging
- **Structured Format**: Timestamp, level, module, function, and line information

## 🐳 Docker Support

### Using Docker Compose

This project includes a comprehensive Docker Compose setup for OceanBase. See the docker-compose documentation for details.

```bash
# Start OceanBase with monitoring stack
docker-compose up -d

# Simple OceanBase setup (for development)
docker-compose -f docker-compose.simple.yml up -d
```

### OceanBase Connection
After starting Docker containers, connect using:
```bash
# MySQL mode connection
mysql -h 127.0.0.1 -P 2881 -u root -p123456

# Update your dbconfig.json to point to Docker instance
{
    "dbHost": "localhost",
    "dbPort": 2881,
    "dbDatabase": "test",
    "dbUsername": "root",
    "dbPassword": "123456",
    "dbType": "mysql"
}
```

## 🧪 Testing

### Generate Test Data
```python
# Generate 100 test records for users table
await generate_demo_data("users", ["name", "email", "phone"], 100)
```

### Test Database Connection
```python
# Test basic SQL execution
result = await sql_exec("SELECT 1 as test")
print(result)  # {'success': True, 'result': [{'test': 1}]}
```

## 📊 Monitoring

### Database Status
```python
# Get database configuration (via MCP resource)
# This will show current active database instance configuration

# Get table information (via MCP resource)  
# This will show all tables with their structure and record counts

# Example output when using MCP client:
# Database: oracle V4.0.0 (or mysql V3.0.0)
# Tables: users, products, orders, etc.
```

### Connection Pool Status
- Pool size and overflow configuration
- Connection timeout settings
- Active connection count

## 🚨 Troubleshooting

### Common Issues

#### Connection Errors
```bash
# Check OceanBase connectivity (MySQL mode)
mysql -h localhost -P 2881 -u username -p database_name

# Check OceanBase connectivity (Oracle mode)
sqlplus username/password@localhost:2881/database_name

# Verify configuration
python -c "from src.utils.db_config import load_db_config; print(load_db_config())"
```

#### Permission Issues
- Ensure database user has necessary privileges
- Check firewall and network access
- Verify database server is running

#### Configuration Errors
- Validate JSON syntax in `dbconfig.json`
- Check file permissions
- Verify environment variables

### Debug Mode
Set log level to DEBUG in configuration:
```json
{
    "logLevel": "debug"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Setup
```bash
# Install dependencies with uv
uv sync

# Run with debug logging
export config_file="/path/to/your/dbconfig.json"
uv run src/server.py

# Or use fastmcp for development
fastmcp run src/server.py
```

### Code Quality Tools
```bash
# Format code
black src/
isort src/

# Lint code
flake8 src/
mypy src/

# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Frank Jin** - *Initial work* - [j00131120@163.com](mailto:j00131120@163.com)

## 🙏 Acknowledgments

- [FastMCP](https://github.com/fastmcp/fastmcp) - MCP framework
- [aiomysql](https://github.com/aio-libs/aiomysql) - Async MySQL driver
- [oracledb](https://oracle.github.io/python-oracledb/) - Oracle Database driver
- [loguru](https://github.com/Delgan/loguru) - Logging library

## 📞 Support

For support and questions:
- Create an issue in the repository
- Contact: [j00131120@163.com](mailto:j00131120@163.com)

## 🔄 Changelog

### v1.0.3 (Current)
- Added Oracle database driver support (`oracledb`)
- Enhanced multi-database compatibility
- Improved configuration management
- Bug fixes and performance optimizations

### v1.0.1
- Enhanced type annotations and error handling
- Fixed configuration file path resolution
- Package name changed to `oceanbase-mcp-server3`

### v1.0.0
- Initial release
- MCP protocol support
- Multi-database compatibility
- Async connection pooling
- Security features implementation

## 📦 Building and Distribution

### Build the Package
```bash
# Using uv (recommended)
uv build

# Or using traditional tools
python -m build
```

### Publish to PyPI
```bash
# Check the package
python -m twine check dist/*

# Upload to PyPI
python -m twine upload dist/*
```

### Package Information
- **Package Name**: `oceanbase-mcp-server3`
- **Entry Point**: `oceanbase-mcp-server3`
- **MCP Server Entry Point**: `main`
- **Python Version**: >= 3.12
- **License**: MIT