from src.utils.db_config import load_activate_db_config
from src.utils.db_operate import execute_sql
from src.utils.logger_util import logger


async def generate_database_tables():
    try:
        # Get all table names
        tables_result = execute_sql("SHOW TABLES")
        tables_info = []

        for table_row in tables_result:
            table_name = list(table_row.values())[0]  # Get table name

            # Get table structure
            describe_result = execute_sql(f"DESCRIBE {table_name}")

            # Get table record count
            count_result = execute_sql(f"SELECT COUNT(*) as count FROM {table_name}")
            record_count = count_result[0]['count'] if count_result else 0

            tables_info.append({
                "name": table_name,
                "columns": describe_result,
                "record_count": record_count
            })

        logger.info(f"Successfully obtained information for {len(tables_info)} tables")
        return {
            "uri": "database://tables",
            "mimeType": "application/json",
            "text": str(tables_info)
        }
    except Exception as e:
        logger.error(f"Failed to get database table information: {e}")
        return {
            "uri": "database://tables",
            "mimeType": "application/json",
            "text": f"Error: {str(e)}"
        }

async def generate_database_config():

    active_db, db_config = load_activate_db_config()

    # Hide sensitive information
    safe_config = {
        "dbInstanceId": active_db.db_instance_id,
        "dbHost": active_db.db_host,
        "dbPort": active_db.db_port,
        "dbDatabase": active_db.db_database,
        "dbUsername": active_db.db_username,
        "dbPassword": "***hidden***",
        "dbType": db_config.db_type,
        "dbVersion": db_config.db_version,
        "pool_size": db_config.db_pool_size,
        "max_overflow": db_config.db_max_overflow,
        "pool_timeout":db_config.db_pool_timeout,
    }
    logger.info("Successfully obtained database configuration information")
    logger.info(f"Database configuration: {safe_config}")
    return safe_config