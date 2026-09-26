from flask import Flask, render_template
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import DevelopmentConfig
from app.models import db, User, Admin
from app.feature_models import WaitlistEntry, Attendance, Feedback, NotificationLog

login_manager = LoginManager()
bcrypt = Bcrypt()


def create_app(config=None):
    """Application Factory Pattern"""
    app = Flask(__name__, instance_relative_config=False)
    
    if config is None:
        config = DevelopmentConfig
    
    app.config.from_object(config)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        if user_id.startswith('admin_'):
            admin_id = int(user_id.split('_')[1])
            return Admin.query.get(admin_id)
        elif user_id.startswith('user_'):
            uid = int(user_id.split('_')[1])
            return User.query.get(uid)
        return None
    
    # Create upload folders
    import os
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['QRCODE_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.user import user_bp
    from app.routes.admin import admin_bp
    from app.routes.patient import patient_bp
    from app.routes.features import features_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(features_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Page not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app
