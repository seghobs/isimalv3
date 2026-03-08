#!/bin/bash
# Instagram Analiz V3 Kurulum Dosyası (PythonAnywhere & Linux)
# Kullanım: wget -qO- https://raw.githubusercontent.com/seghobs/isimalv3/main/install.sh | bash

echo "========================================="
echo "  Instagram Analiz v3 Kurulumu Basliyor  "
echo "========================================="
echo ""

# Repoyu gecerli dizine (bulunulan klasore) kopyala
REPO_URL="https://github.com/seghobs/isimalv3.git"

echo "[+] Proje dosyalari bulundugunuz dizine (alt klasor olusturmadan) indiriliyor..."
if [ ! -d ".git" ]; then
    git init
    git remote add origin $REPO_URL
fi
git fetch --all
git reset --hard origin/main

# Gerekli dosya izinlerini ayarla
echo "[+] Dosya izinleri ayarlaniyor..."
chmod -R 755 .

# Eger sqlite DB yoksa bos olustur ve 666 izni ver
if [ ! -f "tokens.db" ]; then
    touch tokens.db
fi
chmod 666 tokens.db

# Virtual Environment veya bagimliliklari kur
echo "[+] Python bagimliliklari kuruluyor (pip)..."
pip3 install --user -r requirements.txt

echo "========================================="
echo "  Kurulum Basariyla Tamamlandi!          "
echo "========================================="
echo "UYARI: PythonAnywhere uzerinde calisiyorsaniz, Web sekmesinden projenizi (WSGI ayarini) "
echo "gecerli klasoru gosterecek sekilde yapilandirmayi unutmayin."
echo "Otomatik calisma izinleri verildi. Iyi kullanimlar!"
