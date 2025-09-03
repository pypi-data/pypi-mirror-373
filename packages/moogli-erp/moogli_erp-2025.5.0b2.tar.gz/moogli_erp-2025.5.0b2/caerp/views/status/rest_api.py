import logging
from typing import List
from caerp.forms.status import get_status_log_schema

from caerp.models.user import User
from caerp.models.status import StatusLogEntry
from caerp.utils.notification.status_log_entry import notify_memo_added
from caerp.views import BaseRestView

logger = logging.getLogger(__name__)


def get_other_users_for_notification(request, node) -> List[dict]:
    """Find users that may be notified if a memo is added to the node"""

    entries = (
        request.dbsession.query(StatusLogEntry.user_id.distinct())
        .filter(StatusLogEntry.node_id == node.id)
        .filter(StatusLogEntry.user_id != request.identity.id)
        .all()
    )
    if entries:
        return user_json_repr_for_select([User.get(entry[0]) for entry in entries])
    else:
        return []


def user_json_repr_for_select(users: List[User]) -> List[dict]:
    """
    Return a list of dicts with the user id and the user label
    """
    return [{"id": user.id, "label": user.label} for user in users]


class StatusLogEntryRestView(BaseRestView):
    """
    For StatusLogEntry (Mémo) with a parent model inheriting Node.

    We expect context to hold a `statuses` attr with all status log entries.
    """

    def post_format(self, entry: StatusLogEntry, edit: bool, attributes):
        if not edit:
            entry.node = self.context
            entry.user = self.request.identity
        return entry

    def collection_get(self):
        return self.context.statuses

    def get_schema(self, submitted):
        return get_status_log_schema()

    def get_node_url(self, node):
        """Build the url to access the given node from the notification"""
        raise NotImplementedError("You should implement StatusLogEntry.get_node_url")

    def notify_on_status_log_entry(
        self, entry: StatusLogEntry, edit: bool, attributes: dict
    ):
        """Notify users when a mémo is added on a node

        recipients are selected when adding the memo (StatusLogEntry)
        """
        logger.debug("In the memo notification")
        logger.debug(attributes)
        notify = attributes.get("notify", False)
        notification_recipients = attributes.get("notification_recipients", [])

        if not notify or not notification_recipients or entry.visibility != "public":
            return

        node = entry.node
        url = self.get_node_url(node)
        if not url:
            return
        # We send the notification to the contractor owning the task
        notify_memo_added(
            self.request,
            node,
            url,
            memo=entry,
            user_ids=list(notification_recipients),
        )

    def after_flush(self, entry, edit, attributes):
        self.notify_on_status_log_entry(entry, edit, attributes)
        return super().after_flush(entry, edit, attributes)
