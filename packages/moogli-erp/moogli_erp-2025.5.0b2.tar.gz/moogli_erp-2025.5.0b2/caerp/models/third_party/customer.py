"""
    Customer model
"""
import logging

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from caerp_base.models.base import default_table_args
from .third_party import ThirdParty
from caerp.models.project.project import ProjectCustomer
from caerp.models.project.mixins import BusinessMetricsMixin

from .services.customer import CustomerService

log = logging.getLogger(__name__)


class Customer(BusinessMetricsMixin, ThirdParty):
    """
    Customer model
    """

    __tablename__ = "customer"
    __table_args__ = default_table_args
    __mapper_args__ = {
        "polymorphic_identity": "customer",
    }
    _caerp_service = CustomerService
    fk_filter_field = "customer_id"  # BusinessMetricsMixin

    id = Column(
        ForeignKey("third_party.id"),
        primary_key=True,
        info={
            "colanderalchemy": {"exclude": True, "title": "Identifiant"},
        },
    )

    company = relationship(
        "Company",
        primaryjoin="Company.id==Customer.company_id",
        back_populates="customers",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )

    projects = relationship(
        "Project",
        back_populates="customers",
        secondary=ProjectCustomer,
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )

    estimations = relationship(
        "Estimation",
        primaryjoin="Estimation.customer_id==Customer.id",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )

    invoices = relationship(
        "Invoice",
        primaryjoin="Invoice.customer_id==Customer.id",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )

    cancelinvoices = relationship(
        "CancelInvoice",
        primaryjoin="CancelInvoice.customer_id==Customer.id",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )

    def has_tasks(self):
        return self._caerp_service.count_tasks(self) > 0

    def is_deletable(self):
        """
        Return True if this project could be deleted
        """
        return self.archived and not self.has_tasks()

    @classmethod
    def check_project_id(cls, customer_id, project_id):
        """
        Check if the project and the customer are linked

        :param int customer_id: The customer id
        :param int project_id: The project id
        :returns: True if the customer is attached to the project
        :rtype: bool
        """
        return cls._caerp_service.check_project_id(customer_id, project_id)

    def get_project_ids(self):
        return self._caerp_service.get_project_ids(self)

    def has_tva_on_margin_business(self):
        return self._caerp_service.has_tva_on_margin_business(self)

    def has_visible_businesses(self):
        """
        Return if the customer has at least one visible business
        """
        for project in self.projects:
            for business in project.businesses:
                if business.visible:
                    return True
        return False
