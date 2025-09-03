import datetime
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    ForeignKey,
    Text,
    Date,
    String,
    Numeric,
    Float,
    Boolean,
)
from sqlalchemy.orm import (
    relationship,
)
from caerp_base.models.base import (
    DBBASE,
    default_table_args,
    DBSESSION,
)
from caerp_base.models.mixins import (
    DuplicableMixin,
    TimeStampedMixin,
)
from caerp.compute.math_utils import integer_to_amount

from .services import SaleProductService


class BaseSaleProduct(DBBASE, TimeStampedMixin, DuplicableMixin):
    """
    id

    Ventes

        label
        description
        ht
        unity
        tva

    Achats

        supplier_id -> supplier
        supplier_ref
        supplier_unity_amount
        supplier_ht

    Informations Internes

        category_id
        product_type = Material / WorkForce / Product / Article
        ref

    Notes
    """

    __table_args__ = default_table_args
    __tablename__ = "base_sale_product"
    __mapper_args__ = {
        "polymorphic_on": "type_",
        "polymorphic_identity": __tablename__,
    }
    __duplicable_fields__ = [
        "company_id",
        "label",
        "description",
        "ht",
        "unity",
        "tva_id",
        "product_id",
        "supplier_id",
        "supplier_ref",
        "supplier_unity_amount",
        "supplier_ht",
        "purchase_type_id",
        "category_id",
        "ref",
        "notes",
        "mode",
    ]
    id = Column(Integer, primary_key=True)
    type_ = Column("type_", String(30), nullable=False)

    company_id = Column(
        ForeignKey("company.id"), nullable=False, info={"export": {"exclude": True}}
    )
    label = Column(String(255), nullable=False)
    description = Column(Text(), default="")

    # Mode de calcul ht / ttc / supplier_ht
    mode = Column(String(20), default="supplier_ht", nullable=False)

    ht = Column(
        BigInteger(),
        default=0,
        info={
            "export": {
                "formatter": lambda val: integer_to_amount(val, 5, ""),
            },
        },
    )
    unity = Column(String(100), default="", info={"export": {"label": "Unité"}})
    tva_id = Column(ForeignKey("tva.id"), info={"export": {"exclude": True}})
    product_id = Column(ForeignKey("product.id"), info={"export": {"exclude": True}})
    ttc = Column(
        BigInteger(),
        default=0,
        info={
            "export": {
                "formatter": lambda val: integer_to_amount(val, 5, ""),
            },
        },
    )

    # Fournisseur
    supplier_id = Column(ForeignKey("supplier.id"), info={"export": {"exclude": True}})
    # Référence du fournisseur
    supplier_ref = Column(
        String(255), info={"export": {"label": "Référence fournisseur"}}
    )
    # Unité de vente (pour la vente par lot)
    supplier_unity_amount = Column(
        Numeric(15, 5, asdecimal=False),
        info={"export": {"label": "Unité de vente fournisseur"}},
    )
    # Montant HT à l'achat
    supplier_ht = Column(
        BigInteger(),
        default=0,
        info={
            "export": {
                "label": "Prix fournisseur HT",
                "formatter": lambda val: integer_to_amount(val, 5, ""),
            },
        },
    )
    # Type d'achat
    purchase_type_id = Column(
        ForeignKey("expense_type.id"), info={"export": {"exclude": True}}
    )

    # coefficient de marge (pourcentage indiqué en flottant)
    margin_rate = Column(
        Numeric(6, 5, asdecimal=False),
        default=0,
        info={"export": {"label": "Coefficient de marge"}},
    )

    category_id = Column(
        ForeignKey("sale_product_category.id", ondelete="SET NULL"),
        info={"export": {"exclude": True}},
    )
    ref = Column(
        String(100), nullable=True, info={"export": {"label": "Référence interne"}}
    )

    notes = Column(Text(), info={"export": {"label": "Notes"}})

    archived = Column(Boolean(), default=False)

    # Relationships
    company = relationship(
        "Company",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )
    product = relationship(
        "Product",
        primaryjoin="Product.id==BaseSaleProduct.product_id",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {
                "label": "Compte produit",
                "formatter": lambda val: val.name if val else "",
            },
        },
    )
    tva = relationship(
        "Tva",
        primaryjoin="Tva.id==BaseSaleProduct.tva_id",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {
                "label": "Tva",
                "formatter": lambda val: val.name if val else "",
            },
        },
    )
    supplier = relationship(
        "Supplier",
        primaryjoin="BaseSaleProduct.supplier_id==Supplier.id",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {
                "label": "Fournisseur",
                "formatter": lambda val: val.label if val else "",
            },
        },
    )
    purchase_type = relationship(
        "ExpenseType",
        primaryjoin="BaseSaleProduct.purchase_type_id==ExpenseType.id",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {
                "label": "Produit",
                "formatter": lambda val: val if val.label else "",
            },
        },
    )
    category = relationship(
        "SaleProductCategory",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {
                "label": "Catégorie",
                "formatter": lambda val: val.title if val else "",
            },
        },
    )
    work_items = relationship(
        "WorkItem",
        back_populates="base_sale_product",
        info={"colanderalchemy": {"exclude": True}},
    )
    stock_operations = relationship(
        "SaleProductStockOperation",
        back_populates="base_sale_product",
        order_by=(
            "desc(SaleProductStockOperation.date),            "
            " desc(SaleProductStockOperation.id)"
        ),
        cascade="all, delete-orphan",
        info={"colanderalchemy": {"exclude": True}},
    )

    SIMPLE_TYPES = (
        "sale_product_product",
        "sale_product_material",
        "sale_product_work_force",
        "sale_product_service_delivery",
    )
    ALL_TYPES = SIMPLE_TYPES + (
        "sale_product_work",
        "sale_product_training",
        "sale_product_vae",
    )

    TYPE_LABELS = (
        "Produit",
        "Matériau",
        "Main d’œuvre",
        "Prestation de service",
        "Produit composé (Chapitre ou Ouvrage)",
        "Produit composé (Formation)",
        "Produit composé (Validation des Acquis d'Expérience / VAE)",
    )

    _caerp_service = SaleProductService

    def __json__(self, request):
        return dict(
            id=self.id,
            type_=self.type_,
            company_id=self.company_id,
            label=self.label,
            description=self.description,
            ht=integer_to_amount(self.ht, 5, None),
            unity=self.unity,
            tva_id=self.tva_id,
            product_id=self.product_id,
            supplier_id=self.supplier_id,
            supplier_ref=self.supplier_ref,
            supplier_unity_amount=self.supplier_unity_amount,
            supplier_ht=integer_to_amount(self.supplier_ht, 5, None),
            # flat_cost=integer_to_amount(self.flat_cost(), 5, None),
            purchase_type_id=self.purchase_type_id,
            category_id=self.category_id,
            category_label=getattr(self.category, "title", ""),
            ref=self.ref,
            notes=self.notes,
            locked=self.is_locked(),
            current_stock=self.get_current_stock(),
            stock_operations=[item.__json__(request) for item in self.stock_operations],
            ttc=integer_to_amount(self.ttc, 5, None),
            mode=self.mode,
            margin_rate=self.margin_rate,
            updated_at=self.updated_at.isoformat(),
            archived=self.archived,
        )

    def get_current_stock(self):
        current_stock = 0
        stock_operations = SaleProductStockOperation.query(self.id)
        if stock_operations.count() == 0:
            return ""
        for op in stock_operations.all():
            current_stock += op.stock_variation
        return current_stock

    def is_locked(self):
        return self._caerp_service.is_locked(self)

    def get_taskline_description(self):
        return self._caerp_service.get_taskline_description(self)

    def sync_amounts(self):
        return self._caerp_service.sync_amounts(self)

    def on_before_commit(self, state, changes=None):
        self._caerp_service.on_before_commit(self, state, changes=changes)

    @classmethod
    def find_last_used_mode(cls, company_id: int) -> str:
        """
        Retrieve the last mode (ht/ttc/supplier_ht) used by this company in its sale
        product catalog
        """
        query = (
            DBSESSION()
            .query(cls.mode)
            .filter_by(company_id=company_id)
            .order_by(cls.created_at.desc())
            .limit(1)
        )
        return query.scalar()

    def duplicate(self, factory=None, **kwargs):
        return super().duplicate(
            factory,
            label="Copie de %s" % self.label,
            **kwargs,
        )

    @classmethod
    def query(cls):
        query = super(BaseSaleProduct, cls).query()
        return query.filter(BaseSaleProduct.archived == False)  # NOQA: E712


class SaleProductStockOperation(DBBASE):
    """
    History of sale products's stock variations
    """

    __table_args__ = default_table_args
    __tablename__ = "sale_product_stock_operation"
    __mapper_args__ = {"polymorphic_identity": __tablename__}
    id = Column(Integer, primary_key=True)
    date = Column(Date(), default=datetime.date.today)
    description = Column(Text(), default="")
    stock_variation = Column(Float(), default=0)
    base_sale_product_id = Column(
        Integer,
        ForeignKey("base_sale_product.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relationships
    base_sale_product = relationship(
        "BaseSaleProduct",
        foreign_keys=[base_sale_product_id],
        info={"colanderalchemy": {"exclude": True}},
    )

    @classmethod
    def query(cls, sale_product=None):
        q = super(SaleProductStockOperation, cls).query()
        if sale_product is not None:
            q = q.filter(SaleProductStockOperation.base_sale_product_id == sale_product)
        return q.order_by(SaleProductStockOperation.date.desc())

    def __json__(self, request):
        return dict(
            id=self.id,
            date=self.date,
            description=self.description,
            stock_variation=self.stock_variation,
            base_sale_product_id=self.base_sale_product_id,
        )

    def get_company_id(self):
        return self.base_sale_product.company_id
