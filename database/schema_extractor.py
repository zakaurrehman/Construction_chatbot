"""
Extract and format database schema information for AI processing.
"""
import json
import logging
from .db_connector import DatabaseConnector

logger = logging.getLogger(__name__)

class SchemaExtractor:
    def __init__(self, db_config):
        """Initialize schema extractor."""
        self.db = DatabaseConnector(db_config)
    
    def get_full_schema(self):
        """Get complete database schema information."""
        try:
            schema_info = {
                'tables': self.db.get_schema_summary(),
                'relationships': self._get_relationships(),
                'indexes': self._get_indexes(),
                'constraints': self._get_constraints()
            }
            return schema_info
        except Exception as e:
            logger.error(f"Failed to extract full schema: {e}")
            return {}
    
    def get_formatted_schema_prompt(self):
        """Get schema formatted for AI prompts."""
        schema = self.db.get_schema_summary()
        
        prompt_sections = []
        prompt_sections.append("**Available Database Tables:**\n")
        
        for table_name, columns in schema.items():
            # Format table header
            prompt_sections.append(f"\n**{table_name}:**")
            
            # Format columns
            for col in columns:
                col_info = f"- {col['column_name']} ({col['data_type']})"
                if col['is_nullable'] == 'NO':
                    col_info += " [NOT NULL]"
                if col['column_default']:
                    col_info += f" [DEFAULT: {col['column_default']}]"
                prompt_sections.append(col_info)
        
        # Add relationships if available
        relationships = self._get_relationships_summary()
        if relationships:
            prompt_sections.append("\n**Key Relationships:**")
            for rel in relationships:
                prompt_sections.append(f"- {rel}")
        
        return "\n".join(prompt_sections)
    
    def _get_relationships(self):
        """Get foreign key relationships."""
        query = """
        SELECT
            tc.table_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name,
            tc.constraint_name
        FROM
            information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_schema = 'public';
        """
        
        try:
            return self.db.execute_query(query)
        except Exception as e:
            logger.error(f"Failed to get relationships: {e}")
            return []
    
    def _get_relationships_summary(self):
        """Get simplified relationships for AI prompt."""
        relationships = self._get_relationships()
        summary = []
        
        for rel in relationships:
            summary.append(
                f"{rel['table_name']}.{rel['column_name']} -> "
                f"{rel['foreign_table_name']}.{rel['foreign_column_name']}"
            )
        
        return summary
    
    def _get_indexes(self):
        """Get database indexes."""
        query = """
        SELECT
            schemaname,
            tablename,
            indexname,
            indexdef
        FROM pg_indexes
        WHERE schemaname = 'public'
        ORDER BY tablename, indexname;
        """
        
        try:
            return self.db.execute_query(query)
        except Exception as e:
            logger.error(f"Failed to get indexes: {e}")
            return []
    
    def _get_constraints(self):
        """Get table constraints."""
        query = """
        SELECT
            tc.table_name,
            tc.constraint_name,
            tc.constraint_type,
            kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
          AND tc.table_schema = kcu.table_schema
        WHERE tc.table_schema = 'public'
        ORDER BY tc.table_name, tc.constraint_name;
        """
        
        try:
            return self.db.execute_query(query)
        except Exception as e:
            logger.error(f"Failed to get constraints: {e}")
            return []
    
    def get_table_info(self, table_name):
        """Get detailed information about a specific table."""
        try:
            # Get columns
            columns_query = """
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length,
                numeric_precision,
                datetime_precision
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = %s
            ORDER BY ordinal_position;
            """
            
            columns = self.db.execute_query(columns_query, (table_name,))
            
            # Get sample data
            sample_data = self.db.get_table_sample(table_name, 5)
            
            # Get row count
            count_query = f'SELECT COUNT(*) as count FROM "{table_name}"'
            row_count = self.db.execute_query(count_query)[0]['count']
            
            return {
                'table_name': table_name,
                'columns': columns,
                'sample_data': sample_data,
                'row_count': row_count
            }
            
        except Exception as e:
            logger.error(f"Failed to get table info for {table_name}: {e}")
            return None
    
    def export_schema_json(self, filepath='schema.json'):
        """Export schema to JSON file."""
        try:
            schema = self.get_full_schema()
            with open(filepath, 'w') as f:
                json.dump(schema, f, indent=2, default=str)
            logger.info(f"Schema exported to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export schema: {e}")