from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    
    # Configuración de Login
    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'main.login' # 'main' es el blueprint, 'login' la función
    login_manager.init_app(app)
    
    from app.models import Usuario
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # IMPORTAR EL BLUEPRINT AQUÍ (evita import circular)
    from app.routes import main
    app.register_blueprint(main)

    return app
