function updateUserCount() {
            const textarea = document.getElementById('grup_uye');
            const userCountDisplay = document.getElementById('user_count');
            const users = textarea.value.split('\n').filter(user => user.trim() !== '');
            userCountDisplay.textContent = `${users.length} Adet kullanıcı eklendi.`;
        }
function checkTokens() {
            fetch('/api/check_active_tokens')
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.active_count === 0 && data.total_count > 0) {
                        document.getElementById('tokenWarningModal').style.display = 'flex';
                    } else if (data.success && data.active_count > 0) {
                        document.getElementById('tokenWarningModal').style.display = 'none';
                    }
                })
                .catch(err => console.error('Token check error:', err));
        }
        window.addEventListener('DOMContentLoaded', () => {
            checkTokens();
            setInterval(checkTokens, 30000);
        });
