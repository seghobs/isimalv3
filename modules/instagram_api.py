import json
import time
from curl_cffi import requests
from modules.token_manager import token_manager

def get_comment_usernames(media_id, min_id=None):
    """
    Yorumları çekerken otomatik token failover ile çalışır.
    Geçersiz token bulunursa otomatik olarak diğer tokenları dener.
    Token Manager kullanır.
    """
    # TOKEN MANAGER ile aktif token al
    current_account = token_manager.get_active_token()
    if not current_account:
        print("HATA: Aktif token bulunamadı! Lütfen admin panelinden hesap ekleyin.")
        return set()
    
    max_retries = len(token_manager.get_all_accounts())
    retry_count = 0
    usernames = set()
    
    while retry_count < max_retries:
        current_token = current_account.get('token', '')
        android_id = current_account.get('android_id') or current_account.get('android_id_yeni', '')
        current_user_agent = current_account.get('user_agent', '')
        current_username = current_account.get('username', 'bilinmeyen')
        
        print(f"Yorum çekme - Token kullanılıyor: @{current_username}")
        
        headers = {
            'authorization': current_token,
            'user-agent': current_user_agent,
            'x-ig-app-locale': 'tr_TR',
            'x-ig-device-locale': 'tr_TR',
            'x-ig-mapped-locale': 'tr_TR',
            'x-ig-android-id': f'android-{android_id}',
            'x-ig-app-id': '567067343352427',
            'x-ig-capabilities': '3brTv10=',
            'x-ig-connection-type': 'WIFI',
            'x-fb-connection-type': 'WIFI',
            'accept-language': 'tr-TR, en-US',
            'x-fb-http-engine': 'Liger',
            'x-fb-client-ip': 'True',
            'x-fb-server-cluster': 'True',
        }

        params = {
            'min_id': min_id,
            'sort_order': 'popular',
            'analytics_module': 'comments_v2_feed_contextual_profile',
            'can_support_threading': 'true',
            'is_carousel_bumped_post': 'false',
            'feed_position': '0',
        }

        token_valid = True

        try:
            while True:
                # HTTP isteği gönder
                response = requests.get(
                    f'https://i.instagram.com/api/v1/media/{media_id}/stream_comments/',
                    params=params,
                    headers=headers,
                    timeout=15,
                    impersonate="chrome110"
                )

                # Token geçersiz mi kontrol et
                if response.status_code in [401, 403]:
                    print(f"Token geçersiz: @{current_username} (HTTP {response.status_code})")
                    token_valid = False
                    
                    # Token Manager ile token'ı geçersiz olarak işaretle
                    token_manager.validate_token(current_account['id'])
                    print(f"Token otomatik pasif yapıldı: @{current_username}")
                    
                    break  # Dış döngüye çık, yeni token dene
                
                # Diğer hataları kontrol et
                if response.status_code != 200:
                    print(f"API Hatası: HTTP {response.status_code}")
                    token_valid = False
                    break

                # Yanıtı satır satır ayır
                lines = response.text.splitlines()

                # Her bir satırı JSON olarak çözümle
                json_data = None
                for line in lines:
                    try:
                        json_data = json.loads(line)
                        # Kullanıcı adlarını topla
                        for comment in json_data.get('comments', []):
                            username = comment.get('user', {}).get('username')
                            if username:
                                usernames.add(username)
                    except json.JSONDecodeError:
                        continue

                # Daha fazla veri var mı?
                if json_data:
                    next_min_id = json_data.get('next_min_id')
                    if not next_min_id:
                        break
                    params['min_id'] = next_min_id
                else:
                    break
            
            # Eğer token geçerliyse ve veri çektiyse başarılı
            if token_valid:
                print(f"Başarı! Toplam {len(usernames)} kullanıcı bulundu.")
                return usernames
        
        except Exception as e:
            print(f"Hata oluştu: {e}")
            token_valid = False
        
        # Token geçersizse yeni token dene
        if not token_valid:
            retry_count += 1
            print(f"Sonraki token'a geçiliyor... ({retry_count}/{max_retries})")
            
            # Sonraki token'a geç
            current_account = token_manager.get_next_valid_token(current_account['id'])
            if not current_account:
                print("Tüm tokenlar denendi, hiçbiri çalışmıyor!")
                return usernames
            continue
        else:
            # Başarılı, döngüden çık
            break
    
    return usernames


def get_likers(media_id):
    """
    Beğenenleri çekerken otomatik token failover ile çalışır.
    Geçersiz token bulunursa otomatik olarak diğer tokenları dener.
    Token Manager kullanır.
    """
    # TOKEN MANAGER ile aktif token al
    current_account = token_manager.get_active_token()
    if not current_account:
        print("HATA: Aktif token bulunamadı! Lütfen admin panelinden hesap ekleyin.")
        return []
    
    max_retries = len(token_manager.get_all_accounts())
    retry_count = 0
    all_likers = []
    
    while retry_count < max_retries:
        current_token = current_account.get('token', '')
        android_id = current_account.get('android_id') or current_account.get('android_id_yeni', '')
        current_user_agent = current_account.get('user_agent', '')
        current_username = current_account.get('username', 'bilinmeyen')
        
        print(f"Beğeni çekme - Token kullanılıyor: @{current_username}")
        
        headers = {
            'accept-language': 'tr-TR, en-US',
            'authorization': current_token,
            'x-ig-app-id': '567067343352427',
            'x-ig-android-id': f'android-{android_id}',
            'user-agent': current_user_agent,
            'x-fb-http-engine': 'Liger',
            'accept-encoding': 'gzip, deflate',
        }
        
        next_max_id = None
        page = 0
        token_valid = True
        
        try:
            while True:
                page += 1
                url = f'https://i.instagram.com/api/v1/media/{media_id}/likers/'
                
                params = {}
                if next_max_id:
                    params['max_id'] = next_max_id
                
                response = requests.get(url, headers=headers, params=params, timeout=15, impersonate="chrome110")
                
                # Token geçersiz mi kontrol et
                if response.status_code in [401, 403]:
                    print(f"Token geçersiz: @{current_username} (HTTP {response.status_code})")
                    token_valid = False
                    
                    # Token Manager ile token'ı geçersiz olarak işaretle
                    token_manager.validate_token(current_account['id'])
                    print(f"Token otomatik pasif yapıldı: @{current_username}")
                    
                    break  # Dış döngüye çık, yeni token dene
                
                if response.status_code != 200:
                    print(f"API Hatası: HTTP {response.status_code}")
                    token_valid = False
                    break
                
                data = response.json()
                users = data.get('users', [])
                
                if not users:
                    break
                
                # Kullanıcı bilgilerini ekle
                for user in users:
                    all_likers.append({
                        'username': user.get('username', ''),
                        'full_name': user.get('full_name', ''),
                        'is_private': user.get('is_private', False),
                        'is_verified': user.get('is_verified', False),
                        'profile_pic_url': user.get('profile_pic_url', ''),
                        'pk': user.get('pk', '')
                    })
                
                print(f"Sayfa {page}: {len(users)} kullanıcı alındı (Toplam: {len(all_likers)})")
                
                # Sonraki sayfa var mı?
                next_max_id = data.get('next_max_id')
                if not next_max_id:
                    break
                
                # Rate limiting
                time.sleep(1)
            
            # Token geçerliyse başarılı
            if token_valid:
                print(f"Başarı! Toplam {len(all_likers)} beğeni bulundu.")
                return all_likers
        
        except Exception as e:
            print(f"Beğeni çekme hatası: {e}")
            token_valid = False
        
        # Token geçersizse yeni token dene
        if not token_valid:
            retry_count += 1
            print(f"Sonraki token'a geçiliyor... ({retry_count}/{max_retries})")
            
            # Sonraki token'a geç
            current_account = token_manager.get_next_valid_token(current_account['id'])
            if not current_account:
                print("Tüm tokenlar denendi, hiçbiri çalışmıyor!")
                return all_likers
            continue
        else:
            # Başarılı, döngüden çık
            break
    
    return all_likers
