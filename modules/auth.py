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
        kullanici_adi = request.form.get('kullanici_adi', '').strip()
        sifre = request.form.get('sifre', '').strip()

        # Kullanıcının girdiği cihaz kimliği değerleri
        device_id  = request.form.get('device_id', '').strip()
        android_id = request.form.get('android_id', '').strip()
        user_agent = request.form.get('user_agent', '').strip()

        if not all([kullanici_adi, sifre, device_id, android_id, user_agent]):
            return jsonify({
                "success": False,
                "message": "kullanici_adi, sifre, device_id, android_id ve user_agent zorunludur"
            }), 400

        # Giriş yap — cihaz kimliğini dışarıdan ver
        token_degeri, _android, _ua, _device = giris_yap(
            kullanici_adi, sifre,
            device_id=device_id,
            android_id=android_id,
            user_agent=user_agent
        )

        print("Sonuç:", token_degeri, android_id)

        if token_degeri:
            try:
                tokens = load_tokens()

                existing_token = None
                for token in tokens:
                    if token['username'] == kullanici_adi:
                        existing_token = token
                        break

                if existing_token:
                    # Mevcut hesap — sadece token'ı güncelle, CİHAZ KİMLİĞİNİ KORU
                    # (kullanıcı açıkça yeni değer girmişse güncelle, boşsa eskiyi tut)
                    existing_token['password'] = sifre
                    existing_token['token']    = token_degeri
                    existing_token['android_id_yeni'] = android_id or existing_token.get('android_id_yeni', android_id)
                    existing_token['android_id']      = android_id or existing_token.get('android_id', android_id)
                    existing_token['device_id']       = device_id  or existing_token.get('device_id', device_id)
                    existing_token['user_agent']      = user_agent or existing_token.get('user_agent', user_agent)
                    existing_token['is_active'] = True
                    existing_token['is_valid']  = True
                    existing_token.pop('logout_reason', None)
                    existing_token.pop('logout_time', None)
                    print(f"Token güncellendi: @{kullanici_adi}")
                else:
                    # Yeni hesap — tam bilgi ekle
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
                        'username':      kullanici_adi,
                        'full_name':     full_name,
                        'password':      sifre,
                        'token':         token_degeri,
                        'android_id_yeni': android_id,
                        'android_id':    android_id,
                        'device_id':     device_id,
                        'user_agent':    user_agent,
                        'is_active':     True,
                        'is_valid':      True,
                        'added_at':      str(datetime.now())
                    }
                    tokens.append(new_token)
                    print(f"Yeni token eklendi: @{kullanici_adi}")

                save_tokens(tokens)
            except Exception as e:
                print(f"Token kaydetme hatası: {e}")

        return jsonify({
            "success": bool(token_degeri),
            "token": token_degeri,
            "android_id": android_id,
            "device_id": device_id,
            "user_agent": user_agent
        })

