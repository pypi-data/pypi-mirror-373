class InvoiceApiUrl:
    INVOICES = "/api/v3/invoices"
    INVOICE_CREATE = "/api/v2/orders/{id}/invoices"
    EACH_INVOICE = "/api/v2/orders/{id}/invoices"
    EACH_INVOICE_V3 = "/api/v3/orders/{id}/invoices"
    INVOICE_INFORMATION = '/api/v2/invoices/{id}/information'
    INVOICE_ACCOUNT = '/api/v3/accounts/{id}/invoices'
    INVOICE_DELETE = '/api/v2/invoices/{id}'
    INVOICE_UPDATE_AMEND = '/api/v2/invoices/{id}/amend'
