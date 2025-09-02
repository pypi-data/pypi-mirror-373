from exsited.exsited.order.dto.order_dto import OrderDataDTO
from order_usage_db.connect_with_db import DatabaseConnection
from order_usage_db.order_manager import OrderManager
from order_usage_db.order_service import OrderService


class SaveToDB:
    def process_order_data(_order_id: str, _account_id: str, _item_id: str, _item_name: str, _charge_item_uuid: str):
        order_manager = OrderManager('usage_item_association', 'root', '', '127.0.0.1')
        order_manager.connect_to_db()
        order_manager.process_order(
            account_id=_account_id,
            order_id=_order_id,
            item_id=_item_id,
            item_name=_item_name,
            charge_item_uuid=_charge_item_uuid
        )
        order_manager.disconnect_from_db()
