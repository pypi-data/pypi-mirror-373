# -*-coding:utf-8-*-
"""1.5 : Migrating payment modes

Revision ID: 1f07ae132ac8
Revises: 1cc9ff114346
Create Date: 2012-12-31 10:22:14.636420

"""

# revision identifiers, used by Alembic.
revision = "1f07ae132ac8"
down_revision = "1cc9ff114346"

from alembic import op
import sqlalchemy as sa
from caerp_base.models.base import DBSESSION


def upgrade():
    from caerp.models.task.invoice import PaymentMode, Payment

    for payment in Payment.query():
        if payment.mode in ("cheque", "CHEQUE"):
            payment.mode = "par chèque"
        elif payment.mode in ("virement", "VIREMENT"):
            payment.mode = "par virement"
        elif payment.mode in ("liquide", "LIQUIDE"):
            payment.mode = "en liquide"
        else:
            payment.mode = "mode de paiement inconnu"
        DBSESSION().merge(payment)

    for mode in ("par chèque", "par virement", "en liquide"):
        pmode = PaymentMode(label=mode)
        DBSESSION().add(pmode)


def downgrade():
    from caerp.models.task.invoice import PaymentMode, Payment

    for p in PaymentMode.query():
        DBSESSION().delete(p)
    for p in Payment.query():
        if p.mode == "par chèque":
            p.mode = "cheque"
        elif p.mode == "par virement":
            p.mode = "virement"
        elif p.mode == "en liquide":
            p.mode = "liquide"
        else:
            p.mode = "inconnu"
        DBSESSION().merge(p)
