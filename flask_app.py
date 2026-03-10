from flask import Flask
import logging
import flask.cli
from modules.admin import admin_bp
from modules.auth import auth_bp
from modules.main_routes import main_bp
from modules.dm_routes import dm_bp

app = Flask(__name__)
app.secret_key = 'seho_admin_panel_secret_key_2024'  # Session için gerekli

# Blueprintleri kaydet (Modül tabanlı mimari)
app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(dm_bp)

if __name__ == '__main__':
    flask.cli.show_server_banner = lambda *args, **kwargs: None
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    host = '127.0.0.1'
    port = 5000
    print(f"Server basladi. Su adresten ulasabilirsiniz: http://{host}:{port}")
    app.run(host=host, port=port, debug=False, use_reloader=False)
