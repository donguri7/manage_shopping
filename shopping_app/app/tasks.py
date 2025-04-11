from app import db
from app.models import Item, PurchaseListItem
from datetime import datetime, timedelta

def update_purchase_list():
    with db.app.app_context():
        today = datetime.utcnow().date()
        tomorrow = today + timedelta(days=1)

        all_items = Item.query.all()
        
        items_to_purchase = [
            item for item in all_items
            if item.last_purchased + timedelta(days=item.frequency) <= tomorrow
        ]
        
        for item in items_to_purchase:
            if not PurchaseListItem.query.filter_by(name=item.name, user_id=item.user_id).first():
                new_item = PurchaseListItem(name=item.name, user_id=item.user_id)
                db.session.add(new_item)
        
        db.session.commit()