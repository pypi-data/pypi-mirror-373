"""
Project Type management
"""
from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Text,
    not_,
    desc,
)
from sqlalchemy.orm import (
    relationship,
    load_only,
)
from caerp_base.models.base import (
    DBBASE,
    default_table_args,
    DBSESSION,
)
from caerp.consts.permissions import PERMISSIONS
from caerp.models.task.mentions import TaskMention
from .business import Business
from .mentions import BusinessTypeTaskMention


ProjectTypeBusinessType = Table(
    "project_type_business_type",
    DBBASE.metadata,
    Column("project_type_id", Integer, ForeignKey("project_type.id")),
    Column("business_type_id", Integer, ForeignKey("business_type.id")),
    mysql_charset=default_table_args["mysql_charset"],
    mysql_engine=default_table_args["mysql_engine"],
)


class BaseProjectType(DBBASE):
    __tablename__ = "base_project_type"
    __table_args__ = default_table_args
    __mapper_args__ = {
        "polymorphic_on": "type_",
        "polymorphic_identity": "base_project_type",
    }
    id = Column(Integer, primary_key=True)
    type_ = Column(
        "type_",
        String(30),
        info={"colanderalchemy": {"exclude": True}},
        nullable=False,
    )
    private = Column(
        Boolean(),
        info={
            "colanderalchemy": {
                "title": "Nécessite un rôle particulier ?",
                "description": "Les utilisateurs doivent-ils disposer d'un "
                "rôle particulier pour utiliser ce type ?",
            }
        },
    )
    name = Column(
        String(50),
        info={
            "colanderalchemy": {
                "title": "Nom interne",
                "description": "Le nom interne est utilisé pour définir les "
                "rôles des utilisateurs accédant à ce type.",
            }
        },
    )
    editable = Column(Boolean(), default=True)
    active = Column(Boolean(), default=True)

    @classmethod
    def unique_label(cls, label, type_id):
        """
        Check if a label is unique

        :param str label: Label to check
        :param int type_id: The type id to exclude
        :rtype: bool
        """
        query = cls.query()
        if type_id:
            query = query.filter(not_(cls.id == type_id))
        count = query.filter(cls.label == label).count()
        return count == 0

    @classmethod
    def query_for_select(cls):
        """
        Query project types for selection purpose
        """
        query = DBSESSION().query(cls).options(load_only("id", "label", "private"))
        query = query.filter_by(active=True)
        return query

    def __json__(self, request):
        res = {
            "id": self.id,
            "name": self.name,
            "active": self.active,
            "editable": self.editable,
            "private": self.private,
        }
        return res

    def allowed(self, request):
        """
        Check if the current request allows to access this Type

        :param obj request: The Pyramid request object
        :rtype: bool
        """
        res = False
        if not self.private:
            res = True
        elif request.has_permission(PERMISSIONS[f"context.add_{self.name}"]):
            res = True
        return res


class ProjectType(BaseProjectType):
    __tablename__ = "project_type"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "project_type"}
    __colanderalchemy_config__ = {
        "help_msg": """Les types de dossiers permettent de prédéfinir des
        comportements spécifiques (fichiers à attacher, modèles à utiliser
        pour les PDFs, mentions ...)"""
    }
    id = Column(
        ForeignKey("base_project_type.id"),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )
    label = Column(
        String(255),
        info={
            "colanderalchemy": {
                "title": "Libellé",
                "description": "Libellé présenté aux entrepreneurs",
            }
        },
        nullable=False,
        unique=True,
    )
    default = Column(
        Boolean(),
        default=False,
        nullable=False,
        info={
            "colanderalchemy": {
                "title": "Ce type de dossier est-il proposé par défaut ?",
            }
        },
    )
    include_price_study = Column(
        Boolean(),
        default=False,
        nullable=False,
        info={
            "colanderalchemy": {
                "label": "Des études de prix peuvent être menées dans "
                "ce type de projet"
            },
        },
    )
    # mandatory / default / optionnal
    price_study_mode = Column(
        String(10),
        default="default",
        nullable=False,
        info={
            "colanderalchemy": {"title": "Mode de saisie par défaut"},
        },
    )
    with_business = Column(
        Boolean(),
        default=False,
        nullable=False,
        info={
            "colanderalchemy": {
                "title": "Des affaires peuvent être générées depuis ce "
                "type de projet",
            }
        },
    )

    ht_compute_mode_allowed = Column(
        Boolean,
        default=True,
        nullable=False,
        info={
            "colanderalchemy": {
                "title": "Proposer le mode HT",
                "description": (
                    "Si le mode HT et TTC sont tout deux proposés, "
                    "le choix sera offert à la création d'un dossier."
                ),
            },
        },
    )

    ttc_compute_mode_allowed = Column(
        Boolean,
        default=False,
        nullable=False,
        info={
            "colanderalchemy": {
                "title": "Proposer le mode TTC",
                "description": (
                    "Si le mode HT et TTC sont tout deux proposés, "
                    "le choix sera offert à la création d'un dossier."
                ),
            },
        },
    )

    # Relationships
    default_business_type = relationship(
        "BusinessType",
        primaryjoin="and_(ProjectType.id==BusinessType.project_type_id, "
        "BusinessType.active==True)",
        back_populates="project_type",
        uselist=False,
    )

    other_business_types = relationship(
        "BusinessType",
        secondary=ProjectTypeBusinessType,
        back_populates="other_project_types",
    )

    @classmethod
    def get_default(cls):
        return cls.query().filter_by(default=True).one()

    @classmethod
    def get_by_name(cls, name):
        return cls.query().filter_by(name=name).first()

    @classmethod
    def with_ttc_exists(cls) -> bool:
        return DBSESSION.query(
            cls.query().filter_by(ttc_compute_mode_allowed=True, active=True).exists()
        ).scalar()

    def is_used(self):
        """
        Check if there is a project using this specific type
        """
        from caerp.models.project.project import Project

        query = Project.query().filter_by(project_type_id=self.id)
        return DBSESSION().query(query.exists()).scalar()

    def get_default_business_type(self):
        """
        Return the default business type of the project, event if not active
        """
        return (
            BusinessType.query()
            .filter_by(project_type_id=self.id)
            .order_by(desc(BusinessType.active))
            .first()
        )

    def get_other_business_type_ids(self):
        query = DBSESSION().query(ProjectTypeBusinessType.c.business_type_id)
        query = query.filter(ProjectTypeBusinessType.c.project_type_id == self.id)
        return [a[0] for a in query]

    def get_business_type_ids(self):
        """
        Collect business type ids that can be associated to this project type
        """
        result = []
        default_business_type = self.get_default_business_type()
        if default_business_type:
            result.append(default_business_type.id)
        result.extend(self.get_other_business_type_ids())
        return result

    def is_tva_on_margin(self):
        """
        Returns if the project type must be considered as "TVA on margin" or not
        """
        default_business_type = self.get_default_business_type()
        if default_business_type:
            return default_business_type.tva_on_margin
        else:
            return False

    def price_study_mandatory(self):
        return self.include_price_study and self.price_study_mode == "mandatory"

    def price_study_optionnal(self):
        return self.include_price_study and self.price_study_mode == "optionnal"

    def price_study_default(self):
        return self.include_price_study and self.price_study_mode in (
            "default",
            "mandatory",
        )

    @classmethod
    def query_for_select(cls):
        query = DBSESSION().query(cls).options(load_only("id", "label", "private"))
        query = query.filter_by(active=True).order_by(cls.default.desc())
        return query

    def __json__(self, request):
        result = super().__json__(request)
        result["label"] = self.label
        result["default_business_type_id"] = self.get_default_business_type().id
        result["other_business_type_ids"] = [
            btype.id for btype in self.other_business_types
        ]
        return result


class BusinessType(BaseProjectType):
    __tablename__ = "business_type"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "business_type"}
    __colanderalchemy_config__ = {
        "help_msg": """Les types d'affaire permettent de prédéfinir des
        comportements spécifiques. <br />
    Ex: Un type d'affaire 'Formation' permet de regrouper les documents
    liés à la formation.<br />
    Il va ensuite être possible de spécifier :
    <ul>
        <li>Des mentions à inclure dans les documents placées dans cette affaire</li>
        <li>Les documents requis à la validation des devis ou des factures</li>
        <li>Le modèle de document à utiliser pour générer les devis/factures</li>
        <li>Les modèles de document à proposer pour générer les documents
        spécifiques (livret d'accueil ...)</li>
    </ul>
    """
    }
    id = Column(
        ForeignKey("base_project_type.id"),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )
    label = Column(
        String(255),
        info={
            "colanderalchemy": {
                "title": "Libellé",
                "description": "Libellé présenté aux entrepreneurs",
            }
        },
        nullable=False,
        unique=True,
    )
    project_type_id = Column(
        ForeignKey("project_type.id"),
        info={
            "colanderalchemy": {
                "title": "Ce type d'affaire est utilisé par défaut pour "
                "les dossiers de type :"
            }
        },
    )

    project_type = relationship(
        "ProjectType",
        primaryjoin="ProjectType.id==BusinessType.project_type_id",
        info={"colanderalchemy": {"exclude": True}},
        back_populates="default_business_type",
    )

    other_project_types = relationship(
        "ProjectType",
        secondary=ProjectTypeBusinessType,
        back_populates="other_business_types",
        info={
            "colanderalchemy": {
                "title": "Ce type d'affaire peut également être utilisé "
                "dans les dossiers de type : "
            }
        },
    )

    bpf_related = Column(
        Boolean(),
        default=False,
        nullable=False,
        info={
            "colanderalchemy": {
                "title": "Ce type d'affaire est inscrit au Bilan Pédagogique "
                "de Formation"
            }
        },
    )

    tva_on_margin = Column(
        Boolean(),
        default=False,
        nullable=False,
        info={
            "colanderalchemy": {
                "title": "Ce type d'affaire fonctionne en mode TVA sur marge",
                "description": (
                    "Régime fiscal spécifique (vente de voyages, occasion…)"
                ),
            }
        },
    )
    coop_cgv_override = Column(
        Text,
        nullable=False,
        default="",
        info=dict(
            colanderalchemy=dict(
                title="Conditions générales de vente spécifiques à ce type d'affaire",
                description=(
                    "Si remplies, ces CGV prendront le pas, pour ce type d'affaire, sur celles définies dans"
                    "<a href='/admin/sales/pdf/common'>"
                    " Module Ventes ➡ Sorties PDF ➡ Informations communes aux devis et factures"
                    "</a>."
                ),
            ),
        ),
    )

    label_overrides = relationship(
        "LabelOverride",
        info={"colanderalchemy": {"exclude": True}},
        cascade="all, delete",
        passive_deletes=True,
        back_populates="business_type",
    )
    # Configuration de Template de fusion doc utilisable dans ce type d'affaire
    # Le template est accessible via file_template_rel.file_template
    file_template_rel = relationship(
        "BusinessTypeFileTypeTemplate",
        back_populates="business_type",
        cascade="all, delete-orphan",
    )

    @classmethod
    def get_default(cls):
        return ProjectType.get_default().default_business_type

    @classmethod
    def get_by_name(cls, name):
        return cls.query().filter_by(name=name).first()

    def is_used(self):
        """
        Check if there is a project using this specific type
        """
        query = Business.query().filter_by(business_type_id=self.id)
        return DBSESSION().query(query.exists()).scalar()

    def __json__(self, request):
        """
        Dict representation of this element
        """
        res = BaseProjectType.__json__(self, request)
        res["label"] = self.label
        res["project_type_id"] = self.project_type_id
        return res

    @classmethod
    def _query_mentions(cls, btype_id, doctype):
        query = DBSESSION().query(TaskMention)
        query = query.outerjoin(TaskMention.business_type_rel)
        query = query.filter(TaskMention.active == True)  # noqa: E712
        query = query.filter(BusinessTypeTaskMention.business_type_id == btype_id)
        query = query.filter(BusinessTypeTaskMention.doctype == doctype)
        return query

    def mandatory_mentions(self, doctype):
        query = BusinessType._query_mentions(self.id, doctype)
        query = query.filter(BusinessTypeTaskMention.mandatory == True)  # noqa: E712
        return query.all()

    @classmethod
    def get_mandatory_mentions(cls, btype_id, doctype):
        query = cls._query_mentions(btype_id, doctype)
        query = query.filter(BusinessTypeTaskMention.mandatory == True)  # noqa: E712
        return query.all()

    def optionnal_mentions(self, doctype):
        query = BusinessType._query_mentions(self.id, doctype)
        query = query.filter(BusinessTypeTaskMention.mandatory == False)  # noqa: E712
        return query.all()
