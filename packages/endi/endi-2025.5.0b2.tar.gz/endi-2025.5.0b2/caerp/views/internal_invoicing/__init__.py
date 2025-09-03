def includeme(config):
    config.include(".routes")
    config.include(".views")
    config.include(".rest_api")
    config.include("caerp.views.admin.sale.accounting.internal_invoicing_numbers")
