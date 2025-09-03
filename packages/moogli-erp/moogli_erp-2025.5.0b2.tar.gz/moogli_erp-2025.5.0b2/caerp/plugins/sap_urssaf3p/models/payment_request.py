from datetime import datetime
from typing import Union

from caerp_base.models.base import default_table_args
from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.event import listen
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    declared_attr,
    relationship,
    backref,
)

from caerp.models.listeners import SQLAListeners
from caerp.models.node import Node
from caerp.models.status import (
    status_column,
    status_comment_column,
    status_history_relationship,
    status_user_id_column,
    status_user_relationship,
)
from caerp.plugins.sap_urssaf3p.models.services.payment_request import (
    URSSAFPaymentRequestService,
)


class PaymentRequestStatusHolderMixim:
    """
    Follow status
    """

    STATUS_ERROR = "error"
    STATUS_WAITING = "waiting"
    STATUS_ABORTED = "aborted"
    STATUS_PAYMENT_ISSUE = "payment_issue"
    STATUS_RESULTED = "resulted"

    ALL_STATUSES = (
        STATUS_ERROR,
        STATUS_WAITING,
        STATUS_ABORTED,
        STATUS_PAYMENT_ISSUE,
        STATUS_RESULTED,
    )
    FINAL_STATUSES = (STATUS_ERROR, STATUS_ABORTED)

    @declared_attr
    def request_status(cls):
        return status_column(default=cls.STATUS_WAITING)

    @declared_attr
    def request_comment(cls):
        return status_comment_column()

    @declared_attr
    def request_status_user_id(cls):
        return status_user_id_column()

    @declared_attr
    def request_status_user(cls):
        return status_user_relationship(f"{cls.__name__}.request_status_user_id")

    @declared_attr
    def urssaf3p_request_status_history(cls):
        return status_history_relationship("urssaf3p_request_status", viewonly=True)


class URSSAFPaymentRequest(PaymentRequestStatusHolderMixim, Node):
    """
    An URSSAF payment request for a given invoice
    """

    __tablename__ = "urssaf_payment_request"
    __table_args__ = default_table_args
    __mapper_args__ = {
        "polymorphic_identity": "urssaf_payment_request",
    }
    _caerp_service = URSSAFPaymentRequestService()

    id = Column(ForeignKey("node.id"), primary_key=True)
    urssaf_id = Column(String(50), nullable=True, unique=True)
    urssaf_status_code = Column(String(4), nullable=False, default="")
    urssaf_reject_message = Column(Text(), nullable=False, default="")
    urssaf_transfer_message = Column(Text(), nullable=False, default="")

    # typed alias to Node.parent relationship
    invoice = relationship(
        "Invoice",
        primaryjoin="Node.id==URSSAFPaymentRequest.parent_id",
        remote_side=[Node.id],
        viewonly=True,
        uselist=False,
        backref=backref(
            "urssaf_payment_request",
            uselist=False,
            info={"colanderalchemy": {"exclude": True}},
        ),
    )

    @property
    def urssaf_status_title(self):
        return self._caerp_service.get_title(self.urssaf_status_code)

    @property
    def urssaf_status_description(self):
        return self._caerp_service.get_description(self.urssaf_status_code)

    def update_from_urssaf_status_code(self, urssaf_status_code) -> bool:
        return self._caerp_service.update_from_urssaf_status_code(
            urssaf_status_code, self
        )

    def update_from_reject_data(self, reject_code, reject_comment) -> bool:
        return self._caerp_service.update_from_reject_data(
            reject_code, reject_comment, self
        )

    def update_from_transfer_data(self, transfer_date, transfer_amount=None) -> bool:
        return self._caerp_service.update_from_transfer_data(
            self, transfer_date, transfer_amount
        )

    @hybrid_property
    def should_watch(self):
        return self._caerp_service.should_watch_property(self)

    @should_watch.expression
    def should_watch(cls):
        return cls._caerp_service.should_watch_expression(cls)

    @classmethod
    def get_by_urssaf_id(cls, urssaf_id: str) -> Union["URSSAFPaymentRequest", None]:
        if urssaf_id is None:
            return None
        else:
            return cls.query().filter_by(urssaf_id=urssaf_id).first()

    def get_company_id(self):
        return self.invoice.company_id


def on_set_update_updated_at(target, value, oldvalue, initiator):
    if value != oldvalue:
        target.updated_at = datetime.now()


def start_listening():
    # FIXME: such tooling may be stored near TimeStampedMixin
    # Node.updated_at.onupdate won't be triggered when the edited field is on
    # parent model (Node) whose table has not necessarily been updated.

    # React to any change (setattr) on any mapped instance attr:
    for col_attr in URSSAFPaymentRequest.__mapper__.column_attrs:
        column = col_attr.class_attribute

        if column.class_ != Node:  # Node attrs are already handled by sqla builtins
            listen(column, "set", on_set_update_updated_at)


SQLAListeners.register(start_listening)
