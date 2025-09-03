"""
Events used while handling expenses :
    Send email

"""
import datetime
import logging
from typing import Optional

from caerp_base.mail import format_link
from caerp.utils.datetimes import format_date
from caerp.models.expense.sheet import ExpenseSheet
from caerp.utils.notification import AbstractNotification, notify
from caerp.utils.strings import (
    format_account,
)

logger = logging.getLogger(__name__)

# Events for which a mail will be sended
EVENTS = {
    "valid": "validée",
    "invalid": "invalidée",
    "paid": "partiellement payée",
    "resulted": "payée",
}

BODY_TMPL = """\
Bonjour {owner},

La note de dépenses de {owner} pour la période {date} a été {status_verb}.

Vous pouvez la consulter ici :
{addr}

Commentaires associés au document :
    {comment}"""


EXPENSE_NOTIFY_STATUS = dict(
    (
        ("invalid", "Invalidée par {0} le {1}"),
        ("valid", "Validée par {0} le {1}"),
        ("paid", "Paiement partiel notifié par {0} le {1}"),
        ("resulted", "Paiement notifié par {0} le {1}"),
    )
)


def _format_expense_status(request, status: str) -> str:
    """
    Return a formatted string for expense status notification
    """
    status_str = EXPENSE_NOTIFY_STATUS.get(status)
    account_label = format_account(request.identity)
    date_label = format_date(datetime.date.today())

    if status_str is not None:
        return status_str.format(account_label, date_label)
    else:
        return ""


def _get_title(request, node: ExpenseSheet, status: str) -> str:
    """
    return the title of the notification
    """
    subject = "Notes de dépense de {0} : {1}".format(
        format_account(node.user),
        _format_expense_status(request, status),
    )
    return subject


def _get_status_verb(status: str) -> str:
    """
    Return the verb associated to the current status
    """
    return EVENTS.get(status, "")


def _find_comment(node: ExpenseSheet, comment: Optional[str] = None) -> str:
    """
    Collect the latest comment for the current node
    """
    if comment:
        return comment
    else:
        logger.debug("Trying to find expense status")
        status_history = node.statuses
        if len(status_history) > 0:
            return status_history[0].comment
        else:
            return "Aucun"


def _get_body(
    request, node: ExpenseSheet, status: str, comment: Optional[str] = None
) -> str:
    """
    return the body of the notification
    """
    owner = format_account(node.user)
    date = "{0}/{1}".format(node.month, node.year)
    status_verb = _get_status_verb(status)
    addr = request.route_url("/expenses/{id}", id=node.id)
    addr = format_link(request.registry.settings, addr)
    return BODY_TMPL.format(
        owner=owner,
        addr=addr,
        date=date,
        status_verb=status_verb,
        comment=_find_comment(node, comment=comment),
    )


def _get_notification(
    request, node: ExpenseSheet, status: str, comment: Optional[str] = None
) -> AbstractNotification:
    return AbstractNotification(
        key=f"expense:status:{status}",
        title=_get_title(request, node, status),
        body=_get_body(request, node, status, comment),
    )


def notify_expense_status_changed(request, node, status, comment=None):
    """
    Fire notification for expense status changed
    """
    if status not in list(EVENTS.keys()):
        return
    notify(
        request,
        _get_notification(request, node, status, comment),
        user_ids=[node.user.id],
    )
