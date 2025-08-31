import os
from typing import Dict, Any, Optional


class DatabaseSettings:
    """
    Database settings for Raystack ORM.
    Supports various database types through SQLAlchemy.
    """
    
    # Default database URL
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')
    
    # Connection settings
    DATABASE_OPTIONS = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30,
        'pool_recycle': 3600,
    }
    
    # Migration settings
    MIGRATIONS_DIR = 'migrations'
    MIGRATIONS_AUTO_GENERATE = True
    
    # Logging settings
    DATABASE_LOGGING = False
    DATABASE_ECHO = False
    
    @classmethod
    def get_database_url(cls) -> str:
        """
        Returns the database URL.
        """
        return cls.DATABASE_URL
    
    @classmethod
    def get_database_options(cls) -> Dict[str, Any]:
        """
        Returns options for connecting to the database.
        """
        return cls.DATABASE_OPTIONS.copy()
    
    @classmethod
    def get_migrations_dir(cls) -> str:
        """
        Returns the migrations directory.
        """
        return cls.MIGRATIONS_DIR
    
    @classmethod
    def is_sqlite(cls) -> bool:
        """
        Checks if SQLite is used.
        """
        return cls.DATABASE_URL.startswith('sqlite://')
    
    @classmethod
    def is_postgresql(cls) -> bool:
        """
        Checks if PostgreSQL is used.
        """
        return cls.DATABASE_URL.startswith('postgresql://')
    
    @classmethod
    def is_mysql(cls) -> bool:
        """
        Checks if MySQL is used.
        """
        return cls.DATABASE_URL.startswith('mysql://')
    
    @classmethod
    def is_oracle(cls) -> bool:
        """
        Checks if Oracle is used.
        """
        return cls.DATABASE_URL.startswith('oracle://')
    
    @classmethod
    def get_database_type(cls) -> str:
        """
        Returns the database type.
        """
        if cls.is_sqlite():
            return 'sqlite'
        elif cls.is_postgresql():
            return 'postgresql'
        elif cls.is_mysql():
            return 'mysql'
        elif cls.is_oracle():
            return 'oracle'
        else:
            return 'unknown'


# Global settings instance
db_settings = DatabaseSettings() 