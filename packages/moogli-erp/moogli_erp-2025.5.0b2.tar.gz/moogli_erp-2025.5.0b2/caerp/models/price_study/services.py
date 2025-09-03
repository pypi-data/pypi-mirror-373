import logging
from caerp_base.models import DBSESSION
from caerp.compute.math_utils import (
    compute_tva,
    floor_to_precision,
    percentage,
)

from caerp.compute.math_utils import integer_to_amount
from caerp.models.tools import (
    get_labor_units_sqla_filter,
    get_not_labor_units_sqla_filter,
)


logger = logging.getLogger(__name__)


class PriceStudyService:
    @classmethod
    def get_company_id(cls, study):
        if study.task:
            return study.task.company_id
        else:
            return None

    @classmethod
    def get_company(cls, study):
        if study.task:
            return study.task.company
        else:
            return None

    @classmethod
    def is_editable(cls, study):
        """
        Check if the current PriceStudy is editable
        """
        # Sale bout de code qui ne tient pas compte du rôle de l'entrepreneur
        return study.task.status in (
            "draft",
            "invalid",
        )

    @classmethod
    def is_admin_editable(cls, study):
        """
        Check if the current PriceStudy is editable by an admin
        """
        # Sale bout de code qui ne tient pas compte du rôle de l'entrepreneur
        return study.task.status in ("draft", "invalid", "wait")

    @classmethod
    def _get_total_dict(
        cls, request, product_query, work_item_query, labor=False
    ) -> dict:
        """
        Build a dict by type with the different intermediary totals

        :param obj product_query: The PriceStudyProduct query
        :param obj Work_item_query: The PriceStudyWorkItem query
        :param bool labor: Are this totals labor related (should we count hours)
        """
        from caerp.models.config import Config

        result = {
            "flat_cost": 0,
            "cost_price": 0,
            "intermediate_price": 0,
            "price_with_contribution": 0,
            "price_with_insurance": 0,
            "computed_ht": 0,
            "total_ht": 0,
        }
        use_contribution = Config.get_value(
            "price_study_uses_contribution", default=True, type_=bool
        )
        use_insurance = Config.get_value(
            "price_study_uses_insurance", default=True, type_=bool
        )
        if labor:
            result["hours"] = 0
        for product in product_query:
            quantity = product.quantity
            flat_cost = product.flat_cost()
            result["flat_cost"] += flat_cost * quantity
            result["cost_price"] += product.cost_price() * quantity

            intermediate_price = product.intermediate_price()
            result["intermediate_price"] += intermediate_price * quantity

            if use_contribution:
                price_with_contribution = product.price_with_contribution(
                    intermediate_price
                )
            else:
                price_with_contribution = intermediate_price
            result["price_with_contribution"] += price_with_contribution * quantity

            if use_insurance:
                price_with_insurance = product.price_with_insurance(
                    price_with_contribution
                )
            else:
                price_with_insurance = price_with_contribution
            result["price_with_insurance"] += price_with_insurance * quantity

            if flat_cost:
                result["computed_ht"] += product.total_ht
            result["total_ht"] += product.total_ht
            if labor and "heure" in product.unity:
                result["hours"] += quantity

        for work_item in work_item_query:
            flat_cost = work_item.flat_cost(unitary=False)
            result["flat_cost"] += flat_cost
            result["cost_price"] += work_item.cost_price(unitary=False)

            intermediate_price = work_item.intermediate_price(unitary=False)
            result["intermediate_price"] += intermediate_price

            if use_contribution:
                price_with_contribution = work_item.price_with_contribution(
                    base_price=intermediate_price
                )
            else:
                price_with_contribution = intermediate_price
            result["price_with_contribution"] += price_with_contribution

            if use_insurance:
                price_with_insurance = work_item.price_with_insurance(
                    base_price=price_with_contribution
                )
            else:
                price_with_insurance = price_with_contribution
            result["price_with_insurance"] += price_with_insurance

            if flat_cost:
                result["computed_ht"] += work_item.total_ht
            result["total_ht"] += work_item.total_ht
            if labor and "heure" in work_item.unity:
                result["hours"] += work_item.total_quantity

        result["general_overhead"] = result["cost_price"] - result["flat_cost"]
        result["margin"] = result["intermediate_price"] - result["cost_price"]
        result["contribution"] = (
            result["price_with_contribution"] - result["intermediate_price"]
        )
        result["insurance"] = (
            result["price_with_insurance"] - result["price_with_contribution"]
        )
        for key, value in result.items():
            if key != "hours":
                result[key] = integer_to_amount(value, precision=5)
        return result

    @classmethod
    def json_totals(cls, request, price_study) -> dict:
        # 1- collect labor related products in supplier_ht mode
        # 2- collect labor related work items in supplier_ht mode
        from caerp.models.price_study import (
            PriceStudyProduct,
            PriceStudyWorkItem,
            PriceStudyWork,
        )

        product_query = PriceStudyProduct.query().filter(
            PriceStudyProduct.price_study == price_study
        )
        work_item_query = (
            PriceStudyWorkItem.query()
            .join(PriceStudyWork)
            .filter(PriceStudyWork.price_study == price_study)
        )

        result = {}

        product_labor_filter = get_labor_units_sqla_filter(PriceStudyProduct)
        work_item_labor_filter = get_labor_units_sqla_filter(PriceStudyWorkItem)

        result["labor"] = cls._get_total_dict(
            request,
            product_query.filter(product_labor_filter),
            work_item_query.filter(work_item_labor_filter),
            labor=True,
        )
        product_not_labor_filter = get_not_labor_units_sqla_filter(PriceStudyProduct)
        work_item_not_labor_filter = get_not_labor_units_sqla_filter(PriceStudyWorkItem)
        result["material"] = cls._get_total_dict(
            request,
            product_query.filter(product_not_labor_filter),
            work_item_query.filter(work_item_not_labor_filter),
            labor=False,
        )
        result["contributions"] = {
            "cae": result["labor"]["contribution"] + result["material"]["contribution"],
            "insurance": result["labor"]["insurance"] + result["material"]["insurance"],
        }
        return result

    @classmethod
    def amounts_by_tva(cls, price_study):
        """
        Collect HT and TVA amounts stored by tva value (in integer format)

        e.g : {tva_id: {'ht': 1000, 'tva': 200}}
        """
        if not hasattr(price_study, "_amount_cache"):
            result = {}
            for chapter in price_study.chapters:
                for product in chapter.products:
                    for tva, ht in list(product.ht_by_tva().items()):
                        result.setdefault(tva, {"ht": 0, "tva": 0})
                        result[tva]["ht"] += ht

            for tva, amounts in list(result.items()):
                ht = amounts["ht"]
                result[tva]["ht"] = floor_to_precision(ht)

                result[tva]["tva"] = floor_to_precision(
                    compute_tva(ht, max(tva.value, 0))  # Cas des tvas à taux négatifs
                )

            setattr(price_study, "_amount_cache", result)
        return price_study._amount_cache

    @classmethod
    def discounts_by_tva(cls, price_study):
        result = {}
        for discount in price_study.discounts:
            for tva, ht in list(discount.ht_by_tva().items()):
                result.setdefault(tva, {"ht": 0, "tva": 0})
                result[tva]["ht"] -= ht

        for tva, amounts in list(result.items()):
            ht = amounts["ht"]
            result[tva]["ht"] = floor_to_precision(ht)

            result[tva]["tva"] = floor_to_precision(
                compute_tva(ht, max(tva.value, 0))  # Cas des tvas à taux négatifs
            )
        return result

    @classmethod
    def total_ht_before_discount(cls, price_study):
        return sum(
            amount["ht"] for amount in list(cls.amounts_by_tva(price_study).values())
        )

    @classmethod
    def discount_ht(cls, price_study):
        return sum(
            amount["ht"] for amount in list(cls.discounts_by_tva(price_study).values())
        )

    @classmethod
    def total_ht(cls, price_study):
        return cls.total_ht_before_discount(price_study) + cls.discount_ht(price_study)

    @classmethod
    def total_tva_before_discount(cls, price_study):
        return sum(
            amount["tva"] for amount in list(cls.amounts_by_tva(price_study).values())
        )

    @classmethod
    def discount_tva(cls, price_study):
        return sum(
            amount["tva"] for amount in list(cls.discounts_by_tva(price_study).values())
        )

    @classmethod
    def total_tva(cls, price_study):
        return cls.total_tva_before_discount(price_study) + cls.discount_tva(
            price_study
        )

    @classmethod
    def total_ttc(cls, price_study):
        return cls.total_ht(price_study) + cls.total_tva(price_study)

    @classmethod
    def sync_amounts(cls, price_study, sync_down=False):
        """
        Compute cached amount attributes
        :param bool sync_down: Should we sync all children in the hierarchy
        """
        if hasattr(price_study, "_amount_cache"):
            delattr(price_study, "_amount_cache")
        if sync_down:
            for chapter in price_study.chapters:
                for product in chapter.products:
                    product.sync_amounts(propagate=False)
        price_study.ht = cls.total_ht(price_study)
        DBSESSION().merge(price_study)
        return True

    @classmethod
    def sync_with_task(cls, request, price_study):
        """
        Sync price_study elements with the associated Task
        """
        logger.debug("{}.sync_with_task".format(cls))
        task = price_study.task
        for chapter in price_study.chapters:
            chapter.sync_with_task(request, task)

        all_discounts = list(task.discounts)
        for discount in all_discounts:
            request.dbsession.delete(discount)
            task.discounts.remove(discount)

        for discount in price_study.discounts:
            discount.sync_with_task(request, price_study)

        task.cache_totals(request)

    @classmethod
    def on_before_commit(cls, request, price_study, state, changes=None):
        if changes and "general_overhead" in changes:
            # On recalcule tout d'abord l'ensemble des produits en mode coût d'achat
            from .work import PriceStudyWork

            for product in price_study.products:
                if isinstance(product, PriceStudyWork):
                    product.sync_amounts(propagate=False)
                elif product.mode == "supplier_ht":
                    product.sync_amounts()
            price_study.sync_amounts()
            price_study.sync_with_task(request)


class PriceStudyChapterService:
    @classmethod
    def get_company_id(cls, chapter):
        if chapter.price_study:
            return chapter.price_study.get_company_id()
        else:
            return None

    @classmethod
    def get_company(cls, chapter):
        if chapter.price_study:
            return chapter.price_study.get_company()
        else:
            return None

    @classmethod
    def sync_with_task(cls, request, chapter, task, sync_products=True):
        if chapter.task_line_group_id is None:
            from caerp.models.task import TaskLineGroup

            group = TaskLineGroup(task=task)
            request.dbsession.add(group)
            chapter.task_line_group = group
            request.dbsession.merge(chapter)
        else:
            group = chapter.task_line_group
        if task:
            # On s'assure que la valeur est définie
            group.task_id = task.id
        group.title = chapter.title
        group.description = chapter.description
        group.order = chapter.order
        group.display_details = chapter.display_details

        request.dbsession.merge(group)
        request.dbsession.flush()
        if sync_products:
            for product in chapter.products:
                product.sync_with_task(request)
        return group

    @classmethod
    def total_ht(cls, request, chapter):
        """
        Sum the total ht of the products
        """
        return sum(product.total_ht for product in chapter.products)

    @classmethod
    def on_before_commit(cls, request, chapter, state, changes=None):
        if state == "delete":
            price_study = chapter.price_study
            if chapter in price_study.chapters:
                price_study.chapters.remove(chapter)
            price_study.sync_amounts()
            price_study.sync_with_task(request)
        elif state in ("update", "add"):
            # Ordre / titre / description
            cls.sync_with_task(request, chapter, None, sync_products=False)


class BasePriceStudyProductService:
    @classmethod
    def get_company_id(cls, instance):
        if instance.chapter:
            return instance.chapter.get_company_id()
        else:
            return None

    @classmethod
    def get_company(cls, instance):
        if instance.chapter:
            return instance.chapter.get_company()
        else:
            return None

    @classmethod
    def _ensure_tva(cls, product):
        """
        Ensure cohesion between tva and product configuration

        Necessary because we can edit one and not the other leading to
        undesired states
        """
        # We ensure tva/product integrity
        if product.tva_id is None:
            task = product.price_study.task
            if task:
                product.tva = task.get_default_tva()
                if product.tva:
                    product.product_id = task.get_default_product_id(
                        default_tva=product.tva
                    )
            else:
                product.product_id = None
        elif product.product is not None and product.product.tva_id != product.tva_id:
            product.product_id = None

    @classmethod
    def _get_description(cls, product) -> str:
        return product.description

    @classmethod
    def _sync_task_line_attributes(cls, product, line):
        line.description = cls._get_description(product)

        line.quantity = product.quantity
        line.cost = product.ht
        line.unity = product.unity
        if product.tva:
            line.tva = product.tva.value
        line.product = product.product
        line.order = product.order
        return line

    @classmethod
    def sync_with_task(cls, request, product, chapter) -> "TaskLine":
        if product.task_line is None:
            from caerp.models.task import TaskLine

            line = TaskLine(group=chapter.task_line_group)
            request.dbsession.add(line)
            request.dbsession.flush()
            product.task_line = line
            request.dbsession.merge(product)
        else:
            line = product.task_line
        line = cls._sync_task_line_attributes(product, line)

        request.dbsession.merge(line)
        request.dbsession.flush()
        return line

    @classmethod
    def _on_delete(cls, request, price_study, chapter, product):

        if chapter and product in chapter.products:
            chapter.products.remove(product)
        if price_study:
            price_study.sync_amounts()
            price_study.sync_with_task(request)

    @classmethod
    def sync_amounts(cls, product, propagate=True):
        raise NotImplementedError()

    @classmethod
    def on_before_commit(cls, request, product, state, changes=None):
        raise NotImplementedError()


class PriceStudyProductService(BasePriceStudyProductService):
    @classmethod
    def _get_computer(cls, product):
        from caerp.models.config import Config

        if product.mode == "ht":
            from caerp.compute.price_study import (
                ProductHtComputer as Computer,
            )
        else:
            # mode = supplier_ht
            from caerp.compute.price_study import (
                ProductSupplierHtComputer as Computer,
            )
        return Computer(product, Config)

    @classmethod
    def flat_cost(cls, product):
        computer = cls._get_computer(product)
        return computer.flat_cost()

    @classmethod
    def cost_price(cls, product):
        """
        Compute the cost price of the given product work suming the cost of
        its differect items

        :returns: The result in 10*5 format

        :rtype: int
        """
        computer = cls._get_computer(product)
        return computer.cost_price()

    @classmethod
    def intermediate_price(cls, product):
        """
        Compute the intermediate price of a work item

        3/    Prix intermédiaire = Prix de revient / ( 1 - ( Coefficients marge
        + aléas + risques ) )
        """
        computer = cls._get_computer(product)
        return computer.intermediate_price()

    @classmethod
    def unit_ht(cls, product):
        """
        Compute the ht value for the given work item
        """
        computer = cls._get_computer(product)
        return computer.unit_ht()

    @classmethod
    def price_with_contribution(cls, product, base_price=None):
        computer = cls._get_computer(product)
        return computer.price_with_contribution(base_price)

    @classmethod
    def price_with_insurance(cls, product, base_price=None):
        computer = cls._get_computer(product)
        return computer.price_with_insurance(base_price)

    @classmethod
    def compute_total_ht(cls, product):
        """
        Compute total_ht value for this element
        """
        return product.unit_ht() * product.quantity

    @classmethod
    def ttc(cls, product):
        tva = product.tva
        ht = product.compute_total_ht()
        return ht + compute_tva(ht, tva.value)

    @classmethod
    def ht_by_tva(cls, product):
        """
        Return the ht value stored by vta value
        """
        if product.tva:
            return {product.tva: product.total_ht}
        else:
            return {}

    @classmethod
    def sync_amounts(cls, product, propagate=True):
        """
        Setup amounts for the given product and fire the information up
        """
        product.ht = product.unit_ht()
        product.total_ht = product.compute_total_ht()
        DBSESSION().merge(product)
        if propagate:
            product.chapter.price_study.sync_amounts()
        return True

    @classmethod
    def on_before_commit(cls, request, product, state, changes=None):
        """
        Fires actions before commit

        :param str state: 'add'/'update'/delete
        :param dict changes: The field that have been changed (in case of update)
        """
        logger.debug("{}.on_before_commit".format(cls))
        price_study = None
        chapter = product.chapter
        if chapter:
            price_study = product.chapter.price_study
        if state == "delete":
            need_sync_amounts = False
            cls._on_delete(request, price_study, chapter, product)

        elif state == "add":
            cls._ensure_tva(product)
            need_sync_amounts = True

        elif state == "update":

            need_sync_amounts = False
            if changes is not None:
                if "tva_id" in changes:
                    cls._ensure_tva(product)
                for key in (
                    "supplier_ht",
                    "ht",
                    "mode",
                    "margin_rate",
                    "quantity",
                    "mode",
                    "tva_id",
                ):
                    if key in changes:
                        need_sync_amounts = True
                        break
                if not need_sync_amounts:
                    cls.sync_with_task(request, product, None)
            else:
                need_sync_amounts = True

        if need_sync_amounts and price_study:
            cls.sync_amounts(product)
            price_study.sync_with_task(request)


class PriceStudyWorkService(BasePriceStudyProductService):
    @classmethod
    def _get_description(cls, work):
        result = "<strong>{}</strong>".format(work.title)
        if work.description:
            result += work.description
        return result

    @classmethod
    def flat_cost(cls, work):
        """
        Compute the flat cost of a complex work

        1/    Déboursé sec = Total matériaux + Total main d'oeuvre + Total
        matériel affecté
        """
        return sum([item.flat_cost(work_level=True) for item in work.items])

    @classmethod
    def cost_price(cls, work):
        """
        Compute the cost price of the given work work suming the cost of
        its differect items

        Prix de revient = Déboursé sec * ( 1 + Coefficient frais généraux )
        """
        return sum([item.cost_price() for item in work.items])

    @classmethod
    def intermediate_price(cls, work):
        """
        Compute the intermediate price

        If globally specified, uses the work's margin rate for the
        computation
        3/    Prix intermédiaire = Prix de revient / ( 1 - ( Coefficients marge
        + aléas + risques ) )
        """
        return sum([item.intermediate_price() for item in work.items])

    @classmethod
    def price_with_contribution(cls, work, base_price=None):
        return sum([item.price_with_contribution() for item in work.items])

    @classmethod
    def price_with_insurance(cls, work, base_price=None):
        return sum([item.price_with_insurance() for item in work.items])

    @classmethod
    def unit_ht(cls, work):
        return sum([item.work_unit_ht for item in work.items])

    @classmethod
    def compute_total_ht(cls, work):
        return sum([item.total_ht for item in work.items])

    @classmethod
    def ttc(cls, work):
        return sum([item.ttc() for item in work.items])

    @classmethod
    def ht_by_tva(cls, work):
        """
        Return the ht value stored by vta value
        """
        result = {}
        tva = work.tva
        if tva:
            result[tva] = cls.compute_total_ht(work)
        return result

    @classmethod
    def _sync_task_line_attributes(cls, product, line):
        line = super()._sync_task_line_attributes(product, line)
        # Fix #3348 : https://framagit.org/caerp/caerp/-/issues/3348
        # on utilise une quantité de 1
        line.quantity = 1
        line.cost = product.total_ht
        return line

    @classmethod
    def sync_amounts(cls, work, propagate=True):
        """
        Set all amounts on this work entry

        :param bool propagate: Should we propagate the syncing up ?
        """
        if not propagate:
            # On synchronise les enfants
            cls.sync_quantities(work)

        work.ht = work.unit_ht()
        work.total_ht = work.compute_total_ht()
        DBSESSION().merge(work)

        if propagate:
            # On synchronise les parents
            work.chapter.price_study.sync_amounts()

        return True

    @classmethod
    def sync_quantities(cls, work):
        """
        Sync all work items quantities and update amounts
        """
        for item in work.items:
            item.sync_quantities(work)
            item.sync_amounts(work)

    @classmethod
    def on_before_commit(cls, request, work, state, changes=None):
        logger.debug("{}.on_before_commit".format(cls))
        price_study = None
        chapter = work.chapter
        need_sync_amounts = False

        if chapter:
            price_study = work.chapter.price_study
        if state == "delete":
            cls._on_delete(request, price_study, chapter, work)
        elif state == "add":
            cls._ensure_tva(work)
            need_sync_amounts = True
        else:
            if changes:
                # On update les totaux uniquement si certains attributs ont été
                # modifiés
                for key in ("quantity", "margin_rate", "tva_id", "product_id"):
                    if key in changes:
                        need_sync_amounts = True

                if not need_sync_amounts:
                    cls.sync_with_task(request, work, None)
            else:
                need_sync_amounts = True

            if "tva_id" in changes:
                cls._ensure_tva(work)

        if need_sync_amounts:
            cls.sync_quantities(work)
            cls.sync_amounts(work)
            if price_study:
                price_study.sync_with_task(request)


class PriceStudyWorkItemService:
    @classmethod
    def _get_computer(cls, product):
        from caerp.models.config import Config

        if product.mode == "ht":
            from caerp.compute.price_study import (
                WorkItemHtComputer as Computer,
            )
        else:
            # mode = supplier_ht
            from caerp.compute.price_study import (
                WorkItemSupplierHtComputer as Computer,
            )
        return Computer(product, Config)

    @classmethod
    def get_tva(cls, work_item):
        tva = None
        if work_item.price_study_work:
            tva = work_item.price_study_work.tva
        return tva

    @classmethod
    def get_company_id(cls, work_item):
        if work_item.price_study_work:
            return work_item.price_study_work.get_company_id()
        else:
            return None

    @classmethod
    def get_company(cls, work_item):
        if work_item.price_study_work:
            return work_item.price_study_work.get_company()
        else:
            return None

    @classmethod
    def flat_cost(cls, work_item, unitary=False, work_level=False):
        computer = cls._get_computer(work_item)
        if unitary:
            if work_level:
                return computer.work_unit_flat_cost()
            else:
                return computer.flat_cost()
        else:
            return computer.full_flat_cost()

    @classmethod
    def cost_price(cls, work_item, unitary=False):
        """
        Compute the cost price of the given price study work suming the cost of
        its different items

        :returns: The result in 10*5 format

        :rtype: int
        """
        computer = cls._get_computer(work_item)
        if unitary:
            return computer.cost_price()
        else:
            return computer.full_cost_price()

    @classmethod
    def intermediate_price(cls, work_item, unitary=False):
        """
        Compute the intermediate price of a work item

        3/    Prix intermédiaire = Prix de revient / ( 1 - ( Coefficients marge
        + aléas + risques ) )
        """
        computer = cls._get_computer(work_item)
        if unitary:
            return computer.intermediate_price()
        else:
            return computer.full_intermediate_price()

    @classmethod
    def price_with_contribution(cls, work_item, unitary=False, base_price=None):
        computer = cls._get_computer(work_item)
        if unitary:
            return computer.price_with_contribution(base_price)
        else:
            return computer.full_price_with_contribution(base_price)

    @classmethod
    def price_with_insurance(cls, work_item, unitary=False, base_price=None):
        computer = cls._get_computer(work_item)
        if unitary:
            return computer.price_with_insurance(base_price)
        else:
            return computer.full_price_with_insurance(base_price)

    @classmethod
    def unit_ht(cls, work_item):
        """
        Compute the ht value for the given work item
        """
        computer = cls._get_computer(work_item)
        return computer.unit_ht()

    @classmethod
    def compute_work_unit_ht(cls, work_item):
        """
        Compute the ht value per work unit for the given work item
        """
        if work_item.quantity_inherited:
            return cls.unit_ht(work_item) * work_item.work_unit_quantity
        else:
            work = work_item.price_study_work
            work_quantity = 1
            if work is not None:
                work_quantity = work.quantity or 1  # Avoid 0 division
            return cls.compute_total_ht(work_item) / work_quantity

    @classmethod
    def compute_total_ht(cls, work_item):
        """
        Compute the total ht for the given work_item
        """
        unit_ht = work_item.unit_ht()
        total_quantity = work_item.total_quantity
        if total_quantity is None:
            total_quantity = 0
        return unit_ht * total_quantity

    @classmethod
    def compute_total_tva(cls, work_item):
        ht = cls.compute_total_ht(work_item)
        tva = cls.get_tva(work_item)
        if tva is not None:
            return compute_tva(ht, tva.value)
        return 0

    @classmethod
    def ttc(cls, work_item):
        """
        Calcul du ttc indicatif pour ce work_item

        NB : les arrondis se faisant sur les totaux au niveau du devis/facture,
        cette valeur peut être imprécise
        """
        ht = cls.compute_total_ht(work_item)
        tva = cls.get_tva(work_item)
        if tva is not None:
            return ht + compute_tva(ht, tva.value)
        return ht

    @classmethod
    def sync_amounts(cls, work_item, work=None):
        """
        Sync the work_item's cached values

        :param obj work: The PriceStudyWork to be synced in case of ascending syncing
        """
        work_item.ht = work_item.unit_ht()
        work_item.work_unit_ht = work_item.compute_work_unit_ht()
        work_item.total_ht = work_item.compute_total_ht()
        DBSESSION().merge(work_item)

        # On update le work que si ce n'est pas lui qui a fait la demande
        # initiale
        if work is None:
            work_item.price_study_work.sync_amounts()
        return True

    @classmethod
    def sync_quantities(cls, work_item, work=None):
        # Quantities are synced only if the quantity is inherited
        work_unit_quantity = work_item.work_unit_quantity
        if work_item.quantity_inherited:
            if work is None:
                work = work_item.price_study_work
            work_item.total_quantity = work_unit_quantity * work.quantity
        else:
            work_item.total_quantity = work_unit_quantity
        DBSESSION().merge(work_item)
        return True

    @classmethod
    def on_before_commit(cls, request, work_item, state, changes=None):
        """
        :param str state: 'add'/'update'/'delete'
        """
        logger.debug("{}.on_before_commit".format(cls))
        price_study = None
        work = work_item.price_study_work
        if work and work.chapter:
            price_study = work_item.price_study_work.chapter.price_study

        if state == "delete":
            need_sync_amounts = False
            if work and work_item in work.items:
                work.items.remove(work_item)
            work.sync_amounts()
            if price_study:
                price_study.sync_with_task(request)

        elif state == "add":
            need_sync_amounts = True
        else:
            need_sync_amounts = True
            if changes:
                for key in (
                    "mode",
                    "supplier_ht",
                    "ht",
                    "_margin_rate",
                    "work_unit_quantity",
                    "quantity_inherited",
                    "work_unit_ht",
                ):
                    if key in changes:
                        need_sync_amounts = True
                        break

        if need_sync_amounts:
            cls.sync_quantities(work_item)
            cls.sync_amounts(work_item)
            price_study.sync_with_task(request)


class PriceStudyDiscountService:
    @classmethod
    def ht_by_tva(cls, discount):
        result = {}
        if discount.is_percentage:
            for tva, values in discount.price_study.amounts_by_tva().items():
                result.setdefault(tva, 0)
                result[tva] += percentage(values["ht"], discount.percentage)
        elif discount.tva:
            result[discount.tva] = discount.amount
        return result

    @classmethod
    def total_ht(cls, discount):
        return sum(ht for ht in list(cls.ht_by_tva(discount).values()))

    @classmethod
    def total_tva(cls, discount):
        value = 0
        for tva, ht in list(cls.ht_by_tva(discount).items()):
            value += compute_tva(ht, tva.value)
        return value

    @classmethod
    def total_ttc(cls, discount):
        return cls.total_ht(discount) + cls.total_tva(discount)

    @classmethod
    def on_before_commit(cls, request, discount, state, attributes):
        logger.debug("{}.on_before_commit".format(cls))
        price_study = discount.price_study
        sync = False
        if state == "delete":
            if discount in price_study.discounts:
                price_study.discounts.remove(discount)
            sync = True
        elif state == "add":
            sync = True
        elif state == "update":
            keys = ["tva_id", "amount", "percentage"]
            if attributes:
                for key in keys:
                    if key in attributes:
                        sync = True
                        break
            else:
                sync = True

        if sync and price_study is not None:
            price_study.sync_amounts()
            price_study.sync_with_task(request)

    @classmethod
    def get_company_id(cls, instance):
        from caerp.models.task import Task

        return (
            DBSESSION()
            .query(Task.company_id)
            .filter_by(id=instance.price_study.task_id)
            .scalar()
        )

    @classmethod
    def sync_with_task(cls, request, instance, price_study):
        from caerp.models.task import DiscountLine

        result = []

        for tva, ht in cls.ht_by_tva(instance).items():
            discount = DiscountLine(
                task=price_study.task,
                tva=tva.value,
                amount=ht,
                description=instance.description,
            )
            request.dbsession.add(discount)
            request.dbsession.flush()
            result.append(discount)
        return result
