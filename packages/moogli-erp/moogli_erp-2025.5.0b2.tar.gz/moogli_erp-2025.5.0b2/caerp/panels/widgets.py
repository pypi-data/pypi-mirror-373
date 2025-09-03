def _concat_class_attr(*args):
    """
    Concat several values to be put together in an HTML class attribute.
    None or empty *args will be ignored.

    >>> _concat_class_attr("", "btn btn-danger", "huge", None)
    "btn btn-danger huge"

    :param *args str: string or None
    """
    nonempty_args = [i for i in args if i]
    return " ".join(nonempty_args)


def _ensure_class_attr(original: str, more: str) -> str:
    """
    Ensure css classes listed in more are present in original
    """
    original_css = original.split(" ")
    more_css = more.split(" ")
    for i in more_css:
        if i and i not in original_css:
            original_css.append(i)
    return " ".join(original_css)


def link_panel(context, request, extra_classes=""):
    """
    simple link panel used to render links

    :param obj context: The context to render, an instance of the Link class
    :param obj request: The current pyramid request
    :param extra_classes: string to be appendend to the <a> class attr
    """
    return dict(
        link=context,
        css_classes=_concat_class_attr(context.css, extra_classes),
    )


def post_button_panel(context, request, extra_classes=""):
    """
    simple form+submit panel used to render single-POST action links.

    :param obj context: The context to render, an instance of POSTButton
    :param extra_classes: string to be appendend to the <button> class attr
    :param obj request: The current pyramid request
    """
    return dict(
        link=context,
        get_csrf_token=request.session.get_csrf_token,
        css_classes=_concat_class_attr(context.css, extra_classes),
        extra_fields=context.extra_fields,
    )


def admin_index_nav_panel(context, request):
    """
    A panel to render the navigation inside the administration interface

    :param obj context: The context to render, list of Link or AdminLin
    :param obj request: The current pyramid request
    """
    menus = []
    if context:

        for menu in context:
            permission = getattr(menu, "permission", None)
            if permission is None or request.has_permission(permission):
                menus.append(menu)
    return dict(menus=menus, item_panel_name="admin_index_link")


def menu_dropdown_panel(
    context, request, label, links, icon=None, display_label=False, alignment="right"
):
    """
    Menu dropdown panel

    :param obj context: The current context
    :param obj request: The current pyramid request
    :param str label: the label to use
    :param str icon: An optionnal icon to add
    :param list buttons: List of caerp.widgets.Link
    """
    classes = ""
    links = list(links)
    for link in links:
        link.css = _ensure_class_attr(link.css, "btn")
    right_icon = "chevron-down" if display_label else "dots"
    if not display_label:
        classes += " only"
    return dict(
        label=label,
        classes=classes,
        links=links,
        icon=icon,
        right_icon=right_icon,
        display_label=display_label,
        alignment=alignment,
    )


def _action_dropdown_panel(context, request, label="Actions", links=()):
    """
    Action dropdown_panel Shows action buttons in a dropdown
    """
    for link in links:
        link.css = _ensure_class_attr(link.css, "btn icon")

    return dict(
        label=label,
        classes="only",
        links=links,
        icon=None,
        right_icon="dots",
        display_label=False,
        alignment="right",
    )


def _action_inline_buttons_panel(context, request, links=(), **kwargs):
    """
    Buttons shown inline next to each other

    Used :
    * In a td action column
    """
    for link in links:
        link.css = _ensure_class_attr(link.css, "btn icon only")

    return dict(links=links)


def action_buttons_td_panel(
    context,
    request,
    links=(),
    label="Actions",
):
    """
    Action buttons panel returns a dropdown or a button list (without labels)

    :param obj context: The current context
    :param obj request: The current pyramid request
    :param list links: List of caerp.widgets.Link
    """
    links = list(links)
    if len(links) >= 4:
        width = "one"
        panel_name = "_action_dropdown"
    else:
        if len(links) == 1:
            width = "one"
        elif len(links) == 2:
            width = "two"
        else:
            width = "three"
        panel_name = "_action_inline_buttons"

    return dict(
        panel_name=panel_name,
        links=links,
        label=label,
        width=width,
    )


def action_buttons_panel(context, request, links=()):
    """
    Inline action buttons (at the top of the page

    :param obj context: The current context
    :param obj request: The current pyramid request
    :param list links: List of caerp.widgets.Link (or POSTButtons)
    """
    links = list(links)
    for link in links:
        css = "btn icon"
        if not link.label:
            css += " only"
        link.css = _ensure_class_attr(link.css, css)

    return dict(links=links)


def status_title_panel(context, request):
    """Syntethizing the statuses of an object into a sentence and an icon"""
    return dict(context=context)


def includeme(config):
    config.add_panel(
        link_panel,
        "link",
        renderer="caerp:templates/panels/widgets/link.pt",
    )
    config.add_panel(
        post_button_panel,
        "post_button",
        renderer="caerp:templates/panels/widgets/post_button.pt",
    )
    config.add_panel(
        admin_index_nav_panel,
        "admin_index_nav",
        renderer="caerp:templates/panels/widgets/admin_index_nav.pt",
    )
    config.add_panel(
        link_panel,
        "admin_index_link",
        renderer="caerp:templates/panels/widgets/admin_index_link.pt",
    )
    config.add_panel(
        menu_dropdown_panel,
        "menu_dropdown",
        renderer="caerp:templates/panels/widgets/menu_dropdown.pt",
    )
    config.add_panel(
        action_buttons_panel,
        "action_buttons",
        renderer="caerp:templates/panels/widgets/_action_inline_buttons.pt",
    )
    config.add_panel(
        action_buttons_td_panel,
        "action_buttons_td",
        renderer="caerp:templates/panels/widgets/action_buttons.pt",
    )
    config.add_panel(
        status_title_panel,
        name="status_title",
        renderer="caerp:templates/panels/widgets/status_title.pt",
    )

    # Panels that shouldn't be used directly
    config.add_panel(
        _action_dropdown_panel,
        "_action_dropdown",
        renderer="caerp:templates/panels/widgets/menu_dropdown.pt",
    )
    config.add_panel(
        _action_inline_buttons_panel,
        "_action_inline_buttons",
        renderer="caerp:templates/panels/widgets/_action_inline_buttons.pt",
    )
