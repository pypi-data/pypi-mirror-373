"""
    Accounting Export log model
    Allows to store information about every export that have been made
"""
import logging
import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    ForeignKey,
    String,
    Table,
)
from sqlalchemy.orm import relationship

from caerp_base.models.base import (
    DBBASE,
    default_table_args,
)

logger = logging.getLogger(__name__)


class AccountingExportLogEntry(DBBASE):
    __tablename__ = "accounting_export_log_entry"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "accounting_export_log_entry"}

    id = Column(
        Integer,
        primary_key=True,
    )

    datetime = Column(
        DateTime(),
        default=datetime.datetime.now,
        info={"colanderalchemy": {"title": "Date et heure de l'export"}},
    )

    export_type = Column(
        String(255),
    )

    user_id = Column(
        ForeignKey("accounts.id", ondelete="set null"),
        info={"colanderalchemy": {"title": "Auteur de l'export"}},
    )

    export_file_id = Column(
        ForeignKey("file.id", ondelete="set null"),
        info={"colanderalchemy": {"title": "Fichier d'export stocké"}},
    )

    # relationships
    user = relationship(
        "User",
        info={"colanderalchemy": {"exclude": True}},
    )

    export_file = relationship(
        "File",
        info={"colanderalchemy": {"exclude": True}},
    )


# Invoices
invoice_accounting_export_log_entry_association_table = Table(
    "invoice_accounting_export_log_entry_association_table",
    DBBASE.metadata,
    Column(
        "invoice_accounting_export_log_entry_id",
        ForeignKey("invoice_accounting_export_log_entry.id"),
    ),
    Column("task_id", ForeignKey("task.id")),
)


class InvoiceAccountingExportLogEntry(AccountingExportLogEntry):
    __tablename__ = "invoice_accounting_export_log_entry"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "invoice_accounting_export_log_entry"}

    id = Column(
        ForeignKey("accounting_export_log_entry.id", ondelete="CASCADE"),
        primary_key=True,
    )

    exported_invoices = relationship(
        "Task",
        secondary=invoice_accounting_export_log_entry_association_table,
        back_populates="exports",
    )


# Payments
payment_accounting_export_log_entry_association_table = Table(
    "payment_accounting_export_log_entry_association_table",
    DBBASE.metadata,
    Column(
        "payment_accounting_export_log_entry_id",
        ForeignKey("payment_accounting_export_log_entry.id"),
    ),
    Column("base_task_payment_id", ForeignKey("base_task_payment.id")),
)


class PaymentAccountingExportLogEntry(AccountingExportLogEntry):
    __tablename__ = "payment_accounting_export_log_entry"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "payment_accounting_export_log_entry"}

    id = Column(
        ForeignKey("accounting_export_log_entry.id", ondelete="CASCADE"),
        primary_key=True,
    )

    exported_payments = relationship(
        "BaseTaskPayment",
        secondary=payment_accounting_export_log_entry_association_table,
        back_populates="exports",
    )


# Expenses
expense_accounting_export_log_entry_association_table = Table(
    "expense_accounting_export_log_entry_association_table",
    DBBASE.metadata,
    Column(
        "expense_accounting_export_log_entry_id",
        ForeignKey("expense_accounting_export_log_entry.id"),
    ),
    Column("node_id", ForeignKey("node.id")),
)


class ExpenseAccountingExportLogEntry(AccountingExportLogEntry):
    __tablename__ = "expense_accounting_export_log_entry"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "expense_accounting_export_log_entry"}

    id = Column(
        ForeignKey("accounting_export_log_entry.id", ondelete="CASCADE"),
        primary_key=True,
    )

    exported_expenses = relationship(
        "ExpenseSheet",
        secondary=expense_accounting_export_log_entry_association_table,
        back_populates="exports",
    )


# Expense_payments
expense_payment_accounting_export_log_entry_association_table = Table(
    "expense_payment_accounting_export_log_entry_association_table",
    DBBASE.metadata,
    Column(
        "expense_payment_accounting_export_log_entry_id",
        ForeignKey("expense_payment_accounting_export_log_entry.id"),
    ),
    Column("expense_payment_id", ForeignKey("expense_payment.id")),
)


class ExpensePaymentAccountingExportLogEntry(AccountingExportLogEntry):
    __tablename__ = "expense_payment_accounting_export_log_entry"
    __table_args__ = default_table_args
    __mapper_args__ = {
        "polymorphic_identity": "expense_payment_accounting_export_log_entry"
    }

    id = Column(
        ForeignKey("accounting_export_log_entry.id", ondelete="CASCADE"),
        primary_key=True,
    )

    exported_expense_payments = relationship(
        "ExpensePayment",
        secondary=expense_payment_accounting_export_log_entry_association_table,
        back_populates="exports",
    )


# Supplier_invoices
supplier_invoice_accounting_export_log_entry_association_table = Table(
    "supplier_invoice_accounting_export_log_entry_association_table",
    DBBASE.metadata,
    Column(
        "supplier_invoice_accounting_export_log_entry_id",
        ForeignKey("supplier_invoice_accounting_export_log_entry.id"),
    ),
    Column("node_id", ForeignKey("node.id")),
)


class SupplierInvoiceAccountingExportLogEntry(AccountingExportLogEntry):
    __tablename__ = "supplier_invoice_accounting_export_log_entry"
    __table_args__ = default_table_args
    __mapper_args__ = {
        "polymorphic_identity": "supplier_invoice_accounting_export_log_entry"
    }

    id = Column(
        ForeignKey("accounting_export_log_entry.id", ondelete="CASCADE"),
        primary_key=True,
    )

    exported_supplier_invoices = relationship(
        "SupplierInvoice",
        secondary=supplier_invoice_accounting_export_log_entry_association_table,
        back_populates="exports",
    )


# Supplier_payments
supplier_payment_accounting_export_log_entry_association_table = Table(
    "supplier_payment_accounting_export_log_entry_association_table",
    DBBASE.metadata,
    Column(
        "supplier_payment_accounting_export_log_entry_id",
        ForeignKey("supplier_payment_accounting_export_log_entry.id"),
    ),
    Column("base_supplier_invoice_payment_id", ForeignKey("base_supplier_payment.id")),
)


class SupplierPaymentAccountingExportLogEntry(AccountingExportLogEntry):
    __tablename__ = "supplier_payment_accounting_export_log_entry"
    __table_args__ = default_table_args
    __mapper_args__ = {
        "polymorphic_identity": "supplier_payment_accounting_export_log_entry"
    }

    id = Column(
        ForeignKey("accounting_export_log_entry.id", ondelete="CASCADE"),
        primary_key=True,
    )

    exported_supplier_payments = relationship(
        "BaseSupplierInvoicePayment",
        secondary=supplier_payment_accounting_export_log_entry_association_table,
        back_populates="exports",
    )
