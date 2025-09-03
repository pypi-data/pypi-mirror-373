import colander
from caerp.forms import id_node


class MailSchema(colander.MappingSchema):
    company_id = id_node()
    attachment = colander.SchemaNode(
        colander.String(),
        missing=colander.drop,
    )


class MailsSchema(colander.SequenceSchema):
    mail = MailSchema()


class MailSendingSchema(colander.Schema):
    mails = MailsSchema()
    mail_subject = colander.SchemaNode(
        colander.String(), validator=colander.Length(min=1)
    )
    mail_message = colander.SchemaNode(
        colander.String(), validator=colander.Length(min=1)
    )
    force = colander.SchemaNode(
        colander.Boolean(),
        missing=colander.drop,
    )
