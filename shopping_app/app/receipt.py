from flask import Blueprint, flash, redirect, url_for, render_template, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from app.image_to_json import image_to_json
from app.json_to_products import json_to_products
from app.models import Item, db

receipt = Blueprint('receipt', __name__)


# 1. レシート画像のアップロード
# 2. 画像からJSONへの変換（image_to_jsonを使用）
# 3. JSONから商品名の抽出（json_to_productsを使用）
# 4. 抽出された商品名の確認と保存
# 5. 保存された商品リストの表示
# 6. 商品の編集と削除

@receipt.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_receipt():
    if request.method == 'POST':
        if 'receipt' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['receipt']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            json_path = image_to_json(file)
            if json_path:
                return redirect(url_for('receipt.process_receipt', json_path=json_path))
            else:
                flash('Image processing failed')
                return redirect(url_for('receipt.upload'))
    return render_template('upload.html')

@receipt.route('/process', methods=['GET'])
@login_required
def process_receipt():
    json_path = request.args.get('json_path')
    if not json_path:
        flash('No JSON file specified')
        return redirect(url_for('receipt.upload'))
    
    product_json_path = json_to_products(json_path)
    if product_json_path:
        return redirect(url_for('receipt.confirm_items', product_json_path=product_json_path))
    else:
        flash('Failed to process receipt')
        return redirect(url_for('receipt.upload'))

@receipt.route('/confirm', methods=['GET', 'POST'])
@login_required
def confirm_items():
    product_json_path = request.args.get('product_json_path')
    if not product_json_path:
        flash('No product JSON file specified')
        return redirect(url_for('receipt.upload'))

    if request.method == 'POST':
        for key, value in request.form.items():
            if key.startswith('item_'):
                item_name = value
                frequency = int(request.form.get(f'frequency_{key[5:]}', 30))  # デフォルト値は30日
                item = Item(name=item_name, frequency=frequency, user_id=current_user.id)
                db.session.add(item)
        db.session.commit()
        flash('Items have been added to your list.')
        return redirect(url_for('main.index'))

    # GET リクエストの場合、JSONファイルから商品名を読み込む
    with open(product_json_path, 'r', encoding='utf-8') as f:
        import json
        data = json.load(f)
        items = data.get('商品名', [])
    
    return render_template('confirm_items.html', items=items)

@receipt.route('/items')
@login_required
def view_items():
    items = Item.query.filter_by(user_id=current_user.id).all()
    return render_template('items.html', items=items)

@receipt.route('/item/<int:id>/delete', methods=['POST'])
@login_required
def delete_item(id):
    item = Item.query.get_or_404(id)
    if item.user_id != current_user.id:
        flash('You do not have permission to delete this item.')
        return redirect(url_for('receipt.view_items'))
    db.session.delete(item)
    db.session.commit()
    flash('Item has been deleted.')
    return redirect(url_for('receipt.view_items'))

@receipt.route('/item/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(id):
    item = Item.query.get_or_404(id)
    if item.user_id != current_user.id:
        flash('You do not have permission to edit this item.')
        return redirect(url_for('receipt.view_items'))
    
    if request.method == 'POST':
        item.name = request.form['name']
        item.frequency = int(request.form['frequency'])
        db.session.commit()
        flash('Item has been updated.')
        return redirect(url_for('receipt.view_items'))
    
    return render_template('edit_item.html', item=item)