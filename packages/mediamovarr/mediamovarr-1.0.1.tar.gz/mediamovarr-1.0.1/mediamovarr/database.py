"""SQLite database management for MediaMovarr."""

import json
import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MediaMovarrDB:
    """SQLite database manager for MediaMovarr."""

    def __init__(self, db_path: str = "mediamovarr.db"):
        """
        Initialize database connection and create tables.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.connection = None
        self._init_database()

    def _init_database(self):
        """Initialize database connection and create tables if they don't exist."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable dict-like access to rows

            # Create tables
            self._create_tables()

            logger.debug(f"Database initialized: {self.db_path}")

        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}")
            self.connection = None

    def _create_tables(self):
        """Create database tables if they don't exist."""
        if not self.connection:
            return

        cursor = self.connection.cursor()

        # TMDb cache table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tmdb_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cache_key TEXT UNIQUE NOT NULL,
                search_type TEXT NOT NULL,  -- 'movie' or 'tv'
                title TEXT NOT NULL,
                year INTEGER,
                result_data TEXT,  -- JSON string of result or NULL if not found
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # User exclusions table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_exclusions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                folder_path TEXT UNIQUE NOT NULL,
                folder_name TEXT NOT NULL,
                media_type TEXT,
                confidence REAL,
                excluded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reason TEXT  -- Optional user-provided reason
            )
        """
        )

        # Processing history table (for tracking what was moved)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS processing_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                folder_path TEXT NOT NULL,
                folder_name TEXT NOT NULL,
                media_type TEXT NOT NULL,
                confidence REAL NOT NULL,
                destination_path TEXT,
                action TEXT NOT NULL,  -- 'moved', 'skipped', 'excluded', 'error'
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details TEXT  -- JSON string with additional details
            )
        """
        )

        # Create indexes for better performance
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_tmdb_cache_key ON tmdb_cache(cache_key)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_user_exclusions_path ON user_exclusions(folder_path)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_processing_history_path ON processing_history(folder_path)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_processing_history_date ON processing_history(processed_at)"
        )

        self.connection.commit()
        logger.debug("Database tables created/verified")

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    # TMDb Cache Methods

    def get_tmdb_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached TMDb result.

        Args:
            cache_key: Cache key (format: "type:title:year")

        Returns:
            Cached result or None if not found
        """
        if not self.connection:
            return None

        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT result_data FROM tmdb_cache
            WHERE cache_key = ?
        """,
            (cache_key,),
        )

        row = cursor.fetchone()
        if row:
            # Update last accessed time
            cursor.execute(
                """
                UPDATE tmdb_cache
                SET last_accessed = CURRENT_TIMESTAMP
                WHERE cache_key = ?
            """,
                (cache_key,),
            )
            self.connection.commit()

            # Return parsed JSON or None
            result_data = row[0]
            if result_data:
                try:
                    return json.loads(result_data)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON in cache for key: {cache_key}")
                    return None
            else:
                # Cached "not found" result
                return None

        return None

    def set_tmdb_cache(
        self,
        cache_key: str,
        search_type: str,
        title: str,
        year: Optional[int],
        result: Optional[Dict[str, Any]],
    ):
        """
        Store TMDb result in cache.

        Args:
            cache_key: Cache key (format: "type:title:year")
            search_type: 'movie' or 'tv'
            title: Search title
            year: Search year (optional)
            result: TMDb result or None if not found
        """
        if not self.connection:
            return

        result_json = json.dumps(result) if result else None

        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO tmdb_cache
            (cache_key, search_type, title, year, result_data, created_at, last_accessed)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """,
            (cache_key, search_type, title, year, result_json),
        )

        self.connection.commit()
        logger.debug(f"Cached TMDb result: {cache_key}")

    def clean_old_tmdb_cache(self, days: int = 30):
        """
        Remove TMDb cache entries older than specified days.

        Args:
            days: Number of days to keep cache entries
        """
        if not self.connection:
            return

        cursor = self.connection.cursor()
        cursor.execute(
            f"""
            DELETE FROM tmdb_cache
            WHERE last_accessed < datetime('now', '-{days} days')
        """
        )

        deleted_count = cursor.rowcount
        self.connection.commit()

        if deleted_count > 0:
            logger.info(f"Cleaned {deleted_count} old TMDb cache entries")

    # User Exclusions Methods

    def is_excluded(self, folder_path: str) -> bool:
        """
        Check if a folder path is in user exclusions.

        Args:
            folder_path: Absolute path to folder

        Returns:
            True if folder is excluded
        """
        if not self.connection:
            return False

        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT 1 FROM user_exclusions WHERE folder_path = ?", (str(folder_path),)
        )
        return cursor.fetchone() is not None

    def add_exclusion(
        self,
        folder_path: str,
        folder_name: str,
        media_type: Optional[str] = None,
        confidence: Optional[float] = None,
        reason: Optional[str] = None,
    ):
        """
        Add folder to user exclusions.

        Args:
            folder_path: Absolute path to folder
            folder_name: Folder name for display
            media_type: Detected media type (optional)
            confidence: Classification confidence (optional)
            reason: User-provided reason (optional)
        """
        if not self.connection:
            return

        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO user_exclusions
            (folder_path, folder_name, media_type, confidence, excluded_at, reason)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
        """,
            (str(folder_path), folder_name, media_type, confidence, reason),
        )

        self.connection.commit()
        logger.info(f"Added exclusion: {folder_name}")

    def remove_exclusion(self, folder_path: str):
        """
        Remove folder from user exclusions.

        Args:
            folder_path: Absolute path to folder
        """
        if not self.connection:
            return

        cursor = self.connection.cursor()
        cursor.execute(
            "DELETE FROM user_exclusions WHERE folder_path = ?", (str(folder_path),)
        )

        if cursor.rowcount > 0:
            self.connection.commit()
            logger.info(f"Removed exclusion: {folder_path}")

    def get_exclusions(self) -> List[Dict[str, Any]]:
        """
        Get all user exclusions.

        Returns:
            List of exclusion records
        """
        if not self.connection:
            return []

        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT folder_path, folder_name, media_type, confidence, excluded_at, reason
            FROM user_exclusions
            ORDER BY excluded_at DESC
        """
        )

        return [dict(row) for row in cursor.fetchall()]

    # Processing History Methods

    def add_processing_record(
        self,
        folder_path: str,
        folder_name: str,
        media_type: str,
        confidence: float,
        destination_path: Optional[str] = None,
        action: str = "moved",
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Add processing history record.

        Args:
            folder_path: Source folder path
            folder_name: Folder name
            media_type: Media type
            confidence: Classification confidence
            destination_path: Where file was moved (if applicable)
            action: Action taken ('moved', 'skipped', 'excluded', 'error')
            details: Additional details as dict
        """
        if not self.connection:
            return

        details_json = json.dumps(details) if details else None

        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO processing_history
            (folder_path, folder_name, media_type, confidence, destination_path, action, processed_at, details)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
        """,
            (
                str(folder_path),
                folder_name,
                media_type,
                confidence,
                destination_path,
                action,
                details_json,
            ),
        )

        self.connection.commit()

    def get_processing_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent processing history.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of processing records
        """
        if not self.connection:
            return []

        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT folder_path, folder_name, media_type, confidence, destination_path,
                   action, processed_at, details
            FROM processing_history
            ORDER BY processed_at DESC
            LIMIT ?
        """,
            (limit,),
        )

        records = []
        for row in cursor.fetchall():
            record = dict(row)
            if record["details"]:
                try:
                    record["details"] = json.loads(record["details"])
                except json.JSONDecodeError:
                    record["details"] = {}
            records.append(record)

        return records

    def cleanup_old_history(self, days: int = 90):
        """
        Remove processing history older than specified days.

        Args:
            days: Number of days to keep history
        """
        if not self.connection:
            return

        cursor = self.connection.cursor()
        cursor.execute(
            f"""
            DELETE FROM processing_history
            WHERE processed_at < datetime('now', '-{days} days')
        """
        )

        deleted_count = cursor.rowcount
        self.connection.commit()

        if deleted_count > 0:
            logger.info(f"Cleaned {deleted_count} old processing history records")


def get_database(db_path: str = "mediamovarr.db") -> MediaMovarrDB:
    """
    Get database instance.

    Args:
        db_path: Path to database file

    Returns:
        MediaMovarrDB instance
    """
    return MediaMovarrDB(db_path)
