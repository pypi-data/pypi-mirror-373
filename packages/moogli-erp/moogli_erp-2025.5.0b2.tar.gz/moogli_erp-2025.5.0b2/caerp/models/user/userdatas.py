import datetime
import logging

import colander
import deform
from caerp_base.consts import CIVILITE_OPTIONS, SEX_OPTIONS
from caerp_base.models.base import DBBASE, default_table_args
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    event,
)
from sqlalchemy.orm import backref, relationship

from caerp.models.listeners import SQLAListeners
from caerp.models.node import Node
from caerp.models.options import ConfigurableOption, get_id_foreignkey_col
from caerp.models.tools import get_excluded_colanderalchemy, set_attribute
from caerp.models.user.user import User

STATUS_OPTIONS = (
    (
        "",
        "",
    ),
    (
        "single",
        "Célibataire",
    ),
    (
        "maried",
        "Marié(e)",
    ),
    (
        "widow",
        "Veuf(ve)",
    ),
    (
        "divorced",
        "Divorcé(e)",
    ),
    (
        "isolated",
        "Séparé(e)",
    ),
    (
        "free_union",
        "Vie maritale",
    ),
    (
        "pacsed",
        "Pacsé(e)",
    ),
)


CONTRACT_OPTIONS = (
    (
        "",
        "",
    ),
    (
        "cdd",
        "CDD",
    ),
    (
        "cdi",
        "CDI",
    ),
)


logger = logging.getLogger(__name__)


class ZoneOption(ConfigurableOption):
    """
    Different type of geographical zones
    """

    __colanderalchemy_config__ = {
        "title": "Zone d’habitation",
        "validation_msg": "Les zones d'habitation ont bien été configurées",
    }
    id = get_id_foreignkey_col("configurable_option.id")


class ZoneQualificationOption(ConfigurableOption):
    """
    Different possible values to qualify a zone
    """

    __colanderalchemy_config__ = {
        "title": "Qualificatif des zones d’habitation",
        "validation_msg": "Les qualificatifs de zones d'habitation ont bien \
été configurés",
    }
    id = get_id_foreignkey_col("configurable_option.id")


class StudyLevelOption(ConfigurableOption):
    """
    Different values for study level
    """

    __colanderalchemy_config__ = {
        "title": "Niveau d’étude",
        "validation_msg": "Les niveaux d’étude ont bien été configurées",
    }
    id = get_id_foreignkey_col("configurable_option.id")


class SocialStatusOption(ConfigurableOption):
    """
    Different values for social status
    """

    __colanderalchemy_config__ = {
        "title": "Statut social",
        "validation_msg": "Les statuts sociaux ont bien été configurés",
    }
    id = get_id_foreignkey_col("configurable_option.id")


class ActivityTypeOption(ConfigurableOption):
    """
    Different possible values for activity type
    """

    __colanderalchemy_config__ = {
        "title": "Typologie des métiers/secteurs d’activité",
        "validation_msg": "Les typologie des métiers ont bien été configurées",
    }
    id = get_id_foreignkey_col("configurable_option.id")


class PcsOption(ConfigurableOption):
    """
    Different possible value for Pcs
    """

    __colanderalchemy_config__ = {
        "title": "PCS",
        "validation_msg": "Les options pour 'PCS' ont bien été configurées",
    }
    id = get_id_foreignkey_col("configurable_option.id")


class PrescripteurOption(ConfigurableOption):
    """
    Different values for prescripteur
    """

    __colanderalchemy_config__ = {
        "title": "Prescripteur",
        "validation_msg": "Les différents prescripteurs ont bien \
été configurés",
    }
    id = get_id_foreignkey_col("configurable_option.id")


class NonAdmissionOption(ConfigurableOption):
    """
    Possible values for refusing admission
    """

    __colanderalchemy_config__ = {
        "title": "Motif de non admission",
        "validation_msg": "Les motifs de non admission ont bien \
été configurés",
    }
    id = get_id_foreignkey_col("configurable_option.id")


class ParcoursStatusOption(ConfigurableOption):
    """
    Possible values for status
    """

    __colanderalchemy_config__ = {
        "title": "Résultat de la visite médicale",
        "validation_msg": "Les résultats de la visite médicale ont bien \
été configurés",
    }
    id = get_id_foreignkey_col("configurable_option.id")


class CaeSituationOption(ConfigurableOption):
    """
    Possible values for the cae status "Situation actuelle dans la cae"
    """

    __colanderalchemy_config__ = {
        "title": "Situation dans la CAE",
        "validation_msg": "Les types de situations ont bien été configurés",
        "help_msg": "Ce sont les différents statuts que peuvent prendre les \
        entrepreneurs pendant leur parcours au sein de la coopérative.<br /><br />\
        <b>La première situation (dans l’ordre ci-dessous) \
        sera affectée par défaut aux nouveaux entrepreneurs.</b>",
    }
    id = get_id_foreignkey_col("configurable_option.id")
    # Is this element related to the integration process of a PP
    is_integration = Column(
        Boolean(),
        default=False,
        info={
            "colanderalchemy": {
                "title": "Donne droit à un compte MoOGLi",
                "description": "Si un entrepreneur a ce statut, \
un compte MoOGLi lui sera automatiquement associé",
            }
        },
    )


def get_default_cae_situation():
    situation = CaeSituationOption.query().order_by(CaeSituationOption.order).first()
    if situation is not None:
        return situation.id
    else:
        return None


class SocialDocTypeOption(ConfigurableOption):
    """
    Different social doc types
    """

    __colanderalchemy_config__ = {
        "title": "Type de document sociaux",
        "validation_msg": "Les types de documents sociaux ont \
bien été configurés",
    }
    id = get_id_foreignkey_col("configurable_option.id")


class AntenneOption(ConfigurableOption):
    """
    Different antenne
    """

    __colanderalchemy_config__ = {
        "title": "Antennes de la CAE",
        "validation_msg": "Les antennes ont bien été configurées",
    }
    id = get_id_foreignkey_col("configurable_option.id")


class CareContractOption(ConfigurableOption):
    """
    Different values for care contracts
    """

    __colanderalchemy_config__ = {
        "title": "Contrats de protection sociale et prévoyance",
        "validation_msg": "Les contrats de protection sociale et prévoyance \
            ont bien été configurés",
    }
    id = get_id_foreignkey_col("configurable_option.id")


class AidOrganismOption(ConfigurableOption):
    """
    Different values for aid organisms
    """

    __colanderalchemy_config__ = {
        "title": "Organismes d’aide au porteur",
        "validation_msg": "Les organismes d’aide au porteur ont bien été \
            configurés",
    }
    id = get_id_foreignkey_col("configurable_option.id")


class UserDatasSocialDocTypes(DBBASE):
    """
    relationship table used between social document types and user datas set
    """

    __tablename__ = "userdatas_socialdocs"
    __table_args__ = default_table_args
    __colanderalchemy_config__ = {
        "css": "text-right",
    }
    userdatas_id = Column(
        ForeignKey("user_datas.id"),
        primary_key=True,
        info={
            "colanderalchemy": {
                "widget": deform.widget.HiddenWidget(),
                "missing": None,
            },
            "export": {"exclude": True},
        },
    )

    doctype_id = Column(
        ForeignKey("social_doc_type_option.id"),
        primary_key=True,
        info={
            "colanderalchemy": {
                "widget": deform.widget.HiddenWidget(),
                "missing": None,
            },
            "export": {
                "exclude": True,
                "stats": {"exclude": False, "label": "Type de documents"},
            },
        },
    )

    status = Column(
        Boolean(),
        default=False,
        info={
            "export": {
                "exclude": True,
                "stats": {"exclude": False, "label": "A été fourni ?"},
            }
        },
    )
    userdatas = relationship(
        "UserDatas",
        backref=backref(
            "doctypes_registrations",
            cascade="all, delete-orphan",
            info={
                "colanderalchemy": {"exclude": True},
                "export": {
                    "exclude": True,
                    "stats": {
                        "exclude": False,
                        "label": "Documents sociaux - ",
                    },
                },
            },
        ),
        info={"colanderalchemy": {"exclude": True}, "export": {"exclude": True}},
    )

    doctype = relationship(
        "SocialDocTypeOption",
        backref=backref(
            "registration",
            cascade="all, delete-orphan",
            info={"colanderalchemy": {"exclude": True}},
        ),
        info={
            "colanderalchemy": {"exclude": True},
            "export": {
                "exclude": True,
                "stats": {
                    "exclude": False,
                },
            },
        },
    )


def get_dict_key_from_value(val, dict_):
    for key, value in list(dict_.items()):
        if value == val:
            return key
    raise KeyError()


class UserDatas(Node):
    __tablename__ = "user_datas"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "userdata"}

    id = Column(
        ForeignKey("node.id"),
        primary_key=True,
        info={
            "colanderalchemy": {"exclude": True, "title": "ID Gestion sociale"},
        },
    )

    # User account associated with this dataset
    user_id = Column(
        ForeignKey("accounts.id"),
        info={
            "colanderalchemy": {"exclude": True, "title": "ID Utilisateur"},
            "export": {"exclude": False},
        },
    )
    user = relationship(
        "User",
        primaryjoin="User.id==UserDatas.user_id",
        back_populates="userdatas",
        info={
            "colanderalchemy": get_excluded_colanderalchemy("Compte utilisateur"),
            "export": {"exclude": True},
        },
    )

    # INFORMATIONS GÉNÉRALES
    situation_situation_id = Column(
        ForeignKey("cae_situation_option.id"),
        info={"colanderalchemy": {"exclude": True}, "export": {"exclude": True}},
    )
    situation_situation = relationship(
        "CaeSituationOption",
        info={
            "colanderalchemy": get_excluded_colanderalchemy(
                "Situation actuelle dans la CAE",
            ),
            "export": {
                "related_key": "label",
            },
        },
    )
    situation_antenne_id = Column(
        ForeignKey("antenne_option.id"),
        info={
            "colanderalchemy": {
                "title": "Antenne de rattachement",
                "section": "Synthèse",
            }
        },
    )
    situation_antenne = relationship(
        "AntenneOption",
        info={
            "colanderalchemy": get_excluded_colanderalchemy("Antenne de rattachement"),
            "export": {"related_key": "label"},
        },
    )
    situation_follower_id = Column(
        ForeignKey("accounts.id"),
        info={
            "colanderalchemy": {
                "title": "Accompagnateur",
                "section": "Synthèse",
            },
            "export": {"exclude": True},
            "anonymize": True,
        },
    )
    situation_follower = relationship(
        "User",
        primaryjoin="User.id==UserDatas.situation_follower_id",
        info={
            "colanderalchemy": get_excluded_colanderalchemy("Accompagnateur"),
            "export": {"label": "Accompagnateur", "formatter": lambda u: u.label},
            "import": {"related_retriever": User.find_user},
        },
    )
    situation_societariat_entrance = Column(
        Date(),
        info={
            "colanderalchemy": {
                "title": "Sociétariat",
                "section": "Synthèse",
                "description": "Date d’entrée au sociétariat",
            },
            "export": {"label": "Date d’entrée au sociétariat"},
        },
        default=None,
    )

    # COORDONNÉES
    coordonnees_civilite = Column(
        String(10),
        info={
            "colanderalchemy": {
                "title": "Civilité",
                "section": "Coordonnées",
            },
            "export": {
                "formatter": lambda val: dict(CIVILITE_OPTIONS).get(val),
                "stats": {"options": CIVILITE_OPTIONS},
            },
        },
        default=CIVILITE_OPTIONS[0][0],
        nullable=False,
    )
    coordonnees_lastname = Column(
        String(50),
        info={
            "colanderalchemy": {
                "title": "Nom",
                "section": "Coordonnées",
            },
            "anonymize": True,
        },
        nullable=False,
    )
    coordonnees_firstname = Column(
        String(50),
        info={
            "colanderalchemy": {
                "title": "Prénom",
                "section": "Coordonnées",
            },
            "anonymize": True,
        },
        nullable=False,
    )
    coordonnees_ladies_lastname = Column(
        String(50),
        info={
            "colanderalchemy": {
                "title": "Nom de naissance",
                "section": "Coordonnées",
            },
            "anonymize": True,
        },
    )
    coordonnees_email1 = Column(
        String(100),
        info={
            "colanderalchemy": {
                "title": "E-mail 1",
                "section": "Coordonnées",
            },
            "anonymize": True,
        },
        nullable=False,
    )
    coordonnees_email2 = Column(
        String(100),
        info={
            "colanderalchemy": {
                "title": "E-mail 2",
                "section": "Coordonnées",
            },
            "anonymize": True,
        },
    )
    coordonnees_tel = Column(
        String(14),
        info={
            "colanderalchemy": {
                "title": "Tél. fixe",
                "section": "Coordonnées",
            },
            "anonymize": True,
        },
    )
    coordonnees_mobile = Column(
        String(14),
        info={
            "colanderalchemy": {
                "title": "Tél. mobile",
                "section": "Coordonnées",
            },
            "anonymize": True,
        },
    )
    coordonnees_address = Column(
        String(255),
        info={
            "colanderalchemy": {
                "title": "Adresse",
                "section": "Coordonnées",
            },
            "anonymize": True,
        },
    )
    coordonnees_zipcode = Column(
        String(7),
        info={
            "colanderalchemy": {
                "title": "Code postal",
                "section": "Coordonnées",
            },
            "py3o": {"formatter": lambda z: "%05d" % z},
            "anonymize": True,
        },
    )
    coordonnees_city = Column(
        String(100),
        info={
            "colanderalchemy": {
                "title": "Ville",
                "section": "Coordonnées",
            },
            "anonymize": True,
        },
    )
    coordonnees_zone_id = Column(
        ForeignKey("zone_option.id"),
        info={
            "colanderalchemy": {
                "title": "Zone d’habitation",
                "section": "Coordonnées",
            }
        },
    )
    coordonnees_zone = relationship(
        "ZoneOption",
        info={
            "colanderalchemy": get_excluded_colanderalchemy("Zone d’habitation"),
            "export": {"related_key": "label"},
        },
    )
    coordonnees_zone_qual_id = Column(
        ForeignKey("zone_qualification_option.id"),
        info={
            "colanderalchemy": {
                "title": "Qualification de la zone d’habitation",
                "section": "Coordonnées",
            }
        },
    )
    coordonnees_zone_qual = relationship(
        "ZoneQualificationOption",
        info={
            "colanderalchemy": get_excluded_colanderalchemy(
                "Qualification de la zone d’habitation"
            ),
            "export": {"related_key": "label"},
        },
    )
    coordonnees_sex = Column(
        String(1),
        info={
            "colanderalchemy": {
                "title": "Sexe",
                "section": "Coordonnées",
            },
            "export": {"stats": {"options": SEX_OPTIONS}},
        },
    )
    coordonnees_birthday = Column(
        Date(),
        info={
            "colanderalchemy": {
                "title": "Naissance",
                "section": "Coordonnées",
                "description": "Date de naissance",
            },
            "anonymize": True,
        },
    )
    coordonnees_birthplace = Column(
        String(255),
        info={
            "colanderalchemy": {
                "title": "Lieu de naissance",
                "section": "Coordonnées",
            },
            "anonymize": True,
        },
    )
    coordonnees_birthplace_zipcode = Column(
        String(7),
        info={
            "colanderalchemy": {
                "title": "Code postal",
                "section": "Coordonnées",
                "description": "Code postal du lieu de naissance",
            },
            "export": {"label": "Code postal du lieu de naissance"},
            "anonymize": True,
        },
    )
    coordonnees_nationality = Column(
        String(50),
        info={
            "colanderalchemy": {
                "title": "Nationalité",
                "section": "Coordonnées",
            },
            "anonymize": True,
        },
    )
    coordonnees_resident = Column(
        Date(),
        info={
            "colanderalchemy": {
                "title": "Carte de séjour",
                "section": "Coordonnées",
                "description": "Date de fin de validité",
            },
            "anonymize": True,
        },
    )
    coordonnees_secu = Column(
        String(50),
        info={
            "colanderalchemy": {
                "title": "Numéro de sécurité sociale",
                "section": "Coordonnées",
            },
            "anonymize": True,
        },
    )
    coordonnees_family_status = Column(
        String(20),
        info={
            "colanderalchemy": {
                "title": "Situation de famille",
                "section": "Coordonnées",
            },
            "export": {
                "formatter": lambda val: dict(STATUS_OPTIONS).get(val),
                "stats": {"options": STATUS_OPTIONS},
            },
            "anonymize": True,
        },
    )
    coordonnees_children = Column(
        Integer(),
        default=0,
        info={
            "colanderalchemy": {
                "title": "Nombre d’enfants",
                "section": "Coordonnées",
            },
            "anonymize": True,
        },
    )
    coordonnees_study_level_id = Column(
        ForeignKey("study_level_option.id"),
        info={
            "colanderalchemy": {
                "title": "Niveau d’études",
                "section": "Coordonnées",
            }
        },
    )
    coordonnees_study_level = relationship(
        "StudyLevelOption",
        info={
            "colanderalchemy": get_excluded_colanderalchemy("Niveau d’études"),
            "export": {"related_key": "label"},
        },
    )
    coordonnees_emergency_name = Column(
        String(50),
        info={
            "colanderalchemy": {
                "title": "Contact urgent : Nom",
                "section": "Coordonnées",
            },
            "anonymize": True,
        },
    )
    coordonnees_emergency_phone = Column(
        String(14),
        info={
            "colanderalchemy": {
                "title": "Contact urgent : Téléphone",
                "section": "Coordonnées",
            },
            "anonymize": True,
        },
    )
    coordonnees_identifiant_interne = Column(
        String(20),
        info={
            "colanderalchemy": {
                "title": "Identifiant interne",
                "description": "Identifiant interne propre à la CAE \
(facultatif)",
                "section": "Coordonnées",
            },
            "anonymize": True,
        },
    )

    # STATUT
    social_statuses = relationship(
        "SocialStatusDatas",
        cascade="all, delete-orphan",
        primaryjoin="and_(UserDatas.id==SocialStatusDatas.userdatas_id, "
        "SocialStatusDatas.step=='entry')",
        order_by="SocialStatusDatas.id",
        info={
            "colanderalchemy": {
                "title": "Statut social à l’entrée",
                "section": "Statut",
            },
            "export": {
                "label": "Statut social à l’entrée",
                "related_key": "social_status.label",
                "stats": {"label": "Statut social"},
            },
        },
        back_populates="userdatas",
        overlaps="today_social_statuses, userdatas",
    )
    today_social_statuses = relationship(
        "SocialStatusDatas",
        cascade="all, delete-orphan",
        primaryjoin="and_(UserDatas.id==SocialStatusDatas.userdatas_id, "
        "SocialStatusDatas.step=='today')",
        order_by="SocialStatusDatas.id",
        info={
            "colanderalchemy": {
                "title": "Statut social actuel",
                "section": "Statut",
            },
            "export": {
                "label": "Statut social actuel",
                "related_key": "social_status.label",
                # Pour les stats la relation précédente permet de construire
                # des critères couvrant cette relation-ci également
                "stats": {"exclude": True},
            },
        },
        overlaps="social_statuses, userdatas",
    )
    statut_end_rights_date = Column(
        Date(),
        info={
            "colanderalchemy": {
                "title": "Date de fin de droit",
                "section": "Statut",
            },
            "anonymize": True,
        },
    )
    statut_handicap_allocation_expiration = Column(
        Date(),
        default=None,
        info={
            "colanderalchemy": {
                "title": "Allocation adulte handicapé - échéance",
                "description": "Date d’expiration de l’allocation",
                "section": "Statut",
            },
            "anonymize": True,
        },
    )
    statut_external_activity = relationship(
        "ExternalActivityDatas",
        cascade="all, delete-orphan",
        info={
            "colanderalchemy": {
                "title": "Activité externe",
                "section": "Statut",
            },
            "export": {
                "flatten": [
                    ("type", "Type de contrat"),
                    ("hours", "Heures"),
                    ("brut_salary", "Salaire brut"),
                    ("employer_visited", "Visite employeur"),
                ],
            },
            "anonymize": True,
        },
        backref=backref(
            "userdatas",
            info={
                "export": {
                    "related_key": "export_label",
                    "keep_key": True,
                    "label": "Entrepreneur",
                    "stats": {"exclude": True},
                }
            },
        ),
    )
    statut_bank_accounts = relationship(
        "BankAccountsDatas",
        cascade="all, delete-orphan",
        info={
            "colanderalchemy": {
                "title": "Comptes bancaires",
                "section": "Statut",
            },
            "export": {
                "flatten": [
                    ("label", "Libellé du compte"),
                    ("iban", "IBAN"),
                    ("bic", "BIC"),
                ],
            },
            "anonymize": True,
        },
    )
    statut_aid_organisms = relationship(
        "AidOrganismsDatas",
        cascade="all, delete-orphan",
        info={
            "colanderalchemy": {
                "title": "Organismes d’aide au porteur",
                "section": "Statut",
                "missing": colander.drop,
            },
            "anonymize": True,
        },
    )

    # ACTIVITÉ
    activity_typologie_id = Column(
        ForeignKey("activity_type_option.id"),
        info={
            "colanderalchemy": {
                "title": "Typologie",
                "description": "Typologie des métiers ou secteurs d’activités",
                "section": "Activité",
            },
            "anonymize": True,
        },
    )
    activity_typologie = relationship(
        "ActivityTypeOption",
        info={
            "colanderalchemy": get_excluded_colanderalchemy(
                "Typologie des métiers/secteurs d’activités"
            ),
            "export": {"related_key": "label"},
        },
    )
    activity_pcs_id = Column(
        ForeignKey("pcs_option.id"),
        info={
            "colanderalchemy": {
                "title": "PCS",
                "section": "Activité",
            },
            "anonymize": True,
        },
    )
    activity_pcs = relationship(
        "PcsOption",
        info={
            "colanderalchemy": get_excluded_colanderalchemy("PCS"),
            "export": {"related_key": "label"},
        },
    )
    activity_companydatas = relationship(
        "CompanyDatas",
        cascade="all, delete-orphan",
        back_populates="userdatas",
        info={
            "colanderalchemy": {
                "title": "Activités",
                "section": "Activité",
            },
            "export": {
                "flatten": [
                    ("title", "Titre de l’activité"),
                    ("name", "Nom commercial"),
                    ("website", "Site internet"),
                    ("activity.label", "Type d’activité"),
                ]
            },
            "anonymize": True,
        },
    )
    activity_care_contracts = relationship(
        "CareContractsDatas",
        cascade="all, delete-orphan",
        info={
            "colanderalchemy": {
                "title": "Contrats de protection sociale et prévoyance",
                "section": "Activité",
                "missing": colander.drop,
            },
            "anonymize": True,
        },
    )

    # PARCOURS
    parcours_prescripteur_id = Column(
        ForeignKey("prescripteur_option.id"),
        info={
            "colanderalchemy": {
                "title": "Prescripteur",
                "section": "Synthèse",
            }
        },
    )
    parcours_prescripteur = relationship(
        "PrescripteurOption",
        info={
            "colanderalchemy": get_excluded_colanderalchemy("Prescripteur"),
            "export": {"related_key": "label"},
        },
    )
    parcours_prescripteur_name = Column(
        String(50),
        info={
            "colanderalchemy": {
                "title": "Nom du prescripteur",
                "section": "Synthèse",
            }
        },
    )
    parcours_date_info_coll = Column(
        Date(),
        info={
            "colanderalchemy": {
                "title": "Info coll.",
                "section": "Synthèse",
                "description": "Date de la réunion d’information collective",
            }
        },
    )
    parcours_non_admission_id = Column(
        ForeignKey("non_admission_option.id"),
        info={
            "colanderalchemy": {
                "title": "Motif de non admission en CAE",
                "section": "Synthèse",
            }
        },
    )
    parcours_non_admission = relationship(
        "NonAdmissionOption",
        info={
            "colanderalchemy": get_excluded_colanderalchemy(
                "Motif de non admission en CAE"
            ),
            "export": {"related_key": "label"},
        },
    )
    parcours_goals = Column(
        Text(),
        info={
            "colanderalchemy": {
                "title": "Objectifs",
                "section": "Activité",
            },
            "anonymize": True,
        },
    )
    parcours_status_id = Column(
        ForeignKey("parcours_status_option.id"),
        info={
            "colanderalchemy": {
                "title": "Résultat de la visite médicale",
                "section": "Activité",
            },
            "anonymize": True,
        },
    )
    parcours_status = relationship(
        "ParcoursStatusOption",
        info={
            "colanderalchemy": get_excluded_colanderalchemy(
                "Résultat de la visite médicale"
            ),
            "export": {"related_key": "label"},
        },
    )
    parcours_medical_visit = Column(
        Date(),
        info={
            "colanderalchemy": {
                "title": "Visite médicale",
                "description": "Date de la visite médicale",
                "section": "Activité",
            },
            "anonymize": True,
        },
    )
    parcours_medical_visit_limit = Column(
        Date(),
        info={
            "colanderalchemy": {
                "title": "Date limite",
                "description": "Date limite de la prochaine visite médicale",
                "section": "Activité",
            },
            "anonymize": True,
        },
    )
    career_paths = relationship(
        "CareerPath",
        order_by="desc(CareerPath.start_date)",
        info={
            "colanderalchemy": {"exclude": True, "title": "Parcours"},
            "export": {
                "flatten": [
                    ("career_stage.name", "Type d’étape"),
                    ("start_date", "Date d’effet"),
                    ("end_date", "Date d’échéance"),
                    ("cae_situation.label", "Situation dans la CAE"),
                    ("stage_type.label", "Type d’étape"),
                    ("type_contrat.label", "Type de contrat"),
                    ("employee_quality.label", "Qualité du salarié"),
                    ("taux_horaire", "Taux horaire"),
                    ("num_hours", "Nombre d’heures"),
                    ("parcours_salary", "Salaire brut"),
                    ("amendment_number", "Numéro de l’avenant"),
                    ("type_sortie.label", "Type de sortie"),
                    ("motif_sortie.label", "Motif de sortie"),
                ],
                "stats": {
                    "label": "Étape de parcours",
                    "exclude": False,
                },
            },
        },
        back_populates="userdatas",
    )

    custom_fields = relationship(
        "UserDatasCustomFields",
        uselist=False,
        cascade="all, delete-orphan",
        back_populates="userdatas",
        info={
            "colanderalchemy": {"title": ""},
            "export": {"stats": {"label": "Champs complémentaires"}},
            "anonymize": True,
        },
    )

    def __str__(self):
        return "<Userdatas : {0} {1} {2}>".format(
            self.id, self.coordonnees_lastname, self.coordonnees_firstname
        )

    @property
    def export_label(self):
        return "{0} {1}".format(
            self.coordonnees_lastname,
            self.coordonnees_firstname,
        )

    @property
    def age(self):
        birthday = self.coordonnees_birthday
        now = datetime.date.today()
        years = now.year - birthday.year
        # We translate the "now" date to know if his birthday has passed or not
        translated_now = datetime.date(birthday.year, now.month, now.day)
        if translated_now < birthday:
            years -= 1
        return years

    @property
    def full_address(self):
        return (
            f"{self.coordonnees_address}\n"
            f"{self.coordonnees_zipcode} {self.coordonnees_city}"
        )

    def gen_companies(self):
        """
        Generate companies as expected
        """
        from caerp.models.company import Company

        companies = []
        for data in self.activity_companydatas:
            # Try to retrieve an existing company (and avoid duplicates)
            company = Company.query().filter(Company.name == data.name).first()

            if company is None:
                company = Company(
                    name=data.name,
                    goal=data.title,
                    email=self.coordonnees_email1,
                    phone=self.coordonnees_tel,
                    mobile=self.coordonnees_mobile,
                )
                if data.activity is not None:
                    company.activities.append(data.activity)

            company.employees.append(self.user)
            companies.append(company)
        return companies

    def get_cae_situation_from_career_path(self, date=None):
        """
        Return the CaeSituation of the current user
        at the given date computed from the career path
        """
        from caerp.models.career_path import CareerPath
        from caerp.models.user.userdatas import CaeSituationOption

        query = CareerPath.query(self.id).filter(
            CareerPath.cae_situation_id != None  # noqa
        )
        if date is not None:
            query = query.filter(CareerPath.start_date <= date)
        last_situation_path = query.first()
        if last_situation_path is None:
            return None
        else:
            situation = (
                CaeSituationOption.query()
                .filter(CaeSituationOption.id == last_situation_path.cae_situation_id)
                .first()
            )
            return situation

    def get_career_path_by_stages(self):
        """
        Collect CareerPath associated to this instance and stores them by stage
        name

        :returns: A dict {'stage': [List of ordered CareerPath]}
        :rtype: dict
        """
        from caerp.models.career_path import CareerPath
        from caerp.models.career_stage import CareerStage

        result = {}
        for stage in CareerStage.query():
            result[stage.name] = (
                CareerPath.query(self.id).filter_by(career_stage_id=stage.id).all()
            )
        return result

    def gen_related_user_instance(self):
        """
        Generate a User instance based on the current UserDatas instance

        Usefull for importing tools (e.g: caerp_celery)

        :returns: A User instance (not added to the current session)
        """
        if self.user is not None:
            result = self.user
        else:
            from caerp.models.user.user import User

            result = User(
                lastname=self.coordonnees_lastname,
                firstname=self.coordonnees_firstname,
                email=self.coordonnees_email1,
            )
            if self.coordonnees_civilite:
                result.civilite = self.coordonnees_civilite
            from caerp_base.models.base import DBSESSION

            DBSESSION().add(result)
            DBSESSION().flush()
            self.user_id = result.id
            DBSESSION().merge(self)
            self.user = result
        return result


class UserDatasCustomFields(DBBASE):
    """
    Ce modèle, en relation 1-1 avec UserDatas, est utilisé pour permettre
    automatiquement la configuration de l’affichage de chaque champs
    sur les fiches Gestion Sociale.
    > Cf caerp/views/admin/userdatas/custom_files.py

    Les champs sont automatiquement affichés sur le formulaire (si activés)
    mais peuvent être "customisés" si besoin.
    > Cf caerp/forms/user/userdatas.py

    Tout changement sur ce modèle doit faire l’objet d’un script de migration
    Alembic, comme pour n’importe quel modèle, il n’y a pas d’automatisme.

    La "section" ColanderAlchemy est obligatoire pour un affichage correct.
    """

    __tablename__ = "user_datas_custom_fields"
    __table_args__ = default_table_args

    id = Column(
        ForeignKey("user_datas.id", ondelete="CASCADE"),
        primary_key=True,
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )
    userdatas = relationship(
        "UserDatas",
        back_populates="custom_fields",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )

    # EXPÉRIENCE PROFESSIONNELLE ##############################################
    exp__diplome = Column(
        String(255),
        info={
            "colanderalchemy": {
                "title": "Diplôme(s) obtenu(s)",
                "section": "Expérience professionnelle",
            },
        },
    )
    exp__annee_diplome = Column(
        Integer(),
        info={
            "colanderalchemy": {
                "title": "Année d’obtention du dernier diplôme",
                "section": "Expérience professionnelle",
            },
        },
    )
    exp__metier_origine = Column(
        String(255),
        info={
            "colanderalchemy": {
                "title": "Métier d’origine",
                "section": "Expérience professionnelle",
            },
        },
    )
    exp__nb_annees = Column(
        Integer(),
        info={
            "colanderalchemy": {
                "title": "Expérience (en années)",
                "section": "Expérience professionnelle",
            },
        },
    )
    exp__competences = Column(
        Text(),
        info={
            "colanderalchemy": {
                "title": "Compétences",
                "section": "Expérience professionnelle",
            },
        },
    )

    # SECTEUR AGRICOLE ########################################################
    agri__lieu_production = Column(
        Text(),
        info={
            "colanderalchemy": {
                "title": "Lieu de production",
                "section": "Secteur agricole",
            },
        },
    )

    agri__forme_test = Column(
        Text(),
        info={
            "colanderalchemy": {
                "title": "Forme de test (couple, individuel, ou collectif)",
                "section": "Secteur agricole",
            },
        },
    )
    agri__certif_bio = Column(
        Boolean,
        info={
            "colanderalchemy": {
                "title": "Certification bio",
                "section": "Secteur agricole",
            },
        },
    )
    agri__nima = Column(
        Boolean,
        info={
            "colanderalchemy": {
                "title": "N.I.M.A. (Non Issu du Milieu Agricole)",
                "section": "Secteur agricole",
            },
        },
    )
    agri__accomp_technique = Column(
        Text(),
        info={
            "colanderalchemy": {
                "title": "Accompagnement technique",
                "section": "Secteur agricole",
            },
        },
    )
    agri__diplome = Column(
        Text(),
        info={
            "colanderalchemy": {
                "title": "Diplôme agricole",
                "section": "Secteur agricole",
            },
        },
    )
    agri__dispo_terres = Column(
        Text(),
        info={
            "colanderalchemy": {
                "title": "Mise à disposition des terres",
                "section": "Secteur agricole",
            },
        },
    )
    # DISPOSITIFS DE FINANCEMENT LOCAUX ########################################
    loca__dispositif_region = Column(
        Boolean,
        info={
            "colanderalchemy": {
                "title": "Dispositif d’accompagnement de la région",
                "section": "Dispositifs de financements locaux",
            },
        },
    )
    loca__debut_dispositif_region = Column(
        Date(),
        info={
            "colanderalchemy": {
                "title": "Date de début du dispositif d’accompagnement de la\
                région",
                "section": "Dispositifs de financements locaux",
            },
        },
    )
    loca__fin_dispositif_region = Column(
        Date(),
        info={
            "colanderalchemy": {
                "title": "Date de fin du dispositif d’accompagnement de la\
                région",
                "section": "Dispositifs de financements locaux",
            },
        },
    )
    # ADMINISTRATIF ###########################################################
    admin__num_carte_depot = Column(
        Text(),
        info={
            "colanderalchemy": {
                "title": "Numéro de carte de dépôt",
                "section": "Administratif",
            },
        },
    )
    admin__date_fin_carte_depot = Column(
        Date(),
        info={
            "colanderalchemy": {
                "title": "Date de fin de validité de carte de dépôt",
                "section": "Administratif",
            },
        },
    )


# multi-valued user-datas
class ExternalActivityDatas(DBBASE):
    """
    Datas related to external activities
    """

    __colanderalchemy_config__ = {
        "title": "une activité externe à la CAE",
    }
    __tablename__ = "external_activity_datas"
    __table_args__ = default_table_args
    id = Column(
        Integer,
        primary_key=True,
        info={
            "colanderalchemy": {
                "widget": deform.widget.HiddenWidget(),
                "missing": None,
            },
            "export": {"exclude": True},
        },
    )
    type = Column(
        String(50),
        info={
            "colanderalchemy": {
                "title": "Type de contrat",
            },
            "export": {"stats": {"options": CONTRACT_OPTIONS}},
        },
    )
    hours = Column(
        Float(),
        info={
            "colanderalchemy": {
                "title": "Nombre d’heures",
            }
        },
    )
    brut_salary = Column(
        Float(),
        info={
            "colanderalchemy": {
                "title": "Salaire brut",
            }
        },
    )
    employer_visited = Column(
        Boolean(),
        default=False,
        info={
            "colanderalchemy": {
                "title": "Visite autre employeur",
            }
        },
    )
    userdatas_id = Column(
        ForeignKey("user_datas.id"),
        info={
            "colanderalchemy": {"exclude": True},
            "export": {
                "label": "ID Gestion sociale",
                "stats": {"exclude": True},
            },
        },
    )


class CompanyDatas(DBBASE):
    __colanderalchemy_config__ = {
        "title": "une activité",
    }
    __tablename__ = "company_datas"
    __table_args__ = default_table_args
    id = Column(
        Integer,
        primary_key=True,
        info={
            "colanderalchemy": {
                "widget": deform.widget.HiddenWidget(),
                "missing": None,
            },
            "export": {"exclude": True},
        },
    )
    title = Column(
        String(250),
        info={
            "colanderalchemy": {
                "title": "Titre de l’activité",
            }
        },
        nullable=False,
    )
    name = Column(
        String(100),
        info={
            "colanderalchemy": {
                "title": "Nom commercial",
            }
        },
        nullable=False,
    )
    website = Column(
        String(100),
        info={
            "colanderalchemy": {
                "title": "Site internet",
            }
        },
    )
    activity_id = Column(
        ForeignKey("company_activity.id", ondelete="SET NULL"),
        info={
            "colanderalchemy": {
                "title": "Domaine d’activité",
            }
        },
    )
    activity = relationship(
        "CompanyActivity",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"related_key": "label"},
        },
    )
    userdatas_id = Column(
        ForeignKey("user_datas.id", ondelete="CASCADE"),
        info={
            "colanderalchemy": {"exclude": True},
            "export": {
                "label": "ID Gestion sociale",
                "stats": {"exclude": True},
            },
        },
    )
    userdatas = relationship(
        UserDatas,
        back_populates="activity_companydatas",
        info={
            "export": {
                "related_key": "export_label",
                "keep_key": True,
                "label": "Entrepreneur",
                "stats": {"exclude": True},
            }
        },
    )


class SocialStatusDatas(DBBASE):
    """
    Used to store multiple social status
    """

    __tablename__ = "social_status_datas"
    __table_args__ = default_table_args
    __colanderalchemy_config__ = {
        "title": "un statut social",
    }
    # Columns
    id = Column(
        Integer,
        primary_key=True,
        info={
            "colanderalchemy": {
                "widget": deform.widget.HiddenWidget(),
                "missing": None,
            },
            "export": {"exclude": True},
        },
    )
    # Is the status relative to 'entry' or 'today'
    step = Column(
        String(15),
        info={
            "export": {
                "exclude": True,
                "stats": {
                    "exclude": False,
                    "label": "Entrée / actuel ?",
                    "options": (("today", "Actuel"), ("entry", "À l’entrée")),
                },
            }
        },
    )
    userdatas_id = Column(
        ForeignKey("user_datas.id"),
        info={
            "colanderalchemy": {"exclude": True},
            "export": {
                "label": "ID Gestion sociale",
                "stats": {"exclude": True},
            },
        },
    )
    social_status_id = Column(
        ForeignKey("social_status_option.id"),
        nullable=False,
        info={
            "colanderalchemy": {"title": "Statut social"},
            "export": {"exclude": True},
        },
    )
    # Relationships
    userdatas = relationship(
        "UserDatas",
        back_populates="social_statuses",
        info={"colanderalchemy": {"exclude": True}, "export": {"exclude": True}},
    )
    social_status = relationship(
        "SocialStatusOption",
        info={
            "colanderalchemy": get_excluded_colanderalchemy("Statut social"),
            "export": {
                "stats": {"label": "Statut social"},
                "related_key": "label",
            },
        },
    )


class BankAccountsDatas(DBBASE):
    """
    Datas related to user’s bank accounts
    """

    __colanderalchemy_config__ = {
        "title": "un compte bancaire",
    }
    __tablename__ = "userdatas_bank_accounts"
    __table_args__ = default_table_args
    id = Column(
        Integer,
        primary_key=True,
        info={
            "colanderalchemy": {
                "widget": deform.widget.HiddenWidget(),
                "missing": None,
            },
            "export": {"exclude": True},
        },
    )
    label = Column(
        String(250),
        info={
            "colanderalchemy": {
                "title": "Libellé du compte",
            }
        },
        nullable=False,
    )
    iban = Column(
        String(35),
        info={
            "colanderalchemy": {
                "title": "IBAN",
            }
        },
        nullable=False,
    )
    bic = Column(
        String(15),
        info={
            "colanderalchemy": {
                "title": "BIC",
            }
        },
        nullable=False,
    )
    userdatas_id = Column(
        ForeignKey("user_datas.id"),
        info={
            "colanderalchemy": {"exclude": True},
            "export": {
                "label": "ID Gestion sociale",
                "stats": {"exclude": True},
            },
        },
    )
    userdatas = relationship(
        "UserDatas",
        back_populates="statut_bank_accounts",
        info={"colanderalchemy": {"exclude": True}, "export": {"exclude": True}},
    )


class CareContractsDatas(DBBASE):
    """
    Used to store multiple care contracts
    """

    __tablename__ = "userdatas_care_contracts"
    __table_args__ = default_table_args
    __colanderalchemy_config__ = {
        "title": "un contrat",
    }
    id = Column(
        Integer,
        primary_key=True,
        info={
            "colanderalchemy": {
                "widget": deform.widget.HiddenWidget(),
                "missing": None,
            },
            "export": {"exclude": True},
        },
    )
    care_contract_id = Column(
        ForeignKey("care_contract_option.id"),
        nullable=False,
        info={
            "colanderalchemy": {"title": "Type de contrat"},
            "export": {"exclude": True},
        },
    )
    care_contract = relationship(
        "CareContractOption",
        info={
            "colanderalchemy": get_excluded_colanderalchemy("Type de contrat"),
            "export": {"related_key": "label"},
        },
    )
    details = Column(
        Text(),
        info={
            "colanderalchemy": {
                "title": "Détails du contrat",
            }
        },
        nullable=True,
    )
    date = Column(
        Date(),
        info={
            "colanderalchemy": {
                "title": "Date d’échéance",
            },
        },
        default=None,
    )
    userdatas_id = Column(
        ForeignKey("user_datas.id"),
        info={
            "colanderalchemy": {"exclude": True},
            "export": {
                "label": "ID Gestion sociale",
                "stats": {"exclude": True},
            },
        },
    )
    userdatas = relationship(
        "UserDatas",
        back_populates="activity_care_contracts",
        info={"colanderalchemy": {"exclude": True}, "export": {"exclude": True}},
    )


class AidOrganismsDatas(DBBASE):
    """
    Used to store multiple aid organisms
    """

    __tablename__ = "userdatas_aid_organisms"
    __table_args__ = default_table_args
    __colanderalchemy_config__ = {
        "title": "un organisme",
    }
    id = Column(
        Integer,
        primary_key=True,
        info={
            "colanderalchemy": {
                "widget": deform.widget.HiddenWidget(),
                "missing": None,
            },
            "export": {"exclude": True},
        },
    )
    aid_organism_id = Column(
        ForeignKey("aid_organism_option.id"),
        nullable=False,
        info={
            "colanderalchemy": {"title": "Organisme"},
            "export": {"exclude": True},
        },
    )
    aid_organism = relationship(
        "AidOrganismOption",
        info={
            "colanderalchemy": get_excluded_colanderalchemy("Organisme"),
            "export": {"related_key": "label"},
        },
    )
    details = Column(
        Text(),
        info={
            "colanderalchemy": {
                "title": "Détails de l’aide apportée",
                "description": "Numéro de dossier, contact, etc.",
            }
        },
        nullable=True,
    )
    date = Column(
        Date(),
        info={
            "colanderalchemy": {
                "title": "Date d’échéance",
            },
        },
        default=None,
    )
    userdatas_id = Column(
        ForeignKey("user_datas.id"),
        info={
            "colanderalchemy": {"exclude": True},
            "export": {
                "label": "ID Gestion sociale",
                "stats": {"exclude": True},
            },
        },
    )
    userdatas = relationship(
        "UserDatas",
        back_populates="statut_aid_organisms",
        info={"colanderalchemy": {"exclude": True}, "export": {"exclude": True}},
    )


def sync_userdatas_to_user(source_key, user_key):
    def handler(target, value, oldvalue, initiator):
        parentclass = initiator.parent_token.parent.class_
        if parentclass is UserDatas:
            if initiator.key == source_key:
                if hasattr(target, "user") and target.user is not None:
                    if value != oldvalue:
                        set_attribute(target.user, user_key, value, initiator)

    return handler


sync_firstname = sync_userdatas_to_user("coordonnees_firstname", "firstname")
sync_lastname = sync_userdatas_to_user("coordonnees_lastname", "lastname")
sync_email1 = sync_userdatas_to_user("coordonnees_email1", "email")


def start_listening():
    event.listen(
        UserDatas.coordonnees_firstname,
        "set",
        sync_firstname,
    )
    event.listen(
        UserDatas.coordonnees_lastname,
        "set",
        sync_lastname,
    )
    event.listen(
        UserDatas.coordonnees_email1,
        "set",
        sync_email1,
    )


def stop_listening():
    event.remove(
        UserDatas.coordonnees_firstname,
        "set",
        sync_firstname,
    )
    event.remove(
        UserDatas.coordonnees_lastname,
        "set",
        sync_lastname,
    )
    event.remove(
        UserDatas.coordonnees_email1,
        "set",
        sync_email1,
    )


SQLAListeners.register(start_listening, stop_listening)
