"""CLI command for database migration."""

import click
from pathlib import Path
from .migrations import MigrationManager
from .storage_manager import get_storage_manager
from .logger import log_info, log_error, log_warning
from . import __version__


@click.command()
@click.option('--project-path', '-p', type=click.Path(exists=True), 
              help='Path to project (defaults to current directory)')
@click.option('--target-version', '-t', type=str,
              help='Target schema version (defaults to latest)')
@click.option('--dry-run', is_flag=True,
              help='Show what would be migrated without applying changes')
@click.option('--force', is_flag=True,
              help='Force migration even if database appears corrupted')
def migrate(project_path, target_version, dry_run, force):
    """Migrate database schema to the latest version."""
    
    # Get project path
    storage_manager = get_storage_manager()
    if project_path:
        project_path = Path(project_path)
    else:
        project_path = storage_manager.get_project_from_cwd()
    
    # Get database path
    db_path = storage_manager.get_database_path(project_path)
    
    if not db_path.exists():
        log_error(f"No database found at {db_path}")
        return
    
    # Initialize migration manager
    migration_manager = MigrationManager(str(db_path))
    
    # Detect current version
    current_version = migration_manager.detect_schema_version()
    if current_version is None:
        log_warning("Could not detect database version")
        if not force:
            log_error("Use --force to migrate anyway")
            return
        current_version = '0.0.0'
    
    log_info(f"Current database version: {current_version}")
    
    # Determine target version
    if not target_version:
        # Default to package version mapping
        package_version = __version__
        parts = package_version.split('.')
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0
        
        if major >= 1 and minor >= 16:
            target_version = '1.16.0'
        elif major >= 1 and minor >= 15:
            target_version = '1.15.0'
        elif major >= 1 and minor >= 14:
            target_version = '1.14.0'
        elif major >= 1 and minor >= 6:
            target_version = '1.6.0'
        elif major >= 1 and minor >= 1:
            target_version = '1.1.0'
        else:
            target_version = '1.0.0'
    
    log_info(f"Target database version: {target_version}")
    
    # Get pending migrations
    pending = migration_manager.get_pending_migrations(current_version, target_version)
    
    if not pending:
        log_info("Database is already up to date")
        return
    
    # Show migration plan
    log_info("\nMigration plan:")
    for migration in pending:
        log_info(f"  - {migration.version}: {migration.description}")
    
    if dry_run:
        log_info("\n[DRY RUN] No changes were made")
        return
    
    # Confirm migration
    if not force:
        if not click.confirm("\nProceed with migration?"):
            log_info("Migration cancelled")
            return
    
    # Perform migration
    log_info("\nStarting migration...")
    success, message = migration_manager.migrate(target_version)
    
    if success:
        log_info(f"✅ {message}")
        
        # Clean old backups
        migration_manager.clean_old_backups(keep_last=5)
        log_info("Cleaned old backup files")
    else:
        log_error(f"❌ {message}")
        raise click.ClickException("Migration failed")


if __name__ == '__main__':
    migrate()