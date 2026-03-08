function updateUserCount() {
            const textarea = document.getElementById('grup_uye');
            const userCountDisplay = document.getElementById('user_count');
            const users = textarea.value.split('\n').filter(user => user.trim() !== '');
            userCountDisplay.textContent = `${users.length} Adet kullanıcı eklendi.`;
        }
