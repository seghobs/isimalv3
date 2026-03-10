import json
import logging
import os
import sqlite3
from flask import Blueprint, request, render_template, jsonify, session, redirect, url_for
from datetime import datetime
from curl_cffi import requests as req
from werkzeug.security import generate_password_hash, check_password_hash
from modules.token_utils import load_tokens, save_tokens, validate_token
from modules.log_in import giris_yap

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_FILE = os.path.join(BASE_DIR, 'tokens.db')
ADMIN_PASSWORD_KEY = 'admin_password_hash'


def _get_db_connection():
    return sqlite3.connect(DB_FILE)


def _ensure_admin_settings_table():
    conn = _get_db_connection()
    try:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT
            )
        ''')
        conn.commit()
    finally:
        conn.close()


def _ensure_default_admin_password():
    _ensure_admin_settings_table()
    conn = _get_db_connection()
    try:
        c = conn.cursor()
        c.execute('SELECT value FROM app_settings WHERE key = ?', (ADMIN_PASSWORD_KEY,))
        row = c.fetchone()
        if not row:
            c.execute(
                'INSERT INTO app_settings (key, value, updated_at) VALUES (?, ?, ?)',
                (ADMIN_PASSWORD_KEY, generate_password_hash('seho'), str(datetime.now()))
            )
            conn.commit()
    finally:
        conn.close()


def _verify_admin_password(raw_password):
    _ensure_admin_settings_table()
    conn = _get_db_connection()
    try:
        c = conn.cursor()
        c.execute('SELECT value FROM app_settings WHERE key = ?', (ADMIN_PASSWORD_KEY,))
        row = c.fetchone()
        if not row:
            return False
        return check_password_hash(row[0], raw_password or '')
    finally:
        conn.close()


def _set_admin_password(raw_password):
    _ensure_admin_settings_table()
    conn = _get_db_connection()
    try:
        c = conn.cursor()
        c.execute(
            '''
            INSERT INTO app_settings (key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value=excluded.value,
                updated_at=excluded.updated_at
            ''',
            (ADMIN_PASSWORD_KEY, generate_password_hash(raw_password), str(datetime.now()))
        )
        conn.commit()
    finally:
        conn.close()


_ensure_default_admin_password()

@admin_bp.route('/')
def admin_panel():
    """Admin panel sayfası - Şifre korumalı"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    return render_template('admin.html')

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    """Admin giriş sayfası"""
    if request.method == 'POST':
        password = request.form.get('password')
        if _verify_admin_password(password):
            session['admin_logged_in'] = True
            return redirect(url_for('admin.admin_panel'))
        else:
            return render_template('admin_login.html', error=True)
    return render_template('admin_login.html', error=False)

@admin_bp.route('/logout')
def admin_logout():
    """Admin çıkış"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.admin_login'))

@admin_bp.route('/get_tokens', methods=['GET'])
def get_tokens():
    """Tüm tokenleri getir"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Yetkisiz erişim'}), 401
    
    try:
        tokens = load_tokens()
        # Yeni format: accounts array, eski format: direkt array - her ikisini de destekle
        return jsonify({
            'success': True,
            'accounts': tokens,  # Yeni format için
            'tokens': tokens     # Geriye dönük uyumluluk için
        })
    except Exception as e:
        logger.exception("Admin get_tokens failed")
        return jsonify({
            'success': False,
            'message': f'Tokenler yüklenemedi: {str(e)}'
        }), 500

@admin_bp.route('/add_token', methods=['POST'])
def add_token():
    """Yeni token ekle"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Yetkisiz erişim'}), 401
    
    try:
        data = request.get_json(silent=True) or {}
        
        # Sadece token, device_id, android_id ve user_agent gerekli
        required_fields = ['token', 'device_id', 'android_id', 'user_agent']
        if not all(field in data for field in required_fields) or not data['device_id']:
            return jsonify({
                'success': False,
                'message': 'Eksik alan (token, device_id, android_id, user_agent gerekli)'
            }), 400
        
        # Token'dan kullanıcı adını çek
        try:
            headers = {
                'authorization': data['token'],
                'user-agent': data['user_agent'],
                'x-ig-app-id': '567067343352427',
                'x-ig-android-id': f"android-{data['android_id']}"
            }
            response = req.get('https://i.instagram.com/api/v1/accounts/current_user/?edit=true', 
                              headers=headers, timeout=10, impersonate="chrome110")
            
            if response.status_code != 200:
                return jsonify({
                    'success': False,
                    'message': 'Token geçersiz! Lütfen geçerli bir token girin.'
                }), 400
            
            user_data = response.json().get('user', {})
            username = user_data.get('username')
            full_name = user_data.get('full_name', '')
            
            if not username:
                return jsonify({
                    'success': False,
                    'message': 'Token geçerli ama kullanıcı adı alınamadı'
                }), 400
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Token doğrulanamadı: {str(e)}'
            }), 400
        
        tokens = load_tokens()
        
        # Aynı kullanıcı adına sahip token varsa güncelle
        existing_token_index = None
        for i, token in enumerate(tokens):
            if token['username'] == username:
                existing_token_index = i
                break
        
        new_token = {
            'username': username,
            'full_name': full_name,
            'password': data.get('password', ''),
            'token': data['token'],
            'android_id_yeni': data['android_id'],
            'device_id': data['device_id'],
            'user_agent': data['user_agent'],
            'is_active': data.get('is_active', True),
            'is_valid': True,
            'added_at': data.get('added_at', str(datetime.now()))
        }
        
        if existing_token_index is not None:
            tokens[existing_token_index] = new_token
            message = f'@{username} ({full_name}) için token güncellendi'
        else:
            tokens.append(new_token)
            message = f'@{username} ({full_name}) için token eklendi'
        
        save_tokens(tokens)
        
        return jsonify({
            'success': True,
            'message': message,
            'username': username,
            'full_name': full_name
        })
    except Exception as e:
        logger.exception("Admin add_token failed")
        return jsonify({
            'success': False,
            'message': f'Token eklenemedi: {str(e)}'
        }), 500

@admin_bp.route('/delete_token', methods=['POST'])
def delete_token():
    """Token sil"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Yetkisiz erişim'}), 401
    
    try:
        data = request.get_json(silent=True) or {}
        username = data.get('username')
        
        if not username:
            return jsonify({
                'success': False,
                'message': 'Kullanıcı adı belirtilmedi'
            }), 400
        
        tokens = load_tokens()
        tokens = [t for t in tokens if t['username'] != username]
        save_tokens(tokens)
        
        return jsonify({
            'success': True,
            'message': f'{username} için token silindi'
        })
    except Exception as e:
        logger.exception("Admin delete_token failed")
        return jsonify({
            'success': False,
            'message': f'Token silinemedi: {str(e)}'
        }), 500

@admin_bp.route('/toggle_token', methods=['POST'])
def toggle_token():
    """Token'ı aktif/pasif yap"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Yetkisiz erişim'}), 401
    
    try:
        data = request.get_json(silent=True) or {}
        username = data.get('username')
        
        if not username:
            return jsonify({
                'success': False,
                'message': 'Kullanıcı adı belirtilmedi'
            }), 400
        
        tokens = load_tokens()
        for token in tokens:
            if token['username'] == username:
                token['is_active'] = not token.get('is_active', False)
                
                # Aktif yapılıyorsa logout_reason'u temizle
                if token['is_active']:
                    token.pop('logout_reason', None)
                    token.pop('logout_time', None)
                
                save_tokens(tokens)
                status = 'aktif' if token['is_active'] else 'pasif'
                return jsonify({
                    'success': True,
                    'message': f'{username} için token {status} yapıldı',
                    'is_active': token['is_active']
                })
        
        return jsonify({
            'success': False,
            'message': 'Token bulunamadı'
        }), 404
    except Exception as e:
        logger.exception("Admin toggle_token failed")
        return jsonify({
            'success': False,
            'message': f'Token durumu değiştirilemedi: {str(e)}'
        }), 500

@admin_bp.route('/update_token', methods=['POST'])
def update_token():
    """Mevcut token'ı manuel güncelle"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Yetkisiz erişim'}), 401
    
    try:
        data = request.get_json(silent=True) or {}
        
        required_fields = ['username', 'token', 'device_id', 'android_id', 'user_agent']
        if not all(field in data for field in required_fields) or not data['device_id']:
            return jsonify({
                'success': False,
                'message': 'Eksik alan (username, token, device_id, android_id, user_agent gerekli)'
            }), 400
        
        username = data['username']
        tokens = load_tokens()
        
        # Token'ı bul ve güncelle
        token_found = False
        target_token = None
        for token in tokens:
            if token['username'] == username:
                token['token'] = data['token']
                token['android_id_yeni'] = data['android_id']
                token['device_id'] = data['device_id']
                token['user_agent'] = data['user_agent']
                
                # Yeni token'ı doğrula ve asıl kullanıcı adını çekerek veriyi düzelt
                token['is_valid'] = False
                try:
                    headers = {
                        'authorization': data['token'],
                        'user-agent': data['user_agent'],
                        'x-ig-app-id': '567067343352427',
                        'x-ig-android-id': f"android-{data['android_id']}"
                    }
                    resp = req.get('https://i.instagram.com/api/v1/accounts/current_user/?edit=true', 
                                      headers=headers, timeout=10, impersonate="chrome110")
                    if resp.status_code == 200:
                        user_info = resp.json().get('user', {})
                        real_username = user_info.get('username')
                        if real_username:
                            token['username'] = real_username
                            token['full_name'] = user_info.get('full_name', '')
                        token['is_active'] = True
                        token['is_valid'] = True
                except Exception:
                    logger.exception("Admin update_token validation failed")
                    
                # Logout bilgilerini temizle (yeni token girildi)
                token.pop('logout_reason', None)
                token.pop('logout_time', None)
                token_found = True
                target_token = token
                break
        
        if not token_found or not target_token:
            return jsonify({
                'success': False,
                'message': 'Token bulunamadı'
            }), 404
        
        save_tokens(tokens)
        
        is_active_now = bool(target_token.get('is_active', False))
        status_msg = "ve otomatik olarak AKTİF edildi!" if is_active_now else "ancak token geçersiz göründüğü için pasif bırakıldı."
        
        return jsonify({
            'success': True,
            'message': f'@{username} için token başarıyla güncellendi {status_msg}'
        })
    except Exception as e:
        logger.exception("Admin update_token failed")
        return jsonify({
            'success': False,
            'message': f'Token güncellenemedi: {str(e)}'
        }), 500

@admin_bp.route('/relogin_token', methods=['POST'])
def relogin_token():
    """Kaydedilen şifre ile tekrar giriş yap ve token'ı yenile"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Yetkisiz erişim'}), 401
    
    try:
        data = request.get_json(silent=True) or {}
        username = data.get('username')
        
        if not username:
            return jsonify({
                'success': False,
                'message': 'Kullanıcı adı belirtilmedi'
            }), 400
        
        tokens = load_tokens()
        target_token = None
        
        for token in tokens:
            if token['username'] == username:
                target_token = token
                break
        
        if not target_token:
            return jsonify({
                'success': False,
                'message': 'Token bulunamadı'
            }), 404
        
        if not target_token.get('password'):
            return jsonify({
                'success': False,
                'message': 'Bu hesap için şifre kaydedilmemiş'
            }), 400
        
        # Tekrar giriş yap
        try:
            new_token, new_android_id, new_user_agent, new_device_id = giris_yap(
                username, 
                target_token['password'],
                device_id=target_token.get('device_id'),
                android_id=target_token.get('android_id_yeni') or target_token.get('android_id'),
                user_agent=target_token.get('user_agent')
            )
            
            if not new_token:
                return jsonify({
                    'success': False,
                    'message': 'Giriş başarısız - Kullanıcı adı veya şifre hatalı'
                }), 400
            
            # Token'ı güncelle
            target_token['token'] = new_token
            target_token['android_id_yeni'] = new_android_id
            target_token['device_id'] = new_device_id
            target_token['user_agent'] = new_user_agent
            target_token['is_active'] = True  # Otomatik aktif yap
            target_token['is_valid'] = True
            # Logout bilgilerini temizle
            target_token.pop('logout_reason', None)
            target_token.pop('logout_time', None)
            
            save_tokens(tokens)
            
            return jsonify({
                'success': True,
                'message': f'@{username} için token başarıyla yenilendi ve aktif yapıldı!'
            })
            
        except Exception as e:
            logger.exception("Admin relogin_token failed during login")
            return jsonify({
                'success': False,
                'message': f'Giriş hatası: {str(e)}'
            }), 500
            
    except Exception as e:
        logger.exception("Admin relogin_token failed")
        return jsonify({
            'success': False,
            'message': f'Tekrar giriş yapılamadı: {str(e)}'
        }), 500

@admin_bp.route('/validate_token', methods=['POST'])
def validate_token_route():
    """Token'ı doğrula"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Yetkisiz erişim'}), 401
    
    try:
        data = request.get_json(silent=True) or {}
        username = data.get('username')
        
        if not username:
            return jsonify({
                'success': False,
                'message': 'Kullanıcı adı belirtilmedi'
            }), 400
        
        tokens = load_tokens()
        for token in tokens:
            if token['username'] == username:
                is_valid = validate_token(token)
                
                # Token geçersizse otomatik deaktif et
                if not is_valid and token.get('is_active', False):
                    token['is_active'] = False
                    token['logout_reason'] = 'Bu hesabın oturumu Instagram\'dan çıkış yapıldı'
                    token['logout_time'] = str(datetime.now())
                    save_tokens(tokens)
                
                return jsonify({
                    'success': True,
                    'is_valid': is_valid,
                    'is_active': token.get('is_active', False)
                })
        
        return jsonify({
            'success': False,
            'message': 'Token bulunamadı'
        }), 404
    except Exception as e:
        logger.exception("Admin validate_token failed")
        return jsonify({
            'success': False,
            'message': f'Token doğrulanamadı: {str(e)}'
        }), 500


@admin_bp.route('/change_password', methods=['POST'])
def change_password():
    """Admin şifresini değiştir"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Yetkisiz erişim'}), 401

    try:
        data = request.get_json(silent=True) or {}
        current_password = (data.get('current_password') or '').strip()
        new_password = (data.get('new_password') or '').strip()
        new_password_confirm = (data.get('new_password_confirm') or '').strip()

        if not current_password or not new_password or not new_password_confirm:
            return jsonify({'success': False, 'message': 'Tüm şifre alanları zorunludur'}), 400

        if len(new_password) < 4:
            return jsonify({'success': False, 'message': 'Yeni şifre en az 4 karakter olmalı'}), 400

        if new_password != new_password_confirm:
            return jsonify({'success': False, 'message': 'Yeni şifreler eşleşmiyor'}), 400

        if not _verify_admin_password(current_password):
            return jsonify({'success': False, 'message': 'Mevcut şifre hatalı'}), 400

        if current_password == new_password:
            return jsonify({'success': False, 'message': 'Yeni şifre mevcut şifreyle aynı olamaz'}), 400

        _set_admin_password(new_password)

        return jsonify({'success': True, 'message': 'Admin şifresi başarıyla güncellendi'})
    except Exception as e:
        logger.exception("Admin change_password failed")
        return jsonify({'success': False, 'message': f'Şifre değiştirilemedi: {str(e)}'}), 500
