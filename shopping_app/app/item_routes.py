from flask import Blueprint, flash, redirect, url_for, render_template, request, session, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.forms import ItemForm
from app.models import Item

item = Blueprint('item', __name__)

@item.route('/add_item', methods=['GET', 'POST'])
@login_required
def add_item():
    form = ItemForm()
    if form.validate_on_submit():
        item = Item(name=form.name.data, frequency=form.frequency.data, owner=current_user)
        db.session.add(item)
        db.session.commit()
        flash('Item added successfully.')
        return redirect(url_for('item.item_added', item_id=item.id))
    return render_template('add_item.html', title='Add Item', form=form)

@item.route('/item_added/<int:item_id>', methods=['GET'])
@login_required
def item_added(item_id):
    item = Item.query.get_or_404(item_id)
    return render_template('item_added.html', item=item)

@item.route('/view_items')
@login_required
def view_items():
    items = Item.query.filter_by(user_id=current_user.id).all()
    return render_template('items.html', items=items)

@item.route('/edit_item/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_item(id):
    item = Item.query.get_or_404(id)
    if item.user_id != current_user.id:
        flash('You do not have permission to edit this item.')
        return redirect(url_for('item.view_items'))
    
    form = ItemForm(obj=item)
    if form.validate_on_submit():
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

@item.route('/confirm_items', methods=['GET', 'POST'])
@login_required
def confirm_items():
    if request.method == 'POST':
        items = []
        for key, value in request.form.items():
            if key.startswith('item_'):
                index = key.split('_')[1]
                frequency = request.form.get(f'frequency_{index}', 30)
                items.append({
                    'name': value,
                    'frequency': int(frequency)
                })
        
        try:
            for item_data in items:
                item = Item(name=item_data['name'], frequency=item_data['frequency'], user_id=current_user.id)
                db.session.add(item)
            db.session.commit()
            flash('Items have been added to your list.')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding items. Please try again.')
            current_app.logger.error(f"Error adding items: {e}")
        
        return redirect(url_for('item.view_items'))
    
    items = session.get('product_names', [])
    return render_template('confirm_items.html', items=items)