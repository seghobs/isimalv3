import sqlite3
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, 'tokens.json')
DB_FILE = os.path.join(BASE_DIR, 'tokens.db')

def migrate():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        full_name TEXT,
        token TEXT,
        android_id TEXT,
        android_id_yeni TEXT,
        user_agent TEXT,
        login_date TEXT,
        last_check TEXT,
        is_active INTEGER DEFAULT 0,
        is_valid INTEGER DEFAULT 0,
        logout_reason TEXT,
        logout_time TEXT,
        added_at TEXT
    )
    ''')
    
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            accounts = []
            if isinstance(data, dict) and 'accounts' in data:
                accounts = data['accounts']
            elif isinstance(data, list):
                accounts = data
                
            for acc in accounts:
                cursor.execute('''
                    INSERT OR REPLACE INTO accounts 
                    (id, username, password, full_name, token, android_id, android_id_yeni, user_agent, login_date, last_check, is_active, is_valid, logout_reason, logout_time, added_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    acc.get('id'),
                    acc.get('username'),
                    acc.get('password'),
                    acc.get('full_name'),
                    acc.get('token'),
                    acc.get('android_id', acc.get('android_id_yeni')),
                    acc.get('android_id_yeni', acc.get('android_id')),
                    acc.get('user_agent'),
                    acc.get('login_date'),
                    acc.get('last_check'),
                    1 if acc.get('is_active') else 0,
                    1 if acc.get('is_valid') else 0,
                    acc.get('logout_reason'),
                    acc.get('logout_time'),
                    acc.get('added_at')
                ))
            conn.commit()
            print("Migration successful")
        except Exception as e:
            print(f"Error migrating: {e}")
    else:
        print("tokens.json not found, create empty db")
        
    conn.close()

if __name__ == "__main__":
    migrate()
