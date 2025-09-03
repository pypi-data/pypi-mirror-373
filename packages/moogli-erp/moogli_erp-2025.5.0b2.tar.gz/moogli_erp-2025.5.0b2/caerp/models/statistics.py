"""
Models related to statistics

- Sheets
  |- Entries
     |-Criterions


A sheet groups a number of statistics entries.
Each entry is compound of a list of criterions.
"""
import colander
import string
import random

from sqlalchemy import (
    Integer,
    String,
    Text,
    ForeignKey,
    Column,
    Date,
    Boolean,
)
from sqlalchemy.orm import (
    relationship,
)

from caerp_base.models.base import (
    DBBASE,
    default_table_args,
)
from caerp_base.models.mixins import (
    TimeStampedMixin,
)
from caerp_base.models.types import (
    JsonEncodedList,
    ACLType,
    MutableList,
)
from caerp import forms


class StatisticSheet(TimeStampedMixin, DBBASE):
    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    active = Column(Boolean(), default=True)
    _acl = Column(
        MutableList.as_mutable(ACLType),
    )
    entries = relationship("StatisticEntry", back_populates="sheet")

    def __json__(self, request):
        return dict(
            id=self.id,
            title=self.title or "Titre non renseigné",
            active=self.active,
        )

    def has_entry(self, entry_title):
        for entry in self.entries:
            if entry.title == entry_title:
                return True
        return False

    def duplicate(self):
        new_sheet = StatisticSheet(
            title="{0} {1}".format(
                self.title,
                "".join(
                    random.choice(string.ascii_uppercase + string.digits)
                    for _ in range(5)
                ),
            )
        )
        for entry in self.entries:
            new_sheet.entries.append(entry.duplicate())
        return new_sheet


class StatisticEntry(DBBASE):  # , PersistentACLMixin):
    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    description = Column(Text())
    _acl = Column(
        MutableList.as_mutable(ACLType),
    )
    sheet_id = Column(ForeignKey("statistic_sheet.id", ondelete="cascade"))
    sheet = relationship(
        "StatisticSheet",
        back_populates="entries",
    )
    criteria = relationship(
        "StatisticCriterion",
        primaryjoin="and_("
        "StatisticCriterion.entry_id == StatisticEntry.id,"
        "StatisticCriterion.parent_id == None"
        ")",
    )

    def __json__(self, request):
        return dict(
            id=self.id,
            title=self.title,
            description=self.description,
            sheet_id=self.sheet_id,
        )

    def duplicate(self, sheet_id=None):
        entry = StatisticEntry(title=self.title, description=self.description)
        if sheet_id:
            entry.sheet_id = sheet_id

        for criterion in self.criteria:
            entry.criteria.append(criterion.duplicate())
        return entry


class StatisticCriterion(DBBASE):
    """
    Statistic criterion
    :param str key: The key allows us to match the column we will build a query
    on through the inspector's columns dict (ex: 'coordonnees_lastname' or
    'activity_companydatas.name')
    :param str method: The search method (eq, lte, gt ...)
    :param str search1: The first value we search on
    :param str search2: The second value we search on (in case of range search)
    :param str searches: The list of value we will query on (in case of 'oneof'
    search)
    :param str type: string/number/manytoone/date says us which query generator
    we will use
    """

    __table_args__ = default_table_args

    id = Column(Integer, primary_key=True)
    key = Column(String(255))
    method = Column(String(25))
    # string / number / static_opt / onetomany / manytoone / and / or / date /
    # multidate
    type = Column(String(10))
    entry_id = Column(ForeignKey("statistic_entry.id", ondelete="cascade"))
    parent_id = Column(
        ForeignKey("statistic_criterion.id", ondelete="cascade"),
    )

    # Utilisé par les static_opt pour les ids d'options sur lesquelles on
    # filtre
    searches = Column(
        JsonEncodedList(),
        info={
            "colanderalchemy": {
                "typ": colander.List(),
            }
        },
    )
    # Utilisé pour filtre sur des nombres ou du texte
    search1 = Column(String(255), default="")
    search2 = Column(String(255), default="")
    # Utilisé pour filtrer sur un range de date
    date_search1 = Column(Date(), default=None)
    date_search2 = Column(Date(), default=None)

    children = relationship(
        "StatisticCriterion",
        primaryjoin="StatisticCriterion.id==StatisticCriterion.parent_id",
        info={"colanderalchemy": forms.EXCLUDED},
        back_populates="parent",
        cascade="all, delete",
        passive_deletes=True,
    )
    parent = relationship(
        "StatisticCriterion",
        remote_side=[id],
        back_populates="children",
        info={
            "colanderalchemy": forms.EXCLUDED,
        },
    )

    # Attribut statique utilisé pour différencier les types de critères
    # (complexes ou non)
    @property
    def complex(self):
        return self.type in ("or", "and", "onetomany")

    @property
    def root(self):
        return self.parent is None

    def __repr__(self):
        return "{0.__class__} type : {0.type} method : {0.method} parent_id : \
{0.parent_id}".format(
            self
        )

    def __json__(self, request):
        return dict(
            id=str(self.id),
            value=str(self.id),
            key=self.key,
            method=self.method,
            type=self.type,
            entry_id=self.entry_id,
            parent_id=self.parent_id,
            children=[
                criterion.__json__(request) for criterion in self.children
            ],  # We return the children criteria
            searches=self.searches,
            search1=self.search1,
            search2=self.search2,
            date_search1=self.date_search1,
            date_search2=self.date_search2,
        )

    def duplicate(self):
        return self.__class__(
            key=self.key,
            method=self.method,
            type=self.type,
            entry_id=self.entry_id,
            parent_id=self.parent_id,
            children=[
                criterion.duplicate() for criterion in self.children
            ],  # We return the children criteria
            searches=self.searches,
            search1=self.search1,
            search2=self.search2,
            date_search1=self.date_search1,
            date_search2=self.date_search2,
        )

    def has_parent(self, request=None):
        """
        Return True if the current criterion has a parent one
        """
        return self.parent_id is not None
