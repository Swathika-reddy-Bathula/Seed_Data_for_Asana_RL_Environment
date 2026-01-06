"""Database connection and initialization."""
import sqlite3
import os
from pathlib import Path


class Database:
    """Manages SQLite database connection and initialization."""
    
    def __init__(self, db_path: str = "output/asana_simulation.sqlite"):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Create database connection."""
        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        return self.conn
    
    def initialize_schema(self):
        """Initialize database schema from schema.sql file."""
        schema_path = Path(__file__).parent.parent.parent / "schema.sql"
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        self.conn.executescript(schema_sql)
        self.conn.commit()
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

