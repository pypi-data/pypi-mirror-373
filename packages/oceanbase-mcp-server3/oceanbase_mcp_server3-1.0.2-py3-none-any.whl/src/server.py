
"""
MCP OceanBase SQL Server

Main entry point for OceanBase DataSource MCP Client server.
"""
import os
import sys
from typing import List
from fastmcp import FastMCP

project_path=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# Add current directory to Python module search path
sys.path.insert(0,project_path)
from src.utils.logger_util import logger, db_config_path
from src.utils.db_operate import execute_sql
from src.resources.db_resources import generate_database_tables, generate_database_config
from src.utils import load_activate_db_config
from src.tools.db_tool import generate_test_data
# Create global MCP server instance
mcp = FastMCP("DataSource MCP Client Server")

@mcp.tool()
async def sql_exec(sql: str):
    """
    OceanBase SQL execution tool
    
    Function description:
    Execute any type of SQL statement, including SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, etc.
    Supports query and modification operations, automatically handles transaction commit and rollback
    
    Parameter description:
    - sql (str): SQL statement to execute, supports parameterized queries
    
    Return value:
    - dict: Dictionary containing execution results
        - success (bool): Whether execution was successful
        - result: Execution result (query returns data list, modification returns affected rows)
        - message (str): Execution status description
        - error (str): Error message on failure (only exists when success=False)
    
    Usage examples:
    - Query: SELECT * FROM users WHERE age > 18
    - Insert: INSERT INTO users (name, age) VALUES ('John', 25)
    - Update: UPDATE users SET age = 26 WHERE name = 'John'
    - Delete: DELETE FROM users WHERE age < 18
    """
    logger.info(f"MCP tool executing SQL: {sql}")
    try:
        result = await execute_sql(sql)
        
        # Record execution results
        if isinstance(result, list):
            logger.info(f"SQL execution successful, returned {len(result)} rows of data")
        else:
            logger.info(f"SQL execution successful, affected {result} rows")
            
        return {
            "success": True, 
            "result": result,
            "message": "SQL executed successfully"
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"MCP tool SQL execution failed: {error_msg}")
        return {
            "success": False, 
            "error": error_msg,
            "message": "SQL execution failed"
        }

@mcp.tool()
async def describe_table(table_name: str):
    """
   OceanBase Table structure description tool
    
    Function description:
    Get detailed structure information of the specified table, including column names, data types, NULL allowance, default values, key types, etc.
    Equivalent to executing DESCRIBE table_name or SHOW COLUMNS FROM table_name
    
    Parameter description:
    - table_name (str): Table name to describe, supports database.table format
    
    Return value:
    - dict: Same return format as sql_exec tool, result contains table structure information list
    
    Usage examples:
    - describe_table("users")
    - describe_table("mydb.users")
    
    Return data example:
    [
        {"Field": "id", "Type": "int(11)", "Null": "NO", "Key": "PRI", "Default": null, "Extra": "auto_increment"},
        {"Field": "name", "Type": "varchar(100)", "Null": "NO", "Key": "", "Default": null, "Extra": ""}
    ]
    """
    logger.info(f"MCP tool: Describe table structure - {table_name}")
    return await sql_exec(f"DESCRIBE {table_name};")

@mcp.tool()
async def generate_demo_data(table_name: str, columns_name: List[str], num: int):
    """
    OceanBase Test data generation tool

    Function description:
    Generate specified amount of test data for specified tables and columns
    Automatically generates random strings as test data for development and testing environments
    
    Parameter description:
    - table_name (str): Table name to generate test data for
    - columns_name (List[str]): List of column names to fill with data
    - num (int): Number of test records to generate
    
    Return value:
    - dict: Same return format as generate_test_data function
        - success (bool): Whether data generation was successful
        - result: Generation result information
        - error (str): Error message on failure (only exists when success=False)
    
    Data generation rules:
    - Each record generates 8-character random letter strings for each column
    - Uses INSERT statements for batch data insertion
    - Supports any number of columns and data types (string type)
    
    Usage examples:
    - generate_demo_data("users", ["name", "email", "phone"], 100)
    - generate_demo_data("products", ["product_name", "category"], 50)
    
    Notes:
    - Only suitable for development and testing environments
    - Generated data consists of random strings, no business logic included
    - Large data generation may take considerable time
    """
    logger.info(f"MCP tool: Generate test data - {table_name}")
    return await generate_test_data(table_name, columns_name, num)
@mcp.resource("database://tables")
async def get_database_tables():
    """
    OceanBase Database table information resource
    
    Function description:
    Provides metadata information for all tables in the database, including table names, table structures, record counts, etc.
    This is a read-only resource for obtaining database schema information, not involving data modification operations
    
    Resource URI:
    - database://tables - Represents database table collection resource
    
    Return value format:
    - uri (str): Resource identifier "database://tables"
    - mimeType (str): Content type "application/json"
    - text (str): JSON-formatted table information string
    
    Return data content:
    Contains detailed information list for all tables, each table includes:
    - name: Table name
    - columns: Table structure information (column names, data types, constraints, etc.)
    - record_count: Number of records in the table
    
    Usage scenarios:
    - Database schema analysis
    - Table structure viewing
    - Data volume statistics
    - Database monitoring
    
    Notes:
    - This is a read-only resource that will not modify database content
    - Returned information is based on current active database connection
    - Databases with many tables may require longer response time
    """
    logger.info("Getting database table information")
    # Get all table names
    tables_info = await generate_database_tables()

    return {
        "uri": "database://tables",
        "mimeType": "application/json",
        "text": str(tables_info)
    }


@mcp.resource("database://config")
async def get_database_config():
    """
    OceanBase Database configuration information resource
    
    Function description:
    Provides configuration information for current database connection, including connection parameters, connection pool settings, etc.
    Sensitive information (such as passwords) will be hidden to ensure configuration information security
    
    Resource URI:
    - database://config - Represents database configuration resource
    
    Return value format:
    - uri (str): Resource identifier "database://config"
    - mimeType (str): Content type "application/json"
    - text (str): JSON-formatted configuration information string
    
    Return data content:
    Contains configuration information for database instances and connection pools:
    - dbInstanceId: Database instance identifier
    - dbHost: Database host address
    - dbPort: Database port number
    - dbDatabase: Database name
    - dbUsername: Database username
    - dbPassword: "***hidden***" (password is hidden)
    - dbType: Database type (xesql/mysql/ubisql)
    - dbVersion: Database version
    - pool_size: Connection pool size
    - max_overflow: Maximum overflow connections
    - pool_timeout: Connection pool timeout
    
    Usage scenarios:
    - Database connection status check
    - Connection pool configuration viewing
    - Database type and version information retrieval
    - System monitoring and diagnostics
    
    Security features:
    - Database passwords are hidden from display
    - Only returns configuration for current active database
    - Does not expose sensitive information from other database instances
    
    Notes:
    - This is a read-only resource that will not modify database configuration
    - Configuration information is based on dbconfig.json file
    - Environment variable config_file will override default configuration file path
    """
    logger.info("Getting database configuration information")

    safe_config = await generate_database_config()

    return {
        "uri": "database://config",
        "mimeType": "application/json",
        "text": str(safe_config)
    }

# ==================== Server Startup Related ====================

# When using fastmcp run, FastMCP CLI automatically handles server startup
# No need to manually call mcp.run() or handle stdio

def main():
    """Main function: Start MCP server"""
    logger.info(f"Database configuration file path:{db_config_path}")
    logger.info(f"Current project path:{project_path}")
    logger.info("OceanBase DataSource MCP Client server is ready to accept connections")

    active_db, db_config = load_activate_db_config()
    logger.info(f"Current database instance configuration: {active_db}")
    # When using fastmcp run, just call mcp.run() directly
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
