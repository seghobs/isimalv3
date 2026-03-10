#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Token Manager - Çoklu Instagram hesap ve token yönetimi (İsimals + Kontrls Birleşik)
"""

from datetime import datetime
from curl_cffi import requests
from modules.log_in import giris_yap
from modules.token_utils import load_tokens as sql_load, save_tokens as sql_save
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class TokenManager:
    def __init__(self):
        self.tokens = self.load_tokens()
    
    def reload(self):
        """Veritabanından anlık tekrar yükle"""
        self.tokens = self.load_tokens()
        return self.tokens
    
    def load_tokens(self):
        """SQLite veritabanından tokenleri yükle ve dict formatında döndür"""
        sql_data = sql_load()
        return {"accounts": sql_data}
    
    def save_tokens(self, data=None):
        """Değişiklikleri SQLite veritabanına kaydet"""
        if data is None:
            data = self.tokens
        sql_save(data)
    
    def get_active_token(self):
        """Aktif ve geçerli ilk token'ı döndür (anlık reload) - Kontrls uyumlu format"""
        self.reload()
        
        for account in self.tokens.get("accounts", []):
            if account.get("is_active") and account.get("is_valid", True):
                # Kontrls formatına çevir (android_id_yeni)
                result = account.copy()
                if 'android_id' in result and 'android_id_yeni' not in result:
                    result['android_id_yeni'] = result['android_id']
                return result
        return None
    
    def get_all_accounts(self):
        """Tüm hesapları döndür (anlık reload)"""
        self.reload()
        return self.tokens.get("accounts", [])
    
    def get_account_by_id(self, account_id):
        """ID'ye göre hesap getir (anlık reload)"""
        self.reload()
        
        for account in self.tokens.get("accounts", []):
            if account["id"] == account_id:
                return account
        return None
    
    def get_account_by_username(self, username):
        """Username'e göre hesap getir"""
        self.reload()
        
        for account in self.tokens.get("accounts", []):
            if account["username"] == username:
                return account
        return None
    
    def add_account(self, username, password, auto_login=True):
        """Yeni hesap ekle ve login yap"""
        try:
            if auto_login:
                # Instagram'a giriş yap
                token, android_id, user_agent, device_id = giris_yap(username, password)
                
                if not token:
                    return {"success": False, "error": "Token alınamadı"}
            else:
                # Manuel ekleme - boş token
                token = None
                android_id = ""
                user_agent = ""
            
            # Hesap zaten var mı kontrol et
            for account in self.tokens["accounts"]:
                if account["username"] == username:
                    # Varsa güncelle
                    account["password"] = password
                    if token:
                        account["token"] = token
                        account["android_id"] = android_id
                        account["android_id_yeni"] = android_id  # Kontrls uyumluluk
                        account["user_agent"] = user_agent
                    account["login_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    account["last_check"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    account["is_active"] = True
                    account["is_valid"] = True if token else False
                    # Logout bilgilerini temizle
                    account.pop("logout_reason", None)
                    account.pop("logout_time", None)
                    self.save_tokens()
                    return {"success": True, "message": "Hesap güncellendi", "account": account}
            
            # Yeni ID oluştur
            max_id = max([acc.get("id", 0) for acc in self.tokens["accounts"]], default=0)
            new_id = max_id + 1
            
            # Yeni hesap ekle
            new_account = {
                "id": new_id,
                "username": username,
                "password": password,
                "token": token,
                "android_id": android_id,
                "android_id_yeni": android_id,
                "device_id": device_id,
                "user_agent": user_agent,
                "login_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_check": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "is_active": True if token else False,
                "is_valid": True if token else False
            }
            
            self.tokens["accounts"].append(new_account)
            self.save_tokens()
            
            return {"success": True, "message": "Hesap başarıyla eklendi", "account": new_account}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def add_manual_account(self, username, password, token, android_id, user_agent):
        """Manuel token bilgileri ile hesap ekle"""
        try:
            # Hesap zaten var mı kontrol et
            for account in self.tokens["accounts"]:
                if account["username"] == username:
                    # Varsa güncelle
                    account["password"] = password
                    account["token"] = token
                    account["android_id"] = android_id
                    account["android_id_yeni"] = android_id  # Kontrls uyumluluk
                    account["user_agent"] = user_agent
                    account["login_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    account["last_check"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    account["is_active"] = True
                    account["is_valid"] = True
                    # Logout bilgilerini temizle
                    account.pop("logout_reason", None)
                    account.pop("logout_time", None)
                    self.save_tokens()
                    return {"success": True, "message": "Hesap güncellendi", "account": account}
            
            # Yeni ID oluştur
            max_id = max([acc.get("id", 0) for acc in self.tokens["accounts"]], default=0)
            new_id = max_id + 1
            
            # Yeni hesap ekle
            new_account = {
                "id": new_id,
                "username": username,
                "password": password,
                "token": token,
                "android_id": android_id,
                "android_id_yeni": android_id,  # Kontrls uyumluluk
                "user_agent": user_agent,
                "login_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_check": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "is_active": True,
                "is_valid": True
            }
            
            self.tokens["accounts"].append(new_account)
            self.save_tokens()
            
            return {"success": True, "message": "Hesap başarıyla eklendi", "account": new_account}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_account(self, account_id, username, password, token, android_id, user_agent):
        """Hesap bilgilerini güncelle"""
        try:
            for account in self.tokens["accounts"]:
                if account["id"] == account_id:
                    account["username"] = username
                    account["password"] = password
                    account["token"] = token
                    account["android_id"] = android_id
                    account["android_id_yeni"] = android_id  # Kontrls uyumluluk
                    account["user_agent"] = user_agent
                    account["last_check"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    # Logout bilgilerini temizle
                    account.pop("logout_reason", None)
                    account.pop("logout_time", None)
                    self.save_tokens()
                    return {"success": True, "message": "Hesap güncellendi", "account": account}
            
            return {"success": False, "error": "Hesap bulunamadı"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def toggle_active(self, account_id):
        """Hesabı aktif/pasif yap"""
        for account in self.tokens["accounts"]:
            if account["id"] == account_id:
                account["is_active"] = not account.get("is_active", False)
                
                # Aktif yapılıyorsa logout_reason'u temizle
                if account["is_active"]:
                    account.pop("logout_reason", None)
                    account.pop("logout_time", None)
                
                self.save_tokens()
                return {"success": True, "is_active": account["is_active"]}
        return {"success": False, "error": "Hesap bulunamadı"}
    
    def delete_account(self, account_id):
        """Hesabı sil"""
        initial_count = len(self.tokens["accounts"])
        self.tokens["accounts"] = [acc for acc in self.tokens["accounts"] if acc["id"] != account_id]
        
        if len(self.tokens["accounts"]) < initial_count:
            self.save_tokens()
            return {"success": True, "message": "Hesap silindi"}
        return {"success": False, "error": "Hesap bulunamadı"}
    
    def validate_token(self, account_id):
        """Token'ın geçerli olup olmadığını kontrol et"""
        account = self.get_account_by_id(account_id)
        if not account:
            return {"success": False, "error": "Hesap bulunamadı"}
        
        try:
            # Instagram API'ye basit bir test isteği
            headers = {
                'authorization': account["token"],
                'user-agent': account["user_agent"],
                'x-ig-app-id': '567067343352427',
            }
            
            response = requests.get(
                'https://i.instagram.com/api/v1/accounts/current_user/?edit=true',
                headers=headers,
                timeout=10,
                impersonate="chrome110"
            )
            
            is_valid = response.status_code == 200
            
            # Durumu güncelle
            for acc in self.tokens["accounts"]:
                if acc["id"] == account_id:
                    acc["is_valid"] = is_valid
                    acc["last_check"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Geçersizse logout bilgisi ekle
                    if not is_valid:
                        acc["is_active"] = False
                        acc["logout_reason"] = "Bu hesabın oturumu Instagram'dan çıkış yapıldı"
                        acc["logout_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    break
            
            self.save_tokens()
            
            return {
                "success": True,
                "is_valid": is_valid,
                "status_code": response.status_code
            }
        
        except Exception as e:
            # Hata durumunda geçersiz işaretle
            for acc in self.tokens["accounts"]:
                if acc["id"] == account_id:
                    acc["is_valid"] = False
                    acc["last_check"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    break
            self.save_tokens()
            
            return {"success": False, "error": str(e), "is_valid": False}
    
    def refresh_token(self, account_id):
        """Token'ı yenile (yeniden login)"""
        account = self.get_account_by_id(account_id)
        if not account:
            return {"success": False, "error": "Hesap bulunamadı"}
        
        try:
            token, android_id, user_agent, device_id = giris_yap(
                account["username"],
                account["password"]
            )
            
            if not token:
                return {"success": False, "error": "Token yenilenemedi"}
            
            # Token'ı güncelle
            for acc in self.tokens["accounts"]:
                if acc["id"] == account_id:
                    acc["token"] = token
                    acc["android_id"] = android_id
                    acc["android_id_yeni"] = android_id
                    acc["device_id"] = device_id
                    acc["user_agent"] = user_agent
                    acc["login_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    acc["last_check"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    acc["is_valid"] = True
                    acc["is_active"] = True
                    # Logout bilgilerini temizle
                    acc.pop("logout_reason", None)
                    acc.pop("logout_time", None)
                    break
            
            self.save_tokens()
            
            return {"success": True, "message": "Token yenilendi", "token": token}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_next_valid_token(self, current_account_id=None):
        """
        Sıradaki geçerli ve aktif token'ı döndür.
        Eğer current_account_id verilirse, ondan sonrakini döndür.
        """
        self.reload()
        
        accounts = self.tokens.get("accounts", [])
        
        if not accounts:
            return None
        
        # Eğer current_account_id verilmişse, ondan sonrakini bul
        start_index = 0
        if current_account_id:
            for i, acc in enumerate(accounts):
                if acc["id"] == current_account_id:
                    start_index = i + 1
                    break
        
        # Sırayla kontrol et (döngüsel)
        for i in range(len(accounts)):
            index = (start_index + i) % len(accounts)
            account = accounts[index]
            
            if account.get("is_active") and account.get("is_valid", True):
                # Kontrls formatına çevir
                result = account.copy()
                if 'android_id' in result and 'android_id_yeni' not in result:
                    result['android_id_yeni'] = result['android_id']
                return result
        
        return None

# Global instance
token_manager = TokenManager()
