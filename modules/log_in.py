import json
import re
import time
from curl_cffi import requests
import uuid
import os
from modules.androidid import *
import random

def giris_yap(username, password):
    android_id_yeni = android_id()
    current_timestamp = time.time()  # Şu anki zaman damgasını al


    # user_agent.json dosyasını oku
    user_agent_file = os.path.join(os.path.dirname(__file__), 'user_agent.json')
    with open(user_agent_file, 'r', encoding='utf-8') as file:
        user_agents = json.load(file)

    # Rastgele bir user agent seç
    selected_user_agent = random.choice(user_agents)

    print("Seçilen rastgele user agent:", selected_user_agent)

    # Belirli aralıkta rasgele ondalık sayı oluşturma
    min_value = 3.0090323460153e13
    max_value = 6.0090341600154e13
    random_decimal = random.uniform(min_value, max_value)
    #print("Rastgele Ondalık Sayı:", random_decimal)

    nav_chain = f'SelfFragment:self_profile:2:main_profile:{current_timestamp:.3f}::,ProfileMediaTabFragment:self_profile:3:button:{current_timestamp+0.287:.3f}::,SettingsScreenFragment:ig_settings:4:button:{current_timestamp+2.284:.3f}::,com.bloks.www.caa.login.aymh_single_profile_screen_entry:com.bloks.www.caa.login.aymh_single_profile_screen_entry:6:button:{current_timestamp+0.308:.3f}::'
    random_uuid = uuid.uuid4()
    random_uuid_str = str(random_uuid)
    headers = {
        'x-ig-app-locale': 'tr_TR',
        'x-ig-device-locale': 'tr_TR',
        'x-ig-mapped-locale': 'tr_TR',
        'x-bloks-version-id': 'af73ae8cc48182fdcaf2eb0beac7935cb25fd05d18118022cd3f433a4b04e459',
        'x-bloks-is-prism-enabled': 'true',
        'x-bloks-prism-button-version': 'PROPOSAL_A',
        'x-bloks-prism-colors-enabled': 'false',
        'x-bloks-prism-font-enabled': 'false',
        'x-ig-attest-params': '{"attestation":[{"version":2,"type":"keystore","errors":[],"challenge_nonce":"","signed_nonce":"","key_hash":""}]}',
        'x-bloks-is-layout-rtl': 'false',
        'x-ig-device-id': random_uuid_str,
        'x-ig-android-id': f'android-{android_id_yeni}',  # Güncellendi
        'x-ig-timezone-offset': '10800',
        'x-ig-nav-chain': nav_chain,
        'x-fb-connection-type': 'WIFI',
        'x-ig-connection-type': 'WIFI',
        'x-ig-capabilities': '3brTv10=',
        'x-ig-app-id': '567067343352427',
        'priority': 'u=3',
        'user-agent': f'{selected_user_agent}',
        'accept-language': 'tr-TR, en-US',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'x-fb-http-engine': 'Liger',
        'x-fb-client-ip': 'True',
        'x-fb-server-cluster': 'True',
    }
    data = {
        'params': (
            '{"client_input_params":{'
            '"should_show_nested_nta_from_aymh":1,'
            '"device_id":"android-' + android_id_yeni + '",'
            '"login_attempt_count":1,'
            '"secure_family_device_id":"",'
            '"machine_id":"' + android_id_yeni + '",'
            '"accounts_list":[{'
            '"uid":"",'
            '"credential_type":"none",'
            '"token":""},'
            '{"credential_type":"google_oauth",'
            '"account_type":"google_oauth",'
            '"token":""}],'
            '"auth_secure_device_id":"",'
            '"has_whatsapp_installed":1,'
            '"password":"#PWD_INSTAGRAM:0:0:' + password + '",'
            '"sso_token_map_json_string":"{\\"62428590454\\":[]}",'
            '"family_device_id":"' + random_uuid_str + '",'
            '"fb_ig_device_id":[],'
            '"device_emails":[""],'
            '"try_num":1,'
            '"lois_settings":{"lois_token":"","lara_override":""},'
            '"event_flow":"login_manual",'
            '"event_step":"home_page",'
            '"headers_infra_flow_id":"",'
            '"openid_tokens":{"":""},'
            '"client_known_key_hash":"",'
            '"contact_point":"' + username + '",'
            '"encrypted_msisdn":""},'
            '"server_params":{'
            '"should_trigger_override_login_2fa_action":0,'
            '"is_from_logged_out":1,'
            '"should_trigger_override_login_success_action":0,'
            '"login_credential_type":"none",'
            '"server_login_source":"login",'
            '"waterfall_id":"' + random_uuid_str + '",'
            '"login_source":"Login",'
            '"is_platform_login":0,'
            '"INTERNAL__latency_qpl_marker_id":36707139,'
            '"offline_experiment_group":"caa_iteration_v3_perf_ig_4",'
            '"is_from_landing_page":0,'
            '"password_text_input_id":"9xrg1k:86",'
            '"is_from_empty_password":0,'
            '"ar_event_source":"login_home_page",'
            '"qe_device_id":"'+random_uuid_str+'",'
            '"username_text_input_id":"9xrg1k:85",'
            '"layered_homepage_experiment_group":null,'
            '"device_id":"android-'+android_id_yeni+'",'
            '"INTERNAL__latency_qpl_instance_id":6.0090341600153E13,'
            '"reg_flow_source":"aymh_single_profile_native_integration_point",'
            '"is_caa_perf_enabled":1,'
            '"credential_type":"password",'
            '"caller":"gslr",'
            '"family_device_id":null,'
            '"INTERNAL_INFRA_THEME":"harm_f",'
            '"access_flow_version":"F2_FLOW",'
            '"is_from_logged_in_switcher":0}}'
        ),
        'bk_client_context': (
            '{"bloks_version":"af73ae8cc48182fdcaf2eb0beac7935cb25fd05d18118022cd3f433a4b04e459",'
            '"styles_id":"instagram"}'
        ),
        'bloks_versioning_id': 'af73ae8cc48182fdcaf2eb0beac7935cb25fd05d18118022cd3f433a4b04e459',
    }


    response = requests.post(
        'https://i.instagram.com/api/v1/bloks/apps/com.bloks.www.bloks.caa.login.async.send_login_request/',
        headers=headers,
        data=data,
        impersonate="chrome110"
    )

    # Response'u kontrol et
    print(f"Response Status Code: {response.status_code}")
    
    try:
        yeni = response.json()
        print("Response JSON:")
        print(json.dumps(yeni, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"JSON Parse Hatası: {e}")
        print(f"Response Text: {response.text}")
        return None, android_id_yeni, selected_user_agent

    # Bearer token'ını bulmak için fonksiyon
    def find_bearer_token(data):
        token_pattern = re.compile(r'Bearer IGT:[a-zA-Z0-9:_\-]+')

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    match = token_pattern.search(value)
                    if match:
                        return match.group(0)
                elif isinstance(value, (dict, list)):
                    result = find_bearer_token(value)
                    if result:
                        return result
        elif isinstance(data, list):
            for item in data:
                result = find_bearer_token(item)
                if result:
                    return result
        return None

    # Bearer token'ı bulma
    bearer_token = find_bearer_token(yeni)

    # Sonucu yazdırma
    print(f"\n=== BULUNAN BEARER TOKEN ===")
    print(f"Token: {bearer_token}")
    print(f"Android ID: {android_id_yeni}")
    print(f"User Agent: {selected_user_agent}")
    print("=" * 50)
    
    if not bearer_token:
        print("\n[HATA] Token bulunamadı! Response'da token yok olabilir.")
        print("Lütfen response JSON'ı kontrol edin.\n")

    # JSON dosyasına kaydetme iptal edildi (artık auth tokens.json üzerinden yapılıyor)
    # token_file = os.path.join(os.path.dirname(__file__), 'token.json')
    # with open(token_file, 'w', encoding='utf-8') as f:
    #     json.dump({"token": bearer_token, "android_id_yeni": android_id_yeni, "user_agent": selected_user_agent}, f, ensure_ascii=False, indent=2)

    return bearer_token, android_id_yeni,selected_user_agent