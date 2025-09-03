"""
 Task compute methods and attributes for both ht and ttc mode
"""

import math
import operator
import typing

from caerp.compute import math_utils
from caerp.consts import AMOUNT_PRECISION, PAYMENT_EPSILON
from caerp.models.tva import Tva


class CommonTaskCompute:
    """
    Computing tool for both ttc and ht mode in tasks objects
    """

    __round_floor = False

    def __init__(self, task):
        self.task = task

    def floor(self, amount):
        return math_utils.floor_to_precision(amount, self.__round_floor)

    def groups_total_ht(self):
        """
        compute the sum of the task lines total
        """
        return sum(group.total_ht() for group in self.task.line_groups)

    def groups_total_ttc(self):
        """
        compute the sum of the task lines total
        """
        return sum(group.total_ttc() for group in self.task.line_groups)

    def discount_total_ht(self):
        """
        compute the discount total
        """
        return sum(line.total_ht() for line in self.task.discounts)

    def discount_total_ttc(self):
        """
        compute the discount total
        """
        return sum(line.total_ttc() for line in self.task.discounts)

    def post_ttc_total(self):
        """
        compute the sum of the post-ttc lines
        """
        return sum(line.amount for line in self.task.post_ttc_lines)

    def total_due(self):
        """
        compute the total_due
        """
        return self.total() + self.post_ttc_total()

    @staticmethod
    def add_ht_by_tva(ret_dict, lines, operation=operator.add):
        """
        Add ht sums by tva to ret_dict for the given lines
        """
        for line in lines:
            val = ret_dict.get(line.get_tva(), 0)
            ht_amount = operation(val, line.total_ht())
            ret_dict[line.get_tva()] = ht_amount
        return ret_dict

    def total_ht_rate(self, key: str, ht: typing.Optional[int] = None) -> int:
        """
        Compute a rate on the HT value of the current task
        Used by the accounting export modules

        :param str key: Name of the ratio in the software's nomenclature (contribution, insurance ...)
        """
        rate = self.task.get_rate(key)
        result = 0
        if rate:
            if ht is None:
                ht = self.total_ht()
            result = math_utils.percentage(ht, rate)
        return result

    def tva_native_parts(self, with_discounts=True) -> dict:
        """
        Return amounts by tva in "native" mode (HT or TTC regarding the mode)
        """
        raise NotImplementedError()

    def tva_ht_parts(self, with_discounts=True) -> dict:
        """
        Compute HT amounts by tva
        """
        raise NotImplementedError()

    def tva_ttc_parts(self, with_discounts=True) -> dict:
        """
        Compute TTC amounts by tva
        """
        raise NotImplementedError()

    def get_tvas(self) -> dict:
        """
        Compute TVA amount by TVA rate
        """
        raise NotImplementedError()

    def tva_amount(self) -> int:
        """
        Compute the total amount of TVA for this doc
        """
        raise NotImplementedError()

    def get_tvas_by_product(self) -> dict:
        """
        Compute the amount of TVA by product_id
        """
        raise NotImplementedError()

    def total_ht(self) -> int:
        raise NotImplementedError()

    def total_ttc(self) -> int:
        raise NotImplementedError()

    def total(self) -> int:
        raise NotImplementedError()


class CommonGroupCompute:
    """
    Computing tool for both ttc and ht mode in group objects
    """

    def __init__(self, task_line_group):
        from caerp.models.task import TaskLineGroup

        self.task_line_group: TaskLineGroup = task_line_group

    def get_tvas(self):
        """
        return a dict with the tvas amounts stored by tva
        {1960:450.56, 700:45}
        """
        ret_dict = {}
        for line in self.task_line_group.lines:
            val = ret_dict.get(line.tva, 0)
            val += line.tva_amount()
            ret_dict[line.tva] = val
        return ret_dict

    def get_tvas_by_product(self) -> dict:
        """
        return a dict with the tvas amounts stored by product
        We use a key (product.compte_cg, product.tva.compte_cg)
        """
        ret_dict = {}
        for line in self.task_line_group.lines:
            compte_cg_produit = line.product.compte_cg
            compte_cg_tva = line.product.tva.compte_cg
            key = (compte_cg_produit, compte_cg_tva)
            val = ret_dict.get(key, 0)
            val += line.tva_amount()
            ret_dict[key] = val
        return ret_dict

    def tva_amount(self):
        """
        Returns the TVA total for this group
        """
        return sum(tva for tva in list(self.get_tvas().values()))

    def total_ht(self):
        """
        Returns the ht total for this group
        """
        return sum(line.total_ht() for line in self.task_line_group.lines)

    def total_ttc(self):
        return sum(line.total() for line in self.task_line_group.lines)


class CommonLineCompute:
    """
    Computing tool for both ttc and ht mode in task_line
    """

    def __init__(self, task_line):
        from caerp.models.task import TaskLine

        self.task_line: TaskLine = task_line

    def get_tva(self):
        """
        Return the line task_line tva
        :return: int
        """
        return self.task_line.tva

    def _get_quantity(self):
        """
        Retrieve the configured quantity, returns 1 by default
        """
        quantity = getattr(self.task_line, "quantity", None)
        if quantity is None:
            quantity = 1
        return quantity


class CommonDiscountLineCompute:
    """
    Computing tool for both ttc and ht mode in discount_line
    """

    def __init__(self, discount_line):
        from caerp.models.task import DiscountLine

        self.discount_line: DiscountLine = discount_line

    def get_tva(self):
        """
        Return the line discount_line tva
        :return: int
        """
        return self.discount_line.tva

    def total_ht(self):
        raise NotImplementedError()

    def total(self):
        raise NotImplementedError()


class InvoiceCompute:
    """
    Invoice computing object
    Handles payments
    """

    def __init__(self, task):
        from caerp.models.task import Task

        self.task: Task = task

    def payments_sum(self, year: typing.Optional[int] = None):
        """
        Return the amount covered by the recorded payments

        :param year: limit the considered payments to this year
        """
        return sum(
            [
                payment.amount
                for payment in self.task.payments
                if payment.date.year == year or year is None
            ]
        )

    def cancelinvoice_amount(self, year: typing.Optional[int] = None):
        """
        Return the amount covered by th associated cancelinvoices

        :param year: limit the considered cancel invoices to this year
        """
        result = 0
        for cancelinvoice in self.task.cancelinvoices:
            year_match = year == cancelinvoice.date.year
            if cancelinvoice.status == "valid" and (year is None or year_match):
                # cancelinvoice total is negative
                result += -1 * cancelinvoice.total()
        return result

    def paid(self, year: typing.Optional[int] = None):
        """
        return the amount that has already been paid

        :param year: limit the considered payments to one year
        """
        return self.payments_sum(year) + self.cancelinvoice_amount(year)

    def topay(self):
        """
        Return the amount that still need to be paid

        Compute the sum of the payments and what's part of a valid
        cancelinvoice
        """
        result = self.task.total() - self.paid()
        return math_utils.floor_to_precision(result)

    def tva_paid_parts(self) -> dict:
        """
        return the amounts already paid by tva

        :returns: A dict {tva value: paid amount}
        """
        result = {}
        for payment in self.task.payments:
            if payment.tva is not None:
                key = payment.tva.value
            else:
                key = list(self.task.tva_ht_parts().keys())[0]

            result.setdefault(key, 0)
            result[key] += payment.amount

        return result

    def tva_cancelinvoice_parts(self) -> dict:
        """
        Returns the amounts already paid through cancelinvoices by tva

        :returns: A dict {tva value: canceled amount}
        """
        result = {}
        for cancelinvoice in self.task.cancelinvoices:
            if cancelinvoice.status == "valid":
                ttc_parts = cancelinvoice.tva_ttc_parts()
                for key, value in list(ttc_parts.items()):
                    if key in result:
                        result[key] += value
                    else:
                        result[key] = value
        return result

    def topay_by_tvas(self) -> dict:
        """
        Returns the amount to pay by tva part

        :returns: A dict {tva value: to pay amount}
        """
        result = {}
        paid_parts = self.tva_paid_parts()
        cancelinvoice_tva_parts = self.tva_cancelinvoice_parts()
        for tva_value, amount in self.task.tva_ttc_parts().items():
            val = amount
            val = val - paid_parts.get(tva_value, 0)
            val = val + cancelinvoice_tva_parts.get(tva_value, 0)
            result[tva_value] = val
        return result

    def round_payment_amount(self, payment_amount):
        """
        Returns a rounded value of a payment.

        :param int payment_amount: Amount in biginteger representation
        """
        return math_utils.floor_to_precision(
            payment_amount,
            precision=2,
        )

    def _get_payment_excess(self, payment_amount, invoice_topay):
        # Is there an excess of payment ?
        payment_excess = None
        if math.fabs(payment_amount) > math.fabs(invoice_topay):
            payment_excess = payment_amount - invoice_topay

        return payment_excess

    def _is_last_payment(self, payment_amount, invoice_topay):
        """
        Check if the payment amount covers what is to pay

        :rtype: bool
        """
        # Different TVA rates are still to be paid
        if invoice_topay < 0:
            last_payment = payment_amount <= invoice_topay
        else:
            last_payment = payment_amount >= invoice_topay
        return last_payment

    def _get_single_tva_payment(self, payment_amount, topay_by_tvas):
        """
        Return payment list in case of single tva invoice
        """
        # Round the amount in case the user put a number
        # with more than 2 digits
        payment_amount = self.round_payment_amount(payment_amount)

        tva_value = list(topay_by_tvas)[0][0]
        tva_id = Tva.by_value(tva_value).id

        return [{"tva_id": tva_id, "amount": payment_amount}]

    def _get_payments_by_tva(
        self, payment_amount, invoice_topay, payment_excess, topay_by_tvas
    ):
        """
        Split a payment in separate payments by tva

        :rtype: dict
        """
        result = []
        nb_tvas = len(topay_by_tvas)
        last_payment = self._is_last_payment(payment_amount, invoice_topay)

        i_tva = 0
        already_paid = 0
        for tva_value, value in topay_by_tvas:
            i_tva += 1
            tva = Tva.by_value(tva_value)
            if invoice_topay == 0:
                ratio = 0
            else:
                ratio = value / invoice_topay

            amount = 0
            if not last_payment:
                if i_tva < nb_tvas:
                    # Tva intermédiaire, on utilise le ratio
                    amount = ratio * payment_amount
                    already_paid += amount
                    # It has to be rounded otherwise last TVA calculation
                    # will be wrong
                    already_paid = self.round_payment_amount(already_paid)
                else:
                    # Pour la dernière tva de la liste, on utilise une
                    # soustraction pur éviter les problèmes d'arrondi
                    amount = payment_amount - already_paid
            else:
                amount = value
                # On distribue également l'excès sur les différents taux de tva
                if payment_excess:
                    excess = payment_excess * ratio
                    amount = amount + excess

            amount = self.round_payment_amount(amount)

            if amount != 0:
                result.append({"tva_id": tva.id, "amount": amount})
        return result

    def compute_payments(self, payment_amount):
        """
        Returns payments corresponding to the payment amount
        If there is just one TVA rate left to be paid in the invoice it
        returns just one payment.
        If there are different TVA rate left to be paid in the invoice
        it returns a payment for each TVA rate

        :param int payment_amount: Amount coming from the UI (in biginteger
        format)

        :rtype: array
        :returns: [{'tva_id': <Tva>.id, 'amount': 123}, ...]
        """
        invoice_topay = self.topay()
        payment_excess = self._get_payment_excess(payment_amount, invoice_topay)

        topay_by_tvas = self.topay_by_tvas().items()
        nb_tvas = len(topay_by_tvas)

        if nb_tvas == 1:
            result = self._get_single_tva_payment(payment_amount, topay_by_tvas)
        else:
            result = self._get_payments_by_tva(
                payment_amount,
                invoice_topay,
                payment_excess,
                topay_by_tvas,
            )

        # Return an array of dict: Array({amount: ,tva_id: })
        return result


class EstimationCompute:
    """
    Computing class for estimations
    Adds the ability to compute deposit amounts ...
    """

    def __init__(self, task):
        from caerp.models.task import Estimation

        self.task: Estimation = task

    def deposit_amounts_native(self):
        """
        Return the lines of the deposit for the different amount of tvas

        (amounts are native : HT or TTC depending on estimation mode)
        """
        ret_dict = {}

        for tva, total_native in list(self.task.tva_native_parts().items()):
            ret_dict[tva] = self.task.floor(
                math_utils.percentage(total_native, self.task.deposit)
            )
        return ret_dict

    def get_nb_payment_lines(self):
        """
        Returns the number of payment lines configured
        """
        return len(self.task.payment_lines)

    def paymentline_amounts_native(self):
        """
        Compute payment lines amounts in case of equal payment repartition:

            when manualDeliverables is 0

        e.g :

            when the user has selected 3 time-payment

        :returns: A dict describing the payments {'tva1': amount1, 'tva2':
            amount2} (amounts are native : HT or TTC depending on estimation mode)
        """
        ret_dict = {}

        totals = self.task.tva_native_parts()

        deposits = self.deposit_amounts_native()
        # num_parts set the number of equal parts
        num_parts = self.get_nb_payment_lines()
        for tva, total_native in list(totals.items()):
            rest = total_native - deposits[tva]
            line_amount_native = rest / num_parts
            ret_dict[tva] = line_amount_native
        return ret_dict

    # Computations for payment lines management
    def deposit_amount_ht(self):
        if self.task.deposit > 0:
            total_ht = self.task.total_ht()
            deposit = math_utils.percentage(self.task.deposit, total_ht)
            return self.task.floor(deposit)
        return 0

    def deposit_amount_ttc(self):
        """
        Return the ttc amount of the deposit (for estimation display)
        """
        if self.task.deposit > 0:
            total_ttc = self.task.total()
            deposit = math_utils.percentage(self.task.deposit, total_ttc)
            return self.task.floor(deposit)
        return 0

    def paymentline_amount_ttc(self):
        """
        Return the ttc amount of payment (in equal repartition)
        """
        from caerp.models.task import TaskLine

        total_ttc = 0
        for tva, native_total in list(self.paymentline_amounts_native().items()):
            line = TaskLine(cost=native_total, tva=tva, mode=self.task.mode)
            total_ttc += self.task.floor(line.total())
        return total_ttc

    def compute_ht_from_partial_ttc(self, partial_ttc: int) -> int:
        """
        Compute the HT amount from a partial TTC amount proportionnaly to
        the estimation's TTC

        Used to compute quickly the amount_ht of a paymentline
        """
        total = self.task.total()
        ratio = math_utils.percent(partial_ttc, total, precision=5, default=0)
        return self.task.floor(math_utils.percentage(self.task.total_ht(), ratio))

    def sold(self):
        """
        Compute the sold amount to finish on an exact value
        if we divide 10 in 3, we'd like to have something like :
            3.33 3.33 3.34
        (for estimation display)
        """
        result = 0
        total_ttc = self.task.total()
        deposit_ttc = self.deposit_amount_ttc()
        rest = total_ttc - deposit_ttc

        payment_lines_num = self.get_nb_payment_lines()
        if payment_lines_num <= 1:
            # No other payment line
            result = rest
        else:
            payment_lines = self.task.payment_lines[:-1]
            result = rest - sum([line.amount for line in payment_lines])
        return result
