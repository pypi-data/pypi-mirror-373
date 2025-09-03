def includeme(config):
    """
    Add module's related routes
    """
    config.add_route(
        "workshop",
        r"/workshops/{id:\d+}",
        traverse="/workshops/{id}",
    )

    config.add_route(
        "user_workshops_subscribed",
        "/users/{id}/workshops/subscribed",
        traverse="/users/{id}",
    )

    config.add_route(
        "company_workshops_subscribed",
        "/company/{id}/workshops/subscribed",
        traverse="/companies/{id}",
    )

    config.add_route(
        "company_workshops",
        "/company/{id}/workshops",
        traverse="/companies/{id}",
    )

    config.add_route(
        "user_workshop_subscriptions",
        "/users/{id}/workshops/my_subscriptions",
        traverse="/users/{id}",
    )

    config.add_route(
        "workshop.pdf",
        "/workshops/{id}.pdf",
        traverse="/workshops/{id}",
    )

    config.add_route(
        "workshop.pdf.html",
        "/workshops/{id}.pdf.html",
        traverse="/workshops/{id}",
    )

    config.add_route(
        "timeslot.pdf",
        "/timeslots/{id}.pdf",
        traverse="/timeslots/{id}",
    )

    config.add_route("workshops", "/workshops")
    config.add_route("cae_workshops", "/cae/workshops")
    config.add_route("workshops{file_format}", "/workshops{file_format}")
    config.add_route("cae_workshops{file_format}", "/cae/workshops{file_format}")
    config.add_route(
        "company_workshops{file_format}",
        "/company/{id}/workshops/workshops{file_format}",
        traverse="/companies/{id}",
    )
