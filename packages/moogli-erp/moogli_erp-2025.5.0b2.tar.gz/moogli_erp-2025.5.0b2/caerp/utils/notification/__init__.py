# flake8: noqa: E401
from caerp.interfaces import INotificationChannel
from .channels import (
    AlertNotificationChannel,
    HeaderMessageNotificationChannel,
    MessageNotificationChannel,
    MailNotificationChannel,
)
from .notification import (
    notify,
    notify_now,
    publish_event,
    clean_notifications,
)
from .abstract import AbstractNotification
from .activity import notify_activity_participants
from .career_path import notify_career_path_end_date


def includeme(config):
    config.register_service_factory(
        MessageNotificationChannel, iface=INotificationChannel
    )
    config.register_service_factory(
        MessageNotificationChannel, iface=INotificationChannel, name="message"
    )
    config.register_service_factory(
        AlertNotificationChannel, iface=INotificationChannel, name="alert"
    )
    config.register_service_factory(
        HeaderMessageNotificationChannel,
        iface=INotificationChannel,
        name="header_message",
    )
    config.register_service_factory(
        MailNotificationChannel, iface=INotificationChannel, name="email"
    )
