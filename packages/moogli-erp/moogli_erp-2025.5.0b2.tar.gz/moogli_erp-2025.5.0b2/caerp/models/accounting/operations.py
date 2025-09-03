import datetime

from caerp_base.models.base import DBBASE, default_table_args
from caerp_base.models.mixins import TimeStampedMixin
from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from caerp.forms import get_deferred_select
from caerp.models.company import Company

FILETYPE_LABELS = {
    "general_ledger": "Grand livre",
    "analytical_balance": "Balance analytique",
    "synchronized_accounting": "Synchronisation automatique",
}


class AccountingOperationUpload(DBBASE, TimeStampedMixin):
    """
    Represent a newly parsed file
    """

    __tablename__ = "accounting_operation_upload"
    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True)
    filetype = Column(
        String(50),
        info={
            "colanderalchemy": {
                "title": "Type de fichier (analytical_balance/general_ledger)"
            }
        },
    )
    filename = Column(
        String(100), info={"colanderalchemy": {"title": "Nom du fichier"}}
    )
    operations = relationship(
        "AccountingOperation",
        primaryjoin="AccountingOperation.upload_id" "==AccountingOperationUpload.id",
        order_by="AccountingOperation.analytical_account",
        cascade="all,delete,delete-orphan",
    )
    measure_grids = relationship(
        "BaseAccountingMeasureGrid",
        primaryjoin="BaseAccountingMeasureGrid.upload_id"
        "==AccountingOperationUpload.id",
        cascade="all,delete,delete-orphan",
        back_populates="upload",
    )

    date = Column(
        Date(),
        info={
            "colanderalchemy": {
                "title": "Date à associer aux données de ce fichier "
                "(extraite du nom du fichier)"
            }
        },
    )
    md5sum = Column(
        String(34),
        info={
            "colanderalchemy": {
                "title": "Somme md5 du fichier",
                "description": "Permet d'identifier les fichiers déjà traités",
            }
        },
    )
    ANALYTICAL_BALANCE = "analytical_balance"
    GENERAL_LEDGER = "general_ledger"
    SYNCHRONIZED_ACCOUNTING = "synchronized_accounting"

    @property
    def filetype_label(self):
        return FILETYPE_LABELS.get(self.filetype)


class AccountingOperation(DBBASE):
    __tablename__ = "accounting_operation"
    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True)
    date = Column(
        Date(),
        default=datetime.date.today,
        info={"colanderalchemy": {"title": "Date de l'écriture"}},
    )
    analytical_account = Column(
        String(20),
        info={"colanderalchemy": {"title": "Compte analytique de l'enseigne"}},
    )
    general_account = Column(
        String(20), info={"colanderalchemy": {"title": "Compte général de l'opération"}}
    )
    label = Column(
        String(80),
        info={"colanderalchemy": {"title": "Libellé"}},
    )
    debit = Column(
        Numeric(9, 2),
        info={"colanderalchemy": {"title": "Débit"}},
    )
    credit = Column(
        Numeric(9, 2),
        info={"colanderalchemy": {"title": "Crédit"}},
    )
    balance = Column(
        Numeric(9, 2),
        info={"colanderalchemy": {"title": "Solde"}},
    )
    company_id = Column(
        ForeignKey("company.id", ondelete="CASCADE"),
        info={
            "colanderalchemy": {
                "title": "Enseigne associée à cette opération",
                "widget": get_deferred_select(
                    Company, keys=("id", lambda c: "%s %s" % (c.name, c.code_compta))
                ),
            }
        },
    )
    company = relationship(
        "Company",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {
                "related_key": "name",
                "label": "Enseigne",
            },
        },
    )
    upload_id = Column(ForeignKey("accounting_operation_upload.id", ondelete="CASCADE"))

    def __json__(self, request):
        return dict(
            analytical_account=self.analytical_account,
            general_account=self.general_account,
            date=self.date,
            label=self.label,
            debit=self.debit,
            credit=self.credit,
            balance=self.balance,
            company_id=self.company_id,
            upload_id=self.upload_id,
        )

    def total(self):
        return self.debit - self.credit
