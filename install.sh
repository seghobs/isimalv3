#!/bin/bash
# Instagram Analiz V3 Kurulum Dosyası (PythonAnywhere & Linux)
# Kullanım: wget -qO- https://raw.githubusercontent.com/seghobs/isimalv3/main/install.sh | bash

echo "========================================="
echo "  Instagram Analiz v3 Kurulumu Basliyor  "
echo "========================================="
echo ""

# Repoyu kopyala
REPO_URL="https://github.com/seghobs/isimalv3.git"
DIR_NAME="isimalv3"

if [ -d "$DIR_NAME" ]; then
    echo "[!] Klasor zaten mevcut. Guncelleme yapiliyor..."
    cd $DIR_NAME
    git pull
else
    echo "[+] Proje Github'dan indiriliyor..."
    git clone $REPO_URL
    cd $DIR_NAME
fi

# Gerekli dosya izinlerini ayarla
echo "[+] Dosya izinleri ayarlaniyor..."
chmod -R 755 .

# Eger sqlite DB yoksa bos olustur ve 777 izni ver
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
echo "isimalv3 klasorunu gorecek sekilde yapilandirmayi unutmayin."
echo "Otomatik calisma izinleri verildi. Iyi kullanimlar!"
