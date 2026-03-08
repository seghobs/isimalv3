# 🚀 Instagram Analiz Platformu

**Çoklu Token Destekli • Otomatik Failover • Kesintisiz Analiz**

İki güçlü modülü tek bir platformda birleştiren, çoklu Instagram hesap token yönetimi ile çalışan profesyonel analiz platformu.

---

## ✨ Özellikler

### 🎯 Modüller

#### 1. **Yorum Analizi** 📝
- Instagram postlarındaki yorumları analiz eder
- Grup üyelerinden hangilerinin yorum yapmadığını bulur
- Sınırsız yorum çekme (pagination ile)
- İzinli üye listesi desteği

#### 2. **Beğeni Analizi** ❤️
- Instagram post ve reels beğenilerini analiz eder
- Grup üyelerinden hangilerinin beğenmediğini bulur
- Sınırsız beğeni çekme (pagination ile)
- Detaylı istatistikler

### 🔥 Çoklu Token Sistemi

- **Sınırsız hesap:** İstediğiniz kadar Instagram hesabı ekleyin
- **Otomatik failover:** Token geçersiz olursa anında diğerine geçer
- **Sessiz mod:** Kullanıcı hata mesajı görmez, arka planda token değişir
- **Akıllı yönetim:** Geçersiz tokenlar otomatik pasif yapılır
- **Token doğrulama:** Admin panelden tokenları test edin
- **Tekrar giriş yap:** Şifre kaydettiyseniz tek tıkla token yenileyin

### 🎨 Modern Tasarım

- **Dark mode** - Göz yormayan karanlık tema
- **Gradient UI** - Modern gradient renk paletleri
- **Glassmorphism** - Şeffaf cam efektleri
- **Responsive** - Mobil uyumlu tasarım
- **Animasyonlar** - Akıcı geçişler ve hover efektleri

---

## 📂 Proje Yapısı

```
kontrls/
├── flask_app.py                # Ana Flask uygulaması
├── log_in.py                   # Instagram login sistemi
├── androidid.py                # Android ID generator
├── donustur.py                 # URL -> Media ID converter
├── tokens.json                 # Çoklu token deposu
├── token.json                  # Eski token (geriye uyumluluk)
├── user_agent.json             # User agent listesi
├── README.md                   # Bu dosya
├── COKLU_TOKEN_README.md       # Detaylı token sistemi dökümantasyonu
└── templates/
    ├── index.html              # Ana sayfa (modül seçimi)
    ├── yorum_form.html         # Yorum analiz formu
    ├── yorum_result.html       # Yorum analiz sonuçları
    ├── begeni_form.html        # Beğeni analiz formu
    ├── begeni_result.html      # Beğeni analiz sonuçları
    ├── token.html              # Token alma sayfası
    ├── admin_login.html        # Admin giriş
    └── admin.html              # Admin panel
```

---

## 🚀 Kurulum

### 1. Gereksinimleri Yükleyin

```bash
pip install flask requests
```

### 2. Uygulamayı Başlatın

```bash
cd kontrls
python flask_app.py
```

### 3. Tarayıcıda Açın

```
http://127.0.0.1:5000
```

---

## 🎮 Kullanım

### Ana Sayfa

1. Tarayıcıda `http://127.0.0.1:5000` adresine gidin
2. **Yorum Analizi** veya **Beğeni Analizi** modülünü seçin
3. Admin Panel veya Token Al butonlarını kullanabilirsiniz

### Yorum Analizi

1. **Yorum Analizi** kartına tıklayın
2. Instagram post/reel URL'sini girin
3. Grup üye listesini girin (her satıra bir kullanıcı adı)
4. İzinli üye listesini girin (isteğe bağlı)
5. **Yorumları Analiz Et** butonuna tıklayın
6. Sonuçları görün ve kopyalayın

### Beğeni Analizi

1. **Beğeni Analizi** kartına tıklayın
2. Instagram post/reel URL'sini girin
3. Grup üye listesini girin (her satıra bir kullanıcı adı)
4. **Beğenenleri Analiz Et** butonuna tıklayın
5. Sonuçları görün ve kopyalayın

### Admin Panel

1. Sağ üstteki **Admin Panel** butonuna tıklayın
2. Şifre: `seho` (varsayılan)
3. Token ekleme, silme, düzenleme, doğrulama işlemlerini yapın
4. Token durumlarını izleyin

### Token Alma

1. Sağ alttaki **Token Al** butonuna tıklayın
2. Instagram kullanıcı adı ve şifrenizi girin
3. **Token Al** butonuna tıklayın
4. Token otomatik olarak `tokens.json`'a kaydedilir

---

## 🔧 Teknik Detaylar

### Çoklu Token Failover Sistemi

```python
# Sistem otomatik olarak şu sırayı izler:
1. İstek atılır (aktif token ile)
2. HTTP 401/403 gelirse:
   - Token otomatik pasif yapılır
   - Bir sonraki aktif token alınır
   - Aynı istek yeni token ile tekrar denenir
3. HTTP 200 gelirse:
   - Sonuç döndürülür
   - Kullanıcı hiçbir hata görmez
```

### API Endpoints

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/` | GET | Ana sayfa (modül seçimi) |
| `/yorum_analiz` | GET/POST | Yorum analiz modülü |
| `/begeni_analiz` | GET/POST | Beğeni analiz modülü |
| `/token_al` | GET | Token alma sayfası |
| `/giris_yaps` | POST | Token alma (API) |
| `/admin` | GET | Admin panel |
| `/admin/login` | GET/POST | Admin giriş |
| `/admin/get_tokens` | GET | Tüm tokenleri getir |
| `/admin/add_token` | POST | Yeni token ekle |
| `/admin/update_token` | POST | Token güncelle |
| `/admin/relogin_token` | POST | Tekrar giriş yap |
| `/admin/delete_token` | POST | Token sil |
| `/admin/toggle_token` | POST | Token aktif/pasif |
| `/admin/validate_token` | POST | Token doğrula |

### tokens.json Formatı

```json
[
  {
    "username": "kullanici1",
    "full_name": "Ahmet Yılmaz",
    "password": "sifre123",
    "token": "Bearer IGT:2:...",
    "android_id_yeni": "3724108ca33e7977",
    "user_agent": "Instagram 321.0.0.34.111...",
    "is_active": true,
    "added_at": "2024-01-15T10:30:00"
  }
]
```

---

## 🔒 Güvenlik

### Önemli Notlar

⚠️ **Token Güvenliği**
- Token'larınızı kimseyle paylaşmayın
- Token'larınızı GitHub'a yüklemeyin
- `tokens.json` dosyasını güvenli tutun

⚠️ **Şifre Güvenliği**
- Şifreler `tokens.json` dosyasında **açık metin** olarak saklanır
- Sadece güvenli ortamlarda kullanın
- Admin şifresini değiştirin: `flask_app.py` → `ADMIN_PASSWORD`

⚠️ **Rate Limiting**
- Her istek arası 1 saniye bekleme var
- Instagram API limitlerini aşmayın
- Spam yapmayın

---

## 📊 Özellik Karşılaştırması

| Özellik | Eski instagram_like | Eski kontrls | Yeni Platform |
|---------|---------------------|--------------|---------------|
| Beğeni Analizi | ✅ | ❌ | ✅ |
| Yorum Analizi | ❌ | ✅ | ✅ |
| Tek Token | ✅ | ✅ | ✅ |
| Çoklu Token | ❌ | ✅ | ✅ |
| Otomatik Failover | ❌ | ✅ | ✅ |
| Admin Panel | ❌ | ✅ | ✅ |
| Modern Tasarım | ✅ | ⚠️ | ✅ |
| Token Yenileme | ❌ | ✅ | ✅ |
| Tek Platform | ❌ | ❌ | ✅ |

---

## 🎯 Kullanım Senaryoları

### Senaryo 1: İlk Kurulum
```
1. Admin Panel → Token Ekle
2. Token, Android ID, User Agent girin
3. Kullanıcı adı otomatik algılanır
4. Token doğrulanır ve eklenir
5. Artık her iki modülü de kullanabilirsiniz!
```

### Senaryo 2: Token Geçersiz Oldu
```
Kullanıcı perspektifi:
  - Analiz butonuna basar
  - Sonuç ekranını görür
  
Arka planda:
  - Token 1 geçersiz → pasif yapıldı
  - Token 2 denendi → başarılı
  - Sonuç döndürüldü
```

### Senaryo 3: Yeni Token Ekleme
```
Yöntem 1 - Token Al Sayfası:
  1. Token Al butonuna tıkla
  2. Kullanıcı adı + şifre gir
  3. Token otomatik alınır ve kaydedilir
  
Yöntem 2 - Manuel Ekleme:
  1. Admin Panel → Yeni Token Ekle
  2. Token, Android ID, User Agent gir
  3. Kaydet
```

---

## 🐛 Sorun Giderme

### Token Geçersiz Hatası
- Admin Panel → Token Doğrula ile test edin
- Geçersizse "Tekrar Giriş Yap" ile yenileyin
- Veya yeni token ekleyin

### Hiçbir Token Çalışmıyor
- Admin Panel'de en az 1 aktif token olmalı
- Token Al sayfasından yeni token alın
- Token'ların geçerli olduğundan emin olun

### Sayfa Açılmıyor
- Flask uygulamasının çalıştığından emin olun
- Port 5000'in kullanılmadığından emin olun
- Terminal'de hata mesajlarını kontrol edin

---

## 📈 Gelecek Özellikler

- [ ] SQLite/PostgreSQL database entegrasyonu
- [ ] Takipçi/takip edilenler analizi
- [ ] Hikaye görüntüleyenleri analizi
- [ ] Export to CSV/Excel
- [ ] Zamanlama (scheduled tasks)
- [ ] Email/Telegram bildirimleri
- [ ] Multi-language support
- [ ] API documentation
- [ ] Docker containerization

---

## 📝 Lisans

Bu proje eğitim amaçlıdır. Instagram API kullanım şartlarına uygun kullanın.

## ⚠️ Yasal Uyarı

- Instagram'ın resmi API'sını kullanmıyorsunuz
- Instagram kullanım şartlarına aykırı olabilir
- Sadece kendi hesabınız için kullanın
- Spam veya kötüye kullanım yapmayın
- Sorumluluk size aittir

---

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Push edin (`git push origin feature/AmazingFeature`)
5. Pull Request açın

---

## 📞 Destek

Sorularınız için issue açabilirsiniz.

---

**Yapımcı**: Instagram Analiz Platform  
**Versiyon**: 2.0.0 (Birleştirilmiş)  
**Tarih**: 2025

---

## 🎉 Önemli Değişiklikler

### v2.0.0 - Birleştirme Güncellemesi
- ✅ Beğeni analizi eklendi
- ✅ Yorum analizi güncellendi
- ✅ Tek platform tasarımı
- ✅ Çoklu token sistemi her iki modül için
- ✅ Modern ana sayfa
- ✅ Unified tasarım dili
- ✅ Improved error handling
- ✅ Better user experience

### v1.0.0 - İlk Versiyon
- ✅ Yorum analizi
- ✅ Çoklu token sistemi
- ✅ Admin paneli

---

Daha fazla bilgi için `COKLU_TOKEN_README.md` dosyasına bakın.
