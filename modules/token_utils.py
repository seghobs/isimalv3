import sqlite3
import os
from curl_cffi import requests as req

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_FILE = os.path.join(BASE_DIR, 'tokens.db')

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    if 'is_active' in d: d['is_active'] = bool(d['is_active'])
    if 'is_valid' in d: d['is_valid'] = bool(d['is_valid'])
    return d

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = dict_factory
    return conn

def load_tokens():
    """Tüm tokenleri yükle - SQL veritabanından list olarak döndürür"""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM accounts")
        tokens = c.fetchall()
        conn.close()
        return tokens
    except Exception as e:
        print(f"SQLite Tokenler yükleme hatası: {e}")
        return []

def save_tokens(tokens):
    """Tüm tokenleri kaydet - SQL veritabanını günceller"""
    try:
        conn = get_connection()
        c = conn.cursor()
        
        # Eğer sözlük formatında ('accounts') geldiyse ayıkla
        if isinstance(tokens, dict) and 'accounts' in tokens:
            tokens_list = tokens['accounts']
        elif not isinstance(tokens, list):
            tokens_list = [tokens]
        else:
            tokens_list = tokens
            
        c.execute("DELETE FROM accounts")
        
        for acc in tokens_list:
            c.execute('''
                INSERT INTO accounts 
                (id, username, password, full_name, token, android_id, android_id_yeni, user_agent, login_date, last_check, is_active, is_valid, logout_reason, logout_time, added_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                acc.get('id'),
                acc.get('username'),
                acc.get('password'),
                acc.get('full_name'),
                acc.get('token'),
                acc.get('android_id', acc.get('android_id_yeni', '')),
                acc.get('android_id_yeni', acc.get('android_id', '')),
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
        conn.close()
        return True
    except Exception as e:
        print(f"SQLite Tokenler kaydetme hatası: {e}")
        return False

def get_active_token():
    """Sıradaki aktif tokeni getir"""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM accounts WHERE is_active = 1 LIMIT 1")
        token = c.fetchone()
        conn.close()
        return token
    except Exception as e:
        print(f"SQLite Aktif token getirme hatası: {e}")
        return None

def validate_token(token_data):
    """Token'ın geçerli olup olmadığını kontrol et"""
    try:
        headers = {
            'authorization': token_data.get('token', ''),
            'user-agent': token_data.get('user_agent', ''),
            'x-ig-app-id': '567067343352427',
        }
        response = req.get('https://i.instagram.com/api/v1/accounts/current_user/?edit=true', 
                          headers=headers, timeout=5, impersonate="chrome110")
        return response.status_code == 200
    except:
        return False
