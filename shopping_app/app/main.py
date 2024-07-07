from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Item
from datetime import datetime, timedelta

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    items = Item.query.filter_by(user_id=current_user.id).all()
    notifications = [f"It's time to buy {item.name}!"
                     for item in items
                     if datetime.utcnow() - item.last_purchased >= timedelta(days=item.frequency)]
    return render_template('index.html', title='Home', items=items, notifications=notifications)