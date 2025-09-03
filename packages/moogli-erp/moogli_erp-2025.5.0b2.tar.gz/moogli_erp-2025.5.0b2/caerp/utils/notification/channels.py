"""Base Channels implementations

Should not be used directly (only through the request object)

>>> factory = request.find_service_factory(INotificationChannel, name='mail')
>>> channel = factory()
>>> channel.send_user(....)

"""
import logging

from zope.interface import implementer
from pyramid_mailer.message import Attachment

from caerp.interfaces import INotificationChannel
from caerp_base.mail import send_mail
from caerp.models.company import Company
from caerp.models.user.user import User
from caerp.models.notification import NotificationEventType
from .abstract import AbstractNotification

logger = logging.getLogger(__name__)


@implementer(INotificationChannel)
class MailNotificationChannel:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def send_to_user(self, notification: AbstractNotification, user: User, **kw):
        if user.login and not user.login.active:
            return
        email = user.email
        if email:
            attachment = kw.get("attachment")
            logger.debug(attachment)
            if attachment is not None:
                assert isinstance(attachment, Attachment)

            logger.debug(f"Sending an email to {email}")
            send_mail(
                self.request,
                email,
                notification.body,
                notification.title,
                attachment=attachment,
            )
        else:
            logger.error(f"Le User {user.id} n’a pas d’e-mail configuré")

    def send_to_company(
        self, notification: AbstractNotification, company: Company, **kw
    ):
        """Send the notification"""
        if not company.active:
            return
        if company.email:
            attachment = kw.get("attachment")
            if attachment is not None:
                assert isinstance(attachment, Attachment)
            logger.debug(f"Sending an email to {company.email}")
            send_mail(
                self.request,
                company.email,
                notification.body,
                notification.title,
                attachment=attachment,
            )
        else:
            for user in company.employees:
                if user.login and user.login.active:
                    self.send_to_user(notification, user)


@implementer(INotificationChannel)
class MessageNotificationChannel:
    channel_name = "message"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def send_to_user(self, notification: AbstractNotification, user: User, **kw):
        if user.login and not user.login.active:
            return
        model = notification.to_model()
        model.channel = self.channel_name
        model.user = user
        model.event = kw.get("event")
        self.request.dbsession.add(model)
        self.request.dbsession.flush()

    def send_to_company(
        self, notification: AbstractNotification, company: Company, **kw
    ):
        """Send the notification"""
        if not company.active:
            return
        for user in company.employees:
            if user.login and user.login.active:
                self.send_to_user(notification, user)


@implementer(INotificationChannel)
class AlertNotificationChannel(MessageNotificationChannel):
    channel_name = "alert"


@implementer(INotificationChannel)
class HeaderMessageNotificationChannel(MessageNotificationChannel):
    channel_name = "header_message"


def get_notification_channel(request, channel_name: str):
    """
    Collect the INotficationChannel configured for channel_name
    """
    return request.find_service(INotificationChannel, name=channel_name)


def get_channel(request, user, notification_key, force_channel=None):
    """
    Return the Channel configured for this type of notification
    """
    if force_channel is not None:
        channel_name = force_channel
    else:
        typ = NotificationEventType.get_type(notification_key)
        if typ:
            channel_name = typ.default_channel_name
        else:
            channel_name = "message"
    channel = get_notification_channel(request, channel_name)
    return channel
