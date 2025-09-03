"""
This module contains

    - Action managers handling status changes for Sale documents
    - Callbacks fired when the documents status are changed (official number,
    remote internal document generation ...)
"""

import logging
from typing import Optional, Union, List
from zope.interface import implementer

from caerp.consts.permissions import PERMISSIONS
from caerp.interfaces import IValidationStateManager
from caerp.models.node import Node
from caerp.events.document_events import StatusChangedEvent
from caerp.models.price_study.price_study import PriceStudy
from caerp.models.project.business import Business
from caerp.utils.datetimes import utcnow
from caerp.models.config import Config
from caerp.models.action_manager import (
    ActionManager,
    Action,
)
from caerp.models.expense.sheet import ExpenseSheet
from caerp.models.expense.services import ExpenseSheetNumberService
from caerp.models.status import StatusLogEntry
from caerp.models.supply.services.supplierinvoice_official_number import (
    SupplierInvoiceNumberService,
    InternalSupplierInvoiceNumberService,
)
from caerp.models.task import (
    Invoice,
    CancelInvoice,
    InternalInvoice,
    InternalCancelInvoice,
    Estimation,
    InternalEstimation,
)
from caerp.models.task.services import (
    InvoiceNumberService,
    InternalInvoiceNumberService,
)


logger = logging.getLogger(__name__)

CELERY_DELAY = 3


# NB : Fournit la correspondance entre le statut d'un document
# et le verbe utilisé pour changer le statut dans les permissions
# Pour un devis par exemple les permissions pour changer les status
# sont :
# "context.validate_estimation"
# "context.invalidate_estimation"
# "context.set_draft_estimation"
# "context.set_wait_estimation"
STATUS_TO_ACTION_FOR_PERMISSIONS = {
    "draft": "set_draft",
    "wait": "set_wait",
    "invalid": "invalidate",
    "valid": "validate",
}


def get_validation_state_manager(
    data_type: str,
    userid_attr: str = "status_user_id",
    datetime_attr: str = "status_date",
    comment_attr: str = "status_comment",
    callbacks: dict = {},
) -> ActionManager:
    """
    Return a state machine handling the validation states

    :param datetime_attr: the attribute storing the last status change
    :param data_type: estimation/invoice/cancelinvoice/expensesheet
    :param userid_attr: the attribute holding the user who changed status
    :param comment_attr: the attribute holding the comment

    :returns: An action manager machine that can be used to perform state
    changes
    """
    manager = ActionManager()
    for status, prev_status, icon, label, title, css in (
        (
            "valid",
            None,
            "check-circle",
            "Valider",
            "Valider ce document (il ne pourra plus être modifié)",
            "btn-primary icon_only_mobile icon_only_tablet",
        ),
        (
            "wait",
            None,
            "clock",
            "Demander la validation",
            "Enregistrer ce document et en demander la validation",
            "btn-primary icon_only_mobile icon_only_tablet",
        ),
        (
            "invalid",
            None,
            "times-circle",
            "Invalider",
            "Invalider ce document afin que l’entrepreneur le corrige",
            "btn-primary negative icon_only_mobile icon_only_tablet",
        ),
        (
            "draft",
            "wait",
            "pen",
            "Repasser en brouillon",
            "Repasser ce document en brouillon pour pouvoir le modifier",
            "icon_only_mobile icon_only_tablet",
        ),
    ):
        permission_verb = STATUS_TO_ACTION_FOR_PERMISSIONS.get(status, status)
        permission = f"context.{permission_verb}_{data_type}"
        action = Action(
            status,
            permission=PERMISSIONS[permission],
            prev_status=prev_status,
            status_attr="status",
            userid_attr=userid_attr,
            datetime_attr=datetime_attr,
            comment_attr=comment_attr,
            icon=icon,
            label=label,
            title=title,
            css=css,
        )
        action_callbacks: list = callbacks.get(status, [])
        if "__all__" in callbacks:
            action_callbacks.extend(callbacks["__all__"])
        action.set_callbacks(action_callbacks)
        manager.add(action)
    return manager


def _notify_status_change_event_callback(request, node, status: str, **params):
    """
    Notify the change to the registry

    :param str status: The new status that was affected
    :param dict params: The submitted data transmitted with status change
    """

    if params.get("comment"):
        comment = params.get("comment")
    else:
        comment = node.status_comment
    request.registry.notify(
        StatusChangedEvent(
            request,
            node,
            status,
            comment,
        )
    )
    return node


def _record_status_change_callback(request, node, status: str, **params):
    """Record a task status change"""
    if params.get("comment"):
        comment = params.get("comment")
    else:
        comment = node.status_comment
    status_record = StatusLogEntry(
        node=node,
        status=status,
        user_id=node.status_user_id,
        comment=comment,
        state_manager_key="status",
    )
    request.dbsession.add(status_record)
    request.dbsession.flush()
    return node


def _set_invoice_number(request, task: Union[Invoice, CancelInvoice], **kw):
    """
    Set a official number on invoices (or cancelinvoices)

    :param obj request: The current pyramid request
    :param obj task: The current context
    """
    template = Config.get_value("invoice_number_template", None)
    assert template is not None, "invoice_number_template setting should be set"

    if task.official_number is None:
        InvoiceNumberService.assign_number(
            request,
            task,
            template,
        )
    return task


def _set_internalinvoice_number(
    request, task: Union[InternalInvoice, InternalCancelInvoice], **kw
):
    """
    Set a official number on internalinvoices (or cancelinvoices)

    :param obj request: The current pyramid request
    :param obj task: The current context
    """
    template = Config.get_value("internalinvoice_number_template", None)
    assert template is not None, "internalinvoice_number_template setting should be set"

    if task.official_number is None:
        InternalInvoiceNumberService.assign_number(
            request,
            task,
            template,
        )
    return task


def _set_invoice_financial_year(request, task: Union[Invoice, InternalInvoice], **kw):
    """
    Set financial year on invoices (or cancelinvoices)
    based on task date

    :param obj request: The current pyramid request
    :param obj task: The current context
    """
    task.financial_year = task.date.year
    logger.info(
        "Setting financial year for invoice {} to {} (invoice's date is {})".format(
            task.id, task.financial_year, task.date
        )
    )
    request.dbsession.merge(task)
    return task


def _sync_price_studies(
    request, task: Union[Invoice, Estimation, InternalEstimation, InternalInvoice]
):
    """
    Sync price studies to the task

    :param obj request: The current pyramid request
    :param obj task: The current context
    """
    if task.has_price_study():
        price_study: PriceStudy = task.price_study
        price_study.sync_with_task(request)

    return task


def _sync_progress_invoicing_plan(
    request, invoice: Union[Invoice, InternalInvoice], **kwargs
):
    """
    Sync the progress invoicing plan of a business when a task has been validated
    """
    business: Business = invoice.business
    if business.invoicing_mode == Business.PROGRESS_MODE and invoice.is_deposit:
        business.populate_progress_invoicing_status(request, invoice=invoice)


def estimation_valid_callback(
    request, task: Union[Estimation, InternalEstimation], **kw
):
    """
    Estimation validation callback

    :param obj request: The current pyramid request
    :param obj task: The current context
    """
    _sync_price_studies(request, task)
    task.business.populate_deadlines(estimation=task)
    task.business.populate_indicators()
    return task


def internalestimation_valid_callback(request, task: InternalEstimation, **kw):
    """
    InternalEstimation validation callback

    :param obj request: The current pyramid request
    :param obj task: The current InternalEstimation
    """
    import caerp
    from caerp_celery.tasks.utils import check_alive
    from caerp_celery.tasks.tasks import (
        async_internalestimation_valid_callback,
    )

    task = estimation_valid_callback(request, task, **kw)
    logger.info("    + InternalEstimation validation callback")
    logger.info("    + Document {}".format(task))

    if not caerp._called_from_test:
        service_ok, msg = check_alive()
        if not service_ok:
            logger.error("Celery is not available")
        else:
            request.dbsession.merge(task)
            request.dbsession.flush()
            async_internalestimation_valid_callback.apply_async(
                args=[task.id], eta=utcnow(delay=CELERY_DELAY)
            )
            logger.info("A Celery Task has been delayed")
    return task


def invoice_valid_callback(request, task: Invoice, **kw):
    """
    Invoice validation callback

    :param obj request: The current pyramid request
    :param obj task: The current context
    """
    import caerp
    from caerp_celery.tasks.utils import check_alive
    from caerp_celery.tasks.tasks import scheduled_render_pdf_task

    _sync_price_studies(request, task)
    _set_invoice_number(request, task, **kw)
    _set_invoice_financial_year(request, task, **kw)
    _sync_progress_invoicing_plan(request, task, **kw)
    if not caerp._called_from_test:
        service_ok, msg = check_alive()
        if not service_ok:
            logger.error("Celery is not available")
        else:
            request.dbsession.merge(task)
            request.dbsession.flush()
            scheduled_render_pdf_task.apply_async(
                args=[task.id], eta=utcnow(delay=CELERY_DELAY)
            )
            logger.info("A Celery Task has been delayed")
    return task


def internalinvoice_valid_callback(request, task: InternalInvoice, **kw):
    """
    Internal invoice validation callback

    :param obj request: The current pyramid request
    :param obj task: The current context
    """
    import caerp
    from caerp_celery.tasks.utils import check_alive
    from caerp_celery.tasks.tasks import (
        async_internalinvoice_valid_callback,
    )

    _set_internalinvoice_number(request, task, **kw)
    _set_invoice_financial_year(request, task, **kw)

    logger.info("    + InternalInvoice validation callback")
    logger.info("    + Document {}".format(task))

    if not caerp._called_from_test:
        service_ok, msg = check_alive()
        if not service_ok:
            logger.error("Celery is not available")
        else:
            # Fix #
            async_internalinvoice_valid_callback.apply_async(
                args=[task.id], eta=utcnow(delay=CELERY_DELAY)
            )
            logger.info("A Celery Task has been delayed")

    return task


def internalcancelinvoice_valid_callback(request, task: InternalCancelInvoice, **kw):
    """
    Internal cancel invoice validation callback

    Mark original supplier_invoice as resulted before classic internal invoice
    validation callback
    """
    logger.info("    + InternalCancelInvoice validation callback")
    orig_supplier_invoice = task.invoice.supplier_invoice
    if orig_supplier_invoice:
        logger.info(
            "Setting the original supplier invoice {} as resulted".format(
                orig_supplier_invoice.official_number
            )
        )
        orig_supplier_invoice.worker_paid_status = (
            orig_supplier_invoice.supplier_paid_status
        ) = orig_supplier_invoice.paid_status = "resulted"

    return internalinvoice_valid_callback(request, task, **kw)


def get_internalestimation_state_manager() -> ActionManager:
    """
    Renvoie un state manager pour les devis internes
    """
    manager = get_validation_state_manager(
        "estimation",
        callbacks={"valid": [internalestimation_valid_callback]},
    )
    for item in manager.items:
        item.options["help_text"] = (
            "À la validation du devis, celui-ci sera automatiquement transmis "
            "à votre client"
        )
    return manager


def get_internalinvoice_state_manager() -> ActionManager:
    """
    Construit le state manager pour les factures internes
    """
    manager = get_validation_state_manager(
        "invoice",
        callbacks=dict(valid=internalinvoice_valid_callback),
    )
    for item in manager.items:
        item.options["help_text"] = (
            "À la validation de la facture, celle-ci sera automatiquement "
            "transmise à votre client"
        )
    return manager


def get_internalcancelinvoice_state_manager() -> ActionManager:
    """
    Construit le state manager pour les avoirs internes
    """
    manager = get_validation_state_manager(
        "cancelinvoice",
        callbacks=dict(valid=internalcancelinvoice_valid_callback),
    )
    for item in manager.items:
        item.options["help_text"] = (
            "À la validation de l'avoir, celui-ci sera automatiquement "
            "transmis à votre client"
        )
    return manager


def _set_sheet_official_number(
    request, sheet: ExpenseSheet, *args, **kwargs
) -> ExpenseSheet:
    """
    Callback for when sheet turns into valid status
    """
    template = Config.get_value("expensesheet_number_template", None)

    assert template is not None, "expensesheet_number_template setting should be set"

    if sheet.official_number is None:
        ExpenseSheetNumberService.assign_number(request, sheet, template)
    return sheet


def sheet_valid_callback(request, sheet: ExpenseSheet, **kw):
    _set_sheet_official_number(request, sheet, **kw)
    return sheet


def internalsupplier_order_valid_callback(request, supplier_order, *args, **kwargs):
    """
    Callback launched after an internal supplier order is validated
    send an email to the supplier
    """
    from caerp.controllers.state_managers import set_signed_status

    set_signed_status(request, supplier_order.source_estimation, "signed")
    from caerp.utils.notification.internal_supply import (
        send_supplier_order_validated_mail,
    )

    send_supplier_order_validated_mail(request, supplier_order)
    request.dbsession.merge(supplier_order.source_estimation)
    request.dbsession.flush()
    return supplier_order


def _set_supplier_invoice_official_number(request, supplier_invoice, *args, **kwargs):
    """
    Callback for when sheet turns into valid status
    """
    template = Config.get_value("supplierinvoice_number_template", None)

    assert template is not None, "supplierinvoice_number_template setting should be set"

    if supplier_invoice.official_number is None:
        SupplierInvoiceNumberService.assign_number(request, supplier_invoice, template)
    return supplier_invoice


def _set_internalsupplier_invoice_official_number(
    request, supplier_invoice, *args, **kwargs
):
    """
    Callback for when sheet turns into valid status
    """
    template = Config.get_value("internalsupplierinvoice_number_template", None)

    assert (
        template is not None
    ), "internalsupplierinvoice_number_template setting should be set"

    if supplier_invoice.official_number is None:
        InternalSupplierInvoiceNumberService.assign_number(
            request, supplier_invoice, template
        )
    return supplier_invoice


def _set_negative_internalsupplier_invoice_resulted(
    request, supplier_invoice, *args, **kwargs
):
    """
    Set the negative supplier invoices as resulted
    """
    if supplier_invoice.total <= 0:
        logger.info(
            f"Setting the negative supplier invoice {supplier_invoice.official_number} as resulted"
        )
        supplier_invoice.worker_paid_status = (
            supplier_invoice.supplier_paid_status
        ) = supplier_invoice.paid_status = "resulted"
    return supplier_invoice


def supplier_invoice_valid_callback(request, supplier_invoice, *args, **kwargs):
    """Called when a supplier invoice is validated"""
    _set_supplier_invoice_official_number(request, supplier_invoice, *args, **kwargs)
    return supplier_invoice


def internalsupplier_invoice_valid_callback(request, supplier_invoice, *args, **kwargs):
    _set_internalsupplier_invoice_official_number(
        request, supplier_invoice, *args, **kwargs
    )
    _set_negative_internalsupplier_invoice_resulted(
        request, supplier_invoice, *args, **kwargs
    )
    return supplier_invoice


def get_internal_supplier_order_state_manager():
    manager = get_validation_state_manager(
        "supplier_order",
        callbacks=dict(valid=internalsupplier_order_valid_callback),
    )
    for item in manager.items:
        item.options["help_text"] = (
            "La validation de cette commande vaut acceptation du devis "
            "associé. Un e-mail de confirmation sera envoyé au fournisseur."
        )
    return manager


DEFAULT_ACTION_MANAGER = {
    # Sale module
    "estimation": get_validation_state_manager(
        "estimation",
        callbacks=dict(valid=estimation_valid_callback),
    ),
    "internalestimation": get_internalestimation_state_manager(),
    "invoice": get_validation_state_manager(
        "invoice",
        callbacks=dict(valid=invoice_valid_callback),
    ),
    "internalinvoice": get_internalinvoice_state_manager(),
    "internalcancelinvoice": get_internalcancelinvoice_state_manager(),
    "cancelinvoice": get_validation_state_manager(
        "cancelinvoice",
        callbacks=dict(valid=invoice_valid_callback),
    ),
    # Expense module
    "expense": get_validation_state_manager(
        data_type="expensesheet",
        callbacks=dict(valid=sheet_valid_callback),
    ),
    # Supplier Module
    "supplier_order": get_validation_state_manager(
        "supplier_order",
    ),
    "internalsupplier_order": get_internal_supplier_order_state_manager(),
    "supplier_invoice": get_validation_state_manager(
        "supplier_invoice",
        callbacks=dict(valid=supplier_invoice_valid_callback),
    ),
    "internalsupplier_invoice": get_validation_state_manager(
        "supplier_invoice",
        callbacks=dict(valid=internalsupplier_invoice_valid_callback),
    ),
}


@implementer(IValidationStateManager)
def get_default_validation_state_manager(doctype: str) -> ActionManager:
    return DEFAULT_ACTION_MANAGER[doctype]


def set_status(request, node: Node, status: str, **kw) -> Node:
    manager: ActionManager = request.find_service(IValidationStateManager, context=node)
    print(kw)
    node = manager.process(request, node, status, **kw)
    _notify_status_change_event_callback(request, node, status, **kw)
    _record_status_change_callback(request, node, status, **kw)
    return node


def check_allowed(request, node: Node, status: str) -> Optional[Action]:
    manager: ActionManager = request.find_service(IValidationStateManager, context=node)
    return manager.check_allowed(request, node, status)


def get_allowed_actions(request, node: Node) -> List[Action]:
    manager: ActionManager = request.find_service(IValidationStateManager, context=node)
    return manager.get_allowed_actions(request, node)
