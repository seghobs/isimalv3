function copyToClipboard() {
            const userList = document.querySelectorAll('.user-item span');
            let text = '';
            userList.forEach(user => {
                text += user.textContent + '\n';
            });
            
            // Samsung uyumlu kopyalama (fallback mekanizması)
            if (navigator.clipboard && navigator.clipboard.writeText) {
                // Modern API (Poco X3 Pro gibi telefonlar)
                navigator.clipboard.writeText(text).then(() => {
                    const btn = document.querySelector('.copy-btn');
                    const originalHTML = btn.innerHTML;
                    btn.innerHTML = '<i class="fas fa-check"></i> Kopyalandı!';
                    btn.classList.add('copied');
                    
                    setTimeout(() => {
                        btn.innerHTML = originalHTML;
                        btn.classList.remove('copied');
                    }, 2000);
                }).catch(err => {
                    console.log('Modern API başarısız, eski metod deneniyor...', err);
                    // Eski metod ile tekrar dene (Samsung A25 için)
                    fallbackCopyTextToClipboard(text);
                });
            } else {
                // Eski metod (Samsung Internet Browser için)
                fallbackCopyTextToClipboard(text);
            }
        }

        // Samsung ve eski tarayıcılar için fallback fonksiyonu
        function fallbackCopyTextToClipboard(text) {
            var textArea = document.createElement('textarea');
            textArea.value = text;
            
            // Ekrandan gizle
            textArea.style.position = 'fixed';
            textArea.style.top = '0';
            textArea.style.left = '0';
            textArea.style.width = '2em';
            textArea.style.height = '2em';
            textArea.style.padding = '0';
            textArea.style.border = 'none';
            textArea.style.outline = 'none';
            textArea.style.boxShadow = 'none';
            textArea.style.background = 'transparent';
            textArea.style.opacity = '0';
            
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            
            try {
                var successful = document.execCommand('copy');
                
                if (successful) {
                    const btn = document.querySelector('.copy-btn');
                    const originalHTML = btn.innerHTML;
                    btn.innerHTML = '<i class="fas fa-check"></i> Kopyalandı!';
                    btn.classList.add('copied');
                    
                    setTimeout(() => {
                        btn.innerHTML = originalHTML;
                        btn.classList.remove('copied');
                    }, 2000);
                } else {
                    alert('✗ Kopyalama başarısız! Tarayıcınız desteklemiyor.');
                }
            } catch (err) {
                console.error('Fallback kopyalama başarısız:', err);
                alert('✗ Kopyalama başarısız: ' + err.message);
            }
            
            document.body.removeChild(textArea);
        }
