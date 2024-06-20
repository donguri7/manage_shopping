from flask import Blueprint, render_template, flash, redirect, url_for, request
from app import db
from app.forms import LoginForm, RegistrationForm
from app.models import User, Item
from flask_login import current_user, login_user, login_required
from werkzeug.utils import secure_filename
import os
import pytesseract
from PIL import Image

bp = Blueprint('routes', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('routes.login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('routes.index'))
    return render_template('login.html', title='Sign In', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('routes.login'))
    return render_template('register.html', title='Register', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('routes.index'))

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    items = Item.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', title='Home', items=items)

@bp.route('/upload_receipt', methods=['POST'])
@login_required
def upload_receipt():
    if 'receipt' not in request.files:
        flash('No file part')
        return redirect(url_for('routes.index'))
    file = request.files['receipt']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('routes.index'))
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join('uploads', filename)
        file.save(file_path)

        # OCRでテキストを抽出
        extracted_text = ocr_image(file_path)
        # 商品名を抽出するロジックを実装
        product_names = extract_product_names(extracted_text)

        # ここでファイル処理を行う(例：OCRでテキストを抽出)
        flash(f'Products found: {product_names}')
        return redirect(url_for('routes.index'))
    flash('File upload failed')
    return redirect(url_for('routes.index'))

def ocr_image(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text

def extract_product_names(text):
    # 簡単な商品名抽出の例。具体的には正規表現やNLP技術を使って精度を向上させる
    lines = text.split('\n')
    product_names = [line for line in lines if line.strip() and not line.isdigit()]
    return product_names