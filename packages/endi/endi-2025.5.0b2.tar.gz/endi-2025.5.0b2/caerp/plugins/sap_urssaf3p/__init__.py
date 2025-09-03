import caerp


def includeme(config):
    config.include(".populate")
    config.include(".caerp_admin_commands")  # Ugly
    # add_view fails in an hard to debug way within testing context.
    if not caerp._called_from_test:
        config.include(".views")
