from order_usage_db.connect_with_db import DatabaseConnection
from order_usage_db.order_service import OrderService


class OrderManager:
    def __init__(self, db_name, user, password, host):
        self.db_connection = DatabaseConnection(db_name, user, password, host)
        self.order_service = None

    def connect_to_db(self):
        self.db_connection.connect()
        self.order_service = OrderService(self.db_connection)

    def disconnect_from_db(self):
        self.db_connection.close()

    def process_order(self, account_id: str, order_id: str, item_id: str, item_name: str, charge_item_uuid: str):
        new_order = self.order_service.create_association_data(
            account_id=account_id,
            order_id=order_id,
            item_id=item_id,
            item_name=item_name,
            charge_item_uuid=charge_item_uuid
        )
        print(f"Created Order ID: {new_order.id}")

    def fetch_order(self, order_id: str):
        order = self.order_service.get_order_by_id(order_id)
        if order:
            print(f"Order Found: {order.item_name}")
        else:
            print("Order not found.")
