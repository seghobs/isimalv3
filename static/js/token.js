document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const submitBtn = document.getElementById('submitBtn');
            const loadingMessage = document.getElementById('loadingMessage');
            const successMessage = document.getElementById('successMessage');
            const errorMessage = document.getElementById('errorMessage');
            const kullaniciAdi = document.getElementById('kullanici_adi').value;
            const sifre = document.getElementById('sifre').value;
            const deviceId = document.getElementById('device_id').value;
            const androidId = document.getElementById('android_id').value;
            const userAgent = document.getElementById('user_agent').value;
            
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
                formData.append('device_id', deviceId);
                formData.append('android_id', androidId);
                formData.append('user_agent', userAgent);
                
                const response = await fetch('/giris_yaps', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.message || 'Eksik veya hatalı form verisi');
                }
                
                loadingMessage.style.display = 'none';
                
                if (data.success && data.token && data.android_id) {
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
                document.getElementById('errorText').textContent = error.message || 'Giriş başarısız! Bilgilerinizi kontrol edin.';
                
                // Butonu tekrar aktif et
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-sign-in-alt me-2"></i>Giriş Yap ve Token Al';
            }
        });
