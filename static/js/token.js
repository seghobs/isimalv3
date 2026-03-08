document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const submitBtn = document.getElementById('submitBtn');
            const loadingMessage = document.getElementById('loadingMessage');
            const successMessage = document.getElementById('successMessage');
            const errorMessage = document.getElementById('errorMessage');
            const kullaniciAdi = document.getElementById('kullanici_adi').value;
            const sifre = document.getElementById('sifre').value;
            
            // Buton ve mesajları güncelle
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Yüklenilyor...';
            loadingMessage.style.display = 'block';
            successMessage.style.display = 'none';
            errorMessage.style.display = 'none';
            
            try {
                const formData = new FormData();
                formData.append('kullanici_adi', kullaniciAdi);
                formData.append('sifre', sifre);
                
                const response = await fetch('/giris_yaps', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                loadingMessage.style.display = 'none';
                
                if (data.token && data.android_id_yeni) {
                    // Başarılı
                    successMessage.style.display = 'block';
                    document.getElementById('successText').textContent = 'Token başarıyla alındı! Ana sayfaya yönlendiriliyorsunuz...';
                    
                    // 2 saniye sonra ana sayfaya yönlendir
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 2000);
                } else {
                    throw new Error('Token alınamadı');
                }
            } catch (error) {
                loadingMessage.style.display = 'none';
                errorMessage.style.display = 'block';
                document.getElementById('errorText').textContent = 'Giriş başarısız! Kullanıcı adı veya şifrenizi kontrol edin.';
                
                // Butonu tekrar aktif et
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-sign-in-alt me-2"></i>Giriş Yap ve Token Al';
            }
        });
