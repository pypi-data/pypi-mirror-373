import logging

from itertools import chain
from zope.interface import implementer

from caerp.interfaces import (
    ITreasuryGroupper,
    ITreasuryProducer,
)
from caerp.compute.math_utils import (
    floor,
    compute_ht_from_ttc,
    compute_tva,
)
from caerp.utils.accounting import get_customer_accounting_general_account
from caerp.utils.compat import Iterable
from caerp.utils.strings import strip_civilite

from .base import (
    double_lines,
    BaseSageBookEntryFactory,
    filter_accounting_entry,
    MissingData,
)
from .utils import (
    add_entries_amounts,
    fix_sage_ordering,
    normalize_entry,
)

logger = log = logging.getLogger(__name__)


class SagePaymentBase(BaseSageBookEntryFactory):
    # "_"-prefixed are hidden columns (won't appear in CSV export)
    static_columns = (
        "reference",
        "code_journal",
        "date",
        "mode",
        "libelle",
        "type_",
        "num_analytique",
        "_mark_debit_banque",
        "_bank_remittance_id",
        "customer_label",
        "company_name",
        "task_name",
    )

    variable_columns = (
        "compte_cg",
        "compte_tiers",
        "code_taxe",
        "debit",
        "credit",
    )

    _label_template_key = "bookentry_payment_label_template"

    def set_payment(self, payment):
        self.invoice = payment.invoice
        self.payment = payment
        self.company = self.invoice.company
        self.customer = self.invoice.customer

    @property
    def customer_label(self):
        return strip_civilite(self.customer.label)

    @property
    def company_name(self):
        return self.company.name

    @property
    def task_name(self):
        return self.invoice.name

    @property
    def reference(self):
        if self.payment.bank_remittance_id is None:
            return "{}".format(self.invoice.official_number)
        else:
            return "{0}/{1}".format(
                self.invoice.official_number,
                self.payment.bank_remittance_id,
            )

    @property
    def code_journal(self):
        return self.payment.bank.code_journal

    @property
    def date(self):
        return self.payment.date.date()

    @property
    def mode(self):
        return self.payment.mode

    @property
    def libelle(self):
        return strip_civilite(
            self.label_template.format(
                company=self.company,
                invoice=self.invoice,
                payment=self.payment,
            )
            .replace("None", "")
            .strip()
        )

    @property
    def num_analytique(self):
        """
        Return the analytic number common to all entries in the current
        export module
        """
        return self.company.code_compta

    @property
    def _bank_remittance_id(self):
        # mark used for grouping
        return self.payment.bank_remittance_id

    @property
    def _mark_debit_banque(self):
        # mark used for grouping
        return False


class SagePaymentMain(SagePaymentBase):
    """
    Main module for payment export
    """

    @double_lines
    def credit_client(self, val):
        entry = self.get_base_entry()
        tva_id = self.payment.tva.id if self.payment.tva else None
        customer_general_account = get_customer_accounting_general_account(
            self.request, self.customer.id, tva_id, self.config_key_prefix
        )
        entry.update(
            compte_cg=customer_general_account,
            compte_tiers=self.customer.get_third_party_account(
                prefix=self.config_key_prefix
            ),
            credit=val,
        )
        return entry

    def _get_bank_cg(self):
        result = self.payment.bank.compte_cg
        if not result:
            raise MissingData(
                "Code banque non configuré pour l'encaissement {}".format(
                    self.payment.id
                )
            )
        return result

    @double_lines
    def debit_banque(self, val):
        entry = self.get_base_entry()
        entry.update(
            compte_cg=self._get_bank_cg(),
            debit=val,
        )
        return entry

    def _has_remittance(self):
        """
        Renvoie True si une remise en banque est associé au paiement
        """
        return self.payment.bank_remittance_id is not None

    def _should_write_debit(self) -> bool:
        """
        Test si nous devons entréer une écriture de débit pour ce paiement

        Les cas où nous devons :
         - le groupage est désactivé dans la config (pris en charge par SagePaymentRemittance)
         - il n'y a pas de remise associée à ce paiement
        """
        if not self._has_remittance():
            return True
        else:
            receipts_grouping_strategy = self.config.get("receipts_grouping_strategy")
            return receipts_grouping_strategy in ("", None)

    def yield_entries(self):
        yield self.credit_client(self.payment.amount)
        if self._should_write_debit():
            yield self.debit_banque(self.payment.amount)


class InternalSagePaymentMain(SagePaymentMain):
    config_key_prefix = "internal"

    @property
    def reference(self):
        return self.invoice.official_number

    @property
    def code_journal(self):
        return self.config.get("internalcode_journal_encaissement")

    @property
    def mode(self):
        return "interne"

    def _should_write_debit(self):
        return True

    def _get_bank_cg(self):
        result = self.config.get("internalbank_general_account", None)
        if not result:
            raise MissingData(
                "Le compte bank des encaissements interne n'est pas configuré"
            )
        return result

    @property
    def _bank_remittance_id(self):
        # no remittance for internal payments
        return None


class SagePaymentTva(SagePaymentBase):
    """
    Optionnal Tva module
    """

    def get_amount(self):
        """
        Returns the reversed tva amount
        """
        tva_amount = self.payment.tva.value
        ht_value = compute_ht_from_ttc(
            self.payment.amount, tva_amount, division_mode=(self.invoice.mode != "ttc")
        )
        tva_value = compute_tva(ht_value, tva_amount)
        return floor(tva_value)

    @double_lines
    def credit_tva(self, total):
        entry = self.get_base_entry()
        entry.update(
            compte_cg=self.payment.tva.compte_a_payer,
            credit=total,
        )
        if self.payment.tva.code:
            entry.update(
                code_taxe=self.payment.tva.code,
            )
        return entry

    @double_lines
    def debit_tva(self, total):
        entry = self.get_base_entry()
        entry.update(
            compte_cg=self.payment.tva.compte_cg,
            debit=total,
        )
        if self.payment.tva.code:
            entry.update(
                code_taxe=self.payment.tva.code,
            )
        return entry

    def yield_entries(self):
        """
        Yield all the entries for the current payment
        """
        total = self.get_amount()
        if self.payment.tva.value > 0:
            # On ne génère pas les écritures pour les taux de TVA négatifs
            yield self.credit_tva(total)
            yield self.debit_tva(total)


class SagePaymentRemittance(SagePaymentBase):
    """
    Optionnal remittance module

    Write metadata (libelle/reference) about remittance instead of payment

    Export remittance informations instead of payments info
    Works together with PaymentExportGroupper for grouping
    """

    @double_lines
    def debit_banque(self):
        remittance = self.payment.bank_remittance
        remittance_id = self.payment.bank_remittance_id
        entry = self.get_base_entry()
        entry.update(
            date=remittance.remittance_date,
            reference=remittance_id,
            libelle="Remise {}".format(remittance_id),
            compte_cg=self.payment.bank.compte_cg,
            debit=self.payment.amount,
            _mark_debit_banque=True,
        )
        return entry

    def yield_entries(self):
        if self.payment.bank_remittance_id:
            yield self.debit_banque()


@implementer(ITreasuryProducer)
class PaymentExportProducer:
    """
    Export entries following the given path :

        Invoices -> Invoice -> Payments -> Payment
    """

    use_general = True
    use_analytic = True
    _default_modules = (SagePaymentMain,)
    _available_modules = {
        "receipts_active_tva_module": SagePaymentTva,
        "receipts_grouping_strategy": SagePaymentRemittance,
    }

    def __init__(self, context, request):
        self.request = request
        self.config = request.config
        self.modules = []
        for module in self._default_modules:
            self.modules.append(module(context, request))
        for config_key, module in self._available_modules.items():
            if self.config.get(config_key) not in ("0", ""):
                self.modules.append(module(context, request))

    def _get_item_book_entries(self, payment):
        """
        Return the receipts entries for the given payment
        """
        for module in self.modules:
            module.set_payment(payment)
            for entry in module.yield_entries():
                gen_line, analytic_line = entry
                if self.use_general:
                    yield filter_accounting_entry(gen_line)
                if self.use_analytic:
                    yield filter_accounting_entry(analytic_line)

    def get_item_book_entries(self, payment):
        return list(self._get_item_book_entries(payment))

    def get_book_entries(self, payments) -> Iterable[dict]:
        return chain(iter(self._get_item_book_entries(payment)) for payment in payments)


class InternalPaymentExportProducer(PaymentExportProducer):
    _default_modules = (InternalSagePaymentMain,)
    _available_modules = {}


@implementer(ITreasuryGroupper)
class PaymentExportGroupper:
    """
    Group accounting operations of payment exports

    Operations produced by the ExportProducer add some hidden columns :
    - _bank_remittance_id
    - _mark_debit_banque

    Operations are grouped following one of the strategies described here under

    One general operation will cumulate all data attached to a same bank_remittance

    In the second strategy, analytical operations cumulate all data attached to the
    same bank remittance and the same company

    Requirements :

        This exporter only supports operations generated by a producer using both
        analytic and general operations.
        Other producers (external libraries) may not be compatible with this one
    """

    # Defines which fields to use to calculate the grouping key of an item
    GROUPING_STRATEGY_KEYS = {
        "remittance_id": (
            "type_",
            "_bank_remittance_id",
        ),
        "remittance_id+code_analytique": (
            "type_",
            "_bank_remittance_id",
            "num_analytique",
        ),
    }

    def __init__(self, context, request):
        # FIXME: self.config ?
        configured_strategy = request.config.get_value("receipts_grouping_strategy")
        value = self.GROUPING_STRATEGY_KEYS.get(configured_strategy)
        if value is None:
            self._grouping_enabled = False
        else:
            self._grouping_key_structure = value
            self._grouping_enabled = True

    def group_into(self, group_item: dict, member_item: dict) -> None:
        # merge item2 into item1 (inplace).
        debit, credit = add_entries_amounts(group_item, member_item)
        group_item["debit"], group_item["credit"] = debit, credit

        # If we are merging two lines for 2 different companies
        if group_item.get("num_analytique") != member_item.get("num_analytique"):
            group_item["num_analytique"] = "* DIVERS *"

        # will set positive amounts, either in credit or debit
        normalize_entry(group_item)

        self._update_references(member_item, group_item)

    def _update_references(self, member_item, group_item):
        if member_item["type_"] == "G":
            # Keep track of merging on analytic side
            try:
                member_item["_analytic_counterpart"][
                    "_general_counterpart"
                ] = group_item
            except KeyError:
                pass  # may not be used

    def get_grouping_key_value(self, item: dict):
        return tuple(item.get(k) for k in self._grouping_key_structure)

    def group_items(self, items: Iterable[dict]) -> Iterable[dict]:
        if self._grouping_enabled:
            groups_index = {}
            groups = []

            for item in items:
                remittance_id = item["_bank_remittance_id"]

                # groupable item ?
                if remittance_id and item["_mark_debit_banque"]:
                    key = self.get_grouping_key_value(item)
                    existing_group = groups_index.get(key, None)

                    if existing_group:
                        # Update the group
                        self.group_into(existing_group, item)
                    else:
                        groupped_item = item.copy()
                        self._update_references(item, groupped_item)
                        # appended but may be mutated later in for-loop (if grouping occurs)
                        groups.append(groupped_item)
                        groups_index[key] = groupped_item
                else:
                    # not groupable, so yield it as-is
                    groups.append(item)
            groups = list(fix_sage_ordering(groups))
        else:
            groups = items

        return groups
