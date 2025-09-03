"""
Base measure types

Used for IncomeStatementMeasures, TreasuryMeasures ...
"""
import logging
import deform
import colander
import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Numeric,
    Boolean,
    DateTime,
)
from sqlalchemy.orm import (
    relationship,
    load_only,
)
from sqlalchemy.sql.expression import func

from caerp_base.models.base import (
    DBBASE,
    default_table_args,
    DBSESSION,
)
from caerp.forms import get_deferred_select
from caerp.compute.parser import (
    NumericStringParser,
    NumericStringFloatReducer,
)
from caerp.models.company import Company
from caerp.models.accounting.services import (
    BaseAccountingMeasureService,
    BaseAccountingMeasureGridService,
)

logger = logging.getLogger(__name__)


class BaseAccountingMeasureTypeCategory(DBBASE):
    """
    Base Categories for joining the different measure types
    """

    __tablename__ = "base_accounting_measure_type_category"
    __table_args__ = default_table_args
    __colanderalchemy_config__ = {
        "help_msg": """Les catégories permettent de regrouper les types
        d'indicateurs afin d'en faciliter la configuration.
        Ils peuvent ensuite être utilisé pour calculer des totaux.<br />
        """
    }
    __mapper_args__ = {
        "polymorphic_on": "type_",
        "polymorphic_identity": "base",
    }
    id = Column(Integer, primary_key=True, info={"colanderalchemy": {"exclude": True}})
    type_ = Column(
        "type_",
        String(30),
        info={"colanderalchemy": {"exclude": True}},
        nullable=False,
    )
    label = Column(
        String(255),
        info={
            "colanderalchemy": {
                "title": "Libellé de cette catégorie (seulement visible dans "
                "l'interface de configuration)",
            }
        },
        nullable=False,
    )
    active = Column(
        Boolean(),
        default=True,
        info={"colanderalchemy": {"title": "Indicateur actif ?", "exclude": True}},
    )
    order = Column(
        Integer,
        default=1,
        info={
            "colanderalchemy": {
                "title": "Ordre au sein de la catégorie",
                "widget": deform.widget.HiddenWidget(),
            }
        },
    )

    attached_types = relationship(
        "BaseAccountingMeasureType",
        back_populates="category",
        cascade="all,delete,delete-orphan",
        info={"colanderalchemy": {"exclude": True}},
    )

    def move_up(self):
        """
        Move the current instance up in the category's order
        """
        order = self.order
        if order > 0:
            new_order = order - 1
            self.__class__.insert(self, new_order)

    def move_down(self):
        """
        Move the current instance down in the category's order
        """
        order = self.order
        new_order = order + 1
        self.__class__.insert(self, new_order)

    @classmethod
    def get_categories(cls, active=True, keys=()):
        """
        :param bool active: Only load active categories
        :param tuple keys: The keys to load (list of str)
        :returns: BaseAccountingMeasureTypeCategory ordered by order key
        :rtype: list
        """
        query = DBSESSION().query(cls)
        if keys:
            query = query.options(load_only(*keys))
        query = query.filter_by(active=active).order_by(cls.order)
        return query.all()

    @classmethod
    def get_by_label(cls, label, active=True):
        """
        :param str label: The label to retrieve
        :param bool active: Only check in active items

        :returns: An IncomeStatementMeasureTypeCategory or None
        :rtype: class or None
        """
        return (
            DBSESSION()
            .query(cls)
            .filter_by(active=active)
            .filter_by(label=label)
            .first()
        )

    @classmethod
    def get_next_order(cls):
        """
        :returns: The next available order
        :rtype: int
        """
        query = DBSESSION().query(func.max(cls.order)).filter_by(active=True)
        query = query.first()
        if query is not None and query[0] is not None:
            result = query[0] + 1
        else:
            result = 0
        return result

    @classmethod
    def insert(cls, item, new_order):
        """
        Place the item at the given index

        :param obj item: The item to move
        :param int new_order: The new index of the item
        """
        items = (
            DBSESSION()
            .query(cls)
            .filter_by(active=True)
            .filter(cls.id != item.id)
            .order_by(cls.order)
            .all()
        )

        items.insert(new_order, item)

        for index, item in enumerate(items):
            item.order = index
            DBSESSION().merge(item)

    @classmethod
    def reorder(cls):
        """
        Regenerate order attributes
        """
        items = cls.get_categories()

        for index, item in enumerate(items):
            item.order = index
            DBSESSION().merge(item)


class BaseAccountingMeasureType(DBBASE):
    __tablename__ = "base_accounting_measure_type"
    __table_args__ = default_table_args
    __colanderalchemy_config__ = {
        "help_msg": """Les indicateurs de comptes résultats permettent de
        regrouper des écritures sous un même libellé.<br />
        Ils permettent d'assembler les comptes de résultats des entrepreneurs.
        <br />Vous pouvez définir ici les préfixes de comptes généraux pour
        indiquer quelles écritures doivent être utilisées pour calculer cet
        indicateur.
        <br />
        Si nécessaire vous pourrez alors recalculer les derniers indicateurs
        générés.
        """
    }
    __mapper_args__ = {
        "polymorphic_on": "type_",
        "polymorphic_identity": "base",
    }
    id = Column(Integer, primary_key=True, info={"colanderalchemy": {"exclude": True}})
    type_ = Column(
        "type_",
        String(30),
        info={"colanderalchemy": {"exclude": True}},
        nullable=False,
    )
    category_id = Column(
        ForeignKey(BaseAccountingMeasureTypeCategory.id),
        info={
            "colanderalchemy": {
                "widget": deform.widget.HiddenWidget(),
            }
        },
        nullable=True,
    )
    label = Column(
        String(255),
        info={
            "colanderalchemy": {
                "title": "Libellé de cet indicateur",
            }
        },
        nullable=False,
    )
    account_prefix = Column(
        String(255),
        info={
            "colanderalchemy": {
                "title": "Rassemble tous les comptes commençant par",
                "description": "Toutes les écritures dont le compte commence "
                "par le préfixe fourni seront utilisées pour calculer cet "
                "indicateur. "
                "NB : Une liste de préfixe peut être fournie en les "
                "séparant par des virgules (ex : 42,43), un préfixe peut "
                "être exclu en plaçant le signe '-' devant (ex: 42,-425 "
                "incluera tous les comptes 42… sauf les comptes 425…)",
                "missing": colander.required,
            }
        },
    )
    active = Column(
        Boolean(),
        default=True,
        info={"colanderalchemy": {"title": "Indicateur actif ?", "exclude": True}},
    )
    order = Column(
        Integer,
        default=1,
        info={
            "colanderalchemy": {
                "title": "Ordre au sein de la catégorie",
                "widget": deform.widget.HiddenWidget(),
            }
        },
    )
    is_total = Column(
        Boolean(),
        default=False,
        info={
            "colanderalchemy": {
                "title": "Cet indicateur correspond-il à un total (il sera mis en "
                "évidence dans l'interface et ne sera pas utilisé pour le calcul "
                "des totaux globaux) ?",
            }
        },
    )
    total_type = Column(
        String(20),
        info={
            "colanderalchemy": {
                "title": "Type d'indicateurs "
                "(account_prefix/complex_total/categories)",
                "exclude": True,
            }
        },
    )

    category = relationship(
        "BaseAccountingMeasureTypeCategory", info={"colanderalchemy": {"exclude": True}}
    )
    measures = relationship(
        "BaseAccountingMeasure",
        primaryjoin="BaseAccountingMeasure.measure_type_id"
        "==BaseAccountingMeasureType.id",
        info={"colanderalchemy": {"exclude": True}},
        back_populates="measure_type",
    )
    # Si ce booléen est à true, on inverse le signe de la valeur des
    # items de ce type
    # Pour les comptes de résultat la valeur par défaut est : Crédit - débit
    # Pour les états de trésorerie la valeur par défaut : Débit - crédit
    invert_default_cd_or_dc = Column(
        Boolean(),
        default=False,
        info={
            "colanderalchemy": {
                "title": "Le signe de la valeur de l'indicateur doit-il être inversée ?",
                "label": "Le signe de la valeur de l'indicateur doit-il être inversée ?",
                "exclude": True,
            }
        },
    )

    @staticmethod
    def default_sign():
        raise NotImplementedError()

    def sign(self):
        # Comme les totaux "groupement d'écriture" sont la même chose
        # que les indicateurs classiques mais mis en avant, il ne sont pas pris
        # en compte en tant que totaux et gardent une gestion du signe "classique"
        if self.is_computed_total:
            if self.invert_default_cd_or_dc:
                return -1
            else:
                return 1

        if self.invert_default_cd_or_dc:
            return self.default_sign() * -1
        else:
            return self.default_sign()

    @property
    def is_computed_total(self):
        """
        :returns: True if this type is a computed total (mix of other values)
        :rtype: bool
        """
        return self.is_total and self.total_type in ("complex_total", "categories")

    def match(self, account):
        """
        Check if the current Type definition matches the given account number

        :param str account: A string representing an accounting account (e.g:
            42500000)
        :returns: True or False if it matches
        :rtype: bool
        """
        res = False
        for prefix in self.account_prefix.split(","):
            if not prefix:
                continue
            if prefix.startswith("-"):
                prefix = prefix[1:].strip()
                if account.startswith(prefix):
                    res = False
                    break
            elif not res:
                if account.startswith(prefix):
                    res = True
        return res

    def move_up(self):
        """
        Move the current instance up in the category's order
        """
        order = self.order
        if order > 0:
            new_order = order - 1
            self.__class__.insert(self, new_order)

    def move_down(self):
        """
        Move the current instance down in the category's order
        """
        order = self.order
        new_order = order + 1
        self.__class__.insert(self, new_order)

    def compute_total(self, category_totals):
        """
        Compile a total value based on the given category totals

        :param dict category_totals: Totals stored by category labels
        :returns: The compiled total
        :rtype: int
        """
        result = 0
        if self.total_type == "categories":
            result = self._compute_categories_total(category_totals)
        elif self.total_type == "complex_total":
            result = self._compute_complex_total(category_totals)
        return result

    def _compute_categories_total(self, all_category_totals):
        """
        Compute the sum of the current's item categories picking them in the
        all_category_totals dict

        :param dict all_category_totals: Totals stored by category labels
        :returns: The compiled total
        :rtype: int
        """
        result = 0
        for category in self.account_prefix.split(","):
            if category in all_category_totals:
                result += all_category_totals[category]
        return result

    def _compute_complex_total(self, all_category_totals):
        """
        Compile the arithmetic operation configure in the current item, using
        datas coming from the all_category_totals dict

        :param dict all_category_totals: Totals stored by category labels
        :returns: The compiled total
        :rtype: int
        """
        result = 0
        try:
            operation = self.account_prefix.format(**all_category_totals)
        except KeyError:
            logger.exception(
                "KeyError in computing total {} {}".format(
                    self.label, self.account_prefix
                )
            )
            operation = "0"

        parser = NumericStringParser()
        reducer = NumericStringFloatReducer
        try:
            stack = parser.parse(operation)
            result = reducer.reduce(stack)
        except ZeroDivisionError:
            result = 0
        except Exception:
            logger.exception("Error while parsing : %s" % operation)
            result = 0
        return result

    def get_categories(self):
        """
        Return the categories configured in case of a total type

        :rtype: list of BaseAccountingMeasureTypeCategory instances
        """
        category_labels = self.account_prefix.split(",")

        result = []
        for label in category_labels:
            category = BaseAccountingMeasureTypeCategory.get_by_label(label)
            if category is not None:
                result.append(category)
        return result

    def get_categories_labels(self):
        """
        Return the labels of the categories attached to this instance
        :rtype: list
        """
        return [c.label for c in self.get_categories()]

    @classmethod
    def get_by_category(cls, category_id, key=None):
        """
        Collect BaseAccountingMeasureType associated to the given category

        :param int category_id: The id to check for
        :param str key: The key to load (if we want to restrict the query
        :rtype: list
        """
        query = DBSESSION().query(cls)
        if key is not None:
            query = query.options(load_only(key))
        query = query.filter_by(category_id=category_id)
        return query.all()

    @classmethod
    def get_next_order(cls):
        """
        :returns: The next available order
        :rtype: int
        """
        query = DBSESSION().query(func.max(cls.order)).filter_by(active=True)
        query = query.first()
        if query is not None and query[0] is not None:
            result = query[0] + 1
        else:
            result = 0

        return result

    @classmethod
    def get_next_order_by_category(cls, category_id):
        """
        :param int category_id: The id of the category to check for
        :returns: The next order available in types from the given category
        :rtype: int
        """
        query = (
            DBSESSION()
            .query(func.max(cls.order))
            .filter_by(category_id=category_id)
            .filter_by(active=True)
        )
        query = query.first()
        if query is not None and query[0] is not None:
            result = query[0] + 1
        else:
            result = 0
        return result

    @classmethod
    def insert(cls, item, new_order):
        """
        Place the item at the given index in the hierarchy of items of the same
        category

        :param obj item: The item to place
        :param int new_order: The index where to place the item
        """
        items = (
            DBSESSION()
            .query(cls)
            .filter_by(category_id=item.category_id)
            .filter_by(active=True)
            .filter(cls.id != item.id)
            .order_by(cls.order)
            .all()
        )

        items.insert(new_order, item)

        for index, item in enumerate(items):
            item.order = index
            DBSESSION().merge(item)

    @classmethod
    def reorder(cls, category_id):
        """
        Regenerate order attributes
        :param int category_id: The category to manage
        """
        items = (
            DBSESSION()
            .query(cls)
            .filter_by(category_id=category_id)
            .filter_by(active=True)
            .order_by(cls.order)
            .all()
        )

        for index, item in enumerate(items):
            item.order = index
            DBSESSION().merge(item)

    @classmethod
    def get_types(cls, active=True, keys=()):
        query = DBSESSION().query(cls)
        if keys:
            query = query.options(load_only(*keys))
        if active:
            query = query.filter_by(active=True)
        return query


class BaseAccountingMeasureGrid(DBBASE):
    """
    A grid of measures, one grid per month/year couple

    """

    __tablename__ = "base_accounting_measure_grid"
    __table_args__ = default_table_args
    __mapper_args__ = {
        "polymorphic_on": "type_",
        "polymorphic_identity": "base",
    }
    id = Column(Integer, primary_key=True)
    type_ = Column(
        "type_",
        String(30),
        info={"colanderalchemy": {"exclude": True}},
        nullable=False,
    )
    datetime = Column(
        DateTime(),
        default=datetime.datetime.now,
        info={"colanderalchemy": {"title": "Heure et date de création"}},
    )
    company_id = Column(
        ForeignKey("company.id", ondelete="cascade"),
        info={
            "colanderalchemy": {
                "title": "Enseigne associée à cette opération",
                "widget": get_deferred_select(
                    Company, keys=("id", lambda c: "%s %s" % (c.name, c.code_compta))
                ),
            }
        },
    )
    company = relationship("Company")
    upload_id = Column(
        ForeignKey("accounting_operation_upload.id", ondelete="cascade"),
        info={"colanderalchemy": {"title": "Related upload"}},
    )
    upload = relationship("AccountingOperationUpload", back_populates="measure_grids")
    measures = relationship(
        "BaseAccountingMeasure",
        primaryjoin="BaseAccountingMeasureGrid.id==" "BaseAccountingMeasure.grid_id",
        cascade="all,delete,delete-orphan",
    )
    _caerp_service = BaseAccountingMeasureGridService

    def get_company_id(self):
        return self.company_id

    @classmethod
    def get_years(cls, company_id=None):
        return cls._caerp_service.get_years(cls, company_id)

    def get_measure_by_type(self, measure_type_id):
        return self._caerp_service.get_measure_by_type(self, measure_type_id)


class BaseAccountingMeasure(DBBASE):
    """
    Stores an accounting measure associated to a given grid
    """

    __tablename__ = "base_accounting_measure"
    __table_args__ = default_table_args
    __mapper_args__ = {
        "polymorphic_on": "type_",
        "polymorphic_identity": "base",
    }
    id = Column(Integer, primary_key=True)
    type_ = Column(
        "type_",
        String(30),
        info={"colanderalchemy": {"exclude": True}},
        nullable=False,
    )
    label = Column(String(255), info={"colanderalchemy": {"title": "Libellé"}})
    value = Column(
        Numeric(9, 2, asdecimal=False),
        default=0,
        info={"colanderalchemy": {"title": "Montant"}},
    )
    order = Column(
        Integer,
        default=0,
        info={"colanderalchemy": {"title": "Ordre dans la grille"}},
    )
    measure_type_id = Column(
        ForeignKey("base_accounting_measure_type.id"),
        info={
            "colanderalchemy": {
                "title": "Type d'indicateur",
            }
        },
    )
    measure_type = relationship(
        BaseAccountingMeasureType,
        primaryjoin="BaseAccountingMeasureType.id=="
        "BaseAccountingMeasure.measure_type_id",
        info={"colanderalchemy": {"exclude": True}},
        back_populates="measures",
    )
    grid_id = Column(ForeignKey("base_accounting_measure_grid.id", ondelete="cascade"))
    _caerp_service = BaseAccountingMeasureService

    def __json__(self, request):
        return {
            "id": self.id,
            "label": self.label,
            "value": self.get_value(),
            "measure_type_id": self.measure_type_id,
        }

    @classmethod
    def get_measure_types(cls, grid_id):
        """
        Collect all measure types used in the given grid
        """
        return cls._caerp_service.get_measure_types(
            cls,
            grid_id,
            BaseAccountingMeasureType,
        )

    def get_value(self):
        return self.value
