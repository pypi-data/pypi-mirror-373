from raystack.core.management.base import BaseCommand
import sys


class Command(BaseCommand):
    help = "Applies migrations to the database"

    def add_arguments(self, parser):
        parser.add_argument(
            '--revision', '-r',
            type=str,
            default='head',
            help='Revision to apply (default "head")'
        )
        parser.add_argument(
            '--fake',
            action='store_true',
            help='Mark migration as applied without execution'
        )
        parser.add_argument(
            '--show-plan',
            action='store_true',
            help='Show migration plan without applying'
        )

    def handle(self, *args, **options):
        # Lazy imports to avoid errors when loading commands
        try:
            from raystack.core.database.migrations import migration_manager
        except ImportError as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to import database module: {e}')
            )
            return
        
        revision = options.get('revision', 'head')
        fake = options.get('fake', False)
        show_plan = options.get('show_plan', False)
        
        try:
            # Initialize migration system if needed
            migration_manager.init()
            
            # Get current revision
            current = migration_manager.current()
            self.stdout.write(
                self.style.SUCCESS(f'Current revision: {current or "none"}')
            )
            
            if show_plan:
                # Show migration plan
                self.stdout.write(
                    self.style.SUCCESS(f'Migration plan to revision: {revision}')
                )
                # Here you can add logic to show the plan
                return
            
            if fake:
                # Mark migration as applied
                migration_manager.stamp(revision)
                self.stdout.write(
                    self.style.SUCCESS(f'Migration marked as applied: {revision}')
                )
            else:
                # Apply migrations
                migration_manager.upgrade(revision)
                self.stdout.write(
                    self.style.SUCCESS(f'Migrations applied to revision: {revision}')
                )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error applying migrations: {e}')
            )
            sys.exit(1) 