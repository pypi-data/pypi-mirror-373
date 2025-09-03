"""
Computing tools for sage import/export


Main use:

    for a given export (e.g : expense)
    we've got export modules (some mandatory, others optionnal)
    we build a SageExpenseBase that build the columns common to all exported
    lines
    we inherit from that for each module
    we build a ExpenseExport class that will connect all modules, provide
    public methods and yield the book lines
"""

import logging

from zope.interface import implementer

from caerp.models.accounting.bookeeping import CustomInvoiceBookEntryModule
from caerp.interfaces import ITreasuryProducer

logger = log = logging.getLogger(__name__)


def filter_accounting_entry(entry):
    """
    Filter accounting entry to apply some generic rules :
        * Ensure Credit/Debit are always positive

    :param dict entry: A dict with accounting entry datas
    :returns: The formatted entry
    """
    if entry.get("credit", 0) < 0:
        entry["debit"] = -1 * entry.pop("credit")
    if entry.get("debit", 0) < 0:
        entry["credit"] = -1 * entry.pop("debit")
    return entry


def generate_general_entry(analytic_entry: dict) -> dict:
    """
    Generate a General "entry" (dict of data) base on the given analytic_entry
    """
    general_entry = analytic_entry.copy()
    general_entry["type_"] = "G"
    # Keep a pointer from analytic to general
    analytic_entry["_general_counterpart"] = general_entry
    general_entry["_analytic_counterpart"] = analytic_entry
    general_entry.pop("num_analytique", None)
    return general_entry


def double_lines(method):
    """
    Wrap a book entry generator by duplicating the analytic book entry as a
    general one
    """

    def wrapped_method(self, *args, **kwargs):
        """
        Return two entries from one
        """
        analytic_entry = method(self, *args, **kwargs)
        return generate_general_entry(analytic_entry), analytic_entry

    return wrapped_method


class MissingData(Exception):
    """
    Raised when no data was retrieved from a lazy relationship
    If an element has an attribute that should point to another model, and
    that this model doesn't exist anymore, we raise this exception.
    """

    pass


class BaseSageBookEntryFactory:
    """
    Base Sage Book Entry factory : we find the main function used by export
    modules
    """

    # Tells us if we need to add analytic entries to our output (double_lines)
    static_columns = ()
    _part_key = None
    _label_template_key = None
    config_key_prefix = ""

    def __init__(self, context, request):
        self.request = request
        self.config = self.request.config
        self.company = None
        if self._label_template_key:
            self.label_template = self._get_config_value(
                self._label_template_key,
            )
            assert (
                self.label_template is not None
            ), '"{}" Config key should be set'.format(self._label_template_key)

    def _get_config_key(self, key):
        if self.config_key_prefix:
            key = "{}{}".format(self.config_key_prefix, key)
        return key

    def _get_config_value(self, key, default=None):
        key = self._get_config_key(key)
        return self.config.get(key, None)

    def get_base_entry(self):
        """
        Return an entry with common parameters
        """
        return dict((key, getattr(self, key)) for key in self.static_columns)

    def get_part(self) -> float:
        """
        Collect the part for pre-defined accounting bookentries export modules
        (RG Intere, RG externe)
        """
        try:
            part = float(self._get_config_value(self._part_key))
        except (ValueError, TypeError):
            raise MissingData(
                "The Taux {0} should be a float".format(
                    self._get_config_key(self._part_key)
                )
            )
        return part

    def get_contribution(self) -> float:
        """
        Return the contribution for the current invoice, the company's one
        or the cae's one by default
        """
        contrib = self.company.get_rate(
            self.company.id,
            "contribution",
            self.config_key_prefix,
        )
        return contrib

    def get_contribution_module(self) -> "CustomInvoiceBookEntryModule":
        """
        Return the CustomInvoiceBookEntryModule used for the export
        of contribution
        """
        # On attache le module à l'instance pour limiter les requêtes
        if not hasattr(self, "_contribution_module"):
            module = CustomInvoiceBookEntryModule.get_by_name(
                "contribution", self.config_key_prefix
            )
            setattr(self, "_contribution_module", module)
        return self._contribution_module

    @property
    def type_(self):
        """
        Return A for 'Analytic' book entry
        """
        return "A"


@implementer(ITreasuryProducer)
class VoidProducer:
    def __init__(self, context, request):
        self.config = request.config
        self.modules = []

    def _get_item_book_entries(self, supplier_invoice):
        """
        Return book entries for the given supplier invoice

        :param obj supplier_invoice: A SupplierInvoice object

        :results: Nothing
        """
        return []

    def get_item_book_entries(self, supplier_invoice):
        return []

    def get_book_entries(self, supplier_invoices):
        """
        Return book entries for the given supplier invoices

        :param list supplier_invoices: SupplierInvoice objects
        :results: A list
        """
        return []
