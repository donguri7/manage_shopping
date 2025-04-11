import os
from datetime import timedelta

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-very-secret-and-random-key-here'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    # ALLOWED_EXTENSIONS を追加
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # セッションの設定
    PERMANENT_SESSION_LIFETIME = timedelta(days=31)  # セッションの有効期限を31日に設定
    SESSION_TYPE = 'filesystem'  # セッションをファイルシステムに保存
    SESSION_FILE_DIR = os.path.join(BASE_DIR, 'flask_session')  # セッションファイルの保存場所

    # CSRFプロテクション
    WTF_CSRF_ENABLED = True

    # その他のアプリケーション設定
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 最大アップロードサイズを16MBに制限
