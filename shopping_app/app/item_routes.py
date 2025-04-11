from flask import Blueprint, flash, redirect, url_for, render_template, request, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app import db
from app.forms import ItemForm
from app.models import Item, PurchaseListItem
from datetime import datetime, timedelta

item = Blueprint('item', __name__)

@item.route('/add_item', methods=['GET', 'POST'])
@login_required
def add_item():
    form = ItemForm()
    if form.validate_on_submit():
        # 既存の商品を検索
        existing_item = Item.query.filter_by(name=form.name.data, user_id=current_user.id).first()
        if existing_item:
            # 既存の商品がある場合は更新
            existing_item.frequency = form.frequency.data
            flash('Item updated successfully.')
        else:
            # 新しい商品を追加
            new_item = Item(name=form.name.data, frequency=form.frequency.data, user_id=current_user.id)
            db.session.add(new_item)
            flash('Item added successfully.')
        db.session.commit()
        return redirect(url_for('item.view_items'))
    return render_template('add_item.html', title='Add Item', form=form)

@item.route('/view_items')
@login_required
def view_items():
    items = Item.query.filter_by(user_id=current_user.id).all()
    current_app.logger.info(f"User {current_user.username} has {len(items)} items.")
    current_date = datetime.utcnow().date()
    return render_template('items.html', items=items, timedelta=timedelta, current_date=current_date)

@item.route('/edit_item/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_item(id):
    item = Item.query.get_or_404(id)
    if item.user_id != current_user.id:
        flash('You do not have permission to edit this item.')
        return redirect(url_for('item.view_items'))
    
    form = ItemForm(obj=item)
    if form.validate_on_submit():
        # 同じ名前の商品が既に存在するか確認
        existing_item = Item.query.filter(Item.name == form.name.data, Item.id != id, Item.user_id == current_user.id).first()
        if existing_item:
            flash('An item with this name already exists.')
            return render_template('edit_item.html', form=form, item=item)
        
        form.populate_obj(item)
        db.session.commit()
        flash('Item has been updated successfully.')
        return redirect(url_for('item.view_items'))
    
    return render_template('edit_item.html', form=form, item=item)

@item.route('/delete_item/<int:id>', methods=['POST'])
@login_required
def delete_item(id):
    item = Item.query.get_or_404(id)
    if item.user_id != current_user.id:
        flash('You do not have permission to delete this item.')
        return redirect(url_for('item.view_items'))
    
    db.session.delete(item)
    db.session.commit()
    flash('Item has been deleted.')
    return redirect(url_for('item.view_items'))

@item.route('/purchase_list')
@login_required
def purchase_list():
    purchase_list_items = PurchaseListItem.query.filter_by(user_id=current_user.id).all()
    
    today = datetime.utcnow().date()
    tomorrow = today + timedelta(days=1)
    
    all_items = Item.query.filter(Item.user_id == current_user.id).all()

    items_to_purchase = [
        item for item in all_items
        if item.last_purchased + timedelta(days=item.frequency) <= tomorrow
    ]
    
    for item in items_to_purchase:
        if not PurchaseListItem.query.filter_by(name=item.name, user_id=current_user.id).first():
            new_item = PurchaseListItem(name=item.name, user_id=current_user.id)
            db.session.add(new_item)
    
    db.session.commit()
    
    purchase_list_items = PurchaseListItem.query.filter_by(user_id=current_user.id).all()
    
    return render_template('purchase_list.html', items=purchase_list_items)

@item.route('/delete_purchase_items', methods=['POST'])
@login_required
def delete_purchase_items():
    item_ids = request.form.getlist('item_ids')
    today = datetime.utcnow().date()
    
    for item_id in item_ids:
        purchase_item = PurchaseListItem.query.get(item_id)
        if purchase_item and purchase_item.user_id == current_user.id:
            list_item = Item.query.filter_by(name=purchase_item.name, user_id=current_user.id).first()
            if list_item:
                list_item.last_purchased = today
                db.session.add(list_item)
            
            db.session.delete(purchase_item)
    
    db.session.commit()
    flash('選択された項目が削除され、次回購入日が更新されました。', 'success')
    return redirect(url_for('item.purchase_list'))