"""
Database Utility Functions

Provides database utility functions related to SQL execution.
"""

from src.utils.db_operate import execute_sql
from src.utils.logger_util import logger
import random, string



async def sql_exec(sql: str):
    """
    Execute any SQL statement (SELECT/INSERT/UPDATE/DELETE)
    """
    logger.info(f"Executing SQL: {sql}")
    try:
        result = await execute_sql(sql)
        logger.info(f"SQL executed successfully, returned {len(result) if isinstance(result, list) else result} rows/affected rows")
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"SQL execution failed: {e}")
        return {"success": False, "error": str(e)}

async def generate_test_data(table, columns, num):
    logger.info(f"Starting to generate {num} test records for table '{table}'")
    logger.debug(f"Target table {table} columns: {columns}")

    for i in range(num):
        values = []
        for col in columns:
            # Simple example: all use 8-character random strings
            random_value = ''.join(random.choices(string.ascii_letters, k=8))
            values.append(random_value)

        placeholders = ','.join(['%s'] * len(columns))
        sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"

        logger.debug(f"Inserting row {i + 1}/{num}: {dict(zip(columns, values))}")
        result=await execute_sql(sql, values)

    logger.info(f"Successfully generated {num} test records for table '{table}'")