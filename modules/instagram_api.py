import time
from curl_cffi import requests
from modules.token_manager import token_manager
from modules.token_utils import load_tokens, save_tokens


def _mark_token_inactive(current_username, token_manager_ref):
    """Token'ı DB'de pasif yap"""
    try:
        tokens = load_tokens()
        for t in tokens:
            if t.get('username') == current_username:
                t['is_active'] = False
                t['is_valid'] = False
                break
        save_tokens(tokens)
        token_manager_ref.reload()
        print(f"Token pasif yapıldı: @{current_username}")
    except Exception as te:
        print(f"Token pasif yapma hatası: {te}")


def get_comment_usernames(media_id):
    """
    Instagram'ın iki aşamalı yorum sistemini kullanır:
    - Aşama 1: max_id ile en yeni yorumlar (normal)
    - Aşama 2: min_id ile eski/headload yorumlar
    Otomatik token failover desteklidir.
    """
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

        token_valid = True

        def fetch_page(extra_params):
            """Tek sayfa istek atar → (data_dict|None, token_ok)"""
            p = {'can_support_threading': 'true', 'sort_order': 'recent'}
            p.update(extra_params)
            r = requests.get(
                f'https://i.instagram.com/api/v1/media/{media_id}/comments/',
                params=p, headers=headers, timeout=15, impersonate="chrome110"
            )
            if r.status_code in [401, 403]:
                print(f"Token geçersiz: @{current_username} (HTTP {r.status_code})")
                _mark_token_inactive(current_username, token_manager)
                return None, False
            if r.status_code != 200:
                print(f"API Hatası: HTTP {r.status_code}")
                return None, False
            return r.json(), True

        def collect(data):
            """Yanıttan kullanıcı adlarını topla"""
            for section in ('comments', 'preview_comments'):
                for cm in data.get(section, []):
                    u = cm.get('user', {}).get('username')
                    if u:
                        usernames.add(u)
                    for child in cm.get('preview_child_comments', []):
                        cu = child.get('user', {}).get('username')
                        if cu:
                            usernames.add(cu)

        try:
            # ── AŞAMA 1: Normal yorumlar (max_id ile) ──────────────────────
            page = 0
            cur_max_id = None
            while True:
                page += 1
                extra = {}
                if cur_max_id:
                    extra['max_id'] = cur_max_id
                data, ok = fetch_page(extra)
                if not ok:
                    token_valid = False
                    break
                collect(data)
                next_max_id = data.get('next_max_id')
                has_more    = data.get('has_more_comments', False)
                print(f"  [A1] Sayfa {page}: {len(data.get('comments', []))} yorum | "
                      f"Toplam: {len(usernames)} | has_more={has_more}")
                if next_max_id and has_more:
                    cur_max_id = next_max_id
                    time.sleep(0.5)
                else:
                    break

            if not token_valid:
                raise Exception("Token geçersiz")

            # ── AŞAMA 2: Headload yorumlar (min_id ile) ───────────────────
            page = 0
            cur_min_id = None
            while True:
                page += 1
                extra = {}
                if cur_min_id:
                    extra['min_id'] = cur_min_id
                data, ok = fetch_page(extra)
                if not ok:
                    token_valid = False
                    break
                collect(data)
                next_min_id  = data.get('next_min_id')
                has_more_head = data.get('has_more_headload_comments', False)
                print(f"  [A2] Sayfa {page}: {len(data.get('comments', []))} yorum | "
                      f"Toplam: {len(usernames)} | headload={has_more_head}")
                if next_min_id and has_more_head:
                    cur_min_id = next_min_id
                    time.sleep(0.5)
                else:
                    break

            if token_valid:
                print(f"Başarı! Toplam {len(usernames)} yorum yapan kullanıcı bulundu.")
                return usernames

        except Exception as e:
            print(f"Hata oluştu: {e}")
            token_valid = False

        # Failover: Sonraki token'a geç
        if not token_valid:
            retry_count += 1
            print(f"Sonraki token'a geçiliyor... ({retry_count}/{max_retries})")
            current_account = token_manager.get_next_valid_token(current_account['id'])
            if not current_account:
                print("Tüm tokenlar denendi, hiçbiri çalışmıyor!")
                return usernames
            continue
        else:
            break

    return usernames


def get_likers(media_id):
    """
    Beğenenleri çekerken otomatik token failover ile çalışır.
    Geçersiz token bulunursa otomatik olarak diğer tokenları dener.
    Token Manager kullanır.
    """
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
                    print(f"Token geçersiz (beğeni): @{current_username} (HTTP {response.status_code})")
                    token_valid = False
                    _mark_token_inactive(current_username, token_manager)
                    break

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

        # Failover: Sonraki token'a geç
        if not token_valid:
            retry_count += 1
            print(f"Sonraki token'a geçiliyor... ({retry_count}/{max_retries})")
            current_account = token_manager.get_next_valid_token(current_account['id'])
            if not current_account:
                print("Tüm tokenlar denendi, hiçbiri çalışmıyor!")
                return all_likers
            continue
        else:
            break

    return all_likers
