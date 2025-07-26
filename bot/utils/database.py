import sqlite3
import os
from datetime import datetime
import threading

class Database:
    def __init__(self, db_path="bot_data.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Commands log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS command_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command_name TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Events log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS event_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    guild_id INTEGER,
                    description TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Bot settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bot_settings (
                    guild_id INTEGER PRIMARY KEY,
                    log_channel_id INTEGER,
                    allowed_channels TEXT,
                    language TEXT DEFAULT 'es'
                )
            ''')
            
            # Teams table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS teams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    team_name TEXT NOT NULL,
                    points INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0,
                    losses INTEGER DEFAULT 0,
                    draws INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Matches results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS match_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    team1_name TEXT NOT NULL,
                    team2_name TEXT NOT NULL,
                    team1_score INTEGER,
                    team2_score INTEGER,
                    winner TEXT,
                    match_date DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tournaments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tournaments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    tournament_name TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    start_date DATETIME,
                    end_date DATETIME,
                    created_by INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Scheduled announcements table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scheduled_announcements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    schedule_time DATETIME NOT NULL,
                    is_sent BOOLEAN DEFAULT FALSE,
                    created_by INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Member activity table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS member_activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    activity_type TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
    
    def log_command(self, command_name, user_id, guild_id=None):
        """Log a command usage"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO command_logs (command_name, user_id, guild_id)
                VALUES (?, ?, ?)
            ''', (command_name, user_id, guild_id))
            
            conn.commit()
            conn.close()
    
    def log_event(self, event_type, guild_id=None, description=None):
        """Log a bot event"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO event_logs (event_type, guild_id, description)
                VALUES (?, ?, ?)
            ''', (event_type, guild_id, description))
            
            conn.commit()
            conn.close()
    
    def get_command_stats(self, guild_id=None, limit=10):
        """Get command usage statistics"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if guild_id:
                cursor.execute('''
                    SELECT command_name, COUNT(*) as usage_count
                    FROM command_logs
                    WHERE guild_id = ?
                    GROUP BY command_name
                    ORDER BY usage_count DESC
                    LIMIT ?
                ''', (guild_id, limit))
            else:
                cursor.execute('''
                    SELECT command_name, COUNT(*) as usage_count
                    FROM command_logs
                    GROUP BY command_name
                    ORDER BY usage_count DESC
                    LIMIT ?
                ''', (limit,))
            
            results = cursor.fetchall()
            conn.close()
            return results
    
    def get_recent_events(self, guild_id=None, limit=10):
        """Get recent bot events"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if guild_id:
                cursor.execute('''
                    SELECT event_type, description, timestamp
                    FROM event_logs
                    WHERE guild_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (guild_id, limit))
            else:
                cursor.execute('''
                    SELECT event_type, description, timestamp
                    FROM event_logs
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
            
            results = cursor.fetchall()
            conn.close()
            return results
    
    def save_guild_settings(self, guild_id, log_channel_id=None, allowed_channels=None, language=None):
        """Save guild-specific settings"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO bot_settings 
                (guild_id, log_channel_id, allowed_channels, language)
                VALUES (?, ?, ?, ?)
            ''', (guild_id, log_channel_id, allowed_channels, language))
            
            conn.commit()
            conn.close()
    
    def get_guild_settings(self, guild_id):
        """Get guild-specific settings"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT log_channel_id, allowed_channels, language
                FROM bot_settings
                WHERE guild_id = ?
            ''', (guild_id,))
            
            result = cursor.fetchone()
            conn.close()
            return result
    
    # Team management methods
    def add_team(self, guild_id, team_name):
        """Add a new team"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO teams (guild_id, team_name)
                VALUES (?, ?)
            ''', (guild_id, team_name))
            
            conn.commit()
            conn.close()
    
    def get_team_stats(self, guild_id, team_name=None):
        """Get team statistics"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if team_name:
                cursor.execute('''
                    SELECT team_name, points, wins, losses, draws
                    FROM teams
                    WHERE guild_id = ? AND team_name = ?
                ''', (guild_id, team_name))
            else:
                cursor.execute('''
                    SELECT team_name, points, wins, losses, draws
                    FROM teams
                    WHERE guild_id = ?
                    ORDER BY points DESC, wins DESC
                ''', (guild_id,))
            
            results = cursor.fetchall()
            conn.close()
            return results
    
    def update_team_stats(self, guild_id, team_name, points_change, win=False, loss=False, draw=False):
        """Update team statistics"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if team exists, if not create it
            cursor.execute('SELECT id FROM teams WHERE guild_id = ? AND team_name = ?', (guild_id, team_name))
            if not cursor.fetchone():
                cursor.execute('INSERT INTO teams (guild_id, team_name) VALUES (?, ?)', (guild_id, team_name))
            
            # Update stats
            update_query = 'UPDATE teams SET points = points + ?'
            params = [points_change]
            
            if win:
                update_query += ', wins = wins + 1'
            elif loss:
                update_query += ', losses = losses + 1'
            elif draw:
                update_query += ', draws = draws + 1'
            
            update_query += ' WHERE guild_id = ? AND team_name = ?'
            params.extend([guild_id, team_name])
            
            cursor.execute(update_query, params)
            conn.commit()
            conn.close()
    
    # Match results methods
    def save_match_result(self, match_id, guild_id, team1_name, team2_name, team1_score, team2_score, match_date):
        """Save match result"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Determine winner
            if team1_score > team2_score:
                winner = team1_name
            elif team2_score > team1_score:
                winner = team2_name
            else:
                winner = 'draw'
            
            cursor.execute('''
                INSERT INTO match_results 
                (match_id, guild_id, team1_name, team2_name, team1_score, team2_score, winner, match_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (match_id, guild_id, team1_name, team2_name, team1_score, team2_score, winner, match_date))
            
            conn.commit()
            conn.close()
            
            # Update team stats
            if winner == team1_name:
                self.update_team_stats(guild_id, team1_name, 3, win=True)
                self.update_team_stats(guild_id, team2_name, 0, loss=True)
            elif winner == team2_name:
                self.update_team_stats(guild_id, team2_name, 3, win=True)
                self.update_team_stats(guild_id, team1_name, 0, loss=True)
            else:  # draw
                self.update_team_stats(guild_id, team1_name, 1, draw=True)
                self.update_team_stats(guild_id, team2_name, 1, draw=True)
    
    def get_match_results(self, guild_id, limit=10):
        """Get recent match results"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT team1_name, team2_name, team1_score, team2_score, winner, match_date
                FROM match_results
                WHERE guild_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (guild_id, limit))
            
            results = cursor.fetchall()
            conn.close()
            return results
    
    # Tournament methods
    def create_tournament(self, guild_id, tournament_name, start_date, end_date, created_by):
        """Create a new tournament"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO tournaments (guild_id, tournament_name, start_date, end_date, created_by)
                VALUES (?, ?, ?, ?, ?)
            ''', (guild_id, tournament_name, start_date, end_date, created_by))
            
            tournament_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return tournament_id
    
    def get_tournaments(self, guild_id, status=None):
        """Get tournaments"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if status:
                cursor.execute('''
                    SELECT id, tournament_name, status, start_date, end_date
                    FROM tournaments
                    WHERE guild_id = ? AND status = ?
                    ORDER BY created_at DESC
                ''', (guild_id, status))
            else:
                cursor.execute('''
                    SELECT id, tournament_name, status, start_date, end_date
                    FROM tournaments
                    WHERE guild_id = ?
                    ORDER BY created_at DESC
                ''', (guild_id,))
            
            results = cursor.fetchall()
            conn.close()
            return results
    
    # Scheduled announcements methods
    def schedule_announcement(self, guild_id, channel_id, message, schedule_time, created_by):
        """Schedule an announcement"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO scheduled_announcements 
                (guild_id, channel_id, message, schedule_time, created_by)
                VALUES (?, ?, ?, ?, ?)
            ''', (guild_id, channel_id, message, schedule_time, created_by))
            
            announcement_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return announcement_id
    
    def get_pending_announcements(self):
        """Get pending announcements"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, guild_id, channel_id, message, schedule_time
                FROM scheduled_announcements
                WHERE is_sent = FALSE AND schedule_time <= datetime('now')
            ''')
            
            results = cursor.fetchall()
            conn.close()
            return results
    
    def mark_announcement_sent(self, announcement_id):
        """Mark announcement as sent"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE scheduled_announcements
                SET is_sent = TRUE
                WHERE id = ?
            ''', (announcement_id,))
            
            conn.commit()
            conn.close()
    
    # Member activity methods
    def log_member_activity(self, guild_id, user_id, activity_type):
        """Log member activity"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO member_activity (guild_id, user_id, activity_type)
                VALUES (?, ?, ?)
            ''', (guild_id, user_id, activity_type))
            
            conn.commit()
            conn.close()
