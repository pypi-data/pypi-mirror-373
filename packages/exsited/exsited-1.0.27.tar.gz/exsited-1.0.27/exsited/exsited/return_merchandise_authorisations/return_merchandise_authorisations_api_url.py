class ReturnMerchandiseAuthorisationsApiUrl:
    LIST = '/api/v3/return-merchandise-authorisations'
    RECEIVE_LIST = '/api/v2/invoices/{id}/return-merchandise-authorisations/{rma_id}/receive'
    INVOICE_RMA_LIST = "/api/v2/invoices/{id}/return-merchandise-authorisations"
    INVOICE_RMA_DETAILS = "/api/v2/invoices/{id}/return-merchandise-authorisations/{rma_id}"
    INVOICE_RMA_CREATE = "/api/v3/invoices/{id}/return-merchandise-authorisations"
    INVOICE_RECEIVE_RMA_CREATE = "/api/v2/invoices/{id}/return-merchandise-authorisations/{rma_id}/receive"
    RECEIVE_DETAILS = "/api/v2/invoices/{id}/return-merchandise-authorisations/{rma_id}/receive/{rec_id}"
