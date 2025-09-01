import os
import shutil
import logging
from datetime import datetime

# Use .familyai directory for all storage
_USER_DIR = os.path.expanduser('~/.familyai')
BACKUP_DIR = os.path.join(_USER_DIR, 'backup')
LOG_FILE = os.path.join(_USER_DIR, 'logs', 'familycli.log')

# Setup logging
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def backup_database(db_path=None):
    if db_path is None:
        db_path = os.path.join(_USER_DIR, 'familycli.db')

    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(BACKUP_DIR, f'familycli_{timestamp}.db')
    try:
        shutil.copy2(db_path, backup_path)
        logging.info(f'Database backed up to {backup_path}')
        notify_user(f'Backup successful: {backup_path}')
    except Exception as e:
        log_event(f'Backup failed: {e}')
        notify_user(f'Backup failed: {e}')
    return backup_path

def restore_database(backup_path, db_path=None):
    if db_path is None:
        db_path = os.path.join(_USER_DIR, 'familycli.db')
    try:
        shutil.copy2(backup_path, db_path)
        logging.info(f'Database restored from {backup_path}')
        notify_user(f'Restore successful: {db_path}')
    except Exception as e:
        log_event(f'Restore failed: {e}')
        notify_user(f'Restore failed: {e}')

def log_event(event: str):
    logging.info(event)

def notify_user(message: str):
    """Production-grade user notification system."""
    try:
        # Log the notification
        logging.info(f'Notification: {message}')

        # Production notification methods
        # 1. CLI notification (immediate)
        from rich.console import Console
        console = Console()
        console.print(f"[bold blue]ℹ️  {message}[/bold blue]")

        # 2. File-based notification for persistence
        notification_file = os.path.join(_USER_DIR, 'logs', 'notifications.log')
        os.makedirs(os.path.dirname(notification_file), exist_ok=True)
        with open(notification_file, 'a', encoding='utf-8') as f:
            timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{timestamp}] {message}\n")

        # 3. Future: Email notifications could be added here
        # if email_config_enabled():
        #     send_email_notification(message)

    except Exception as e:
        # Fallback to basic logging if notification fails
        logging.error(f'Notification failed: {e}')
        print(f'[NOTIFY] {message}')  # Minimal fallback
