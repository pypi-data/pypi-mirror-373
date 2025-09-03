"""
    Models related to activities :

        Activity Types
        Activities
"""
import logging
import datetime
from beaker.cache import cache_region
from sqlalchemy import (
    Table,
    Integer,
    Column,
    ForeignKey,
    String,
    DateTime,
    Text,
    Boolean,
    distinct,
    func,
)
from sqlalchemy.orm import (
    deferred,
    relationship,
    backref,
)

from sqlalchemy.ext.associationproxy import association_proxy

from caerp_base.models.base import (
    DBBASE,
    DBSESSION,
    default_table_args,
)
from caerp.models.node import Node
from caerp.forms import EXCLUDED, get_hidden_field_conf


log = logging.getLogger(__name__)


# Statut des participants à un évènement
ATTENDANCE_STATUS = (
    (
        "registered",
        "Attendu",
    ),
    (
        "attended",
        "Présent",
    ),
    (
        "absent",
        "Absent",
    ),
    (
        "excused",
        "Excusé",
    ),
)

ATTENDANCE_STATUS_SEARCH = (
    (
        "",
        "Tous les rendez-vous",
    ),
    (
        "absent",
        "Un des participants était absent",
    ),
    (
        "excused",
        "Un des participants était excusé",
    ),
    (
        "attended",
        "Les participants étaient présents",
    ),
)

EVENT_SIGNUP_MODE = (
    ("closed", "Fermé (le gestionnaire gère les inscriptions)"),
    ("open", "Ouvert (les travailleurs de la CAE peuvent s'inscrire librement"),  # noqa
)

# Statut d'une activité
STATUS = (
    (
        "planned",
        "Planifié",
    ),
    (
        "closed",
        "Terminé",
    ),
    (
        "cancelled",
        "Annulé",
    ),
)

STATUS_SEARCH = (
    (
        "",
        "Tous les rendez-vous",
    ),
    (
        "planned",
        "Planifiés",
    ),
    (
        "closed",
        "Terminés",
    ),
    (
        "cancelled",
        "Annulés",
    ),
)


ACTIVITY_CONSEILLER = Table(
    "activity_conseiller",
    DBBASE.metadata,
    Column("activity_id", Integer, ForeignKey("activity.id")),
    Column("account_id", Integer, ForeignKey("accounts.id")),
    mysql_charset=default_table_args["mysql_charset"],
    mysql_engine=default_table_args["mysql_engine"],
)

ACTIVITY_COMPANY = Table(
    "activity_company_rel",
    DBBASE.metadata,
    Column("activity_id", Integer, ForeignKey("activity.id")),
    Column("company_id", Integer, ForeignKey("company.id")),
    mysql_charset=default_table_args["mysql_charset"],
    mysql_engine=default_table_args["mysql_engine"],
)


class Attendance(DBBASE):
    """
    Relationship table used to store the attendance of a user for a given
    event
    """

    __tablename__ = "attendance"
    __table_args__ = default_table_args
    account_id = Column(ForeignKey("accounts.id"), primary_key=True)
    event_id = Column(ForeignKey("event.id"), primary_key=True)
    status = Column(String(15), default="registered")

    event = relationship(
        "Event",
        backref=backref(
            "attendances",
            cascade="all, delete-orphan",
            info={
                "export": {"exclude": True},
            },
        ),
    )
    user = relationship(
        "User",
        backref=backref(
            "event_attendances",
            cascade="all, delete-orphan",
            info={"colanderalchemy": EXCLUDED, "export": {"exclude": True}},
        ),
        info={"colanderalchemy": EXCLUDED, "export": {"exclude": True}},
    )

    # Used as default creator function by the association_proxy
    def __init__(self, user=None, account_id=None, status=None, **kwargs):
        if user is not None:
            self.user = user
        if account_id is not None:
            self.account_id = account_id
        if status is not None:
            self.status = status

        for k, v in kwargs.items():
            setattr(self, k, v)

    def duplicate(self):
        attendance = Attendance(
            account_id=self.account_id,
        )
        return attendance


class Event(Node):
    """
    An event model
    """

    __tablename__ = "event"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "event"}
    id = Column(Integer, ForeignKey("node.id"), primary_key=True)
    datetime = Column(DateTime, default=datetime.datetime.now)
    status = Column(String(15), default="planned")
    signup_mode = Column(String(100), default="closed", nullable=False)

    owner_id = Column(
        ForeignKey("accounts.id"),
        info={
            "export": {"exclude": True},
        },
    )

    owner = relationship(
        "User",
        primaryjoin="Event.owner_id==User.id",
        backref=backref(
            "owned_events",
            info={
                "colanderalchemy": {"exclude": True},
                "export": {"exclude": True},
            },
        ),
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )

    participants = association_proxy("attendances", "user")

    # Waiting for a way to declare order_by clause in an association_proxy
    @property
    def sorted_participants(self):
        p = self.participants
        p = sorted(p, key=lambda u: u.lastname.lower())
        return p

    @property
    def sorted_attendances(self):
        attendances = self.attendances
        attendances = sorted(attendances, key=lambda att: att.user.lastname.lower())
        return attendances

    def user_status(self, user_id):
        """
        Return a user's status for this given timeslot

            user_id

                Id of the user we're asking the attendance status for
        """
        res = ""

        for attendance in self.attendances:
            if attendance.account_id == user_id:
                res = attendance.status
                break

        return dict(ATTENDANCE_STATUS).get(res, "Statut inconnu")

    def is_participant(self, user_id):
        """
        Return True if the user_id is one of a participant

            user_id

                Id of the user we're asking the information for
        """
        res = False

        for attendance in self.attendances:
            if attendance.account_id == user_id:
                res = True
                break

        return res


class Activity(Event):
    """
    An activity model
    """

    __tablename__ = "activity"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "activity"}
    id = Column(Integer, ForeignKey("event.id"), primary_key=True)
    type_id = Column(ForeignKey("activity_type.id"))
    action_id = Column(ForeignKey("activity_action.id"))
    subaction_id = Column(ForeignKey("activity_action.id"))
    mode = Column(String(100))
    # Libellé pour la sortie pdf
    # action_label = Column(String(125), default="")
    # subaction_label = Column(String(125), default="")
    # Champ text multiligne pour les activités
    point = deferred(Column(Text()), group="edit")
    objectifs = deferred(Column(Text()), group="edit")
    action = deferred(Column(Text()), group="edit")
    documents = deferred(Column(Text()), group="edit")
    notes = deferred(Column(Text()), group="edit")
    duration = deferred(Column(Integer, default=0), group="edit")

    type_object = relationship(
        "ActivityType",
        primaryjoin="Activity.type_id==ActivityType.id",
        uselist=False,
        foreign_keys=type_id,
    )
    conseillers = relationship(
        "User",
        secondary=ACTIVITY_CONSEILLER,
        backref=backref(
            "activities",
            order_by="Activity.datetime",
            info={"colanderalchemy": EXCLUDED, "export": EXCLUDED},
        ),
        info={"colanderalchemy": EXCLUDED, "export": EXCLUDED},
    )
    action_label_obj = relationship(
        "ActivityAction",
        primaryjoin="Activity.action_id==ActivityAction.id",
    )
    subaction_label_obj = relationship(
        "ActivityAction",
        primaryjoin="Activity.subaction_id==ActivityAction.id",
    )
    # PErmet de configurer des 'acl' pour permettre à d'autres personnes de
    # consulter les rendez-vous
    companies = relationship(
        "Company",
        secondary=ACTIVITY_COMPANY,
        backref=backref(
            "accompagnement_activities",
            order_by="Activity.datetime",
            info={"colanderalchemy": EXCLUDED, "export": EXCLUDED},
        ),
        info={"colanderalchemy": EXCLUDED, "export": EXCLUDED},
    )

    @property
    def action_label(self):
        if self.action_label_obj is not None:
            return self.action_label_obj.label
        else:
            return ""

    @property
    def subaction_label(self):
        if self.subaction_label_obj is not None:
            return self.subaction_label_obj.label
        else:
            return ""


class ActivityType(DBBASE):
    __colanderalchemy_config__ = {
        "title": "Natures des rendez-vous",
        # "description": "Mode d'entretiens",
        "seq_widget_options": {
            "add_subitem_text_template": "Ajouter une nature de rendez-vous",
        },
        "help_msg": "Configuration des natures de rendez-vous",
        "validation_msg": "Les natures de rendez-vous ont bien été configurées",
    }
    __tablename__ = "activity_type"
    __table_args__ = default_table_args
    id = Column(
        Integer,
        primary_key=True,
        info={"colanderalchemy": get_hidden_field_conf()},
    )
    label = Column(
        String(100),
        info={"colanderalchemy": {"title": "Libellé"}},
    )
    active = Column(
        Boolean(),
        default=True,
        info={"colanderalchemy": get_hidden_field_conf()},
    )
    order = Column(
        Integer,
        nullable=False,
        default=0,
        info={"colanderalchemy": get_hidden_field_conf()},
    )

    @classmethod
    def query(cls, *args):
        query = super(ActivityType, cls).query(*args)
        query = query.order_by("order")
        return query


class ActivityMode(DBBASE):
    __colanderalchemy_config__ = {
        "title": "Modes d'entretiens",
        # "description": "Mode d'entretiens",
        "seq_widget_options": {
            "add_subitem_text_template": "Ajouter un mode d'entretien",
        },
        "help_msg": "Configurer les modes de d'entretiens possibles pour les rendez-vous.",
        "validation_msg": "Les modes d'entretiens ont bien été configurés",
    }
    __tablename__ = "activity_modes"
    __table_args__ = default_table_args
    id = Column(
        Integer,
        primary_key=True,
        info={"colanderalchemy": get_hidden_field_conf()},
    )
    label = Column(
        String(100),
        info={"colanderalchemy": {"title": "Libellé"}},
    )
    order = Column(
        Integer,
        nullable=False,
        default=0,
        info={"colanderalchemy": get_hidden_field_conf()},
    )

    @classmethod
    def query(cls, *args):
        query = super(ActivityMode, cls).query(*args)
        query = query.order_by("order")
        return query


class ActivityAction(DBBASE):
    __tablename__ = "activity_action"
    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True)
    label = Column(String(255))
    active = Column(Boolean(), default=True)
    parent_id = Column(ForeignKey("activity_action.id"))
    children = relationship(
        "ActivityAction",
        primaryjoin="ActivityAction.id==ActivityAction.parent_id",
        backref=backref("parent", remote_side=[id]),
        cascade="all",
    )


# Usefull queries
def get_activity_years(kw=None):
    """
    Return a cached query for the years we have activities in database

    :param kw: is here only for API compatibility
    """

    @cache_region("long_term", "activityyears")
    def activityyears():
        activity_year = func.extract("YEAR", Activity.datetime)
        query = DBSESSION().query(distinct(activity_year)).order_by(activity_year)
        years = [year[0] for year in query]
        current = datetime.date.today().year
        if current not in years:
            years.append(current)
        return years

    return activityyears()
