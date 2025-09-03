def includeme(config):
    config.add_route("login", "/login")
    config.add_route("logout", "/logout")
    config.add_route("apiloginv1", "/api/v1/login")
    config.add_route("nosupport", "/nosupport")
