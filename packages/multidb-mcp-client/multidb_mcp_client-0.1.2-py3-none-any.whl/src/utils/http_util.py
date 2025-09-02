"""
HTTP Utility Module

Provides asynchronous HTTP GET and POST request functions.
"""

import asyncio
from typing import Dict, Optional

import aiohttp

from .logger_util import logger

async def http_get(url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, str]] = None) -> Dict:
    """
    Asynchronously execute HTTP GET request
    """
    logger.info(f"Executing GET request to {url}, params: {params}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                response.raise_for_status()
                return await response.json()
    except Exception as e:
        logger.error(f"GET request failed: {e}")
        raise

async def http_post(url: str, headers: Optional[Dict[str, str]] = None, data: Optional[Dict] = None) -> Dict:
    """
    Asynchronously execute HTTP POST request
    """
    logger.info(f"Executing POST request to {url}, data: {data}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                response.raise_for_status()
                return await response.json()
    except Exception as e:
        logger.error(f"POST request failed: {e}")
        raise