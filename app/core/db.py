"""
Neo4j Database Connection Module.

This module provides a singleton database connection instance for Neo4j with async support.
"""

import os
import time
from functools import wraps
from neo4j import GraphDatabase, AsyncGraphDatabase
from neo4j.time import Date, DateTime, Time, Duration
from neo4j.spatial import Point
from app.utils.logger import get_logger
import json

logger = get_logger()

def retry_with_exponential_backoff(
    initial_delay=1,
    exponential_base=2,
    max_retries=5,
    max_delay=60
):
    """
    Decorator that implements exponential backoff for retrying operations.
    
    Args:
        initial_delay (float): Initial delay between retries in seconds
        exponential_base (float): Base for exponential backoff
        max_retries (int): Maximum number of retry attempts
        max_delay (float): Maximum delay between retries in seconds
        
    Returns:
        callable: Decorated function with retry logic
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == max_retries - 1:
                        logger.error(f"Max retries ({max_retries}) reached. Last error: {str(e)}")
                        raise
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}. "
                        f"Retrying in {delay} seconds..."
                    )
                    await asyncio.sleep(delay)
                    delay = min(delay * exponential_base, max_delay)
            
            raise last_exception
        return wrapper
    return decorator

class Neo4jConnection:
    """
    A Singleton Neo4j connection class to maintain a single database connection throughout the application.
    
    Attributes:
        _instance (Neo4jConnection): The singleton instance
        _driver (neo4j.Driver): The Neo4j driver instance
        _async_driver (neo4j.AsyncDriver): The async Neo4j driver instance
        _initialized (bool): Whether the connection has been initialized
    """
    _instance = None
    _driver = None
    _async_driver = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Neo4jConnection, cls).__new__(cls)
        return cls._instance

    @retry_with_exponential_backoff(
        initial_delay=1,
        exponential_base=2,
        max_retries=5,
        max_delay=60
    )
    async def _initialize_connection(self):
        """
        Initialize both sync and async Neo4j database connections using environment variables.
        Implements exponential backoff retry logic for connection attempts.
        """
        if self._initialized:
            return

        try:
            uri = os.getenv('NEO4J_URI')
            user = os.getenv('NEO4J_USER')
            password = os.getenv('NEO4J_PASSWORD')

            if not all([uri, user, password]):
                raise ValueError("Missing required Neo4j connection environment variables")

            # Close existing connections if any
            if self._driver:
                self._driver.close()
            if self._async_driver:
                await self._async_driver.close()

            # Initialize sync driver
            self._driver = GraphDatabase.driver(uri, auth=(user, password))
            self._driver.verify_connectivity()
            
            # Initialize async driver
            self._async_driver = AsyncGraphDatabase.driver(uri, auth=(user, password))
            
            self._initialized = True
            logger.info("Successfully connected to Neo4j database")
        except Exception as e:
            self._initialized = False
            logger.error(f"Failed to connect to Neo4j database: {str(e)}")
            raise

    async def get_driver(self):
        """
        Get the synchronous Neo4j driver instance.
        Attempts to reinitialize connection if not initialized or if connection is broken.
        
        Returns:
            neo4j.Driver: The configured Neo4j driver instance
        """
        if not self._initialized:
            await self._initialize_connection()
        try:
            # Verify connection is still alive
            self._driver.verify_connectivity()
        except Exception:
            logger.warning("Connection verification failed, attempting to reconnect...")
            await self._initialize_connection()
        return self._driver

    async def get_async_driver(self):
        """
        Get the asynchronous Neo4j driver instance.
        Attempts to reinitialize connection if not initialized or if connection is broken.
        
        Returns:
            neo4j.AsyncDriver: The configured async Neo4j driver instance
        """
        if not self._initialized:
            await self._initialize_connection()
        return self._async_driver

    async def close(self):
        """Close both sync and async Neo4j driver connections."""
        if self._driver:
            self._driver.close()
        if self._async_driver:
            await self._async_driver.close()
        self._initialized = False
        logger.info("Neo4j connections closed")

    async def execute_query(self, query: str, params: dict = None) -> list:
        """
        Execute a Cypher query asynchronously and return the results.
        
        Args:
            query (str): The Cypher query to execute
            params (dict, optional): Parameters for the query. Defaults to None.
            
        Returns:
            list: List of records from the query result
            
        Raises:
            Exception: If there's an error executing the query
        """
        try:
            db_name = os.getenv('NEO4J_DATABASE', 'neo4j')
            driver = await self.get_async_driver()
            async with driver.session(database=db_name) as session:
                result = await session.run(query, params or {})
                records = await result.data()
                
                # Convert Neo4j types to serializable Python types
                serializable_records = self._convert_to_serializable(records)
                return serializable_records
                
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise

    def _convert_to_serializable(self, data):
        """
        Convert Neo4j types to serializable Python types.
        
        Args:
            data: The data to convert (can be dict, list, or primitive type)
            
        Returns:
            The converted data structure with serializable types
        """
        
        if isinstance(data, dict):
            return {key: self._convert_to_serializable(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._convert_to_serializable(item) for item in data]
        elif isinstance(data, (Date, DateTime)):
            return data.iso_format()  # Convert to ISO format string
        elif isinstance(data, Time):
            return data.iso_format()  # Convert to ISO format string
        elif isinstance(data, Duration):
            return str(data)  # Convert duration to string
        elif isinstance(data, Point):
            return {
                'x': data.x,
                'y': data.y,
                'z': getattr(data, 'z', None),
                'srid': data.srid
            }
        elif isinstance(data, str):
            # Try to parse if it looks like JSON
            try:
                if data.strip().startswith('{') or data.strip().startswith('['):
                    parsed = json.loads(data)
                    return self._convert_to_serializable(parsed)
            except json.JSONDecodeError:
                pass
            return data
        else:
            return data

# Create a convenience function to get the database connection
async def get_db():
    """
    Convenience function to get the database connection instance.
    
    Returns:
        Neo4jConnection: The configured database connection instance
    """
    return Neo4jConnection() 