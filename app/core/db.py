"""
Neo4j Database Connection Module.

This module provides a singleton database connection instance for Neo4j with async support.
"""

import os
from neo4j import GraphDatabase, AsyncGraphDatabase
from app.utils.logger import get_logger

logger = get_logger()

class Neo4jConnection:
    """
    A Singleton Neo4j connection class to maintain a single database connection throughout the application.
    
    Attributes:
        _instance (Neo4jConnection): The singleton instance
        _driver (neo4j.Driver): The Neo4j driver instance
        _async_driver (neo4j.AsyncDriver): The async Neo4j driver instance
    """
    _instance = None
    _driver = None
    _async_driver = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Neo4jConnection, cls).__new__(cls)
            cls._instance._initialize_connection()
        return cls._instance

    def _initialize_connection(self):
        """Initialize both sync and async Neo4j database connections using environment variables."""
        try:
            uri = os.getenv('NEO4J_URI')
            user = os.getenv('NEO4J_USER')
            password = os.getenv('NEO4J_PASSWORD')

            if not all([uri, user, password]):
                raise ValueError("Missing required Neo4j connection environment variables")

            # Initialize sync driver
            self._driver = GraphDatabase.driver(uri, auth=(user, password))
            self._driver.verify_connectivity()
            
            # Initialize async driver
            self._async_driver = AsyncGraphDatabase.driver(uri, auth=(user, password))
            
            logger.info("Successfully connected to Neo4j database")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j database: {str(e)}")
            raise

    def get_driver(self):
        """
        Get the synchronous Neo4j driver instance.
        
        Returns:
            neo4j.Driver: The configured Neo4j driver instance
        """
        return self._driver

    def get_async_driver(self):
        """
        Get the asynchronous Neo4j driver instance.
        
        Returns:
            neo4j.AsyncDriver: The configured async Neo4j driver instance
        """
        return self._async_driver

    async def close(self):
        """Close both sync and async Neo4j driver connections."""
        if self._driver:
            self._driver.close()
        if self._async_driver:
            await self._async_driver.close()
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
            async with self._async_driver.session(database=db_name) as session:
                result = await session.run(query, params or {})
                records = await result.data()
                return records
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise

# Create a convenience function to get the database connection
def get_db():
    """
    Convenience function to get the database connection instance.
    
    Returns:
        Neo4jConnection: The configured database connection instance
    """
    return Neo4jConnection() 