from flask import Blueprint, request, render_template, jsonify, send_file
from io import BytesIO
from curl_cffi import requests
from modules.instagram_api import get_comment_usernames, get_likers
from modules.donustur import donustur
from modules.token_utils import load_tokens

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Ana sayfa - Modül seçimi"""
    return render_template('index.html')

@main_bp.route('/yorum_analiz', methods=['GET', 'POST'])
def yorum_analiz():
    """Yorum analiz modülü"""
    if request.method == 'POST':
        link = request.form['post_link']
        als = donustur(link)
        media_id = als
        all_usernames = get_comment_usernames(media_id)

        grup_uye = request.form['grup_uye']
        grup_uye_kullanicilar = set(grup_uye.split())

        sponsor = []

        izinli_uye = request.form['izinliler']
        izinli_uyelerr = set(izinli_uye.split())

        updated_eksikler = grup_uye_kullanicilar - izinli_uyelerr - all_usernames - set(sponsor)

        return render_template('yorum_result.html', eksikler=updated_eksikler, toplam=len(grup_uye_kullanicilar))

    return render_template('yorum_form.html')

@main_bp.route('/begeni_analiz', methods=['GET', 'POST'])
def begeni_analiz():
    """Beğeni analiz modülü"""
    if request.method == 'POST':
        try:
            # Form verilerini al
            url = request.form.get('url', '').strip()
            group_members_text = request.form.get('group_members', '').strip()
            
            if not url:
                return render_template('begeni_result.html', error='URL boş olamaz')
            
            if not group_members_text:
                return render_template('begeni_result.html', error='Grup üye listesi boş olamaz')
            
            # Media ID çıkar
            media_id = donustur(url)
            if not media_id:
                return render_template('begeni_result.html', error='Geçersiz Instagram URL\'si')
            
            # Beğenenleri al (çoklu token ile)
            likers = get_likers(media_id)
            
            if not likers:
                return render_template('begeni_result.html', error='Beğeni bulunamadı veya tüm tokenlar geçersiz')
            
            # Grup üyelerini satır satır al ve temizle
            group_members = []
            for line in group_members_text.split('\n'):
                username = line.strip().replace('@', '').lower()
                if username:
                    group_members.append(username)
            
            # Beğenenlerin kullanıcı adlarını al
            likers_usernames = set([liker['username'].lower() for liker in likers])
            
            # Beğenmeyenleri bul
            not_liked = []
            for member in group_members:
                if member not in likers_usernames:
                    not_liked.append(member)
            
            return render_template('begeni_result.html', 
                                 not_liked=not_liked,
                                 group_total=len(group_members),
                                 liked_count=len(group_members) - len(not_liked),
                                 total_likes=len(likers))
            
        except Exception as e:
            return render_template('begeni_result.html', error=str(e))
    
    return render_template('begeni_form.html')

@main_bp.route('/profile_picture')
def profile_picture():
    """Profil fotoğrafı proxy (CORS bypass)"""
    url = request.args.get('url')
    try:
        response = requests.get(url, timeout=15, impersonate="chrome110")
        response.raise_for_status()
        return send_file(BytesIO(response.content), mimetype='image/jpeg')
    except requests.errors.RequestsError as e:
        return jsonify({"error": "Resim isteği başarısız", "details": str(e)}), 404

@main_bp.route('/api/check_active_tokens')
def check_active_tokens():
    """Tüm aktif tokenları kontrol eden public endpoint"""
    try:
        tokens = load_tokens()
        active_count = sum(1 for t in tokens if t.get('is_active', False))
        return jsonify({'success': True, 'active_count': active_count, 'total_count': len(tokens)})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
