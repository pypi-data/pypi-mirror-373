from sqlalchemy import create_engine, MetaData, text
from retrying import retry
import mysql.connector
from typing import Dict, Any, Optional

class MySQLHelper:
    """MySQL database helper with configurable connection."""
    
    def __init__(self, config: Dict[str, str]) -> None:
        self.hostname = config["mysql_hostname_internal"]
        self.port = config["mysql_port_internal"]
        self.database = config["mysql_database_name"]
        self.username = config["mysql_user_name"]
        self.password = config["mysql_user_password"]
        
        # Define the database connection
        self.database_url = f"mysql+mysqlconnector://{self.username}:{self.password}@{self.hostname}:{self.port}/{self.database}"
        
        # Create the SQLAlchemy engine
        self.engine = create_engine(self.database_url, echo=False)
        
        # Reflect the database schema (load metadata)
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)

    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=5)
    def execute_sql(self, sql: str, parameters: Dict[str, Any] = {}) -> Any:
        """Execute SQL query with retry logic."""
        query = text(sql)
        
        with self.engine.connect() as connection:
            result = connection.execute(query, parameters)
            return result.mappings()


# Legacy function for backward compatibility
@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=5)
def executeSQL(config: Dict[str, str], sql: str, parameters: Dict[str, Any] = {}) -> Any:
    """Legacy function for backward compatibility."""
    helper = MySQLHelper(config)
    return helper.execute_sql(sql, parameters) 