import psycopg
from psycopg.rows import dict_row
import re
import json
import logging

logger = logging.getLogger(__name__)

class DatabaseConnector:
    def __init__(self, db_config):
        """Initialize database connection with psycopg3."""
        self.config = db_config
        self.conn = None
        self.connect()
    
    def connect(self):
        """Establish database connection."""
        try:
            # Create connection string for psycopg3
            conn_string = f"postgresql://{self.config.get('user')}:{self.config.get('password')}@{self.config.get('host')}:{self.config.get('port', 5432)}/{self.config.get('dbname')}?sslmode={self.config.get('sslmode', 'prefer')}"
            
            self.conn = psycopg.connect(
                conn_string,
                row_factory=dict_row,
                autocommit=False
            )
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def execute_query(self, query, params=None):
        """Execute any SQL query with optional parameters."""
        try:
            # Ensure connection is alive
            if self.conn.closed:
                self.connect()
            
            with self.conn.cursor() as cursor:
                cursor.execute(query, params or ())
                
                # Handle different query types
                if cursor.description:  # SELECT query
                    result = cursor.fetchall()
                    # Already in dict format due to dict_row factory
                    return result
                else:  # INSERT/UPDATE/DELETE query
                    self.conn.commit()
                    return cursor.rowcount
                    
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Query execution failed: {e}")
            raise
    
    def get_schema_summary(self):
        """Get a summary of all tables and their columns."""
        query = """
        SELECT 
            table_name,
            json_agg(json_build_object(
                'column_name', column_name,
                'data_type', data_type,
                'is_nullable', is_nullable,
                'column_default', column_default
            ) ORDER BY ordinal_position) as columns
        FROM information_schema.columns
        WHERE table_schema = 'public'
        GROUP BY table_name
        ORDER BY table_name;
        """
        
        try:
            result = self.execute_query(query)
            schema = {}
            for row in result:
                schema[row['table_name']] = row['columns']
            return schema
        except Exception as e:
            logger.error(f"Failed to get schema summary: {e}")
            return {}
    
    def search_projects(self, search_term=None):
        """Get projects with optional search filter."""
        base_query = """
        SELECT 
            p.*,
            u.email as designer_email,
            CONCAT(l."firstName", ' ', l."lastName") as client_name
        FROM projects p
        LEFT JOIN users u ON p.project_designer_id = u.id
        LEFT JOIN leads l ON p.client_id = l.id
        """
        
        params = None
        where_clause = ""
        
        if search_term:
            where_clause = " WHERE p.name ILIKE %s"
            params = (f'%{search_term}%',)
        
        order_clause = ' ORDER BY p."updatedAt" DESC LIMIT 50'
        
        return self.execute_query(base_query + where_clause + order_clause, params)
    
    def get_table_sample(self, table_name, limit=10):
        """Get sample rows from any table."""
        # Sanitize table name to prevent SQL injection
        if not table_name.replace('_', '').isalnum():
            raise ValueError("Invalid table name")
        
        query = f'SELECT * FROM "{table_name}" LIMIT %s'
        return self.execute_query(query, (limit,))
    
    def execute_safe(self, query, params=None):
        """Clean, safety-check, and execute SELECT/CTE queries only."""
        # 1) Remove fences
        cleaned = query.replace('```', '')

        # 2) Remove leading 'sql' tag if present
        cleaned = re.sub(r'^\s*sql\s*', '', cleaned, flags=re.IGNORECASE)

        # 3) Strip out extra whitespace
        cleaned = cleaned.strip()

        # Debug log so you can see exactly what you’re executing
        print("Executing cleaned SQL:", repr(cleaned))

        # 4) Safety check on the _cleaned_ SQL
        if not self._is_safe_query(cleaned):
            raise ValueError("Only SELECT (or WITH) queries are allowed for safety")

        # 5) Finally execute the truly clean SQL
        return self.execute_query(cleaned, params)
    
     # In db_connector.py, replace your _is_safe_query() with:

    def _is_safe_query(self, query):
        """Check if query is safe to execute."""
        # We assume 'query' is already cleaned.
        normalized = re.sub(r'\s+', ' ', query.strip()).lower()
        return normalized.startswith('select') or normalized.startswith('with')


    def close(self):
        """Close database connection."""
        if self.conn and not self.conn.closed:
            self.conn.close()
            logger.info("Database connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()