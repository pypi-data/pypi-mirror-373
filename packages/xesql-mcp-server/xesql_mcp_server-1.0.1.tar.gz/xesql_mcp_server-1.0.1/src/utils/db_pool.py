"""
Database Connection Pool Management Module
Provides asynchronous MySQL connection pool functionality
"""
import asyncio
import aiomysql
from src.utils.logger_util import logger
from src.utils.db_config import load_activate_db_config


class DatabasePool:
    """Database connection pool management class"""

    _instance = None
    _pool = None
    _config = None

    @classmethod
    async def get_instance(cls):
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = DatabasePool()
            await cls._instance._initialize()
        return cls._instance

    async def _initialize(self):
        """Initialize connection pool"""
        if self._pool is not None:
            return

        # Get active database instance and configuration
        db_instance, db_config = load_activate_db_config()
        self._config = db_config

        try:
            pool_size = int(db_config.db_pool_size)
            max_overflow = int(db_config.db_max_overflow)
            pool_timeout = int(db_config.db_pool_timeout)
            max_size=pool_size + max_overflow
            self._pool = await aiomysql.create_pool(
                host=db_instance.db_host,
                port=int(db_instance.db_port),
                user=db_instance.db_username,
                password=db_instance.db_password,
                db=db_instance.db_database,
                minsize=pool_size,
                maxsize=max_size,
                pool_recycle=pool_timeout,
                autocommit=True  # Keep consistent with synchronous version
            )
            logger.info(f"Database connection pool initialized successfully, pool minsize: {pool_size}, maxsize: {max_size}, pool timeout:{pool_timeout}s")
            logger.info(
                f"Database connection pool Config: {db_instance}")
        except Exception as e:
            logger.error(f"Database connection pool initialization failed: {str(e)}")
            raise

    async def get_connection(self):
        """Get database connection"""
        if self._pool is None:
            await self._initialize()

        try:
            conn = await self._pool.acquire()
            logger.debug("Successfully obtained connection from pool")
            return conn
        except Exception as e:
            logger.error(f"Failed to get connection from pool: {str(e)}")
            raise

    async def release_connection(self, conn):
        """Release database connection back to connection pool"""
        if self._pool is None:
            logger.warning("Connection pool does not exist, cannot release connection")
            return

        try:
            self._pool.release(conn)
            logger.debug("Successfully released connection back to pool")
        except Exception as e:
            logger.error(f"Failed to release connection back to pool: {str(e)}")

    async def close_pool(self):
        """Close connection pool"""
        if self._pool is None:
            logger.warning("Connection pool does not exist, no need to close")
            return

        try:
            self._pool.close()
            await self._pool.wait_closed()
            self._pool = None
            logger.info("Database connection pool has been closed")
        except Exception as e:
            logger.error(f"Failed to close database connection pool: {str(e)}")


# Export connection pool getter function
async def get_db_pool():
    """Get database connection pool instance"""
    return await DatabasePool.get_instance()

if __name__ == "__main__":
    # Test connection pool
    async def test_pool():
        db_pool = await get_db_pool()
        conn = await db_pool.get_connection()
        await db_pool.release_connection(conn)
        await db_pool.close_pool()
        
    asyncio.run(test_pool())