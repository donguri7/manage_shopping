from app import db
from app.models import Item, PurchaseListItem
from datetime import datetime, timedelta
from sqlalchemy import func

def update_purchase_list():
    with db.app.app_context():
        today = datetime.utcnow().date()
        tomorrow = today + timedelta(days=1)
        
        items_to_purchase = Item.query.filter(
            func.date(func.julianday(Item.last_purchased) + Item.frequency) <= tomorrow
        ).all()
        
        for item in items_to_purchase:
            if not PurchaseListItem.query.filter_by(name=item.name, user_id=item.user_id).first():
                new_item = PurchaseListItem(name=item.name, user_id=item.user_id)
                db.session.add(new_item)
        
        db.session.commit()