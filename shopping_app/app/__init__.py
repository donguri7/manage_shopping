from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_apscheduler import APScheduler
import os
import logging

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
scheduler = APScheduler()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    from app.auth_routes import auth as auth_blueprint
    from app.main import bp as main_blueprint
    from app.receipt import receipt as receipt_blueprint
    from app.item_routes import item as item_blueprint

    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(main_blueprint)
    app.register_blueprint(receipt_blueprint, url_prefix='/receipt')
    app.register_blueprint(item_blueprint, url_prefix='/item')

    # エラーハンドリングとログ機能の追加
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        try:
            os.makedirs(app.config['UPLOAD_FOLDER'])
        except OSError as e:
            app.logger.error(f"Error creating upload folder: {e}")

    # ログ設定
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = logging.FileHandler('logs/shopping_app.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Shopping app startup')

    # スケジューラーの初期化と購入リスト更新ジョブの追加
    init_scheduler(app)

    return app

def init_scheduler(app):
    scheduler.init_app(app)
    scheduler.start()
    
    from app.tasks import update_purchase_list
    scheduler.add_job(id='update_purchase_list', func=update_purchase_list, trigger='interval', hours=24)
