from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'

def create_app():
    app = Flask(__name__) # Flask instance create
    app.config.from_object('config.Config') # app setting from config.py

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    from app.auth_routes import auth as auth_blueprint # 認証
    from app.main import bp as main_blueprint # メイン
    from app.receipt import receipt as receipt_blueprint # レシート処理
    from app.item_routes import item as item_blueprint

    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(main_blueprint)
    app.register_blueprint(receipt_blueprint, url_prefix='/receipt')
    app.register_blueprint(item_blueprint, url_prefix='/item')

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    return app