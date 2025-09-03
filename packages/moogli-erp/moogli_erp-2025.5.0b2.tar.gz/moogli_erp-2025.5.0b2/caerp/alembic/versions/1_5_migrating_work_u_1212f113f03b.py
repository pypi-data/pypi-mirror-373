"""1.5 : Migrating work unity

Revision ID: 1212f113f03b
Revises: 1f07ae132ac8
Create Date: 2013-01-21 11:53:56.598914

"""

# revision identifiers, used by Alembic.
revision = "1212f113f03b"
down_revision = "1f07ae132ac8"

from alembic import op
import sqlalchemy as sa


UNITIES = dict(
    NONE="",
    HOUR="heure(s)",
    DAY="jour(s)",
    WEEK="semaine(s)",
    MONTH="mois",
    FEUIL="feuillet(s)",
    PACK="forfait",
)

UNITS = (
    "heure(s)",
    "jour(s)",
    "semaine(s)",
    "mois",
    "forfait",
    "feuillet(s)",
)


def translate_unity(unity):
    return UNITIES.get(unity, UNITIES["NONE"])


def translate_inverse(unity):
    for key, value in list(UNITIES.items()):
        if unity == value:
            return key
    else:
        return "NONE"


def upgrade():
    from caerp.models.task import WorkUnit
    from caerp.models.task.estimation import EstimationLine
    from caerp.models.task.invoice import InvoiceLine
    from caerp.models.task.invoice import CancelInvoiceLine
    from caerp_base.models.base import DBSESSION

    # Adding some characters to the Lines
    for table in "estimation_line", "invoice_line", "cancelinvoice_line":
        op.alter_column(table, "unity", type_=sa.String(100))

    for value in UNITS:
        unit = WorkUnit(label=value)
        DBSESSION().add(unit)
    for factory in (EstimationLine, InvoiceLine, CancelInvoiceLine):
        for line in factory.query():
            line.unity = translate_unity(line.unity)
            DBSESSION().merge(line)


def downgrade():
    from caerp.models.task import WorkUnit
    from caerp.models.task.estimation import EstimationLine
    from caerp.models.task.invoice import InvoiceLine
    from caerp.models.task.invoice import CancelInvoiceLine
    from caerp_base.models.base import DBSESSION

    for factory in (EstimationLine, InvoiceLine, CancelInvoiceLine):
        for line in factory.query():
            line.unity = translate_inverse(line.unity)
            DBSESSION().merge(line)
    for value in WorkUnit.query():
        DBSESSION().delete(value)
