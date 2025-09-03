import sqlite3
from typing import Any
from django.db.backends.signals import connection_created
from django.dispatch import receiver

@receiver(connection_created)
def sqlite_pragmas(sender, connection: Any, **kwargs):
    """Enable integrity constraint with sqlite."""
    if connection.vendor == 'sqlite':
        cursor = connection.cursor()
        _ = cursor.execute('PRAGMA foreign_keys = ON')
        _ = cursor.execute('PRAGMA journal_mode = WAL')
        _ = cursor.execute('PRAGMA synchronous = NORMAL')
