"""
Expense computing tool
"""
from itertools import chain

from caerp.compute import math_utils


class ExpenseCompute:
    lines = ()
    kmlines = ()
    payments = ()
    sepa_waiting_payments = ()

    def _lines_by_category(self, lines, category=None):
        """
        Return the lines matching the category if provided
        """
        for line in lines:
            if category in ("1", "2") and line.category != category:
                continue
            else:
                yield line

    def get_lines(self, category="0"):
        """
        Return all expense lines (lines and kmlines)
        """
        res = []
        for line in self._lines_by_category(self.lines, category):
            res.append(line)
        for line in self._lines_by_category(self.kmlines, category):
            res.append(line)
        return res

    def get_lines_by_type(self, category="0"):
        """
        Return expense lines grouped by treasury code
        """
        ret_dict = {}
        for line in self._lines_by_category(self.lines, category):
            ret_dict.setdefault(line.expense_type.code, []).append(line)

        for line in self._lines_by_category(self.kmlines, category):
            ret_dict.setdefault(line.expense_type.code, []).append(line)

        return list(ret_dict.values())

    @property
    def total(self):
        return sum([line.total for line in self.lines]) + sum(
            [line.total for line in self.kmlines]
        )

    def paid(self) -> int:
        return sum([payment.get_amount() for payment in self.payments])

    def topay(self) -> int:
        return self.total - self.paid()

    def sepa_waiting_amount(self) -> int:
        """Amount already waiting for being inserted in SEPA order"""
        return sum(
            [
                payment.amount
                for payment in self.sepa_waiting_payments
                if payment.paid_status == payment.WAIT_STATUS
            ]
        )

    def amount_waiting_for_payment(self) -> int:
        """Amount not yet inserted in SEPA order and not yet paid"""
        return self.topay() - self.sepa_waiting_amount()

    @property
    def total_tva(self):
        return sum([line.total_tva for line in self.lines]) + sum(
            [line.total_tva for line in self.kmlines]
        )

    @property
    def total_ht(self):
        return sum([line.total_ht for line in self.lines]) + sum(
            [line.total_ht for line in self.kmlines]
        )

    @property
    def total_km(self):
        return sum([line.km for line in self.kmlines])

    def get_total(self, category=None):
        line_total = sum(
            [line.total for line in self._lines_by_category(self.lines, category)]
        )
        kmlines_total = sum(
            [line.total for line in self._lines_by_category(self.kmlines, category)]
        )
        return line_total + kmlines_total

    @property
    def is_void(self):
        return not self.get_lines()


class ExpenseLineCompute:
    """
    Expense lines related computation tools
    """

    expense_type = None

    def _compute_value(self, val):
        result = 0
        if self.expense_type is not None:
            if self.expense_type.type == "expensetel":
                percentage = self.expense_type.percentage
                val = val * percentage / 100.0
            result = math_utils.floor(val)
        return result

    @property
    def total(self):
        return self.total_ht + self.total_tva

    @property
    def total_ht(self):
        return self._compute_value(self.ht)

    @property
    def total_tva(self):
        return self._compute_value(self.tva)


class ExpenseKmLineCompute:
    expense_type = None

    @property
    def total(self):
        return math_utils.floor(self.ht)

    @property
    def total_ht(self):
        return self.total

    @property
    def total_tva(self):
        return 0
