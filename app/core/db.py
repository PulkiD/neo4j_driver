"""
Neo4j Database Connection Module.

This module provides a singleton database connection instance for Neo4j.
"""

import os
from neo4j import GraphDatabase
from app.utils.logger import get_logger

logger = get_logger()

class Neo4jConnection:
    """
    A Singleton Neo4j connection class to maintain a single database connection throughout the application.
    
    Attributes:
        _instance (Neo4jConnection): The singleton instance
        _driver (neo4j.Driver): The Neo4j driver instance
    """
    _instance = None
    _driver = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Neo4jConnection, cls).__new__(cls)
            cls._instance._initialize_connection()
        return cls._instance

    def _initialize_connection(self):
        """Initialize the Neo4j database connection using environment variables."""
        try:
            uri = os.getenv('NEO4J_URI')
            user = os.getenv('NEO4J_USER')
            password = os.getenv('NEO4J_PASSWORD')

            if not all([uri, user, password]):
                raise ValueError("Missing required Neo4j connection environment variables")

            self._driver = GraphDatabase.driver(uri, auth=(user, password))
            # Verify connection
            self._driver.verify_connectivity()
            logger.info("Successfully connected to Neo4j database")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j database: {str(e)}")
            raise

    def get_driver(self):
        """
        Get the Neo4j driver instance.
        
        Returns:
            neo4j.Driver: The configured Neo4j driver instance
        """
        return self._driver

    def close(self):
        """Close the Neo4j driver connection."""
        if self._driver:
            self._driver.close()
            logger.info("Neo4j connection closed")

    def execute_query(self, query, params=None):
        """
        Execute a Cypher query and return the results.
        
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
            with self._driver.session(database=db_name) as session:
                result = session.run(query, params or {})
                return [record.data() for record in result]
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