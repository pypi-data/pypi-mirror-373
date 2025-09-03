"""
Base tools for administrable options
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
)
from sqlalchemy.util import classproperty
from sqlalchemy.sql.expression import func

from caerp.utils.ascii import camel_case_to_name
from caerp_base.models.base import (
    DBBASE,
    default_table_args,
    DBSESSION,
)
from caerp.forms import (
    get_hidden_field_conf,
    EXCLUDED,
)


class ConfigurableOption(DBBASE):
    """
    Base class for options
    """

    __table_args__ = default_table_args
    id = Column(
        Integer, primary_key=True, info={"colanderalchemy": get_hidden_field_conf()}
    )
    label = Column(
        String(200),
        info={"colanderalchemy": {"title": "Libellé"}},
        nullable=False,
    )
    active = Column(Boolean(), default=True, info={"colanderalchemy": EXCLUDED})
    order = Column(
        Integer, default=0, info={"colanderalchemy": get_hidden_field_conf()}
    )
    type_ = Column(
        "type_", String(30), nullable=False, info={"colanderalchemy": EXCLUDED}
    )

    @classproperty
    def __mapper_args__(cls):
        name = cls.__name__
        if name == "ConfigurableOption":
            return {
                "polymorphic_on": "type_",
                "polymorphic_identity": "configurable_option",
            }
        else:
            return {"polymorphic_identity": camel_case_to_name(name)}

    @classmethod
    def query(cls, *args):
        query = super(ConfigurableOption, cls).query(*args)
        query = query.filter(ConfigurableOption.active == True)
        query = query.order_by(ConfigurableOption.order)
        return query

    def __json__(self, request):
        return dict(
            id=self.id,
            label=self.label,
            active=self.active,
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
    def get_next_order(cls):
        """
        :returns: The next available order
        :rtype: int
        """
        query = DBSESSION().query(func.max(cls.order)).filter_by(active=True)
        query = query.filter_by(type_=cls.__mapper_args__["polymorphic_identity"])
        query = query.first()
        if query is not None and query[0] is not None:
            result = query[0] + 1
        else:
            result = 0
        return result

    @classmethod
    def _query_active_items(cls):
        """
        Build a query to collect active items of the current class

        :rtype: :class:`sqlalchemy.Query`
        """
        return (
            DBSESSION()
            .query(cls)
            .filter_by(type_=cls.__mapper_args__["polymorphic_identity"])
            .filter_by(active=True)
        )

    @classmethod
    def insert(cls, item, new_order):
        """
        Place the item at the given index

        :param obj item: The item to move
        :param int new_order: The new index of the item
        """
        query = cls._query_active_items()
        items = query.filter(cls.id != item.id).order_by(cls.order).all()

        items.insert(new_order, item)

        for index, item in enumerate(items):
            item.order = index
            DBSESSION().merge(item)

    @classmethod
    def reorder(cls):
        """
        Regenerate order attributes
        """
        items = cls._query_active_items().order_by(cls.order).all()

        for index, item in enumerate(items):
            item.order = index
            DBSESSION().merge(item)


def get_id_foreignkey_col(foreignkey_str):
    """
    Return an id column as a foreignkey with correct colander configuration

        foreignkey_str

            The foreignkey our id is pointing to
    """
    column = Column(
        "id",
        Integer,
        ForeignKey(foreignkey_str),
        primary_key=True,
        info={"colanderalchemy": get_hidden_field_conf()},
    )
    return column
