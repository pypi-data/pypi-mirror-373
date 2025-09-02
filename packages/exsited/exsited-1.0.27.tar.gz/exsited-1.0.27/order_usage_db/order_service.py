from order_usage_db.order_model import Order


class OrderService:
    def __init__(self, db_connection):
        self.db = db_connection.get_db()
        Order._meta.database = self.db

    def create_association_data(self, account_id, order_id, item_id, item_name, charge_item_uuid):
        with self.db.atomic():
            new_order = Order.create(
                account_id=account_id,
                order_id=order_id,
                item_id=item_id,
                item_name=item_name,
                charge_item_uuid=charge_item_uuid
            )
        return new_order

    def get_order_by_id(self, order_id):
        try:
            order = Order.get(Order.order_id == order_id)
            return order
        except Order.DoesNotExist:
            return None
