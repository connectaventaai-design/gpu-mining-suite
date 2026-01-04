"""
Database Management Module
Handles SQLite database operations for historical data
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DB_PATH = os.path.join(DB_DIR, 'mining.db')

class Database:
    def __init__(self):
        self.db_path = DB_PATH
        self.init_database()
    
    def get_connection(self):
        """Get a database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # GPU stats history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gpu_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                gpu_id INTEGER,
                temperature REAL,
                fan_speed INTEGER,
                power_draw REAL,
                gpu_utilization INTEGER,
                memory_used INTEGER,
                memory_total INTEGER,
                core_clock INTEGER,
                memory_clock INTEGER
            )
        ''')
        
        # Mining stats history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mining_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                coin TEXT,
                hashrate REAL,
                accepted_shares INTEGER,
                rejected_shares INTEGER,
                pool TEXT
            )
        ''')
        
        # Earnings history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS earnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                coin TEXT,
                amount REAL,
                usd_value REAL,
                session_id TEXT
            )
        ''')
        
        # Mining sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                coin TEXT,
                start_time DATETIME,
                end_time DATETIME,
                total_hashrate REAL,
                total_shares INTEGER,
                status TEXT
            )
        ''')
        
        # Events/Alerts log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT,
                severity TEXT,
                message TEXT,
                details TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_gpu_stats(self, gpu_id: int, stats: Dict[str, Any]):
        """Add GPU statistics entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO gpu_stats 
            (gpu_id, temperature, fan_speed, power_draw, gpu_utilization, 
             memory_used, memory_total, core_clock, memory_clock)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            gpu_id,
            stats.get('temperature', 0),
            stats.get('fan_speed', 0),
            stats.get('power_draw', 0),
            stats.get('gpu_utilization', 0),
            stats.get('memory_used', 0),
            stats.get('memory_total', 0),
            stats.get('core_clock', 0),
            stats.get('memory_clock', 0)
        ))
        
        conn.commit()
        conn.close()
    
    def add_mining_stats(self, coin: str, hashrate: float, accepted: int, rejected: int, pool: str):
        """Add mining statistics entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO mining_stats (coin, hashrate, accepted_shares, rejected_shares, pool)
            VALUES (?, ?, ?, ?, ?)
        ''', (coin, hashrate, accepted, rejected, pool))
        
        conn.commit()
        conn.close()
    
    def add_earnings(self, coin: str, amount: float, usd_value: float, session_id: str):
        """Add earnings entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO earnings (coin, amount, usd_value, session_id)
            VALUES (?, ?, ?, ?)
        ''', (coin, amount, usd_value, session_id))
        
        conn.commit()
        conn.close()
    
    def add_event(self, event_type: str, severity: str, message: str, details: str = ""):
        """Add event/alert entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO events (event_type, severity, message, details)
            VALUES (?, ?, ?, ?)
        ''', (event_type, severity, message, details))
        
        conn.commit()
        conn.close()
    
    def get_gpu_history(self, hours: int = 24, gpu_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get GPU statistics history"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        since = datetime.now() - timedelta(hours=hours)
        
        if gpu_id is not None:
            cursor.execute('''
                SELECT * FROM gpu_stats 
                WHERE timestamp > ? AND gpu_id = ?
                ORDER BY timestamp DESC
            ''', (since, gpu_id))
        else:
            cursor.execute('''
                SELECT * FROM gpu_stats 
                WHERE timestamp > ?
                ORDER BY timestamp DESC
            ''', (since,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_mining_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get mining statistics history"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        since = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT * FROM mining_stats 
            WHERE timestamp > ?
            ORDER BY timestamp DESC
        ''', (since,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_earnings_summary(self, period: str = 'today') -> Dict[str, Any]:
        """Get earnings summary for a period"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if period == 'today':
            since = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            since = datetime.now() - timedelta(days=7)
        elif period == 'month':
            since = datetime.now() - timedelta(days=30)
        else:
            since = datetime.now() - timedelta(days=1)
        
        cursor.execute('''
            SELECT coin, SUM(amount) as total_amount, SUM(usd_value) as total_usd
            FROM earnings
            WHERE timestamp > ?
            GROUP BY coin
        ''', (since,))
        
        rows = cursor.fetchall()
        conn.close()
        
        result = {
            'period': period,
            'coins': {},
            'total_usd': 0
        }
        
        for row in rows:
            coin, amount, usd = row
            result['coins'][coin] = {
                'amount': amount,
                'usd_value': usd
            }
            result['total_usd'] += usd or 0
        
        return result
    
    def cleanup_old_data(self, days: int = 30):
        """Remove data older than specified days"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cutoff = datetime.now() - timedelta(days=days)
        
        cursor.execute('DELETE FROM gpu_stats WHERE timestamp < ?', (cutoff,))
        cursor.execute('DELETE FROM mining_stats WHERE timestamp < ?', (cutoff,))
        cursor.execute('DELETE FROM events WHERE timestamp < ?', (cutoff,))
        
        conn.commit()
        conn.close()

# Global database instance
db = Database()
