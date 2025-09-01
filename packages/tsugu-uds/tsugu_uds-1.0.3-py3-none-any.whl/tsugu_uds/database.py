"""Modern database management for Tsugu User Data Server."""

import sqlite3
import json
from typing import Optional, Dict, Any, List
from pathlib import Path
from loguru import logger
from contextlib import contextmanager


class DatabaseManager:
    """Modern SQLite database manager with context management."""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self._conn: Optional[sqlite3.Connection] = None
        self.init_db()
    
    def init_db(self) -> None:
        """Initialize the database and create tables if they don't exist."""
        try:
            self._conn = sqlite3.connect(
                str(self.db_path), 
                check_same_thread=False,
                isolation_level=None  # Autocommit mode
            )
            # Enable foreign keys
            self._conn.execute("PRAGMA foreign_keys = ON")
            logger.success(f"Database connected successfully: {self.db_path}")
            
            self._create_tables()
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        if not self._conn:
            raise RuntimeError("Database connection not established")
        cursor = self._conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                main_server INTEGER DEFAULT 3,
                displayed_server_list TEXT DEFAULT '[3, 0]',
                share_room_number INTEGER DEFAULT 1,
                user_player_index INTEGER DEFAULT 0,
                user_player_list TEXT DEFAULT '[]',
                UNIQUE(user_id, platform)
            )
        ''')
        
        logger.info("Database tables created/verified successfully")
    
    def migrate_v2_to_v3(self, source_db_path: str) -> bool:
        """Migrate from v2 database schema to v3 schema."""
        try:
            # Connect to source database
            source_conn = sqlite3.connect(source_db_path)
            source_cursor = source_conn.cursor()
            
            # Get data from source
            source_cursor.execute('''
                SELECT user_id, platform, main_server, displayed_server_list, 
                       share_room_number, user_player_index, user_player_list
                FROM users 
                WHERE user_id IS NOT NULL AND platform IS NOT NULL
            ''')
            source_data = source_cursor.fetchall()
            
            logger.info(f"Found {len(source_data)} records to migrate")
            
            # Clear current database and recreate
            if not self._conn:
                raise RuntimeError("Database connection not established")
            cursor = self._conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS users")
            self._create_tables()
            
            # Batch insert data
            migrated_count = 0
            batch_size = 1000
            
            for i in range(0, len(source_data), batch_size):
                batch = source_data[i:i + batch_size]
                try:
                    cursor.executemany('''
                        INSERT OR IGNORE INTO users (user_id, platform, main_server, displayed_server_list, 
                                         share_room_number, user_player_index, user_player_list)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', batch)
                    migrated_count += cursor.rowcount
                    if i % 5000 == 0:
                        logger.info(f"Migrated {i}/{len(source_data)} records")
                except sqlite3.Error as e:
                    logger.warning(f"Error in batch {i}: {e}")
            
            if not self._conn:
                raise RuntimeError("Database connection not established")
            self._conn.commit()
            source_conn.close()
            
            logger.success(f"Migration completed: {migrated_count} records migrated")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            return False
    
    @contextmanager
    def get_cursor(self):
        """Get a database cursor with automatic transaction management."""
        if not self._conn:
            raise RuntimeError("Database not connected")
        
        cursor = self._conn.cursor()
        try:
            yield cursor
        except Exception:
            self._conn.rollback()
            raise
        else:
            self._conn.commit()
        finally:
            cursor.close()
    
    def get_user_data(self, platform: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user data from database."""
        with self.get_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE user_id = ? AND platform = ?", 
                (user_id, platform)
            )
            row = cursor.fetchone()
            
            if row:
                return {
                    "id": row[0],
                    "userId": row[1],
                    "platform": row[2],
                    "mainServer": row[3],
                    "displayedServerList": json.loads(row[4]) if row[4] else [3, 0],
                    "shareRoomNumber": bool(row[5]),
                    "userPlayerIndex": row[6],
                    "userPlayerList": json.loads(row[7]) if row[7] else [],
                }
            return None
    
    def create_user(self, platform: str, user_id: str, **kwargs) -> Dict[str, Any]:
        """Create a new user with default values."""
        defaults = {
            "main_server": 3,
            "displayed_server_list": json.dumps([3, 0]),
            "share_room_number": 1,
            "user_player_index": 0,
            "user_player_list": json.dumps([]),
        }
        defaults.update(kwargs)
        
        with self.get_cursor() as cursor:
            cursor.execute('''
                INSERT INTO users (user_id, platform, main_server, displayed_server_list, 
                                 share_room_number, user_player_index, user_player_list)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, platform, defaults["main_server"], 
                defaults["displayed_server_list"], defaults["share_room_number"],
                defaults["user_player_index"], defaults["user_player_list"]
            ))
            
            logger.info(f"Created new user: {user_id} on {platform}")
            
        # Get the created user data
        user_data = self.get_user_data(platform, user_id)
        if not user_data:
            raise RuntimeError(f"Failed to create user: {user_id} on {platform}")
        return user_data
    
    def update_user(self, platform: str, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user data."""
        if not updates:
            return False
        
        # Map field names to database columns
        field_mapping = {
            "mainServer": "main_server",
            "displayedServerList": "displayed_server_list",
            "shareRoomNumber": "share_room_number",
            "userPlayerIndex": "user_player_index",
            "userPlayerList": "user_player_list",
        }
        
        update_clauses = []
        params = []
        
        for field, value in updates.items():
            db_field = field_mapping.get(field, field)
            if db_field in ["displayed_server_list", "user_player_list"]:
                value = json.dumps(value)
            elif db_field == "share_room_number":
                value = 1 if value else 0
            
            update_clauses.append(f"{db_field} = ?")
            params.append(value)
        
        params.extend([user_id, platform])
        
        with self.get_cursor() as cursor:
            cursor.execute(
                f"UPDATE users SET {', '.join(update_clauses)} WHERE user_id = ? AND platform = ?",
                params
            )
            
            if cursor.rowcount > 0:
                logger.info(f"Updated user: {user_id} on {platform}")
                return True
            return False
    
    def list_users(self, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all users, optionally filtered by platform."""
        with self.get_cursor() as cursor:
            if platform:
                cursor.execute("SELECT * FROM users WHERE platform = ? ORDER BY id DESC", (platform,))
            else:
                cursor.execute("SELECT * FROM users ORDER BY id DESC")
            
            users = []
            for row in cursor.fetchall():
                user_dict = {
                    "id": row[0],
                    "userId": row[1],
                    "platform": row[2],
                    "mainServer": row[3],
                    "displayedServerList": json.loads(row[4]) if row[4] else [3, 0],
                    "shareRoomNumber": bool(row[5]),
                    "userPlayerIndex": row[6],
                    "userPlayerList": json.loads(row[7]) if row[7] else [],
                }
                users.append(user_dict)
            return users
    
    def delete_user(self, platform: str, user_id: str) -> bool:
        """Delete a user."""
        with self.get_cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE user_id = ? AND platform = ?", (user_id, platform))
            
            if cursor.rowcount > 0:
                logger.info(f"Deleted user: {user_id} on {platform}")
                return True
            return False
    
    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
            logger.info("Database connection closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Global verification code cache
verify_code_cache: Dict[str, Any] = {}
