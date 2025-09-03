from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    backref,
    relationship,
)


from caerp.models.options import (
    ConfigurableOption,
    get_id_foreignkey_col,
)

from caerp.utils.datetimes import get_current_year
from caerp_base.models.base import (
    default_table_args,
    DBBASE,
)
from caerp_base.models.mixins import (
    TimeStampedMixin,
)


class TraineeCount(DBBASE):
    __tablename__ = "business_bpf_data_trainee_count"
    __table_args__ = default_table_args

    id = Column(
        Integer,
        primary_key=True,
    )
    business_bpf_data_id = Column(
        Integer,
        ForeignKey("business_bpf_data.id", ondelete="cascade"),
        nullable=False,
        info={"colanderalchemy": {"exclude": True}},
    )
    trainee_type_id = Column(
        Integer,
        nullable=False,
        info={
            "colanderalchemy": {
                "title": "Type de stagiaire",
            },
        },
    )
    headcount = Column(
        Integer,
        nullable=False,
        info={
            "colanderalchemy": {
                "title": "Nb. stagiaires",
            },
        },
    )
    total_hours = Column(
        Float(),
        nullable=False,
        info={
            "colanderalchemy": {
                "title": "Nb. Heures total",
            },
        },
    )


class IncomeSource(DBBASE):
    __tablename__ = "business_bpf_data_income_source"
    __table_args__ = default_table_args
    id = Column(
        Integer,
        primary_key=True,
    )
    business_bpf_data_id = Column(
        Integer,
        ForeignKey("business_bpf_data.id", ondelete="cascade"),
        nullable=False,
        info={"colanderalchemy": {"exclude": True}},
    )
    invoice_id = Column(
        Integer,
        ForeignKey("invoice.id", ondelete="CASCADE"),
        nullable=False,
        info={
            "colanderalchemy": {
                "title": "Facture",
            },
        },
    )
    invoice = relationship(
        "Invoice",
        primaryjoin="IncomeSource.invoice_id==Invoice.id",
        info={
            "colanderalchemy": {"exclude": True},
        },
    )
    income_category_id = Column(
        Integer,
        nullable=False,
        info={
            "colanderalchemy": {
                "title": "Catégorie",
            },
        },
    )


class BusinessBPFData(TimeStampedMixin, DBBASE):
    """
    Meant to be subclassed (multi-table inheritance) and never
    used alone.
    """

    __tablename__ = "business_bpf_data"
    __table_args__ = (
        UniqueConstraint("business_id", "financial_year"),
        default_table_args,
    )

    id = Column(
        Integer,
        primary_key=True,
    )

    business_id = Column(
        ForeignKey("business.id", ondelete="cascade"),
        nullable=False,
    )
    business = relationship(
        "Business",
        primaryjoin="BusinessBPFData.business_id==Business.id",
        # on utilise passive_deletes car on a définit le ondelete cascade au
        # niveau DB
        backref=backref("bpf_datas", uselist=True, passive_deletes=True),
    )
    financial_year = Column(
        Integer,
        nullable=False,
        default=get_current_year,
        info={
            "colanderalchemy": {
                "title": "Année fiscale de référence",
            }
        },
    )
    cerfa_version = Column(
        String(10),
        nullable=False,
        info={
            "colanderalchemy": {
                "title": "Version du formulaire CERFA",
            },
        },
    )
    total_hours = Column(
        Float(),
        nullable=False,
        info={
            "colanderalchemy": {
                "title": "Nb. Heures total suivies par l'ensemble des stagiaires",
            },
        },
    )
    headcount = Column(
        Integer(),
        nullable=False,
        info={
            "colanderalchemy": {
                "title": "Nb. de stagiaires",
            },
        },
    )
    has_subcontract = Column(
        String(5),
        nullable=False,
        info={
            "colanderalchemy": {
                "title": "Cette formation est-elle sous-traitée à un autre OF ?",
            },
        },
    )
    has_subcontract_hours = Column(
        Float(),
        nullable=False,
        info={
            "colanderalchemy": {
                "title": "Nb. heures sous-traitées",
            },
        },
    )
    has_subcontract_headcount = Column(
        Integer(),
        nullable=False,
        default=0,
        info={
            "colanderalchemy": {
                "title": "Nb. stagiaires concernés",
            },
        },
    )
    has_subcontract_amount = Column(
        Float(),
        nullable=False,
        default=0,
        info={
            "colanderalchemy": {
                "title": "Montant HT",
            },
        },
    )
    # Only used up to CERFA 10443*16 (2022):
    remote_headcount = Column(
        Integer(),
        nullable=False,
        default=0,
        info={
            "colanderalchemy": {
                "title": "Stagiaires et apprentis ayant suivi une action en tout ou partie à distance",
            },
        },
    )
    # Only used since CERFA 10443*17 (2023)
    has_remote = Column(
        Boolean(),
        nullable=False,
        default=0,
        info={
            "colanderalchemy": {
                "title": "Cette formation est-elle tout ou partie en distanciel ?",
            },
        },
    )
    is_subcontract = Column(
        Boolean(),
        nullable=False,
        default=0,
        info={
            "colanderalchemy": {
                "title": "Cette formation est-elle portée en direct par la CAE ?",
            },
        },
    )
    training_speciality_id = Column(
        Integer(),
        ForeignKey("nsf_training_speciality_option.id"),
        nullable=True,  # not required for sucontracts
        info={
            "colanderalchemy": {
                "title": "Spécialité de formation",
            },
        },
    )
    training_goal_id = Column(
        Integer(),
        nullable=True,  # not required for sucontracts
        info={
            "colanderalchemy": {
                "title": "Objectif principal de formation",
            },
        },
    )
    training_speciality = relationship(
        "NSFTrainingSpecialityOption",
        primaryjoin="BusinessBPFData.training_speciality_id==NSFTrainingSpecialityOption.id",
    )
    trainee_types = relationship(
        "TraineeCount",
        primaryjoin="BusinessBPFData.id==TraineeCount.business_bpf_data_id",
        cascade="all, delete-orphan",
        info={
            "colanderalchemy": {
                "title": "Typologie des stagiaires",
            }
        },
    )

    income_sources = relationship(
        "IncomeSource",
        primaryjoin="BusinessBPFData.id==IncomeSource.business_bpf_data_id",
        cascade="all, delete-orphan",
        info={
            "colanderalchemy": {
                "title": "Financement",
            }
        },
    )


class NSFTrainingSpecialityOption(ConfigurableOption):
    """
    Nomenclature des spécialités de formation

    https://public.opendatasoft.com/explore/dataset/codes-nsf/
    https://www.data.gouv.fr/fr/datasets/582c8978c751df788ec0bb7e/
    """

    __tablename__ = "nsf_training_speciality_option"
    __mapper_args__ = {"polymorphic_identity": "nsf_training_speciality_option"}

    id = get_id_foreignkey_col("configurable_option.id")
