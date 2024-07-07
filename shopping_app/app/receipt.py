from flask import Blueprint, flash, redirect, url_for, render_template, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from app.image_to_json import image_to_json
from app.json_to_products import json_to_products
from app.models import Item, db

receipt = Blueprint('receipt', __name__)

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
        if file and allowed_file(file.filename):
            try:
                json_path = image_to_json(file)
                if json_path:
                    return redirect(url_for('receipt.process_receipt', json_path=json_path))
                else:
                    flash('Image processing failed')
            except Exception as e:
                current_app.logger.error(f"Error processing image: {str(e)}")
                flash('An error occurred while processing the image')
        else:
            flash('Invalid file type')
        return redirect(url_for('receipt.upload'))
    return render_template('upload.html', title='レシートアップロード')

@receipt.route('/process', methods=['GET'])
@login_required
def process_receipt():
    json_path = request.args.get('json_path')
    if not json_path:
        flash('No JSON file specified')
        return redirect(url_for('receipt.upload'))
    
    try:
        product_json_path = json_to_products(json_path)
        if product_json_path:
            return redirect(url_for('receipt.confirm_items', product_json_path=product_json_path))
        else:
            flash('Failed to process receipt')
    except Exception as e:
        current_app.logger.error(f"Error processing JSON: {str(e)}")
        flash('An error occurred while processing the receipt')
    return redirect(url_for('receipt.upload'))

@receipt.route('/confirm', methods=['GET', 'POST'])
@login_required
def confirm_items():
    product_json_path = request.args.get('product_json_path')
    if not product_json_path:
        flash('No product JSON file specified')
        return redirect(url_for('receipt.upload'))

    if request.method == 'POST':
        try:
            for key, value in request.form.items():
                if key.startswith('item_'):
                    item_name = value
                    frequency = int(request.form.get(f'frequency_{key[5:]}', 30))
                    item = Item(name=item_name, frequency=frequency, user_id=current_user.id)
                    db.session.add(item)
            db.session.commit()
            flash('Items have been added to your list.')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding items: {str(e)}")
            flash('An error occurred while adding items')
            return redirect(url_for('receipt.upload'))

    with open(product_json_path, 'r', encoding='utf-8') as f:
        import json
        data = json.load(f)
        items = data.get('商品名', [])
    
    return render_template('confirm_items.html', items=items)

# 他のルート（view_items, delete_item, edit_item）も同様にエラーハンドリングを追加

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']