from caerp.utils.strings import major_status
from caerp.views.task.utils import get_task_view_type


STATUS_LABELS = {
    "draft": "Brouillon",
    "wait": "En attente de validation",
    "invalid": {
        "estimation": "Invalidé",
        "internalestimation": "Invalidé",
        "invoice": "Invalidée",
        "internalinvoice": "Invalidée",
        "internalcancelinvoice": "Invalidée",
        "cancelinvoice": "Invalidé",
        "expensesheet": "Invalidée",
        "supplier_order": "Invalidée",
        "internalsupplier_order": "Invalidée",
        "supplier_invoice": "Invalidée",
        "internalsupplier_invoice": "Invalidée",
    },
    "valid": {
        "estimation": "En cours",
        "internalestimation": "En cours",
        "invoice": "En attente de paiement",
        "internalinvoice": "En attente de paiement",
        "internalcancelinvoice": "Soldé",
        "cancelinvoice": "Soldé",
        "expensesheet": "Validée",
        "supplier_order": "Validée",
        "internalsupplier_order": "Validée",
        "supplier_invoice": "Validée",
        "internalsupplier_invoice": "Validée",
    },
    "aborted": "Sans suite",
    "sent": "Envoyé",
    "signed": "Signé par le client",
    "geninv": "Factures générées",
    "paid": "Payée partiellement",
    "resulted": "Soldée",
    "justified": "Justificatifs reçus",
}


def html_wrapper_panel(context, request):
    """
    Panel for html task rendering
    """
    return dict(task=context)


def task_title_panel(context, request, title):
    """
    Panel returning a label for the given context's status
    """
    # FIXME: factorize properly into render_api and common panels : this is
    # used for other stuff than tasks.
    # See render_api.STATUS_CSS_CLASS, among others

    status = major_status(context)
    print(("The major status is : %s" % status))
    status_label = STATUS_LABELS.get(status)

    context_type = get_task_view_type(context)
    if isinstance(status_label, dict):
        status_label = status_label[context_type]

    css = "status status-%s" % context.status
    if hasattr(context, "paid_status"):
        css += " paid-status-%s" % context.paid_status
        if hasattr(context, "is_tolate"):
            css += " tolate-%s" % context.is_tolate()
        elif hasattr(context, "justified"):
            css += " justified-%s" % context.justified
    elif hasattr(context, "signed_status"):
        css += " signed-status-%s geninv-%s" % (
            context.signed_status,
            context.geninv,
        )
    else:  # cancelinvoice
        if status == "valid":
            css += " paid-status-resulted"

    return dict(title=title, item=context, css=css, status_label=status_label)


def includeme(config):
    """
    Pyramid's inclusion mechanism
    """
    config.add_panel(
        task_title_panel,
        "task_title_panel",
        renderer="caerp:templates/panels/task/title.mako",
    )
    config.add_panel(
        html_wrapper_panel, "task_html", renderer="panels/task/task_html.mako"
    )
