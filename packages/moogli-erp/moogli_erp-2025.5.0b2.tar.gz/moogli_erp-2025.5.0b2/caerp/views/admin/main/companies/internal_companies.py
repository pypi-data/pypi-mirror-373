"""
View related to internal CAE companies
"""
import os

from pyramid.httpexceptions import HTTPFound

from caerp.consts.permissions import PERMISSIONS
from caerp_base.models.base import DBSESSION
from caerp.forms.admin.main.internal_companies import InternalCompaniesSchema
from caerp.models.company import Company
from caerp.views.admin.tools import (
    BaseAdminFormView,
)
from caerp.views.admin.main.companies import (
    MainCompaniesIndex,
    COMPANIES_INDEX_URL,
)

INTERNAL_COMPANIES_ROUTE = os.path.join(COMPANIES_INDEX_URL, "internal_companies")


class InternalCompaniesView(BaseAdminFormView):
    title = "Enseigne(s) interne(s) à la CAE"
    route_name = INTERNAL_COMPANIES_ROUTE
    schema = InternalCompaniesSchema()
    message = (
        "Facultatif, peut servir à regrouper des activités internes à la CAE. "
        + "Ces enseignes n’abritent donc pas l’activité des entrepreneurs."
    )

    def all_companies(self):
        """All companies, including disabled ones."""
        return DBSESSION.query(Company)

    def query(self):
        return self.all_companies().filter_by(internal=True)

    def before(self, form):
        companies = self.query()
        appstruct = {
            "companies": [i.id for i in companies],
        }
        form.set_appstruct(appstruct)

    def submit_success(self, appstruct):
        new_ids = [int(i) for i in appstruct.pop("companies", [])]
        old_ids = [int(company.id) for company in self.query()]

        removed_ids = set(old_ids) - set(new_ids)
        added_ids = set(new_ids) - set(old_ids)

        all_companies = self.all_companies()

        for company in all_companies.filter(Company.id.in_(added_ids)):
            company.internal = True
            DBSESSION().merge(company)

        for company in all_companies.filter(Company.id.in_(removed_ids)):
            company.internal = False
            DBSESSION().merge(company)

        self.request.session.flash("Les enseignes internes ont bien été enregistrées.")

        return HTTPFound(self.request.route_path(COMPANIES_INDEX_URL))


def includeme(config):
    config.add_route(INTERNAL_COMPANIES_ROUTE, INTERNAL_COMPANIES_ROUTE),
    config.add_admin_view(
        InternalCompaniesView,
        parent=MainCompaniesIndex,
        permission=PERMISSIONS["global.config_company"],
    )
