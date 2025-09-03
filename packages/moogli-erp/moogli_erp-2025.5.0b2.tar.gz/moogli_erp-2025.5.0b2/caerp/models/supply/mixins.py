from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from caerp_base.models.mixins import DuplicableMixin
from caerp.compute.math_utils import (
    translate_integer_precision,
    integer_to_amount,
)


class LineModelMixin(DuplicableMixin, object):
    """
    Common fields between SupplierOrderLine and SupplierInvoiceLine
    """

    __duplicable_fields__ = [
        "ht",
        "tva",
        "description",
        "type_id",
    ]

    @declared_attr
    def description(cls):
        return Column(
            Text(),
            info={"colanderalchemy": {"title": "Description"}},
            default="",
        )

    @declared_attr
    def ht(cls):
        return Column(
            Integer,
            info={
                "colanderalchemy": {"title": "Montant HT"},
            },
        )

    @declared_attr
    def tva(cls):
        return Column(
            Integer,
            info={"colanderalchemy": {"title": "Montant de la TVA"}},
        )

    @declared_attr
    def type_id(cls):
        return Column(
            Integer,
            ForeignKey("expense_type.id", ondelete="SET NULL"),
            info={"colanderalchemy": {"title": "Type de dépense"}},
        )

    @declared_attr
    def expense_type(cls):
        return relationship(
            "ExpenseType",
            uselist=False,
            info={"colanderalchemy": {"exclude": True}},
        )

    def __json__(self, request):
        return dict(
            id=self.id,
            type_id=self.type_id,
            ht=integer_to_amount(self.ht, 2),
            tva=integer_to_amount(self.tva, 2),
            description=self.description,
        )

    @classmethod
    def from_task(cls, task):
        instance = cls()
        instance.ht = translate_integer_precision(task.total(), 5, 2)
        instance.tva = 0
        instance.description = task.description

        from caerp.models.expense.types import ExpenseType

        internal_types = ExpenseType.find_internal()
        if len(internal_types) == 1:
            instance.type_id = internal_types[0].id
        return instance
