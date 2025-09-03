from caerp.compute.math_utils import compute_tva


class SaleProductSupplierHtComputer:
    """
    Computer class used to compute the values based on suplier_ht value

    flat_cost (supplier_ht) -> cost_price -> intermediate price -> unit_ht -> unit_ttc
    """

    def __init__(self, product, config):
        self.product = product
        self.company = self._get_company()
        self.tva = self._get_tva()
        self.config = config

    def _use_insurance(self):
        return self.config.get_value(
            "price_study_uses_insurance", default=True, type_=bool
        )

    def _use_contribution(self):
        return self.config.get_value(
            "price_study_uses_contribution", default=True, type_=bool
        )

    def _get_company(self):
        return self.product.company

    def _get_tva(self):
        return self.product.tva

    def flat_cost(self):
        """
        Return the base cost of this sale product

        :returns: The result in 10^5 format
        :rtype: int
        """
        return self.product.supplier_ht or 0

    def get_general_overhead(self):
        return self.company.general_overhead

    def cost_price(self):
        """
        Compute the cost price of the given self.product

        :returns: The result in 10*5 format

        :rtype: int
        """
        overhead = self.get_general_overhead()
        if overhead is None:
            overhead = 0

        supplier_ht = self.flat_cost()
        if overhead != 0:
            result = supplier_ht * (1 + overhead)
        else:
            result = supplier_ht
        return result

    def get_margin_rate(self):
        if self.company.use_margin_rate_in_catalog:
            return self.product.margin_rate or 0
        else:
            return self.company.margin_rate

    def intermediate_price(self):
        """
        Compute the intermediate price of a work item

        3/    Prix intermédiaire = Prix de revient / ( 1 - ( Coefficients marge
        + aléas + risques ) )
        """
        margin_rate = self.get_margin_rate()
        if margin_rate is None:
            margin_rate = 0

        if margin_rate == 0:
            result = self.cost_price()
        elif margin_rate != 1:
            result = self.cost_price()
            result = result / (1 - margin_rate)
        else:
            result = 0
        return result

    def _get_contribution(self):
        from caerp.models.company import Company

        return Company.get_contribution(self.company.id)

    def _get_insurance(self):
        from caerp.models.company import Company

        return Company.get_rate(self.company.id, "insurance")

    def _compute_ratio(self, base_price, rate) -> float:
        """
        Compute a new price integrating the rate amount in it

        :param int base_price: The base price
        :param float rate: The rate for which we compute the ratio

        :returns: A new price that answers : new_price - contribution = base_price
        """
        result = base_price
        if isinstance(rate, (int, float)):
            ratio = 1 - rate / 100.0
            if ratio != 0:
                result = base_price / ratio
        return result

    def price_with_contribution(self, base_price=None) -> float:
        """
        Apply contribution to the base_price (or intermediate_price)

        :param float base_price: The price from which we compute contribution
        :rtype: float
        """
        if base_price is None:
            base_price = self.intermediate_price()

        result = base_price or 0
        if base_price != 0 and self._use_contribution():
            contribution = self._get_contribution()
            result = self._compute_ratio(result, contribution)
        return result

    def price_with_insurance(self, base_price=None) -> float:
        """
        Apply insurance to the base_price (or price_with_contribution)

        :param float base_price: The price from which we compute insurance
        :rtype: float
        """
        if base_price is None:
            base_price = self.price_with_contribution()

        result = base_price or 0
        if base_price != 0 and self._use_insurance():
            insurance = self._get_insurance()
            result = self._compute_ratio(result, insurance)
        return result

    def unit_ht(self):
        """
        Compute the ht value for the given work item
        """
        intermediate_price = self.intermediate_price()
        result = intermediate_price
        if intermediate_price != 0:
            if self._use_contribution():
                result = self.price_with_contribution(result)

            if self._use_insurance():
                result = self.price_with_insurance(result)
        elif self.product.supplier_ht == 0:
            result = 0
        else:
            result = self.product.ht or 0
        return result

    def unit_ttc(self):
        """
        Compute the ttc value for the given sale product
        """
        ht = self.unit_ht()
        tva = self.tva
        if tva is not None:
            return ht + compute_tva(ht, tva.value)
        else:
            return ht


class SaleProductWorkItemSupplierHtComputer(SaleProductSupplierHtComputer):
    def _get_company(self):
        return self.product.get_company()

    def _get_tva(self):
        return self.product.get_tva()

    def _get_quantity(self):
        quantity = self.product.quantity
        if quantity is None:
            quantity = 0
        return quantity

    def get_margin_rate(self):
        if self.company.use_margin_rate_in_catalog:
            return self.product.sale_product_work.margin_rate
        else:
            return self.company.margin_rate

    def full_flat_cost(self):
        value = self.flat_cost()
        return value * self._get_quantity()

    def full_cost_price(self):
        value = self.cost_price()
        return value * self._get_quantity()

    def full_intermediate_price(self):
        value = self.intermediate_price()
        return value * self._get_quantity()

    def full_price_with_contribution(self, base_price=None):
        value = self.price_with_contribution(base_price)
        if base_price:
            return value
        else:
            return value * self._get_quantity()

    def full_price_with_insurance(self, base_price=None):
        value = self.price_with_insurance(base_price)
        if base_price:
            return value
        else:
            return value * self._get_quantity()
