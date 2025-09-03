"""
Handle task (invoice/estimation) related events
"""
import logging
from caerp.events.document_events import StatusChangedEvent

logger = logging.getLogger(__name__)


def on_status_changed_alert_related_business(event: StatusChangedEvent):
    """
    Alert the related business on Invoice status change

    :param event: A StatusChangedEvent instance with an Invoice attached
    """
    business = event.node.business
    logger.info(
        "+ Status Changed : updating business {} invoicing status".format(business.id)
    )
    business.status_service.on_task_status_change(
        event.request, business, event.node, event.status
    )
