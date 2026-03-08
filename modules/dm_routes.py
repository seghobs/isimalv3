from flask import Blueprint, request, render_template
from datetime import datetime, timedelta
import time
from curl_cffi import requests
from modules.token_manager import token_manager
from modules.profil_sorgula import profili_sorgula

dm_bp = Blueprint('dm', __name__)

@dm_bp.route('/dm_analiz', methods=['GET', 'POST'])
def dm_analiz():
    """DM Grup Paylaşım Analizi - İsimals modülü"""
    if request.method == 'GET':
        return render_template('dm_form.html')
    
    try:
        date_str = request.form['date']
        time_str = request.form['time']
        maxo = request.form.get('max', '50')
        datetime_str = f"{date_str} {time_str}"
        datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')

        group = request.form['group']
        grup_ids = {
            'begeni1': '340282366841710301281159538622628703126',
            'begeni2': '340282366841710301281160514595477770576',
            'zirveyorum1': '340282366841710301281156982018321100464',
            'zirveyorum2': '340282366841710301281176651461280340717'
        }
        grup_id = grup_ids.get(group)
        if not grup_id:
            return render_template('dm_result.html', error='Geçersiz grup seçimi')

        timestamp_start = int(time.mktime((datetime_obj - timedelta(hours=3)).timetuple()) * 1_000_000)
        timestamp_end = int(time.mktime((datetime_obj + timedelta(days=1) - timedelta(hours=3)).timetuple()) * 1_000_000)

        params = {
            'min_timestamp': str(timestamp_start),
            'max_timestamp': str(timestamp_end),
            'limit': maxo,
            'media_type': 'media_shares',
        }

        # TOKEN MANAGER ile aktif token al
        current_account = token_manager.get_active_token()
        if not current_account:
            return render_template('dm_result.html', error='Aktif token bulunamadı! Lütfen admin panelinden hesap ekleyin.')
        
        max_retries = len(token_manager.get_all_accounts())
        retry_count = 0
        response = None
        
        while retry_count < max_retries:
            try:
                # Şu anki token ile headers oluştur
                android_id = current_account.get('android_id') or current_account.get('android_id_yeni', '')
                current_headers = {
                    'x-ig-app-locale': 'tr_TR',
                    'x-ig-device-locale': 'tr_TR',
                    'x-ig-mapped-locale': 'tr_TR',
                    'x-ig-device-id': '33337356-a663-4d42-9983-6a449cd6f963',
                    'x-ig-android-id': f'android-{android_id}',
                    'x-ig-timezone-offset': '10800',
                    'x-ig-nav-chain': 'MainFeedFragment:feed_timeline:1:cold_start:1717775982.957::',
                    'x-fb-connection-type': 'WIFI',
                    'x-ig-connection-type': 'WIFI',
                    'x-ig-capabilities': '3brTv10=',
                    'x-ig-app-id': '567067343352427',
                    'priority': 'u=3',
                    'user-agent': current_account['user_agent'],
                    'accept-language': 'tr-TR, en-US',
                    'authorization': current_account['token'],
                    'x-fb-http-engine': 'Liger',
                    'x-fb-client-ip': 'True',
                    'x-fb-server-cluster': 'True',
                }
                
                print(f"DM Analiz - Token kullanılıyor: @{current_account['username']}")
                
                response = requests.get(
                    f'https://i.instagram.com/api/v1/direct_v2/threads/{grup_id}/media/',
                    params=params,
                    headers=current_headers,
                    timeout=20,
                    impersonate="chrome110"
                )
                
                # Başarılı istek
                if response.status_code == 200:
                    print(f"Token başarılı: @{current_account['username']}")
                    break
                
                # Token geçersiz (401, 403, etc.)
                if response.status_code in [401, 403]:
                    print(f"Token geçersiz: @{current_account['username']} - Sonraki token'a geçiliyor")
                    # Token'ı geçersiz olarak işaretle
                    token_manager.validate_token(current_account['id'])
                    
                    # Sonraki token'a geç
                    current_account = token_manager.get_next_valid_token(current_account['id'])
                    if not current_account:
                        return render_template('dm_result.html', error='Tüm tokenlar geçersiz! Lütfen admin panelinden tokenları yenileyin.')
                    
                    retry_count += 1
                    continue
                else:
                    # Diğer hatalar için tekrar dene
                    response.raise_for_status()
                    break
                    
            except requests.errors.RequestsError as e:
                print(f"İstek hatası: {e}")
                # Sonraki token'a geç
                current_account = token_manager.get_next_valid_token(current_account['id'])
                if not current_account:
                    return render_template('dm_result.html', error='İstek başarısız ve yedek token bulunamadı.')
                retry_count += 1
                continue
        
        if not response or response.status_code != 200:
            return render_template('dm_result.html', error='API isteği başarısız oldu. Tüm tokenlar denendi.')

        json_data = response.json()

        # API yanıtını kontrol et
        if not json_data:
            return render_template('dm_result.html', error='API\'den boş yanıt alındı')

        items = json_data.get('items', [])
        if not items:
            return render_template('dm_result.html', error='Bu tarihte paylaşım bulunamadı', date_str=datetime_str)

        print(f"API'den {len(items)} öğe alındı")

        results = []

        for item in items:
            try:
                timestamp = item.get('timestamp')
                media = item.get('media', {})
                caption = media.get('caption') if media else None

                # Caption None ise boş dict kullan
                if caption is None:
                    caption = {}

                username = caption.get('user', {}).get('username') if caption and caption.get('user') else None
                profile_picture = caption.get('user', {}).get('profile_pic_url') if caption and caption.get('user') else None
                short_code = media.get('code') if media else None
                user_id_ = item.get('sender_id')
                original_user_id = caption.get('user', {}).get('pk') if caption and caption.get('user') else None

                timestamp = timestamp or "empty"
                username = username or "empty"
                profile_picture = profile_picture or "empty"
                short_code = short_code or "empty"
                user_id_ = user_id_ or "empty"
                original_user_id = original_user_id or "empty"

                # Timestamp güvenli kontrolü
                try:
                    if timestamp and timestamp != "empty":
                        timestamp_seconds = int(timestamp) / 1_000_000
                        item_date = datetime.fromtimestamp(timestamp_seconds)
                        item_date_tr = item_date + timedelta(hours=3)
                    else:
                        item_date_tr = datetime.now()
                except (ValueError, TypeError, OSError) as e:
                    print(f"Timestamp hatası: {e}, bugünün tarihi kullanılıyor")
                    item_date_tr = datetime.now()

                # AKILLI PROFİL SORGULAMA STRATEJİSİ
                if item_date_tr.date() == datetime_obj.date():
                    # Kendi postunu mu paylaşıyor?
                    if user_id_ == original_user_id:
                        # Kendi postu - Kullanıcı adı zaten var!
                        sender_username = str(username)
                        sender_info = "(Kendi postunu paylaştı)"
                        
                        if sender_username != "empty":
                            results.append({
                                'timestamp': timestamp,
                                'username': str(username),
                                'profile_picture': str(profile_picture),
                                'short_code': short_code,
                                'item_date': item_date_tr,
                                'sender_username': sender_username,
                                'sender_info': sender_info
                            })
                    else:
                        # Başkasının postu - Profil sorgulamalıyız
                        try:
                            sender_user_info = profili_sorgula(
                                str(user_id_),
                                current_account['token'],
                                user_agent=current_account.get('user_agent'),
                                ig_user_id=current_account.get('username')
                            )
                            
                            if sender_user_info and isinstance(sender_user_info, dict):
                                sender_username = sender_user_info.get('username', f'ID:{user_id_}')
                                sender_info = f"(@{sender_username} tarafından paylaşıldı)"
                                
                                if sender_username != "empty" and not sender_username.startswith('ID:'):
                                    results.append({
                                        'timestamp': timestamp,
                                        'username': str(username),
                                        'profile_picture': str(profile_picture),
                                        'short_code': short_code,
                                        'item_date': item_date_tr,
                                        'sender_username': sender_username,
                                        'sender_info': sender_info
                                    })
                            else:
                                print(f"Profil alınamadı, atlanıyor: {user_id_}")
                        except Exception as e:
                            print(f"Profil sorgulama hatası, atlanıyor ({user_id_}): {e}")

            except Exception as e:
                print(f"Item işleme hatası: {e}")
                continue

        return render_template('dm_result.html', results=results, date_str=datetime_str)

    except requests.errors.RequestsError as e:
        error_msg = str(e).encode('utf-8', 'replace').decode('utf-8')
        return render_template('dm_result.html', error=f'API isteği başarısız: {error_msg}')
    except Exception as e:
        error_msg = str(e).encode('utf-8', 'replace').decode('utf-8')
        return render_template('dm_result.html', error=f'Beklenmeyen bir hata oluştu: {error_msg}')
