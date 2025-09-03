"""
    Holiday model used to store employee's holiday declaration
"""
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref

from caerp_base.models.base import (
    DBBASE,
    default_table_args,
)
from caerp.forms import EXCLUDED


class Holiday(DBBASE):
    """
    Holidays table
    Stores the start and end date for holiday declaration
    user_id
    start_date
    end_date
    """

    __tablename__ = "holiday"
    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True)
    user_id = Column("user_id", Integer, ForeignKey("accounts.id"))
    start_date = Column(Date)
    end_date = Column(Date)
    user = relationship(
        "User",
        backref=backref(
            "holidays",
            info={
                "colanderalchemy": EXCLUDED,
                "export": EXCLUDED,
            },
            order_by="Holiday.start_date",
        ),
        primaryjoin="Holiday.user_id==User.id",
    )

    def __json__(self, request):
        return dict(
            id=self.id,
            user_id=self.user_id,
            start_date=self.start_date,
            end_date=self.end_date,
        )
