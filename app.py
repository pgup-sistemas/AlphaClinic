from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
import os

# Initialize extensions - import db from models to avoid duplicate instances
from models import db
migrate = Migrate()
login_manager = LoginManager()

# Import Flask-WTF for CSRF protection
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    
    # Register blueprints
    from blueprints.auth import auth_bp
    from blueprints.main import main_bp
    from blueprints.documents import documents_bp
    from blueprints.norms import norms_bp
    from blueprints.audits import audits_bp
    from blueprints.teams import teams_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(documents_bp, url_prefix='/documents')
    app.register_blueprint(norms_bp, url_prefix='/norms')
    app.register_blueprint(audits_bp, url_prefix='/audits')
    app.register_blueprint(teams_bp, url_prefix='/teams')
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)