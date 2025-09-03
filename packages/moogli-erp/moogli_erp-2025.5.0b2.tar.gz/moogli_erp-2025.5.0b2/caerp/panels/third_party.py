def third_party_general_info(context, request):
    return dict(third_party=context)


def third_party_accounting_info(context, request):
    return dict(third_party=context)


def includeme(config):
    config.add_panel(
        third_party_general_info,
        "third_party_general_info",
        renderer="panels/third_party/third_party_general_info.mako",
    )
    config.add_panel(
        third_party_accounting_info,
        "third_party_accounting_info",
        renderer="panels/third_party/third_party_accounting_info.mako",
    )
