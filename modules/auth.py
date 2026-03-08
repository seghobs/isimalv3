from flask import Blueprint, request, render_template, jsonify
from datetime import datetime
from curl_cffi import requests as req
from modules.token_utils import load_tokens, save_tokens
from modules.log_in import giris_yap

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/token_al')
def ana_sayfa():
    return render_template('token.html')

@auth_bp.route('/giris_yaps', methods=['POST'])
def giris():
    if request.method == 'POST':
        kullanici_adi = request.form['kullanici_adi']
        sifre = request.form['sifre']
        token_degeri, androidid, user_agent = giris_yap(kullanici_adi, sifre)

        print("Sonuç:", token_degeri, androidid)
        
        # Token başarılıysa tokens.json'a ekle/güncelle
        if token_degeri:
            try:
                tokens = load_tokens()
                
                # Aynı kullanıcı adı varsa güncelle, yoksa ekle
                existing_token = None
                for token in tokens:
                    if token['username'] == kullanici_adi:
                        existing_token = token
                        break
                
                if existing_token:
                    # Mevcut token'ı güncelle
                    existing_token['password'] = sifre
                    existing_token['token'] = token_degeri
                    existing_token['android_id_yeni'] = androidid
                    existing_token['user_agent'] = user_agent
                    existing_token['is_active'] = True
                    existing_token['is_valid'] = True
                    # Logout bilgilerini temizle
                    existing_token.pop('logout_reason', None)
                    existing_token.pop('logout_time', None)
                    print(f"Token güncellendi: @{kullanici_adi}")
                else:
                    # Yeni token ekle
                    # Önce kullanıcı bilgilerini al
                    try:
                        headers = {
                            'authorization': token_degeri,
                            'user-agent': user_agent,
                            'x-ig-app-id': '567067343352427',
                        }
                        response = req.get('https://i.instagram.com/api/v1/accounts/current_user/?edit=true', 
                                          headers=headers, timeout=10, impersonate="chrome110")
                        full_name = ''
                        if response.status_code == 200:
                            user_data = response.json().get('user', {})
                            full_name = user_data.get('full_name', '')
                    except:
                        full_name = ''
                    
                    new_token = {
                        'username': kullanici_adi,
                        'full_name': full_name,
                        'password': sifre,
                        'token': token_degeri,
                        'android_id_yeni': androidid,
                        'user_agent': user_agent,
                        'is_active': True,
                        'is_valid': True,
                        'added_at': str(datetime.now())
                    }
                    tokens.append(new_token)
                    print(f"Yeni token eklendi: @{kullanici_adi}")
                
                save_tokens(tokens)
            except Exception as e:
                print(f"Token kaydetme hatası: {e}")

        return jsonify({"token": token_degeri, "android_id_yeni": androidid, "user_agent": user_agent})
