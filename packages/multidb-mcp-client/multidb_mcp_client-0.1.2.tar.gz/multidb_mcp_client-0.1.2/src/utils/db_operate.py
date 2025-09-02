"""
Database Operations Module

Provides database operation functions with HTTP proxy support.
"""

import json
from typing import Any, Dict, Optional

from .db_config import load_activate_db_config
from .http_util import http_post
from .logger_util import logger

async def execute_sql(sql: str, params: Optional[Dict] = None) -> Any:
    """Execute SQL statement (asynchronous version, using remote HTTP call)"""

    # Load active database configuration
    active_db, config = load_activate_db_config()

    # Remote server API endpoint
    url = config.multidb_server

    # Prepare request data and convert the database instance to a dictionary
    active_db_dict = {
        "dbInstanceId": active_db.db_instance_id,
        "dbHost": active_db.db_host,
        "dbPort": active_db.db_port,
        "dbDatabase": active_db.db_database,
        "dbUsername": active_db.db_username,
        "dbPassword": active_db.db_password,
        "dbType": active_db.db_type,
        "dbActive": active_db.db_active
    }

    data = {
        "sql": sql,
        "params": params,
        "databaseInstance": active_db_dict
    }

    json_str=json.dumps(data, indent=4)
    logger.debug(f"Preparing to execute remote SQL via HTTP POST to {url}, data: {json_str}")

    try:
        response = await http_post(url, data=data)
        logger.info(f"Remote SQL executed successfully, result: {response}")
        return response.get("data", [])
    except Exception as e:
        logger.error(f"Remote SQL execution failed: {e}")
        raise