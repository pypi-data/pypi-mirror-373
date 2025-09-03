"""Abstract dataclasses for notifications

... code-block:: python

        from caerp.utils.notification import AbstractNotification, notify
        notif = AbstractNotification(
            key='task:status:valid',
            title='Votre facture a été validée',
            body='Voir votre facture <a href='#'>Ici</a>'
        )
        notify(request, notification, user_ids=[1,2,3], groups=['manager', 'admin'])
"""
import datetime
import typing
from dataclasses import dataclass

from caerp.models.notification import (
    Notification,
    NotificationEvent,
    NotificationEventType,
)


@dataclass
class AbstractNotification:
    """Abstract Notification object should be used by code
    firing notification

    key

        The caerp key of notification

    title

        A title

    body

        The message body

    check_query

        An str query that should return at least en element,
        if not, planned notification should be cancelled


    context_tablename

        The name of the table this notification is related to

    context_id

        The id of the element this notification is related to
    """

    key: str
    title: str
    body: str
    check_query: typing.Optional[str] = None
    due_datetime: typing.Optional[datetime.datetime] = None
    context_tablename: typing.Optional[str] = None
    context_id: typing.Optional[int] = None

    def to_event(self) -> NotificationEvent:
        return NotificationEvent(
            key=self.key,
            title=self.title,
            body=self.body,
            check_query=self.check_query,
            due_datetime=self.due_datetime,
            context_tablename=self.context_tablename,
            context_id=self.context_id,
        )

    def to_model(self) -> Notification:
        status_type = NotificationEventType.get_status_type(self.key)
        return Notification(
            key=self.key,
            title=self.title,
            body=self.body,
            status_type=status_type,
        )

    @classmethod
    def from_event(cls, event: NotificationEvent):
        return cls(
            key=event.key,
            title=event.title,
            body=event.body,
            check_query=event.check_query,
            due_datetime=event.due_datetime,
            context_tablename=event.context_tablename,
            context_id=event.context_id,
        )
