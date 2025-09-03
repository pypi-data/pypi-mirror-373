def includeme(config):
    config.include(".routes")
    config.include(".forbidden_views")
    auth_module = config.registry.settings.get(
        "caerp.authentification_module", ".basic_views"
    ).strip()
    config.include(auth_module)
