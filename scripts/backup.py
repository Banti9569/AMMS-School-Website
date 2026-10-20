"""
Al Majid Mission School - Automated Database & Assets Backup Utility
Hazipur, West Bengal 731245

Usage:
  python scripts/backup.py          -> Creates a timestamped backup of database
  python scripts/backup.py list     -> Lists all existing backup files
"""
import os
import shutil
import sys
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_FILE = os.path.join(BASE_DIR, 'database', 'school.db')
BACKUP_DIR = os.path.join(BASE_DIR, 'database', 'backups')

def create_backup():
    if not os.path.exists(DB_FILE):
        print(f"[ERROR] Database file not found at: {DB_FILE}")
        return False

    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    timestamped_file = os.path.join(BACKUP_DIR, f"school_db_{timestamp}.db")
    latest_file = os.path.join(BACKUP_DIR, "school_db_backup.db")

    # Make timestamped copy
    shutil.copy2(DB_FILE, timestamped_file)
    # Update latest pointer
    shutil.copy2(DB_FILE, latest_file)

    size_kb = os.path.getsize(timestamped_file) / 1024
    print("=" * 60)
    print("  DATABASE BACKUP SUCCESSFUL")
    print(f"  Source:      {DB_FILE}")
    print(f"  Backup File: {timestamped_file}")
    print(f"  Size:        {size_kb:.2f} KB")
    print("=" * 60)
    return True

def list_backups():
    if not os.path.exists(BACKUP_DIR):
        print("No backups directory found.")
        return

    files = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')]
    if not files:
        print("No backup files found.")
        return

    print("=" * 60)
    print("  EXISTING DATABASE BACKUPS")
    print("=" * 60)
    for f in sorted(files, reverse=True):
        full_path = os.path.join(BACKUP_DIR, f)
        size_kb = os.path.getsize(full_path) / 1024
        mtime = datetime.fromtimestamp(os.path.getmtime(full_path)).strftime('%Y-%m-%d %H:%M:%S')
        print(f"  - {f:<30} ({size_kb:>6.1f} KB) - {mtime}")
    print("=" * 60)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'list':
        list_backups()
    else:
        create_backup()
