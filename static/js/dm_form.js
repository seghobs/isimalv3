function setDate(daysOffset) {
            const dateInput = document.getElementById('date');
            const today = new Date();
            today.setDate(today.getDate() + daysOffset);
            const formattedDate = today.toISOString().split('T')[0];
            dateInput.value = formattedDate;
        }

        function setTime(time) {
            const timeInput = document.getElementById('time');
            timeInput.value = time;
        }

        function setMax(max) {
            const maxInput = document.getElementById('max');
            maxInput.value = max;
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
