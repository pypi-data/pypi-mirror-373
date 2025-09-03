import logging

import deform
import deform_extensions
from caerp_base.models.base import DBBASE, default_table_args
from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.event import listen
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from caerp.models.career_stage import STAGE_TYPE_OPTIONS
from caerp.models.listeners import SQLAListeners
from caerp.models.options import ConfigurableOption, get_id_foreignkey_col
from caerp.models.tools import get_excluded_colanderalchemy

logger = logging.getLogger(__name__)

PERIOD_OPTIONS = (
    ("", ""),
    ("month", "par mois"),
    ("quarter", "par trimestre"),
    ("semester", "par semestre"),
    ("year", "par an"),
)

CAREER_PATH_GRID = (
    (("career_stage_id", 12),),
    (("start_date", 6), ("end_date", 6)),
    (("cae_situation_id", 12),),
    (("stage_type", 6),),
    (("type_contrat_id", 6), ("employee_quality_id", 6)),
    (("taux_horaire", 6), ("num_hours", 6)),
    (("hourly_rate_string", 6), ("parcours_salary", 6)),
    (("goals_amount", 6), ("goals_period", 6)),
    (("amendment_number", 6),),
    (("type_sortie_id", 6), ("motif_sortie_id", 6)),
)


# CAREER PATH / FILE ASSOCIATION TABLE
###############################################################################
class CareerPathFileRel(DBBASE):
    """
    Relationship between userdata's files and career path
    """

    __tablename__ = "career_path_file_rel"
    __table_args__ = default_table_args

    career_path_id = Column(
        "career_path_id",
        Integer,
        ForeignKey("career_path.id", ondelete="CASCADE"),
        primary_key=True,
    )
    file_id = Column(
        "file_id",
        Integer,
        ForeignKey("file.id", ondelete="CASCADE"),
        primary_key=True,
    )
    related_file = relationship("File")


def save_file_careerpath_relationship(request, appstruct, file_object):
    """
    Save relationship between userdata's file and career path

    Delete existing relationship then insert new if needed
    """
    CareerPathFileRel.query().filter(
        CareerPathFileRel.file_id == file_object.id
    ).delete()
    if appstruct.get("career_path_id") is not None:
        career_path_rel = CareerPathFileRel()
        career_path_rel.career_path_id = appstruct.get("career_path_id")
        career_path_rel.file_id = file_object.id
        request.dbsession.add(career_path_rel)
        request.dbsession.flush()


# CONFIGURABLE OPTIONS
###############################################################################
class TypeContratOption(ConfigurableOption):
    """
    Possible values for contract type
    """

    __colanderalchemy_config__ = {
        "title": "Type de contrat",
        "validation_msg": "Les types de contrat ont bien été configurés",
    }
    id = get_id_foreignkey_col("configurable_option.id")


class EmployeeQualityOption(ConfigurableOption):
    """
    Different values for employee quality
    """

    __colanderalchemy_config__ = {
        "title": "Qualité du salarié",
        "validation_msg": "Les qualité du salarié ont bien été configurées",
        "help_msg": "Configurer les options possibles pour définir la qualité\
 d'un salarié (cadre, employé…)",
    }
    id = get_id_foreignkey_col("configurable_option.id")


class TypeSortieOption(ConfigurableOption):
    """
    Possible values for exit type
    """

    __colanderalchemy_config__ = {
        "title": "Type de sortie",
        "validation_msg": "Les types de sortie ont bien été configurés",
    }
    id = get_id_foreignkey_col("configurable_option.id")


class MotifSortieOption(ConfigurableOption):
    """
    Possible values for exit motivation
    """

    __colanderalchemy_config__ = {
        "title": "Motif de sortie",
        "validation_msg": "Les motifs de sortie ont bien été configurés",
    }
    id = get_id_foreignkey_col("configurable_option.id")


# CAREER PATH CLASS
###############################################################################
class CareerPath(DBBASE):
    """
    Different career path stages
    """

    __colanderalchemy_config__ = {
        "title": "Etape de parcours",
        "help_msg": "",
        "validation_msg": "L'étape de parcours a bien été enregistrée",
        "widget": deform_extensions.GridFormWidget(named_grid=CAREER_PATH_GRID),
    }
    __tablename__ = "career_path"
    __table_args__ = default_table_args
    id = Column(
        "id",
        Integer,
        primary_key=True,
        info={
            "colanderalchemy": {"widget": deform.widget.HiddenWidget()},
            "export": {"py3o": {"exclude": True}},
        },
    )
    userdatas_id = Column(
        ForeignKey("user_datas.id", ondelete="CASCADE"),
        info={
            "colanderalchemy": {"exclude": True},
            "export": {
                "label": "ID Gestion sociale",
                "stats": {"exclude": True},
                "py3o": {"exclude": True},
            },
        },
    )
    userdatas = relationship(
        "UserDatas",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
        back_populates="career_paths",
    )
    start_date = Column(
        Date(), nullable=False, info={"colanderalchemy": {"title": "Date d'effet"}}
    )
    end_date = Column(Date(), info={"colanderalchemy": {"title": "Date d'échéance"}})
    career_stage_id = Column(
        ForeignKey("career_stage.id"),
        info={
            "colanderalchemy": {"title": "Type d'étape"},
            "export": {"exclude": True},
        },
    )
    career_stage = relationship(
        "CareerStage",
        primaryjoin="CareerStage.id==CareerPath.career_stage_id",
        info={
            "colanderalchemy": get_excluded_colanderalchemy("Etape de parcours"),
            "export": {
                "py3o": {"exclude": True},
                "flatten": [
                    ("name", "type d'étape"),
                    ("cae_situation", "Situation dans la CAE"),
                ],
                "stats": {"related_key": "name", "label": "Type d'étape"},
            },
        },
    )
    cae_situation_id = Column(
        ForeignKey("cae_situation_option.id"),
        info={
            "colanderalchemy": {
                "title": "Nouvelle situation dans la CAE",
                "description": "Lorsque cette étape sera affectée à un \
porteur cette nouvelle situation sera proposée par défaut",
            },
            "export": {"py3o": {"exclude": True}},
        },
    )
    cae_situation = relationship(
        "CaeSituationOption",
        primaryjoin="CaeSituationOption.id==CareerPath.cae_situation_id",
        info={
            "colanderalchemy": get_excluded_colanderalchemy("Situation dans la CAE"),
            "export": {"formatter": lambda a: a.label, "py3o": {"exclude": True}},
        },
    )
    stage_type = Column(
        String(15),
        info={
            "colanderalchemy": {"title": "Type d'étape"},
            "export": {
                "formatter": lambda val: dict(STAGE_TYPE_OPTIONS).get(val),
                "stats": {
                    "options": STAGE_TYPE_OPTIONS,
                    "label": "Nature",
                },
                "py3o": {"exclude": True},
            },
        },
    )
    type_contrat_id = Column(
        ForeignKey("type_contrat_option.id"),
        info={
            "colanderalchemy": {"title": "Type de contrat"},
            "export": {"exclude": True},
        },
    )
    type_contrat = relationship(
        "TypeContratOption",
        info={
            "colanderalchemy": get_excluded_colanderalchemy("Type de contrat"),
            "export": {
                "related_key": "label",
                "label": "Type de contrat",
            },
        },
    )
    employee_quality_id = Column(
        ForeignKey("employee_quality_option.id"),
        info={
            "colanderalchemy": {"title": "Qualité du salarié"},
            "export": {"exclude": True},
        },
    )
    employee_quality = relationship(
        "EmployeeQualityOption",
        info={
            "colanderalchemy": get_excluded_colanderalchemy("Qualité du salarié"),
            "export": {
                "related_key": "label",
                "label": "Qualité du salarié",
            },
        },
    )
    taux_horaire = Column(Float(), info={"colanderalchemy": {"title": "Taux horaire"}})
    hourly_rate_string = Column(
        String(100),
        info={
            "colanderalchemy": {
                "title": "Taux horaire en toutes lettres",
                "description": "Exemple: Treize euros",
            }
        },
    )
    num_hours = Column(
        Float(),
        info={
            "colanderalchemy": {
                "title": "Nombre d'heures",
                "description": "Mensuel",
            }
        },
    )
    parcours_salary = Column(
        Float(),
        info={
            "colanderalchemy": {
                "title": "Salaire brut",
                "description": "Cette valeur est calculée automatiquement",
            }
        },
    )
    goals_amount = Column(
        Float(), info={"colanderalchemy": {"title": "Objectif de CA / d'activité"}}
    )
    goals_period = Column(
        String(15),
        info={
            "colanderalchemy": {"title": "Période de l'objectif"},
            "export": {
                "formatter": lambda val: dict(PERIOD_OPTIONS).get(val),
                "stats": {"options": PERIOD_OPTIONS},
            },
        },
    )
    amendment_number = Column(
        Integer(), info={"colanderalchemy": {"title": "Numéro de l'avenant"}}
    )
    type_sortie_id = Column(
        ForeignKey("type_sortie_option.id"),
        info={
            "colanderalchemy": {"title": "Type de sortie"},
            "export": {"exclude": True},
        },
    )
    type_sortie = relationship(
        "TypeSortieOption",
        info={
            "colanderalchemy": get_excluded_colanderalchemy("Type de sortie"),
            "export": {
                "related_key": "label",
                "label": "Type de sortie",
            },
        },
    )
    motif_sortie_id = Column(
        ForeignKey("motif_sortie_option.id"),
        info={
            "colanderalchemy": {"title": "Motif de sortie"},
            "export": {"exclude": True},
        },
    )
    motif_sortie = relationship(
        "MotifSortieOption",
        info={
            "colanderalchemy": get_excluded_colanderalchemy("Motif de sortie"),
            "export": {
                "related_key": "label",
                "label": "Motif de sortie",
            },
        },
    )
    file_rel = relationship(
        "CareerPathFileRel",
        info={"export": {"exclude": True}},
        cascade="all, delete-orphan",
    )
    files = association_proxy("file_rel", "related_file")

    @classmethod
    def query(cls, user=None):
        q = super(CareerPath, cls).query()
        if user is not None:
            q = q.filter(CareerPath.userdatas_id == user)
        return q.order_by(CareerPath.start_date.desc())


def update_user_situation_cae(mapper, connection, target):
    """
    Update - if needed - the CAE situation of the user
    when it's career path change
    """
    if target.cae_situation_id is not None:
        from caerp.models.user.userdatas import UserDatas

        userdatas = (
            UserDatas.query().filter(UserDatas.id == target.userdatas_id).first()
        )
        if userdatas is not None:
            situation = userdatas.get_cae_situation_from_career_path()
            if situation:
                if userdatas.situation_situation_id != situation.id:
                    logger.debug(
                        "Update CAE situation for user %s to '%s'"
                        % (target.userdatas_id, situation.label)
                    )
                    connection.execute(
                        "UPDATE user_datas SET situation_situation_id=%s \
                        WHERE id=%s"
                        % (situation.id, userdatas.id)
                    )


def start_listening():
    listen(CareerPath, "after_insert", update_user_situation_cae)
    listen(CareerPath, "after_update", update_user_situation_cae)
    listen(CareerPath, "after_delete", update_user_situation_cae)


SQLAListeners.register(start_listening)
