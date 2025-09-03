from caerp.compute import math_utils
from caerp.compute.base_line import BaseLineCompute


class SupplierOrderCompute:
    """
    Handles numbers as decimal stored as int with 2 decimals.

    Attributs utilisés pour le calcul:

    lines : SupplierOrderLine[]
    cae_percentage: int

    """

    @property
    def total(self) -> int:
        return sum([line.total for line in self.lines])

    @property
    def cae_total(self) -> int:
        cae_total_as_integer = math_utils.floor_to_precision(
            self.total * self.cae_percentage / 100,
            precision=2,
            dialect_precision=2,
        )
        return cae_total_as_integer

    @property
    def worker_total(self) -> int:
        return self.total - self.cae_total

    @property
    def total_tva(self) -> int:
        return sum([line.total_tva for line in self.lines])

    @property
    def total_ht(self) -> int:
        return sum([line.total_ht for line in self.lines])


class SupplierOrderLineCompute(BaseLineCompute):
    pass
