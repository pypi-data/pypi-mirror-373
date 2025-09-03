import logging
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Text,
    String,
    func,
)
from sqlalchemy.orm import (
    relationship,
)

from caerp.models.company import Company
from caerp_base.models.base import (
    DBBASE,
    default_table_args,
)


logger = logging.getLogger(__name__)


class SaleProductCategory(DBBASE):
    """
    A product category allowing to group products
    """

    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True)
    title = Column(
        String(255), nullable=False, info={"colanderalchemy": {"title": "Titre"}}
    )
    description = Column(Text(), default="")
    company_id = Column(
        ForeignKey("company.id", ondelete="CASCADE"),
        info={
            "export": {"exclude": True},
        },
    )
    company = relationship(
        "Company",
        info={
            "export": {"exclude": True},
        },
    )

    @classmethod
    def get_by_title(
        cls, title: str, company: Company, case_sensitive: bool = True
    ) -> Optional["SaleProductCategory"]:
        """
        Exact match will always be preferred.
        """
        query = cls.query().filter(SaleProductCategory.company == company)
        exact_match = query.filter(SaleProductCategory.title == title).one_or_none()

        if exact_match or case_sensitive:
            return exact_match
        else:
            insensitive_match = query.filter(
                func.lower(SaleProductCategory.title) == func.lower(title)
            ).one_or_none()
            return insensitive_match

    def __json__(self, request):
        """
        Json repr of our model
        """
        return dict(
            id=self.id,
            title=self.title,
            description=self.description,
            company_id=self.company_id,
        )
