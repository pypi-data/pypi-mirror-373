def includeme(config):
    config.add_route(
        "/estimations/{id}/gen_supplier_order",
        "/estimations/{id}/gen_supplier_order",
        traverse="/tasks/{id}",
    )
    config.add_route(
        "/invoices/{id}/gen_supplier_invoice",
        "/invoices/{id}/gen_supplier_invoice",
        traverse="/tasks/{id}",
    )
    config.add_route(
        "/cancelinvoices/{id}/gen_supplier_invoice",
        "/cancelinvoices/{id}/gen_supplier_invoice",
        traverse="/tasks/{id}",
    )
