"""Notification tools

A single function : notify()

Notifications can be published now or delayed

When notifications are published, they are sent to the appropriate
channels

- email
- caerp internal messages
- caerp alert
- caerp header

E.g : Send a notification 6 months later to the manager team

.. code-block:: python

    >>> abstract_notification = AbstractNotification(
            title="Notification",
            body="Le compte <a href='/users/23'>Jean Dupont</a> doit peut-être "
            "être désactivé, à vérifier",
            key='message:internal'
        )
    >>> notify(request, abstract_notification, group_names=['manager'])

"""
import logging
import typing

from caerp.models.company import Company

from caerp.models.user.group import Group
from caerp.models.notification import NotificationEvent, Notification
from caerp.models.user.login import Login
from caerp.models.user.user import User

from .channels import get_channel
from .abstract import AbstractNotification


logger = logging.getLogger(__name__)


def notify(
    request,
    notification: AbstractNotification,
    group_names: typing.Optional[list] = None,
    user_ids: typing.Optional[list] = None,
    company_id: typing.Optional[int] = None,
    follower_user_id: typing.Optional[int] = None,
    force_channel: typing.Optional[str] = None,
    account_type: typing.Optional[str] = None,
    **kw,
):
    """
    Handle user notifications in MoOGLi, notify directly or program a future notification
    """

    if not notification.due_datetime and not notification.check_query:
        # On publie directement la notification
        notify_now(
            request,
            notification,
            group_names,
            user_ids,
            company_id,
            follower_user_id,
            force_channel,
            account_type,
            **kw,
        )
    else:
        # On programme la notification
        notify_later(
            request,
            notification,
            group_names,
            user_ids,
            company_id,
            follower_user_id,
            force_channel,
            account_type,
        )


def notify_later(
    request,
    notification: AbstractNotification,
    group_names: typing.Optional[list] = None,
    user_ids: typing.Optional[list] = None,
    company_id: typing.Optional[int] = None,
    follower_user_id: typing.Optional[int] = None,
    force_channel: typing.Optional[str] = None,
    account_type: typing.Optional[str] = None,
):
    """
    Plan a notification for later on
    """
    event = notification.to_event()
    event.group_names = group_names
    event.user_ids = user_ids
    event.company_id = company_id
    event.follower_user_id = follower_user_id
    event.force_channel = force_channel
    event.account_type = account_type
    request.dbsession.add(event)
    request.dbsession.flush()


def notify_now(
    request,
    notification: AbstractNotification,
    group_names: typing.Optional[list] = None,
    user_ids: typing.Optional[list] = None,
    company_id: typing.Optional[int] = None,
    follower_user_id: typing.Optional[int] = None,
    force_channel: typing.Optional[str] = None,
    account_type: typing.Optional[str] = None,
    **kw,
):
    """
    Send notification to the users
    """
    if group_names:
        for group_name in group_names:
            notify_group(request, notification, group_name, force_channel, **kw)
    if company_id:
        notify_company(request, notification, company_id, force_channel, **kw)
    if user_ids:
        notify_users(request, notification, user_ids, force_channel, **kw)
    if follower_user_id:
        notify_follower(request, notification, follower_user_id, force_channel, **kw)
    if account_type:
        notify_account_type(request, notification, account_type, force_channel, **kw)


def notify_group(
    request,
    notification: AbstractNotification,
    group_name: typing.Optional[str],
    force_channel: typing.Optional[str] = None,
    **kw,
):
    """Notify a group of users

    :param notification: The notification object
    :param group_name: The name of a group
    :param force_channel: the name of the channel
    """
    try:
        group = Group._find_one(group_name)
    except Exception:
        logger.exception(f"Erreur à la récupération du group {group_name}")
        return

    for login in group.users:
        channel = get_channel(request, login.user, notification.key, force_channel)
        channel.send_to_user(notification, login.user, **kw)


def notify_users(
    request,
    notification: AbstractNotification,
    users: list,
    force_channel: typing.Optional[str] = None,
    **kw,
):
    """Notify a list of users

    :param notification: The notification object
    :param users: List of usernames
    :param force_channel: the name of the channel
    """
    for user_id in users:
        user = User.get(user_id)
        if user:
            channel = get_channel(request, user, notification.key, force_channel)
            channel.send_to_user(notification, user, **kw)


def notify_company(
    request,
    notification: AbstractNotification,
    company_id: int,
    force_channel: typing.Optional[str] = None,
    **kw,
):
    """Notify a company

    :param notification: The notification object
    :param company_id: Id of the destination company
    :param force_channel: the name of the channel
    """
    company = Company.get(company_id)
    if company is None:
        return
    # Ici on hack pour prendre les préférences du premier user de l'enseigne.
    channel = get_channel(
        request, company.employees[0], notification.key, force_channel
    )
    channel.send_to_company(notification, company, **kw)


def notify_follower(
    request,
    notification: AbstractNotification,
    follower_user_id: int,
    force_channel: typing.Optional[str] = None,
    **kw,
):
    """Notify a follower

    :param notification: The notification object
    :param follower_user_id: Id of a user whose follower will get a notification
    :param force_channel: the name of the channel
    """
    user: User = User.get(follower_user_id)
    if user is None or user.userdatas is None:
        return
    follower = user.userdatas.situation_follower
    if follower is None:
        # If no follower we fallback on manager/admin group
        notify_group(request, notification, "manager", **kw)
        notify_group(request, notification, "admin", **kw)
        return

    channel = get_channel(request, follower, notification.key, force_channel)
    channel.send_to_user(notification, follower, **kw)


def notify_account_type(
    request,
    notification: AbstractNotification,
    account_type: str,
    force_channel: typing.Optional[str] = None,
    **kw,
):
    """Notify users with a specific account type

    :param notification: The notification object
    :param account_type: Type of account
    :param force_channel: the name of the channel
    """
    if account_type not in ("entrepreneur", "equipe_appui", "all"):
        logger.error(f"Invalid account type: {account_type}")
        return

    users = User.query().join(Login)

    if account_type != "all":
        users = users.filter(Login.account_type.in_(("hybride", account_type))).all()

    for user in users:
        channel = get_channel(request, user, notification.key, force_channel)
        channel.send_to_user(notification, user, **kw)


def publish_event(request, event: NotificationEvent):
    """
    Publish notifications planned through the event object
    """
    notification: AbstractNotification = AbstractNotification.from_event(event)
    notify_now(
        request,
        notification,
        group_names=event.group_names,
        user_ids=event.user_ids,
        company_id=event.company_id,
        follower_user_id=event.follower_user_id,
        event=event,
        force_channel=event.force_channel,
        account_type=event.account_type,
    )
    event.published = True
    request.dbsession.merge(event)
    request.dbsession.flush()


def clean_notifications(request):
    """Clean outdated Notifications"""
    events = NotificationEvent.query().outerjoin(Notification)
    for event in events:
        if not event.is_valid(request) or event.is_read(request):
            request.dbsession.delete(event)
    request.dbsession.flush()
    for notification in Notification.query().filter(Notification.read == True):
        request.dbsession.delete(notification)
    request.dbsession.flush()
