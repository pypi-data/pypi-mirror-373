"""2024.3.0 Remplit les codes journaux pour le paiement des fournisseurs

Create Date: 2024-06-05 16:37:25.267919

"""

# revision identifiers, used by Alembic.

# Revision ID:
revision = "f5d6f4b6c984"

# Revises (previous revision or revisions):
down_revision = "58c1c52190b3"

from alembic import op
import sqlalchemy as sa

from caerp.models.config import Config


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    conn = get_bind()

    internalcode_journal_frns = Config.get_value("internalcode_journal_frns")
    internalcode_journal_paiements_frns = Config.get_value(
        "internalcode_journal_paiements_frns"
    )
    if (
        internalcode_journal_paiements_frns is None
        and internalcode_journal_frns is not None
    ):
        Config.set("internalcode_journal_paiements_frns", internalcode_journal_frns)

    mark_changed(session)
    session.flush()


def upgrade():
    migrate_datas()


def downgrade():
    pass
