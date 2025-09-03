import logging

from typing import List, Union
from pyramid_mailer.mailer import Mailer
from pyramid_mailer.debug import DebugMailer
from pyramid_mailer.message import Message, Attachment

from caerp.export.task_pdf import ensure_task_pdf_persisted
from caerp.models.files import File
from caerp.models.smtp import NodeSmtpHistory, SmtpSettings
from caerp.models.status import StatusLogEntry
from caerp.models.task.estimation import Estimation
from caerp.models.task.invoice import Invoice
from caerp.services.smtp.smtp import (
    get_mailer_from_smtp_settings,
    get_company_smtp_by_company_id,
)


logger = logging.getLogger(__name__)


def make_attachment_from_file(request, pdf_file: File) -> Attachment:
    return Attachment(
        pdf_file.name,
        content_type="application/pdf",
        data=pdf_file.data_obj,
    )


def get_message_from_task(
    request,
    sender_email: str,
    task: Union[Estimation, Invoice],
    subject: str,
    body: str,
    recipient_email: str,
    copy_to: List[str],
    reply_to: str,
) -> Message:

    extra_headers = {}
    company = task.company
    if reply_to:
        extra_headers["reply-to"] = f"{company.name}<{reply_to}>"

    ensure_task_pdf_persisted(task, request)
    attachments = [make_attachment_from_file(request, task.pdf_file)]
    return Message(
        subject=subject,
        sender=f"{task.company.name}<{sender_email}>",
        recipients=[recipient_email],
        body=body,
        extra_headers=extra_headers,
        attachments=attachments,  # type: List[Attachment]
        cc=copy_to,
    )


def _record_mail_sent(
    request,
    node,
    smtp_settings: SmtpSettings,
    mailer: Union[Mailer, DebugMailer],
    message: Message,
):
    """
    Generate a status log entry for successfull email
    And generate a new NodeSmtpHistory entry
    """
    comment = (
        f"Envoyé par e-mail au client à l'adresse {message.recipients[0]} "
        f"depuis l'adresse {message.sender}\n"
    )

    status_record = StatusLogEntry(
        node=node,
        status="sent",
        label="Envoyé par e-mail au client",
        user=request.identity,
        comment=comment,
        state_manager_key="signed_status",
    )
    request.dbsession.add(status_record)

    history = NodeSmtpHistory(
        smtp_settings=str(smtp_settings),
        status=NodeSmtpHistory.SUCCESS_STATUS,
        node_id=node.id,
        subject=message.subject,
        body=message.body,
        recipient=message.recipients[0],
        sender_label=message.sender,
        reply_to=message.extra_headers.get("reply-to"),
        copy_to=",".join(message.cc),
    )
    request.dbsession.add(history)

    if isinstance(node, Estimation):
        if node.signed_status == "waiting":
            node.signed_status = "sent"
            request.dbsession.merge(node)
    request.dbsession.flush()
    return node


def _record_mail_error(
    request,
    node,
    smtp_settings: SmtpSettings,
    mailer: Union[Mailer, DebugMailer],
    message: Message,
    error: str,
):
    comment = (
        f"Erreur d'envoi de l'e-mail au client à l'adresse {message.recipients[0]} "
        f"depuis l'adresse {message.sender}\n"
        f"<b>Erreur : </b>{error}\n"
    )

    status_record = StatusLogEntry(
        node=node,
        status="invalid",
        label="Erreur d'envoi par e-mail au client",
        user=request.identity,
        comment=comment,
        state_manager_key="signed_status",
    )
    request.dbsession.add(status_record)

    history = NodeSmtpHistory(
        smtp_settings=str(smtp_settings),
        status=NodeSmtpHistory.ERROR_STATUS,
        node_id=node.id,
        subject=message.subject,
        body=message.body,
        error=error,
        recipient=message.recipients[0],
        sender_label=message.sender,
        reply_to=message.extra_headers.get("reply-to"),
        copy_to=",".join(message.cc),
    )
    request.dbsession.add(history)
    request.dbsession.flush()
    return node


def send_task_to_customer(
    request,
    task: Union[Estimation, Invoice],
    subject: str,
    body: str,
    recipient_email: str,
    copy_to: List[str],
    reply_to: str,
):
    """
    Send a Task object (Invoice/Estimation) to the customer associated with it.
    """
    company = task.company
    smtp_settings = get_company_smtp_by_company_id(request, company.id)
    if smtp_settings is None:
        raise Exception(
            "No SMTP settings found nor for this company neither for the CAE"
        )

    mailer = get_mailer_from_smtp_settings(request, smtp_settings)
    message = get_message_from_task(
        request,
        smtp_settings.sender_email,
        task,
        subject,
        body,
        recipient_email,
        copy_to,
        reply_to,
    )
    try:
        mailer.send_immediately(message)
        _record_mail_sent(request, task, smtp_settings, mailer, message)
    except Exception as e:
        logger.exception(f"Error sending task {task} to customer")
        _record_mail_error(request, task, smtp_settings, mailer, message, str(e))
        raise e
