# Database models and operations for SafeVoice
import sqlite3
import hashlib
import base64
from datetime import datetime
from typing import Optional, List, Dict
import json

class Database:
    def __init__(self, db_path="safevoice.db"):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table with disguise key and face data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                disguise_key TEXT UNIQUE NOT NULL,
                face_encoding TEXT NOT NULL,
                gender TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Evidence vault table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                encrypted_data TEXT NOT NULL,
                filename TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Chat history (optional, encrypted)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # FIR filings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fir_filings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                case_details TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                filed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, disguise_key: str, face_encoding: str, gender: str) -> Optional[int]:
        """Create new user with disguise key and face encoding"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Hash disguise key for security
            key_hash = hashlib.sha256(disguise_key.encode()).hexdigest()
            
            cursor.execute('''
                INSERT INTO users (disguise_key, face_encoding, gender)
                VALUES (?, ?, ?)
            ''', (key_hash, face_encoding, gender))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            return None  # User already exists
    
    def verify_user(self, disguise_key: str) -> Optional[Dict]:
        """Verify user by disguise key"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        key_hash = hashlib.sha256(disguise_key.encode()).hexdigest()
        
        cursor.execute('''
            SELECT id, face_encoding, gender FROM users WHERE disguise_key = ?
        ''', (key_hash,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row['id'],
                'face_encoding': row['face_encoding'],
                'gender': row['gender']
            }
        return None
    
    def update_last_login(self, user_id: int):
        """Update last login timestamp"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
        ''', (user_id,))
        conn.commit()
        conn.close()
    
    def save_evidence(self, user_id: int, evidence_type: str, encrypted_data: str, filename: str = None):
        """Save encrypted evidence to vault"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO evidence (user_id, type, encrypted_data, filename)
            VALUES (?, ?, ?, ?)
        ''', (user_id, evidence_type, encrypted_data, filename))
        conn.commit()
        conn.close()
    
    def get_user_evidence(self, user_id: int) -> List[Dict]:
        """Get all evidence for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, type, encrypted_data, filename, timestamp
            FROM evidence WHERE user_id = ?
            ORDER BY timestamp DESC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def delete_evidence(self, evidence_id: int, user_id: int):
        """Delete evidence item"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM evidence WHERE id = ? AND user_id = ?
        ''', (evidence_id, user_id))
        conn.commit()
        conn.close()
    
    def save_chat(self, user_id: int, message: str, response: str):
        """Save chat interaction (optional)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_history (user_id, message, response)
            VALUES (?, ?, ?)
        ''', (user_id, message, response))
        conn.commit()
        conn.close()
    
    def file_fir(self, user_id: str, complainant_name: str, complainant_phone: str, 
                 complainant_address: str, accused_details: str, incident_details: str, 
                 laws_invoked: str, case_id: str) -> int:
        """File FIR online with detailed information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Combine all details into case_details JSON
        import json
        case_details = json.dumps({
            "case_id": case_id,
            "complainant_name": complainant_name,
            "complainant_phone": complainant_phone,
            "complainant_address": complainant_address,
            "accused_details": accused_details,
            "incident_details": incident_details,
            "laws_invoked": laws_invoked
        })
        
        cursor.execute('''
            INSERT INTO fir_filings (user_id, case_details)
            VALUES (?, ?)
        ''', (user_id, case_details))
        fir_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return fir_id
    
    def get_user_firs(self, user_id: int) -> List[Dict]:
        """Get all FIRs filed by user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, case_details, status, filed_at
            FROM fir_filings WHERE user_id = ?
            ORDER BY filed_at DESC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
