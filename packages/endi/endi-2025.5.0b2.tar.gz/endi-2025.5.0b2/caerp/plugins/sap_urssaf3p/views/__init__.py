def includeme(config):
    config.include(".third_party.customer")
    config.include(".invoices.invoice")
    config.include(".invoices.lists")
    config.include(".admin.sale.tva")
    config.include(".admin.sap.avance_immediate")
    config.include(".payment_request")
