from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, Boolean, DateTime, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# asynccontextmanager for Python 3.6 compatibility
try:
    from contextlib import asynccontextmanager
except ImportError:
    from contextlib import contextmanager as asynccontextmanager
import os
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

Base = declarative_base()

class SQLAlchemyBackend:
    """
    SQLAlchemy backend for Raystack ORM.
    Supports various databases through SQLAlchemy.
    """
    
    def __init__(self, database_url: str = None):
        """
        Backend initialization.
        
        :param database_url: Database URL (e.g., 'sqlite:///db.sqlite3', 
                           'postgresql://user:pass@localhost/dbname',
                           'mysql://user:pass@localhost/dbname')
        """
        if database_url is None:
            # By default use SQLite
            database_url = "sqlite:///db.sqlite3"
        
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
        self.async_engine = None
        self.AsyncSessionLocal = None
        self.metadata = MetaData()
        self._tables: Dict[str, Table] = {}
        self._initialized = False
        self._async_initialized = False
        
    def is_async_url(self) -> bool:
        """
        Determines if URL is asynchronous by presence of async driver.
        """
        return any(driver in self.database_url for driver in [
            '+aiosqlite://', '+asyncpg://', '+aiomysql://', '+asyncmy://'
        ])
        
    def initialize(self):
        """Initialize database connection."""
        if self._initialized:
            return
            
        # Create engine
        if self.database_url.startswith('sqlite://'):
            # For SQLite use StaticPool for better compatibility
            self.engine = create_engine(
                self.database_url,
                poolclass=StaticPool,
                connect_args={"check_same_thread": False}
            )
        else:
            self.engine = create_engine(self.database_url)
        
        # Create session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
        
        self._initialized = True
    
    @contextmanager
    def get_session(self) -> Session:
        """Context manager for getting database session."""
        if not self._initialized:
            self.initialize()
            
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def create_table(self, table_name: str, columns: List[Dict[str, Any]]) -> Table:
        """
        Creates table in database.
        
        :param table_name: Table name
        :param columns: List of columns with their definitions
        :return: Created table
        """
        if table_name in self._tables:
            return self._tables[table_name]
        
        table_columns = []
        
        for col_def in columns:
            name = col_def['name']
            column_type = col_def['type']
            primary_key = col_def.get('primary_key', False)
            nullable = col_def.get('nullable', True)
            unique = col_def.get('unique', False)
            foreign_key = col_def.get('foreign_key')
            
            # Determine column type
            if column_type == 'INTEGER':
                sqlalchemy_type = Integer
            elif column_type.startswith('VARCHAR'):
                max_length = int(column_type[8:-1])  # Extract length from VARCHAR(n)
                sqlalchemy_type = String(max_length)
            elif column_type == 'TEXT':
                sqlalchemy_type = Text
            elif column_type == 'BOOLEAN':
                sqlalchemy_type = Boolean
            elif column_type == 'DATETIME':
                sqlalchemy_type = DateTime
            else:
                sqlalchemy_type = String
            
            # Create column
            column = Column(
                name, 
                sqlalchemy_type, 
                primary_key=primary_key,
                nullable=not nullable,
                unique=unique
            )
            
            # Add foreign key if specified
            if foreign_key:
                column = Column(
                    name,
                    sqlalchemy_type,
                    ForeignKey(foreign_key),
                    primary_key=primary_key,
                    nullable=not nullable,
                    unique=unique
                )
            
            table_columns.append(column)
        
        # Create table
        table = Table(table_name, self.metadata, *table_columns)
        self._tables[table_name] = table
        
        # Create table in database
        table.create(self.engine, checkfirst=True)
        
        return table
    
    def execute(self, query: str, params: tuple = None, fetch: bool = False):
        """
        Executes SQL query.
        
        :param query: SQL query
        :param params: Query parameters (ignored for SQLAlchemy)
        :param fetch: If True, returns query results
        :return: Query results or cursor
        """
        with self.get_session() as session:
            # Wrap SQL query in text() for SQLAlchemy
            print('query', query)
            sql_text = text(query)
            
            # Execute query without parameters
            result = session.execute(sql_text)
                
            if fetch:
                return result.fetchall()
            return result
    
    def commit(self):
        """Dummy method for compatibility with existing code."""
        pass
    
    def lastrowid(self):
        """Returns ID of last inserted record."""
        with self.get_session() as session:
            # Different approaches for different databases
            if self.database_url.startswith('sqlite://'):
                return session.execute(text("SELECT last_insert_rowid()")).scalar()
            elif self.database_url.startswith('postgresql://'):
                return session.execute(text("SELECT lastval()")).scalar()
            elif self.database_url.startswith('mysql://'):
                return session.execute(text("SELECT LAST_INSERT_ID()")).scalar()
            else:
                return None
    
    # Asynchronous methods
    async def initialize_async(self):
        """Asynchronous database connection initialization."""
        if self._async_initialized:
            return
            
        # Create async engine
        if self.database_url.startswith('sqlite://'):
            # Convert to asynchronous URL
            async_url = self.database_url.replace('sqlite://', 'sqlite+aiosqlite://')
            self.async_engine = create_async_engine(
                async_url,
                connect_args={"check_same_thread": False}
            )
        elif self.database_url.startswith('postgresql://'):
            async_url = self.database_url.replace('postgresql://', 'postgresql+asyncpg://')
            self.async_engine = create_async_engine(async_url)
        elif self.database_url.startswith('mysql://'):
            async_url = self.database_url.replace('mysql://', 'mysql+aiomysql://')
            self.async_engine = create_async_engine(async_url)
        else:
            # For other databases use the same URL
            self.async_engine = create_async_engine(self.database_url)
        
        # Create asynchronous session factory (compatibility with SQLAlchemy 1.4)
        from sqlalchemy.orm import sessionmaker
        self.AsyncSessionLocal = sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=self.async_engine,
            class_=AsyncSession
        )
        
        # Create tables
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        self._async_initialized = True
    
    async def get_async_session(self) -> AsyncSession:
        """Gets asynchronous database session."""
        if not self._async_initialized:
            await self.initialize_async()
            
        return self.AsyncSessionLocal()
    
    async def execute_async(self, query: str, params: tuple = None, fetch: bool = False):
        """
        Asynchronously executes SQL query.
        
        :param query: SQL query
        :param params: Query parameters (ignored for SQLAlchemy)
        :param fetch: If True, returns query results
        :return: Query results or cursor
        """
        if not self._async_initialized:
            await self.initialize_async()
            
        session = await self.get_async_session()
        try:
            # Wrap SQL query in text() for SQLAlchemy
            sql_text = text(query)
            
            # Execute query without parameters
            result = await session.execute(sql_text)
            
            # Make commit to save changes
            await session.commit()
                
            if fetch:
                return result.fetchall()
            return result
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    async def create_table_async(self, table_name: str, columns: List[Dict[str, Any]]) -> Table:
        """
        Asynchronously creates table in database.
        
        :param table_name: Table name
        :param columns: List of columns with their definitions
        :return: Created table
        """
        if not self._async_initialized:
            await self.initialize_async()
            
        if table_name in self._tables:
            return self._tables[table_name]
        
        table_columns = []
        
        for col_def in columns:
            name = col_def['name']
            column_type = col_def['type']
            primary_key = col_def.get('primary_key', False)
            nullable = col_def.get('nullable', True)
            unique = col_def.get('unique', False)
            foreign_key = col_def.get('foreign_key')
            
            # Determine column type
            if column_type == 'INTEGER':
                sqlalchemy_type = Integer
            elif column_type.startswith('VARCHAR'):
                max_length = int(column_type[8:-1])  # Extract length from VARCHAR(n)
                sqlalchemy_type = String(max_length)
            elif column_type == 'TEXT':
                sqlalchemy_type = Text
            elif column_type == 'BOOLEAN':
                sqlalchemy_type = Boolean
            elif column_type == 'DATETIME':
                sqlalchemy_type = DateTime
            else:
                sqlalchemy_type = String
            
            # Create column
            column = Column(
                name, 
                sqlalchemy_type, 
                primary_key=primary_key,
                nullable=not nullable,
                unique=unique
            )
            
            # Add foreign key if specified
            if foreign_key:
                column = Column(
                    name,
                    sqlalchemy_type,
                    ForeignKey(foreign_key),
                    primary_key=primary_key,
                    nullable=not nullable,
                    unique=unique
                )
            
            table_columns.append(column)
        
        # Create table
        table = Table(table_name, self.metadata, *table_columns)
        self._tables[table_name] = table
        
        # Create table in database asynchronously
        async with self.async_engine.begin() as conn:
            await conn.run_sync(lambda sync_conn: table.create(sync_conn, checkfirst=True))
        
        return table
    
    async def lastrowid_async(self):
        """Asynchronously returns ID of last inserted record."""
        if not self._async_initialized:
            await self.initialize_async()
            
        session = await self.get_async_session()
        try:
            # Different approaches for different databases
            if self.database_url.startswith('sqlite://'):
                result = await session.execute(text("SELECT last_insert_rowid()"))
                row = result.fetchone()
                return row[0] if row else None
            elif self.database_url.startswith('postgresql://'):
                result = await session.execute(text("SELECT lastval()"))
                row = result.fetchone()
                return row[0] if row else None
            elif self.database_url.startswith('mysql://'):
                result = await session.execute(text("SELECT LAST_INSERT_ID()"))
                row = result.fetchone()
                return row[0] if row else None
            else:
                return None
        finally:
            await session.close()

def get_database_url_from_settings():
    """
    Gets database URL from settings.
    """
    try:
        # Try to import settings
        import config.settings
        return config.settings.DATABASES['default']['URL']
    except (ImportError, KeyError, AttributeError):
        # If failed to get from settings, return default value
        return "sqlite:///db.sqlite3"

# Global backend instance
db = SQLAlchemyBackend(get_database_url_from_settings()) 