def includeme(config):
    config.include(".routes")
    config.include(".layout")
    config.include(".invoice")
    config.include(".cancelinvoice")
    config.include(".lists")
    config.include(".rest_api")
