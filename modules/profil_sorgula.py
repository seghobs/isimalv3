from curl_cffi import requests
import json

def profili_sorgula(user_id, token, user_agent=None, ig_user_id=None):
    """
    Kullanıcı profil bilgilerini sorgula
    
    Args:
        user_id: Sorgulanacak kullanıcı ID
        token: Authorization token
        user_agent: Dinamik user agent (opsiyonel)
        ig_user_id: Instagram user ID (opsiyonel)
    """
    # Varsayılan değerler (eski uyumluluk için)
    if user_agent is None:
        user_agent = 'Instagram 333.0.0.42.91 Android (25/7.1.1; 240dpi; 540x960; samsung; SM-J250F; j2y18lte; qcom; es_ES; 604247835)'
    
    if ig_user_id is None:
        ig_user_id = '33205094022'
    
    headers = {
        'x-fb-friendly-name': 'ProfileUserInfo',
        'x-ig-capabilities': '3brTv10=',
        'authorization': token,
        'ig-u-ds-user-id': str(ig_user_id),  # Dinamik!
        'content-type': 'application/x-www-form-urlencoded',
        'x-root-field-name': 'xdt_users__info',
        'accept-language': 'tr-TR, en-US',
        'x-fb-request-analytics-tags': '{"network_tags":{"product":"567067343352427","purpose":"none","request_category":"graphql","retry_attempt":"0"},"application_tags":"pando"}',
        'x-ig-app-id': '567067343352427',
        'x-graphql-client-library': 'pando',
        'x-fb-rmd': 'fail=Server:NoUrlMap,Default:INVALID_MAP;v=;ip=;tkn=;reqTime=0;recvTime=0',
        'x-tigon-is-retry': 'False',
        'user-agent': user_agent,  # Dinamik!
        'x-fb-http-engine': 'Liger',
        'x-fb-client-ip': 'True',
        'x-fb-server-cluster': 'True',
    }

    data = {
        'method': 'post',
        'pretty': 'false',
        'format': 'json',
        'server_timestamps': 'true',
        'locale': 'user',
        'fb_api_req_friendly_name': 'ProfileUserInfo',
        'client_doc_id': '201960159614828159292946682190',
        'enable_canonical_naming': 'true',
        'enable_canonical_variable_overrides': 'true',
        'enable_canonical_naming_ambiguous_type_prefixing': 'true',
        'variables': '{"use_defer":true,"user_id":"'+user_id+'","from_module":"direct_thread","entry_point":"profile"}',
    }

    try:
        response = requests.post('https://i.instagram.com/graphql/query', headers=headers, data=data, timeout=10, impersonate="chrome110") # Zaman aşımı eklendi
        response.raise_for_status()  # Başarısız istekler için hata yükselt

        try:
            response_data = json.loads(response.text.split("\n", 1)[0])
        except json.JSONDecodeError:
            print(f"JSONDecodeError: Yanıt ayrıştırılamadı (User ID: {user_id})")
            return None
    except requests.errors.RequestsError as e:
        print(f"İstek Hatası (User ID: {user_id}): {e}")
        return None

    def extract_user_info(data):
        try:
            user_info = data['data']['1$xdt_users__info(entry_point:$entry_point,from_module:$from_module,user_id:$user_id)']['user']
            return {
                'username': user_info.get('username', ''),
                'profile_pic_url': user_info.get('profile_pic_url', '')
            }
        except KeyError as e:
            print(f"KeyError (User ID: {user_id}): {e}")
            return None

    user_info = extract_user_info(response_data)
    return user_info