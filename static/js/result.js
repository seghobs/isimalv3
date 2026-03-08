let notificationTimeout; // Bildirim zamanlayıcısı

        function kopyalaListeyi() {
            var listeElemanları = document.getElementById('eksiklerListesi').getElementsByTagName('li');
            var listeMetni = '';

            // Her bir liste elemanına @ ekleyerek liste metnini oluştur
            for (let i = 0; i < listeElemanları.length; i++) {
                listeMetni += '@' + listeElemanları[i].innerText.trim(); // @ ekle
                if (i < listeElemanları.length - 1) {
                    listeMetni += '\n'; // Her bir elemandan sonra yeni satır
                }
            }

            navigator.clipboard.writeText(listeMetni)
                .then(() => {
                    var elemanSayisi = listeElemanları.length;
                    showNotification(`Liste kopyalandı! Toplam eksik sayısı: ${elemanSayisi}`);
                })
                .catch(err => {
                    console.error('Kopyalama başarısız:', err);
                });
        }

        function filterList() {
            var input = document.getElementById('searchInput').value.toLowerCase();
            var listeElemanları = document.getElementById('eksiklerListesi').getElementsByTagName('li');

            // Her bir liste elemanını kontrol et
            for (let i = 0; i < listeElemanları.length; i++) {
                let eleman = listeElemanları[i];
                let textValue = eleman.innerText.toLowerCase();

                // Eğer arama terimi elemanın içindeyse, göster; değilse gizle
                if (textValue.indexOf(input) > -1) {
                    eleman.style.display = '';
                } else {
                    eleman.style.display = 'none';
                }
            }

            // Eleman sayısını güncelle
            var visibleCount = Array.from(listeElemanları).filter(eleman => eleman.style.display !== 'none').length;
            document.getElementById('elemanSayisi').innerText = 'Eksik Sayısı: ' + visibleCount;
        }

        function showNotification(message) {
            var notification = document.getElementById('notification');
            document.getElementById('notification-message').innerText = message;

            // Eğer bildirim açıksa, gizlemeden önce zamanlayıcıyı sıfırla
            if (notification.classList.contains('visible')) {
                clearTimeout(notificationTimeout);
                notification.classList.remove('visible');
                setTimeout(() => {
                    notification.classList.remove('hide');
                }, 500); // 0.5 saniye sonra gizle
            }

            // Bildirimi göster
            notification.classList.add('visible');

            // 3 saniye sonra kaybolması için zamanlayıcı ayarla
            notificationTimeout = setTimeout(() => {
                notification.classList.remove('visible'); // Bildirimi gizle
                setTimeout(() => {
                    notification.style.display = 'none'; // Bildirimi gizle
                }, 500); // 0.5 saniye sonra gizle
            }, 3000); // 3 saniye sonra kaybol
        }

        // Eleman sayısını gösteren fonksiyon
        window.onload = function () {
            var elemanSayisi = document.getElementById('eksiklerListesi').getElementsByTagName('li').length;
            document.getElementById('elemanSayisi').innerText = 'Eksik Sayısı: ' + elemanSayisi;
        };
