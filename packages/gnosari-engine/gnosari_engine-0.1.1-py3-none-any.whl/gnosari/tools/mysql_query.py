"""
OpenAI MySQL Query Tool - Using OpenAI Agents SDK FunctionTool
"""

import logging
import asyncio
import json
from typing import Any, Optional, Dict, List
from pydantic import BaseModel, Field
from agents import RunContextWrapper, FunctionTool
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool


class MySQLQueryArgs(BaseModel):
    """Arguments for the MySQL query tool."""
    query: str = Field(..., description="The SQL query to execute")
    query_type: str = Field(default="SELECT", description="Type of query (SELECT, INSERT, UPDATE, DELETE)")
    limit: Optional[int] = Field(default=None, description="Maximum number of rows to return (for SELECT queries)")
    timeout: Optional[int] = Field(default=None, description="Query timeout in seconds (overrides configured timeout)")


class MySQLQueryTool:
    """Configurable MySQL Query Tool that can be used in YAML configurations."""
    
    def __init__(self, 
                 host: str = "localhost",
                 port: int = 3306,
                 database: str = "",
                 username: str = "",
                 password: str = "",
                 charset: str = "utf8mb4",
                 pool_size: int = 5,
                 max_overflow: int = 10,
                 pool_timeout: int = 30,
                 pool_recycle: int = 3600,
                 query_timeout: int = 30,
                 echo: bool = False,
                 tool_name: str = "mysql_query",
                 tool_description: str = "Execute SQL queries against a MySQL database"):
        """Initialize the MySQL query tool.
        
        Args:
            host: MySQL server hostname
            port: MySQL server port
            database: Database name
            username: Database username
            password: Database password
            charset: Character set for the connection
            pool_size: Number of connections to maintain in the pool
            max_overflow: Maximum overflow connections beyond pool_size
            pool_timeout: Timeout for getting connection from pool
            pool_recycle: Time in seconds before connection is recycled
            query_timeout: Default timeout for queries in seconds
            echo: Whether to echo SQL statements (for debugging)
            tool_name: Name of the tool
            tool_description: Description of the tool
        """
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.charset = charset
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        self.query_timeout = query_timeout
        self.echo = echo
        self.tool_name = tool_name
        self.tool_description = tool_description
        
        # Setup logger
        self.logger = logging.getLogger(__name__)
        
        # Initialize engine and session factory
        self.engine = None
        self.SessionFactory = None
        self._initialize_connection()
        
        # Create the FunctionTool
        self.tool = FunctionTool(
            name=self.tool_name,
            description=self.tool_description,
            params_json_schema=MySQLQueryArgs.model_json_schema(),
            on_invoke_tool=self._run_mysql_query
        )
    
    def _initialize_connection(self):
        """Initialize the database connection and session factory."""
        try:
            # Construct connection URL
            connection_url = (
                f"mysql+pymysql://{self.username}:{self.password}@"
                f"{self.host}:{self.port}/{self.database}?charset={self.charset}"
            )
            
            # Create engine with connection pooling
            self.engine = create_engine(
                connection_url,
                poolclass=QueuePool,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_timeout=self.pool_timeout,
                pool_recycle=self.pool_recycle,
                echo=self.echo,
                connect_args={
                    "connect_timeout": 10,
                    "read_timeout": self.query_timeout,
                    "write_timeout": self.query_timeout
                }
            )
            
            # Create session factory
            self.SessionFactory = sessionmaker(bind=self.engine)
            
            self.logger.info(f"🔗 MySQL CONNECTION INITIALIZED - Host: {self.host}:{self.port}, Database: {self.database}")
            
        except Exception as e:
            self.logger.error(f"❌ FAILED TO INITIALIZE MYSQL CONNECTION: {str(e)}")
            raise
    
    def _validate_query(self, query: str, query_type: str) -> bool:
        """Validate the SQL query for safety and type consistency."""
        query_upper = query.strip().upper()
        
        # Check if query type matches the actual query
        if not query_upper.startswith(query_type.upper()):
            self.logger.warning(f"Query type '{query_type}' doesn't match query start: {query_upper[:20]}...")
        
        # Basic safety checks
        dangerous_keywords = ['DROP', 'TRUNCATE', 'ALTER', 'CREATE', 'GRANT', 'REVOKE']
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                self.logger.warning(f"Query contains potentially dangerous keyword: {keyword}")
        
        return True
    
    async def _run_mysql_query(self, ctx: RunContextWrapper[Any], args: str) -> str:
        """
        Execute a MySQL query.
        
        Args:
            ctx: Run context wrapper
            args: JSON string containing MySQLQueryArgs
            
        Returns:
            Query result as string
        """
        session = None
        try:
            # Parse arguments
            parsed_args = MySQLQueryArgs.model_validate_json(args)
            
            # Use config values as defaults, allow per-call overrides
            final_timeout = parsed_args.timeout or self.query_timeout
            
            self.logger.info(f"🗄️ MYSQL QUERY STARTED - Type: {parsed_args.query_type} | Timeout: {final_timeout}s")
            self.logger.debug(f"Query: {parsed_args.query}")
            
            # Validate query
            self._validate_query(parsed_args.query, parsed_args.query_type)
            
            # Create session
            session = self.SessionFactory()
            
            # Execute query (run synchronous code in executor)
            if parsed_args.query_type.upper() == "SELECT":
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self._execute_select_query,
                    session,
                    parsed_args.query,
                    parsed_args.limit,
                    final_timeout
                )
            else:
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self._execute_modify_query,
                    session,
                    parsed_args.query,
                    final_timeout
                )
            
            # Log successful result
            result_preview = str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
            self.logger.info(f"✅ MYSQL QUERY SUCCESSFUL - {parsed_args.query_type} executed")
            self.logger.info(f"📄 Result preview: {result_preview}")
            
            return result
            
        except SQLAlchemyError as e:
            error_msg = f"Database error executing {parsed_args.query_type} query: {str(e)}"
            self.logger.error(f"❌ MYSQL QUERY FAILED with SQLAlchemyError: {error_msg}")
            return error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error executing {parsed_args.query_type} query: {str(e)}"
            self.logger.error(f"❌ MYSQL QUERY FAILED with unexpected error: {error_msg}")
            return error_msg
            
        finally:
            if session:
                session.close()
    
    def _execute_select_query(self, session, query: str, limit: Optional[int], timeout: int) -> str:
        """Execute a SELECT query and return formatted results."""
        try:
            # Add LIMIT if specified and not already present
            if limit and "LIMIT" not in query.upper():
                query = f"{query.rstrip(';')} LIMIT {limit}"
            
            # Execute query with timeout
            result = session.execute(text(query))
            
            # Get column names
            columns = result.keys()
            
            # Fetch all rows
            rows = result.fetchall()
            
            if not rows:
                return "Query executed successfully. No rows returned."
            
            # Format results as JSON
            results_list = []
            for row in rows:
                row_dict = {}
                for i, column in enumerate(columns):
                    value = row[i]
                    # Convert non-serializable types
                    if hasattr(value, 'isoformat'):  # datetime objects
                        value = value.isoformat()
                    elif hasattr(value, '__dict__'):  # other complex objects
                        value = str(value)
                    row_dict[column] = value
                results_list.append(row_dict)
            
            return json.dumps({
                "status": "success",
                "row_count": len(results_list),
                "columns": list(columns),
                "data": results_list
            }, indent=2, default=str)
            
        except Exception as e:
            raise SQLAlchemyError(f"Error executing SELECT query: {str(e)}")
    
    def _execute_modify_query(self, session, query: str, timeout: int) -> str:
        """Execute INSERT/UPDATE/DELETE queries and return affected row count."""
        try:
            # Execute query
            result = session.execute(text(query))
            
            # Commit the transaction
            session.commit()
            
            # Get affected row count
            row_count = result.rowcount
            
            return json.dumps({
                "status": "success",
                "affected_rows": row_count,
                "message": f"Query executed successfully. {row_count} rows affected."
            }, indent=2)
            
        except Exception as e:
            # Rollback on error
            session.rollback()
            raise SQLAlchemyError(f"Error executing modify query: {str(e)}")
    
    def get_tool(self) -> FunctionTool:
        """Get the FunctionTool instance.
        
        Returns:
            FunctionTool instance
        """
        return self.tool
    
    def close_connections(self):
        """Close all database connections."""
        if self.engine:
            self.engine.dispose()
            self.logger.info("🔒 MySQL connections closed")


def get_default_mysql_query_tool() -> FunctionTool:
    """Get a default MySQL query tool instance.
    
    Returns:
        FunctionTool instance
    """
    return MySQLQueryTool().get_tool()