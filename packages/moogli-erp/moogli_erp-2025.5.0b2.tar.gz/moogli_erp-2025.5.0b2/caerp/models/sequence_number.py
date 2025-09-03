from datetime import date
from sqlalchemy import (
    Column,
    extract,
    ForeignKey,
    func,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from typing import (
    Tuple,
    Type,
)

from caerp_base.models.base import (
    DBBASE,
    DBSESSION,
    default_table_args,
)
from caerp_base.models.mixins import OfficialNumberMixin
from caerp.models.config import Config
from caerp.models.node import Node


class SequenceNumber(DBBASE):
    """
    Sequence numbers of different chronological sequences
    """

    __tablename__ = "sequence_number"
    __table_args__ = (
        UniqueConstraint("sequence", "index", "key"),
        default_table_args,
    )

    SEQUENCE_INVOICE_GLOBAL = "invoice_global"
    SEQUENCE_INVOICE_YEAR = "invoice_year"
    SEQUENCE_INVOICE_MONTH = "invoice_month"
    SEQUENCE_INVOICE_MONTH_COMPANY = "invoice_month_company"

    SEQUENCE_INTERNALINVOICE_GLOBAL = "internalinvoice_global"
    SEQUENCE_INTERNALINVOICE_YEAR = "internalinvoice_year"
    SEQUENCE_INTERNALINVOICE_MONTH = "internalinvoice_month"
    SEQUENCE_INTERNALINVOICE_MONTH_COMPANY = "internalinvoice_month_company"

    SEQUENCE_EXPENSESHEET_GLOBAL = "expense_sheet_global"
    SEQUENCE_EXPENSESHEET_YEAR = "expense_sheet_year"
    SEQUENCE_EXPENSESHEET_MONTH = "expense_sheet_month"
    SEQUENCE_EXPENSESHEET_MONTH_COMPANY = "expense_sheet_month_company"

    SEQUENCE_SUPPLIERINVOICE_GLOBAL = "supplier_invoice_global"
    SEQUENCE_SUPPLIERINVOICE_YEAR = "supplier_invoice_year"
    SEQUENCE_SUPPLIERINVOICE_MONTH = "supplier_invoice_month"
    SEQUENCE_SUPPLIERINVOICE_MONTH_COMPANY = "supplier_invoice_month_company"
    SEQUENCE_INTERNALSUPPLIERINVOICE_GLOBAL = "supplier_internalinvoice_global"
    SEQUENCE_INTERNALSUPPLIERINVOICE_YEAR = "supplier_internalinvoice_year"
    SEQUENCE_INTERNALSUPPLIERINVOICE_MONTH = "supplier_internalinvoice_month"
    SEQUENCE_INTERNALSUPPLIERINVOICE_MONTH_COMPANY = (
        "supplier_internalinvoice_month_company"
    )

    id = Column("id", Integer, primary_key=True)
    node_id = Column(
        Integer,
        ForeignKey("node.id", ondelete="cascade"),
        nullable=False,
    )
    sequence = Column(String(100), nullable=False)
    index = Column(Integer, nullable=False)
    key = Column(String(100), nullable=False)
    node = relationship("Node")


class GlobalSequence:
    def __init__(
        self,
        db_key: str,
        init_value_config_key: str,
        types: Tuple[str],
        model_class: Type[OfficialNumberMixin],
    ):
        """
        A simple global sequence for a given Node model class implementing
        SequenceNumberedModelMixin. All instances are numbered in the same
        sequence.

        :param db_key: the key of the sequence as stored in
        SequenceNbmer.sequence
        :param init_value_config_key: the config key that stores optionally the
        initial value of the sequence
        :types: the types (see Node.type_) that are numbered altogether by this
        sequence
        """
        self.db_key = db_key
        self.init_value_config_key = init_value_config_key
        self.types = types
        self.model_class = model_class

    def _get_initial_value(self, node):
        return Config.get_value(
            self.init_value_config_key,
            None,
            type_=int,
        )

    def get_next_index(self, node):
        latest = self.get_latest_index(node)
        if latest is None:
            initial_value = self._get_initial_value(node)
            if initial_value is None:
                return 1
            else:
                return initial_value + 1
        else:
            return latest + 1

    def _query(self, node):
        q = DBSESSION().query(func.Max(SequenceNumber.index))
        q = q.join(self.model_class, SequenceNumber.node_id == Node.id)
        q = q.filter(self.model_class.type_.in_(self.types))
        q = q.filter(SequenceNumber.sequence == self.db_key)
        return q

    def get_latest_index(self, node):
        """
        :rtype: int or None
        """
        return self._query(node).scalar()

    def get_key(self, node):
        return ""


class YearSequence(GlobalSequence):
    def __init__(self, init_date_config_key, *args, **kwargs):
        self.init_date_config_key = init_date_config_key
        super().__init__(*args, **kwargs)

    def _get_initial_value(self, node):
        init_date = Config.get_value(
            self.init_date_config_key,
            default="",
            type_=date,
        )
        init_value = Config.get_value(
            self.init_value_config_key,
            default=0,
            type_=int,
        )
        if init_date and init_value and init_date.year == node.validation_date.year:
            return init_value

    def _query(self, node):
        assert node.validation_date is not None, "validated node should have a date"
        date_col = self.model_class.get_validation_date_column()
        q = super()._query(node)
        q = q.filter(extract("year", date_col) == node.validation_date.year)
        return q

    def get_key(self, node):
        return node.validation_date.year


class MonthSequence(YearSequence):
    def _get_initial_value(self, node):
        init_date = Config.get_value(
            self.init_date_config_key,
            default="",
            type_=date,
        )
        init_value = Config.get_value(
            self.init_value_config_key,
            default=0,
            type_=int,
        )
        if (
            init_date
            and init_value
            and init_date.year == node.validation_date.year
            and init_date.month == node.validation_date.month
        ):
            return init_value
        else:
            return None

    def _query(self, node):
        date_col = self.model_class.get_validation_date_column()
        q = super(MonthSequence, self)._query(node)
        q = q.filter(extract("month", date_col) == node.validation_date.month)
        return q

    def get_key(self, node):
        return "{}-{}".format(node.validation_date.year, node.validation_date.month)


class MonthCompanySequence(MonthSequence):
    def __init__(self, *args, **kwargs):
        self.company_init_date_fieldname = kwargs.pop(
            "company_init_date_fieldname", None
        )
        self.company_init_value_fieldname = kwargs.pop(
            "company_init_value_fieldname", None
        )
        super(MonthCompanySequence, self).__init__(
            # this is defined per-company, thus passing None for app-wide init
            # args
            init_date_config_key=None,
            init_value_config_key=None,
            *args,
            **kwargs,
        )

    def _get_initial_value(self, node):
        if (
            self.company_init_date_fieldname is None
            or self.company_init_value_fieldname is None
        ):
            return None
        init_date = getattr(node.company, self.company_init_date_fieldname)
        init_value = getattr(node.company, self.company_init_value_fieldname)
        if (
            init_date
            and init_value
            and init_date.year == node.validation_date.year
            and init_date.month == node.validation_date.month
        ):
            return init_value
        else:
            return None

    def _query(self, node):
        q = super(MonthCompanySequence, self)._query(node)
        q = q.filter(self.model_class.company == node.company)
        return q

    def get_key(self, node):
        return "{}-{}-{}".format(
            node.validation_date.year, node.validation_date.month, node.company.id
        )
