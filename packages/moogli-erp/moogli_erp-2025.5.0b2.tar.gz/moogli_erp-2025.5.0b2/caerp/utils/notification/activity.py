import logging
import datetime
import typing

from caerp.models.activity import Activity
from caerp.models.notification.notification import NotificationEvent
from caerp.utils.renderer import render_template

from .abstract import AbstractNotification
from .notification import notify

logger = logging.getLogger(__name__)

NOTIFICATION_CHECK_QUERY_TMPL = """
SELECT count(activity.id) FROM activity join event on event.id=activity.id
WHERE event.id={activity.id} AND event.status = 'planned'
"""
NOTIFICATION_TITLE_TMPL = """Vous avez rendez-vous"""


def get_sql_check_query(activity):
    return NOTIFICATION_CHECK_QUERY_TMPL.format(activity=activity)


def get_existing_notification(activity) -> typing.Optional[NotificationEvent]:
    """Find an existing event referring to this specific career_path"""
    return NotificationEvent.find_existing(activity.__tablename__, activity.id)


def collect_user_ids(activity):
    result = [user.id for user in activity.participants]
    if activity.owner_id:
        result.append(activity.owner_id)
    result.extend([user.id for user in activity.conseillers])
    return list(set(result))


def should_notification_event_be_updated(
    activity: Activity, event: NotificationEvent
) -> bool:
    """Check if the notification event should be updated"""
    return (
        activity.datetime != event.due_datetime
        or len(set(event.user_ids).difference(set(collect_user_ids(activity)))) != 0
    )


def get_due_datetime(activity) -> datetime.datetime:
    """Return the due_datetime to use for the notification"""
    d = activity.datetime
    now = datetime.datetime.now()
    result = max(now, d - datetime.timedelta(days=7))
    return result


def get_notification_body(request, activity):
    return render_template(
        "caerp:templates/notifications/activity.mako",
        dict(activity=activity),
        request=request,
    )


def update_notification_event(request, activity: Activity, event: NotificationEvent):
    """Update existing notification event with activity related info"""
    event.due_datetime = get_due_datetime(activity)
    event.check_query = get_sql_check_query(activity)

    event.title = NOTIFICATION_TITLE_TMPL
    event.body = get_notification_body(request, activity)
    request.dbsession.merge(event)


def get_abstract_notification(request, activity: Activity) -> AbstractNotification:
    sql_check_query: str = get_sql_check_query(activity)
    notification = AbstractNotification(
        key="activity:reminder",
        title=NOTIFICATION_TITLE_TMPL,
        body=get_notification_body(request, activity),
        check_query=sql_check_query,
        context_tablename=activity.__tablename__,
        context_id=activity.id,
        due_datetime=get_due_datetime(activity),
    )
    return notification


def notify_activity_participants(request, activity: Activity, update=False):
    """Notify user's for their appointment"""
    now = datetime.datetime.now()
    # Pas de notification moins de 4h avant
    if not activity.datetime or activity.datetime <= now + datetime.timedelta(hours=4):
        return

    if update:
        event = get_existing_notification(activity)
        if event is not None:
            if not should_notification_event_be_updated(activity, event):
                # Pas d'update nécessaire
                return
            # update
            already_published = event.published
            if already_published:
                logger.debug("Suppression de Notification existantes")
                # Si il est déjà publié, on supprime les notifications existantes
                for i in event.notifications:
                    request.dbsession.delete(i)
                request.dbsession.flush()
                # On remet published à False car il sera (re) publié à la date
                # d'échéance
                event.published = False
            logger.debug("Update d'une NotificationEvent existante")
            update_notification_event(request, activity, event)
            return
    # add
    notification = get_abstract_notification(request, activity)
    logger.debug("Planification d'une notification à échéance")
    notify(request, notification, user_ids=collect_user_ids(activity))
