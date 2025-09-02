class PurchaseOrderApiUrl:
    PURCHASE_ORDERS = "/api/v3/purchase-orders"
    PURCHASE_ORDER_DETAILS = "/api/v3/purchase-orders/{id}"
    PURCHASE_ORDER_DELETE = "/api/v2/purchase-orders/{id}"
    PURCHASE_ORDER_REACTIVATE = '/api/v3/purchase-orders/{id}/reactivate'
    PURCHASE_ORDER_INFO = "/api/v3/purchase-orders/{id}/information"
    PURCHASE_ORDER_LINE_UUID = "/api/v3/purchase-orders/{id}/lines/{uuid}"
    PURCHASE_ORDER_LINE = "/api/v3/purchase-orders/{id}/lines"
    PURCHASE_ORDER_CREATE = "/api/v3/purchase-orders"
    PURCHASE_ORDER_CANCEL = "/api/v3/purchase-orders/{id}/cancel"
    PURCHASE_ORDER_CHANGE = "/api/v3/purchase-orders/{id}/change"
