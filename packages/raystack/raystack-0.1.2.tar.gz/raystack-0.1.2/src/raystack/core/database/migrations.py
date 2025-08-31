from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
import uuid
from datetime import datetime


class MigrationManager:
    """
    Migration manager for Raystack ORM using Alembic.
    """
    
    def __init__(self, database_url: str = None, migrations_dir: str = "migrations"):
        """
        Initialize migration manager.
        
        :param database_url: Database URL
        :param migrations_dir: Migrations directory
        """
        if database_url is None:
            database_url = "sqlite:///db.sqlite3"
        
        self.database_url = database_url
        self.migrations_dir = Path(migrations_dir)
        self.alembic_cfg = None
        self._setup_alembic()
    
    def _setup_alembic(self):
        """Configure Alembic configuration."""
        # Create migrations directory if it doesn't exist
        self.migrations_dir.mkdir(exist_ok=True)
        
        # Create versions directory if it doesn't exist
        versions_dir = self.migrations_dir / "versions"
        versions_dir.mkdir(exist_ok=True)
        
        # Create alembic.ini if it doesn't exist
        alembic_ini_path = Path("alembic.ini")
        if not alembic_ini_path.exists():
            self._create_alembic_ini()
        
        # Create env.py if it doesn't exist
        env_py_path = self.migrations_dir / "env.py"
        if not env_py_path.exists():
            self._create_env_py()
        
        # Create script.py.mako if it doesn't exist
        script_py_mako_path = self.migrations_dir / "script.py.mako"
        if not script_py_mako_path.exists():
            self._create_script_py_mako()
        
        # Configure Alembic configuration
        self.alembic_cfg = Config("alembic.ini")
        self.alembic_cfg.set_main_option("script_location", str(self.migrations_dir))
        self.alembic_cfg.set_main_option("sqlalchemy.url", self.database_url)
    
    def _create_alembic_ini(self):
        """Creates alembic.ini file."""
        ini_content = """[alembic]
script_location = migrations
sqlalchemy.url = sqlite:///db.sqlite3

# version number format
version_num_format = {0:04d}

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = ERROR
handlers = console
qualname =

[logger_sqlalchemy]
level = ERROR
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = ERROR
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = {levelname}-5.5s [{name}] {message}
datefmt = {H}:{M}:{S}
"""
        with open("alembic.ini", "w") as f:
            f.write(ini_content)
    
    def _create_env_py(self):
        """Creates env.py file for Alembic."""
        env_content = '''from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from raystack.core.database.sqlalchemy import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''
        with open(self.migrations_dir / "env.py", "w") as f:
            f.write(env_content)
    
    def _create_script_py_mako(self):
        """Creates script.py.mako file for Alembic."""
        mako_content = '''"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade():
    ${upgrades if upgrades else "pass"}


def downgrade():
    ${downgrades if downgrades else "pass"}
'''
        with open(self.migrations_dir / "script.py.mako", "w") as f:
            f.write(mako_content)
    
    def init(self):
        """Initializes the migration system."""
        if self.alembic_cfg is None:
            self._setup_alembic()
        
        try:
            command.init(self.alembic_cfg, str(self.migrations_dir))
        except Exception as e:
            # If directory is already initialized, ignore the error
            if "already exists" not in str(e):
                raise
    
    def create_migration(self, message: str, models: List[Any] = None):
        """
        Creates a new migration.
        
        :param message: Migration message
        :param models: List of models for migration
        :return: Migration creation result
        """
        if self.alembic_cfg is None:
            self._setup_alembic()
        
        # Create SQL migration in file
        if models:
            migration_content = self._generate_migration_content(models, message)
            # Create migration file
            migration_file = self._create_migration_file(migration_content, message)
            return migration_file
        
        # Create empty migration for Alembic
        result = command.revision(self.alembic_cfg, message=message, autogenerate=False)
        return result
    
    def _generate_migration_content(self, models, message):
        """
        Generates migration content.
        """
        migration_sql = []
        
        for model in models:
            sql = self._create_table_sql(model)
            if sql:
                migration_sql.append(sql)
        
        return migration_sql
    
    def _create_migration_file(self, migration_content, message):
        """
        Creates migration file with SQL commands.
        """
        
        # Create unique migration ID (without hyphens)
        migration_id = str(uuid.uuid4()).replace('-', '')[:12]
        
        # Create SQL commands for upgrade
        upgrade_commands = []
        for sql in migration_content:
            upgrade_commands.append(f"    op.execute('''{sql}''')")
        
        # Create SQL commands for downgrade
        downgrade_commands = []
        for sql in migration_content:
            table_name = sql.split()[5]  # Get table name from CREATE TABLE
            downgrade_commands.append(f"    op.execute('DROP TABLE IF EXISTS {table_name}')")
        
        # Create migration file content
        file_content = f'''"""Migration: {message}

Revision ID: {migration_id}
Revises: 
Create Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '{migration_id}'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Apply migration."""
    # ### commands auto generated by Raystack ###
{chr(10).join(upgrade_commands)}
    # ### end Raystack commands ###


def downgrade():
    """Revert migration."""
    # ### commands auto generated by Raystack ###
{chr(10).join(downgrade_commands)}
    # ### end Raystack commands ###
'''
        
        # Create migration file
        versions_dir = Path('migrations/versions')
        versions_dir.mkdir(exist_ok=True)
        
        migration_file = versions_dir / f"{migration_id}_.py"
        with open(migration_file, 'w') as f:
            f.write(file_content)
        
        return str(migration_file)
    
    def _create_table_sql(self, model):
        """
        Creates SQL for creating model table.
        """
        table_name = model.get_table_name()
        columns = []
        
        for field_name, field in model._fields.items():
            # Determine column type
            if field.column_type == int:
                column_type = "INTEGER"
            elif field.column_type == str:
                column_type = "TEXT"
            elif field.column_type == bool:
                column_type = "BOOLEAN"
            elif field.column_type == float:
                column_type = "REAL"
            else:
                column_type = "TEXT"
            
            # Add constraints
            constraints = []
            if field.primary_key:
                constraints.append("PRIMARY KEY")
            if field.unique:
                constraints.append("UNIQUE")
            if not field.primary_key:
                constraints.append("NOT NULL")
            
            column_def = f'"{field_name}" {column_type}'
            if constraints:
                column_def += f" {' '.join(constraints)}"
            
            columns.append(column_def)
        
        if columns:
            sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
            return sql
        
        return None
    
    def upgrade(self, revision: str = "head"):
        """
        Applies migrations.
        
        :param revision: Revision to apply (default "head")
        """
        if self.alembic_cfg is None:
            self._setup_alembic()
        
        command.upgrade(self.alembic_cfg, revision)
    
    def downgrade(self, revision: str):
        """
        Rolls back migrations.
        
        :param revision: Revision to rollback
        """
        if self.alembic_cfg is None:
            self._setup_alembic()
        
        command.downgrade(self.alembic_cfg, revision)
    
    def current(self):
        """
        Returns current revision.
        """
        if self.alembic_cfg is None:
            self._setup_alembic()
        
        try:
            return command.current(self.alembic_cfg)
        except Exception:
            return None
    
    def history(self):
        """
        Returns migration history.
        """
        if self.alembic_cfg is None:
            self._setup_alembic()
        
        return command.history(self.alembic_cfg)
    
    def show(self, revision: str):
        """
        Shows revision information.
        
        :param revision: Revision to show
        """
        if self.alembic_cfg is None:
            self._setup_alembic()
        
        return command.show(self.alembic_cfg, revision)
    
    def stamp(self, revision: str):
        """
        Marks current revision without applying migrations.
        
        :param revision: Revision to mark
        """
        if self.alembic_cfg is None:
            self._setup_alembic()
        
        command.stamp(self.alembic_cfg, revision)


# Global migration manager instance
migration_manager = MigrationManager() 