"""
Fiche formateur

Extension du module User qui vient rajouter la possibilité de stocker des
informations sur les formateurs
"""
from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Text,
    Boolean,
)
from sqlalchemy.orm import (
    relationship,
)

from caerp_base.models.base import (
    default_table_args,
)
from caerp.models.node import Node
from caerp.models.tools import get_excluded_colanderalchemy


class TrainerDatas(Node):
    __tablename__ = "trainer_datas"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "trainerdata"}

    id = Column(
        ForeignKey("node.id"),
        primary_key=True,
        info={
            "colanderalchemy": {"exclude": True, "title": "ID Formateur"},
        },
    )

    # User account associated with this dataset
    user_id = Column(
        ForeignKey("accounts.id", ondelete="cascade"),
        info={
            "export": {"exclude": True},
        },
    )
    user = relationship(
        "User",
        primaryjoin="User.id==TrainerDatas.user_id",
        info={
            "colanderalchemy": get_excluded_colanderalchemy("Compte utilisateur"),
            "export": {"exclude": True},
        },
    )

    # Profil professionnel
    specialty = Column(
        Text(),
        info={
            "colanderalchemy": {
                "title": "Spécialité",
                "description": "Votre spécialité - Votre cœur de métier, \
champ de compétence et domaines d'expertise (3 lignes au maximum)",
                "section": "Profil Professionnel",
            }
        },
    )
    linkedin = Column(
        String(255),
        info={
            "colanderalchemy": {
                "title": "Réseau Sociaux - Adresse du profil linkedin",
                "section": "Profil Professionnel",
            }
        },
    )
    viadeo = Column(
        String(255),
        info={
            "colanderalchemy": {
                "title": "Réseau Sociaux - Adresse du profil Viadeo",
                "section": "Profil Professionnel",
            }
        },
    )
    career = Column(
        Text(),
        info={
            "colanderalchemy": {
                "title": "Votre parcours professionnel en 3 dates ou périodes",
                "description": "Par exemple pour date : en 1991 - Par \
exemple pour période : de 1991 à 1995",
                "section": "Profil Professionnel",
            }
        },
    )
    qualifications = Column(
        Text(),
        info={
            "colanderalchemy": {
                "title": "Votre qualification ou/et diplôme le plus pertinent",
                "description": "2 lignes maximum",
                "section": "Profil Professionnel",
            }
        },
    )
    background = Column(
        Text(),
        info={
            "colanderalchemy": {
                "title": "Votre formation de formateur",
                "section": "Profil Professionnel",
            }
        },
    )
    references = Column(
        Text(),
        info={
            "colanderalchemy": {
                "title": "Vos références de missions de formation effectuées",
                "description": "5 références maximum en mentionnant nom du \
client, contexte de l'intervention, année",
                "section": "Profil Professionnel",
            }
        },
    )
    # Section "Concernant votre activité de formation"
    motivation = Column(
        Text(),
        info={
            "colanderalchemy": {
                "title": "Quelle est votre motivation, pourquoi faites-vous \
de la formation ?",
                "description": "3 lignes maximum",
                "section": "Concernant votre activité de formation",
            }
        },
    )
    approach = Column(
        Text(),
        info={
            "colanderalchemy": {
                "title": "Concernant votre activité de formation",
                "description": "3 lignes maximum, ne pas entrer dans la \
méthodologie",
                "section": "Concernant votre activité de formation",
            }
        },
    )
    active = Column(
        Boolean(),
        info={
            "colanderalchemy": {
                "title": "Fiche active ?",
                "description": "Cette fiche formateur est-elle active ?",
            }
        },
    )
