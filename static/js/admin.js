function showAlert(message, type = 'success') {
            const alertContainer = document.getElementById('alertContainer');
            const alert = document.createElement('div');
            alert.className = `alert alert-${type}`;
            
            const icon = type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle';
            alert.innerHTML = `<i class="fas fa-${icon}"></i><span>${message}</span>`;
            
            alertContainer.appendChild(alert);
            
            setTimeout(() => {
                alert.remove();
            }, 5000);
        }
        
        async function loadTokens() {
            const loading = document.getElementById('loading');
            const tokensList = document.getElementById('tokensList');
            
            loading.classList.add('show');
            tokensList.innerHTML = '';
            
            try {
                const response = await fetch('/admin/get_tokens');
                const data = await response.json();
                
                if (!data.success) {
                    throw new Error(data.message || 'Token yüklenemedi');
                }
                
                loading.classList.remove('show');
                
                const tokens = data.accounts || data.tokens || [];
                
                if (tokens.length === 0) {
                    tokensList.innerHTML = `
                        <div class="empty-state">
                            <i class="fas fa-inbox"></i>
                            <p>Henüz eklenmiş token yok.<br>Yukarıdaki formu kullanarak token ekleyin.</p>
                        </div>
                    `;
                    return;
                }
                
                tokens.forEach((token, index) => {
                    const tokenCard = createTokenCard(token, index);
                    tokensList.appendChild(tokenCard);
                });
                
            } catch (error) {
                loading.classList.remove('show');
                showAlert(error.message, 'error');
            }
        }
        
        function createTokenCard(token, index) {
            const card = document.createElement('div');
            card.className = `token-card ${token.is_active ? '' : 'inactive'}`;
            
            const statusText = token.is_active ? 'Aktif' : 'Pasif';
            const statusClass = token.is_active ? 'active' : 'inactive';
            
            const fullNameDisplay = token.full_name ? `<div style="color: rgba(255, 255, 255, 0.6); font-size: 14px; margin-top: 5px;">${token.full_name}</div>` : '';
            
            // Logout reason varsa göster
            const logoutReasonDisplay = token.logout_reason ? `
                <div style="background: rgba(231, 76, 60, 0.15); border: 1px solid rgba(231, 76, 60, 0.3); border-radius: 8px; padding: 12px; margin: 10px 0;">
                    <div style="color: #e74c3c; font-weight: 600; font-size: 13px; margin-bottom: 5px;">
                        <i class="fas fa-exclamation-circle"></i> Çıkış Yapıldı
                    </div>
                    <div style="color: rgba(255, 255, 255, 0.8); font-size: 12px;">
                        ${token.logout_reason}
                    </div>
                    ${token.logout_time ? `<div style="color: rgba(255, 255, 255, 0.5); font-size: 11px; margin-top: 5px;">
                        ${new Date(token.logout_time).toLocaleString('tr-TR')}
                    </div>` : ''}
                </div>
            ` : '';
            
            card.innerHTML = `
                <div class="token-header">
                    <div>
                        <span class="token-username"><i class="fab fa-instagram"></i> @${token.username}</span>
                        ${fullNameDisplay}
                    </div>
                    <span class="token-status ${statusClass}">${statusText}</span>
                </div>
                
                ${logoutReasonDisplay}
                
                <div class="token-info">
                    <strong>Token:</strong>
                    <div class="token-value">${token.token.substring(0, 60)}...</div>
                </div>
                
                <div class="token-info">
                    <strong>Android ID:</strong> <span class="token-value" style="display: inline-block;">${token.android_id_yeni}</span>
                </div>
                
                <div class="token-info">
                    <strong>Device ID:</strong> <span class="token-value" style="display: inline-block;">${token.device_id || '<em style="color:rgba(255,255,255,0.4)">Yok (otomatik atanır)</em>'}</span>
                </div>
                
                <div class="token-info">
                    <strong>Eklenme Tarihi:</strong> ${token.added_at ? new Date(token.added_at).toLocaleString('tr-TR') : 'Bilinmiyor'}
                </div>
                
                <div class="token-actions">
                    <button class="btn" onclick="editToken('${token.username}')">
                        <i class="fas fa-edit"></i> Düzenle
                    </button>
                    ${token.password ? `
                        <button class="btn" style="background: rgba(52, 152, 219, 0.2); border-color: rgba(52, 152, 219, 0.4);" onclick="reloginToken('${token.username}')">
                            <i class="fas fa-sync-alt"></i> Tekrar Giriş Yap
                        </button>
                    ` : ''}
                    <button class="btn btn-warning" onclick="toggleToken('${token.username}')">
                        <i class="fas fa-toggle-${token.is_active ? 'off' : 'on'}"></i> ${token.is_active ? 'Pasif Yap' : 'Aktif Yap'}
                    </button>
                    <button class="btn btn-success" onclick="validateToken('${token.username}')">
                        <i class="fas fa-check-circle"></i> Doğrula
                    </button>
                    <button class="btn btn-danger" onclick="deleteToken('${token.username}')">
                        <i class="fas fa-trash"></i> Sil
                    </button>
                </div>
            `;
            
            return card;
        }
        
        async function toggleToken(username) {
            try {
                const response = await fetch('/admin/toggle_token', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showAlert(data.message, 'success');
                    loadTokens();
                } else {
                    showAlert(data.message, 'error');
                }
            } catch (error) {
                showAlert('Bir hata oluştu: ' + error.message, 'error');
            }
        }
        
        async function validateToken(username) {
            showAlert('Token doğrulanıyor...', 'info');
            
            try {
                const response = await fetch('/admin/validate_token', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    if (data.is_valid) {
                        showAlert(`✓ ${username} için token geçerli!`, 'success');
                    } else {
                        showAlert(`✗ ${username} için token geçersiz! Otomatik olarak pasif yapıldı.`, 'error');
                        loadTokens();
                    }
                } else {
                    showAlert(data.message, 'error');
                }
            } catch (error) {
                showAlert('Bir hata oluştu: ' + error.message, 'error');
            }
        }
        
        async function deleteToken(username) {
            if (!confirm(`⚠️ ${username} için tokeni silmek istediğinizden emin misiniz?`)) {
                return;
            }
            
            try {
                const response = await fetch('/admin/delete_token', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showAlert(data.message, 'success');
                    loadTokens();
                } else {
                    showAlert(data.message, 'error');
                }
            } catch (error) {
                showAlert('Bir hata oluştu: ' + error.message, 'error');
            }
        }
        
        document.getElementById('addTokenForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = {
                token: document.getElementById('token').value.trim(),
                android_id: document.getElementById('android_id').value.trim(),
                device_id: document.getElementById('device_id').value.trim(),
                user_agent: document.getElementById('user_agent').value.trim(),
                password: document.getElementById('password').value.trim(),
                is_active: true,
                added_at: new Date().toISOString()
            };
            
            if (!formData.token || !formData.android_id || !formData.user_agent) {
                showAlert('Lütfen tüm alanları doldurun!', 'error');
                return;
            }
            
            showAlert('Token doğrulanıyor ve kullanıcı adı alınıyor...', 'info');
            
            try {
                const response = await fetch('/admin/add_token', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    const successMsg = data.username && data.full_name 
                        ? `✓ Token başarıyla eklendi: @${data.username} (${data.full_name})` 
                        : data.message;
                    showAlert(successMsg, 'success');
                    document.getElementById('addTokenForm').reset();
                    loadTokens();
                } else {
                    showAlert(data.message, 'error');
                }
            } catch (error) {
                showAlert('Bir hata oluştu: ' + error.message, 'error');
            }
        });
        
        // Tekrar giriş yap
        async function reloginToken(username) {
            if (!confirm(`@${username} için tekrar giriş yapılacak ve token yenilenecek. Devam edilsin mi?`)) {
                return;
            }
            
            showAlert('Tekrar giriş yapılıyor...', 'info');
            
            try {
                const response = await fetch('/admin/relogin_token', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showAlert(data.message, 'success');
                    loadTokens();
                } else {
                    showAlert(data.message, 'error');
                }
            } catch (error) {
                showAlert('Bir hata oluştu: ' + error.message, 'error');
            }
        }
        
        // Token düzenleme modalini aç
        async function editToken(username) {
            try {
                const response = await fetch('/admin/get_tokens');
                const data = await response.json();
                
                if (!data.success) {
                    showAlert('Tokenler yüklenemedi', 'error');
                    return;
                }
                
                const tokens = data.accounts || data.tokens || [];
                const token = tokens.find(t => t.username === username);
                
                if (!token) {
                    showAlert('Token bulunamadı', 'error');
                    return;
                }
                
                // Form alanlarını doldur
                document.getElementById('edit_username').value = token.username;
                document.getElementById('edit_username_display').value = '@' + token.username + (token.full_name ? ' (' + token.full_name + ')' : '');
                document.getElementById('edit_token').value = token.token;
                document.getElementById('edit_android_id').value = token.android_id_yeni;
                document.getElementById('edit_device_id').value = token.device_id || '';
                document.getElementById('edit_user_agent').value = token.user_agent;
                
                // Modalı aç
                document.getElementById('editModal').classList.add('show');
                
            } catch (error) {
                showAlert('Bir hata oluştu: ' + error.message, 'error');
            }
        }
        
        // Modalı kapat
        function closeEditModal() {
            document.getElementById('editModal').classList.remove('show');
        }
        
        // Modal dışına tıklanınca kapat
        document.getElementById('editModal').addEventListener('click', (e) => {
            if (e.target.id === 'editModal') {
                closeEditModal();
            }
        });
        
        // ESC tuşuyla modal kapat
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closeEditModal();
            }
        });
        
        // Düzenleme formunu gönder
        document.getElementById('editTokenForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('edit_username').value;
            const formData = {
                username: username,
                token: document.getElementById('edit_token').value.trim(),
                android_id: document.getElementById('edit_android_id').value.trim(),
                device_id: document.getElementById('edit_device_id').value.trim(),
                user_agent: document.getElementById('edit_user_agent').value.trim()
            };
            
            if (!formData.token || !formData.android_id || !formData.user_agent) {
                showAlert('Lütfen tüm alanları doldurun!', 'error');
                return;
            }
            
            showAlert('Token güncelleniyor...', 'info');
            
            try {
                const response = await fetch('/admin/update_token', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showAlert(data.message, 'success');
                    closeEditModal();
                    loadTokens();
                } else {
                    showAlert(data.message, 'error');
                }
            } catch (error) {
                showAlert('Bir hata oluştu: ' + error.message, 'error');
            }
        });
        
        // Sayfa yüklenirken tokenleri yükle
        loadTokens();
        
        // Her 30 saniyede bir otomatik yenile
        setInterval(loadTokens, 30000);