from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from dotenv import load_dotenv
import os
from datetime import date

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__, static_folder='static')

    # =========================
    # CONFIG
    # =========================
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret')

    # 🔥 FIX: PostgreSQL dari Render
    uri = os.getenv("DATABASE_URL")

    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['BASE_URL'] = os.getenv('BASE_URL', 'http://localhost:5000')
    app.config['QR_FOLDER'] = os.path.join(app.root_path, 'static', 'qrcodes')

    # =========================
    # EXTENSIONS
    # =========================
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    CORS(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # =========================
    # FIX ERROR JINJA (today)
    # =========================
    @app.context_processor
    def inject_today():
        return dict(today=date.today())

    # =========================
    # IMPORT MODELS
    # =========================
    from models.user import User
    from models.product import Product
    from models.batch import Batch
    from models.scan_log import ScanLog

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # =========================
    # REGISTER BLUEPRINTS
    # =========================
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.product import product_bp
    from routes.qr import qr_bp
    from routes.public import public_bp

    app.register_blueprint(auth_bp,      url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(product_bp,   url_prefix='/product')
    app.register_blueprint(qr_bp,        url_prefix='/qr')
    app.register_blueprint(public_bp,    url_prefix='/')

    # =========================
    # FIX HTTPS RENDER
    # =========================
    if os.environ.get("RENDER"):
        app.config['PREFERRED_URL_SCHEME'] = 'https'

    return app