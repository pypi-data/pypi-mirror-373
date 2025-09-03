"""
Database Operations Module

Provides database operation functions with HTTP proxy support.
"""

from src.utils.db_pool import get_db_pool
from src.utils.logger_util import logger
import aiomysql

async def get_pooled_connection():
    """Get database connection from connection pool"""
    try:
        pool = await get_db_pool()
        conn = await pool.get_connection()
        return conn
    except Exception as e:
        logger.error(f"Failed to get connection from pool: {e}")
        raise
async def execute_sql(sql, params=None):
    """Execute SQL statement (asynchronous version, using connection pool)"""
    conn = None
    cursor = None
    try:
        logger.debug("Getting database connection from connection pool...")
        conn = await get_pooled_connection()
        cursor = await conn.cursor(aiomysql.DictCursor)

        # Execute SQL
        logger.debug(f"Preparing to execute asynchronous SQL: {sql}  params:{params}")
        await cursor.execute(sql, params or ())

        # Handle different types of SQL statements
        sql_lower = sql.strip().lower()
        if sql_lower.startswith(("select", "show", "describe", "desc")):
            result = await cursor.fetchall()
            logger.debug(f"Asynchronous query returned {len(result)} rows of data")
            # Consume all result sets
            try:
                while await cursor.nextset():
                    await cursor.fetchall()
            except:
                pass
        elif sql_lower.startswith(("insert", "update", "delete")):
            result = cursor.rowcount
            await conn.commit()
            logger.debug(f"Asynchronous query affected {result} rows of data")
        else:
            # For other statements (such as CREATE, DROP, etc.)
            result = "Query executed successfully"
            await conn.commit()
            logger.debug("Asynchronous DDL query executed successfully")

        logger.debug(f"Asynchronous SQL executed successfully: result:{result}")
        return result

    except Exception as e:
        logger.error(f"Asynchronous SQL execution failed: {e}")
        logger.debug(f"Failed asynchronous SQL: {sql}")
        if conn:
            await conn.rollback()
            logger.debug("Asynchronous transaction has been rolled back")
        raise
    finally:
        if cursor:
            await cursor.close()
            logger.debug("Asynchronous cursor has been closed")
        if conn:
            pool = await get_db_pool()
            await pool.release_connection(conn)
            logger.debug("Asynchronous connection has been released back to pool")