import logging
from typing import Optional, List, Union
from zope.interface import implementer

from caerp.consts.permissions import PERMISSIONS
from caerp.interfaces import IJustifiedStateManager
from caerp.events.document_events import StatusChangedEvent

from caerp.models.action_manager import ActionManager, Action
from caerp.models.expense.sheet import ExpenseLine, ExpenseSheet
from caerp.models.status import StatusLogEntry

logger = logging.getLogger(__name__)


def _notify_status_change_event_callback(request, sheet, status, **kw):
    """
    Notify the change to the registry

    :param str status: The new status that was affected
    :param dict params: The submitted data transmitted with status change
    """
    if status is True:
        request.registry.notify(StatusChangedEvent(request, sheet, "justified"))
    return sheet


def _record_status_change_callback(request, sheet, status, **params):
    logger.debug("Sheet status changed : {}".format(status))
    entry = StatusLogEntry(
        node=sheet,
        comment=params.get("comment"),
        user_id=request.identity.id,
        status="justified" if status else "waiting",
        state_manager_key="justified_status",
    )
    request.dbsession.add(entry)
    request.dbsession.flush()
    return sheet


def _build_justified_state_manager():
    """
    Return a state manager for setting the justified status attribute on
    ExpenseSheet objects
    """
    manager = ActionManager()
    for status, icon, label, title, css in (
        (
            False,
            "clock",
            "En attente",
            "Les justificatifs n'ont pas ou pas tous été acceptés",
            "btn",
        ),
        (
            True,
            "check",
            "Acceptés",
            "Les justificatifs ont été acceptés",
            "btn",
        ),
    ):
        action = Action(
            status,
            permission=PERMISSIONS["context.set_justified_expensesheet"],
            status_attr="justified",
            icon=icon,
            label=label,
            title=title,
            css=css,
        )
        manager.add(action)
    return manager


@implementer(IJustifiedStateManager)
def get_default_justified_state_manager(doctype: str) -> ActionManager:
    return _build_justified_state_manager()


def set_status(
    request, expense_sheet: Union[ExpenseSheet, ExpenseLine], status: str, **kw
) -> ExpenseSheet:
    manager: ActionManager = request.find_service(
        IJustifiedStateManager, context=expense_sheet
    )
    expense_sheet = manager.process(request, expense_sheet, status, **kw)
    if isinstance(expense_sheet, ExpenseSheet):
        _notify_status_change_event_callback(request, expense_sheet, status, **kw)
        _record_status_change_callback(request, expense_sheet, status, **kw)
    return expense_sheet


def check_allowed(
    request, expense_sheet: ExpenseSheet, status: str
) -> Optional[Action]:
    manager: ActionManager = request.find_service(
        IJustifiedStateManager, context=expense_sheet
    )
    return manager.check_allowed(request, expense_sheet, status)


def get_allowed_actions(request, expense_sheet: ExpenseSheet) -> List[Action]:
    manager: ActionManager = request.find_service(
        IJustifiedStateManager, context=expense_sheet
    )
    return manager.get_allowed_actions(request, expense_sheet)
