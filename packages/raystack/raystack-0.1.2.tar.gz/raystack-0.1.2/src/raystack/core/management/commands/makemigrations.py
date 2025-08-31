from raystack.core.management.base import BaseCommand
import sys
import os
from pathlib import Path
import glob


class Command(BaseCommand):
    help = "Creates new migrations for models"

    def add_arguments(self, parser):
        parser.add_argument(
            '--message', '-m',
            type=str,
            help='Migration message'
        )
        parser.add_argument(
            '--empty',
            action='store_true',
            help='Create empty migration'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what will be created without creating migration'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force migration creation even if there are no changes'
        )

    def handle(self, *args, **options):
        # Lazy imports to avoid errors when loading commands
        try:
            from raystack.core.database.migrations import migration_manager
            from raystack.core.database.models import ModelMeta
            from raystack.core.database.sqlalchemy import db
        except ImportError as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to import database module: {e}')
            )
            return
        
        message = options.get('message', 'Auto-generated migration')
        empty = options.get('empty', False)
        dry_run = options.get('dry_run', False)
        force = options.get('force', False)
        
        try:
            # Import all models for registration
            self._import_all_models()
            
            # Initialize migration system if needed
            migration_manager.init()
            
            # Initialize database if needed
            if hasattr(db, 'initialize') and not db._initialized:
                db.initialize()
            
            # Get all registered models
            models = list(ModelMeta._registry.values())
            
            # Show information about found models
            self.stdout.write(
                self.style.SUCCESS(f'Found models: {len(models)}')
            )
            
            if models:
                self.stdout.write('Registered models:')
                for model in models:
                    self.stdout.write(f'  - {model.__name__} ({model.get_table_name()})')
            else:
                self.stdout.write('  (no registered models)')
            
            if not models and not empty:
                if dry_run:
                    self.stdout.write(
                        self.style.WARNING('No models for migration creation')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING('No models for migration creation. Use --empty to create empty migration.')
                    )
                return
            
            # Check which tables already exist in the database
            existing_tables = self._get_existing_tables()
            self.stdout.write(f'Existing tables in DB: {len(existing_tables)}')
            if existing_tables:
                self.stdout.write('  - ' + '\n  - '.join(existing_tables))
            
            # Determine which tables need to be created
            tables_to_create = []
            for model in models:
                table_name = model.get_table_name()
                if table_name not in existing_tables:
                    tables_to_create.append(model)
            
            self.stdout.write(f'Tables to create: {len(tables_to_create)}')
            if tables_to_create:
                self.stdout.write('  - ' + '\n  - '.join([model.get_table_name() for model in tables_to_create]))
            
            if not tables_to_create and not empty and not force:
                if dry_run:
                    self.stdout.write(
                        self.style.SUCCESS('All tables already exist in the database')
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS('All tables already exist in the database. Migration not created.')
                    )
                return
            
            if dry_run:
                self.stdout.write(
                    self.style.SUCCESS(f'Migration will be created: {message}')
                )
                if tables_to_create:
                    self.stdout.write('Changes:')
                    for model in tables_to_create:
                        self.stdout.write(f'  - Create table: {model.get_table_name()}')
                elif empty:
                    self.stdout.write('  - Empty migration')
                return
            
            # Create migration
            if empty:
                result = migration_manager.create_migration(message, [])
            else:
                result = migration_manager.create_migration(message, tables_to_create)
            
            if result:
                # Check if migration is empty (only if not --empty)
                if not empty and self._is_migration_empty(result):
                    self.stdout.write(
                        self.style.WARNING('Migration not created (no changes)')
                    )
                    # Remove empty migration
                    self._remove_empty_migration(result)
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f'Migration created: {message}')
                    )
                    if tables_to_create:
                        self.stdout.write('Created tables:')
                        for model in tables_to_create:
                            self.stdout.write(f'  - {model.get_table_name()}')
                    elif empty:
                        self.stdout.write('  - Empty migration')
            else:
                self.stdout.write(
                    self.style.WARNING('Migration not created (no changes)')
                )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating migration: {e}')
            )
            sys.exit(1)
    
    def _get_existing_tables(self):
        """Gets a list of existing tables in the database"""
        try:
            if hasattr(db, 'engine') and db.engine:
                # For SQLAlchemy
                with db.engine.connect() as connection:
                    if db.engine.dialect.name == 'sqlite':
                        result = connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    elif db.engine.dialect.name == 'postgresql':
                        result = connection.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")
                    elif db.engine.dialect.name == 'mysql':
                        result = connection.execute("SHOW TABLES")
                    else:
                        # For other databases use general approach
                        result = connection.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
                    
                    tables = [row[0] for row in result.fetchall()]
                    return tables
            return []
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Warning: failed to get table list: {e}')
            )
            return []
    
    def _import_all_models(self):
        """Imports all models for registration in ModelMeta"""
        try:
            # Import models from contrib
            import raystack.contrib.auth.users.models
            import raystack.contrib.auth.groups.models
            import raystack.contrib.admin.models
            
            # Import models from project apps
            try:
                import apps.home.models
            except ImportError:
                pass
                
        except ImportError as e:
            self.stdout.write(
                self.style.WARNING(f'Warning: failed to import some models: {e}')
            )
    
    def _get_latest_migration_file(self):
        """Gets the path to the latest created migration file"""
        try:
            versions_dir = Path('migrations/versions')
            if versions_dir.exists():
                migration_files = list(versions_dir.glob('*.py'))
                if migration_files:
                    # Return the newest file
                    return str(max(migration_files, key=lambda x: x.stat().st_mtime))
        except:
            pass
        return None
    
    def _is_migration_empty(self, migration_file):
        """Checks if the migration is empty"""
        try:
            with open(migration_file, 'r') as f:
                content = f.read()
                # Migration is considered empty if it has no SQL commands
                # Look for SQL commands in upgrade function
                if 'op.execute(' in content:
                    return False
                # If there's only pass or empty functions, consider it empty
                if 'pass' in content and 'def upgrade():' in content and 'def downgrade():' in content:
                    return True
                return False
        except:
            return False
    
    def _remove_empty_migration(self, migration_file):
        """Removes empty migration"""
        try:
            os.remove(migration_file)
        except:
            pass 