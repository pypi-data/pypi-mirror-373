import datetime
import logging

import colander
from sqlalchemy import extract
from sqlalchemy.orm import contains_eager, load_only

from caerp.consts.permissions import PERMISSIONS
from caerp.forms.tasks.estimation import get_list_schema
from caerp.models.company import Company
from caerp.models.task import Estimation, Task
from caerp.models.third_party.customer import Customer
from caerp.utils.widgets import Link
from caerp.views import BaseListView
from caerp.views.company.routes import (
    COMPANY_ESTIMATION_ADD_ROUTE,
    COMPANY_ESTIMATIONS_ROUTE,
)

from .routes import ESTIMATION_COLLECTION_ROUTE, ESTIMATION_ITEM_ROUTE

logger = logging.getLogger(__name__)


class GlobalEstimationListTools:
    """
    Schema and filters related to GlobalEstimationList
    """

    is_global = True
    excluded_fields = "status,"

    def get_schema(self):
        return get_list_schema(
            self.request, is_global=self.is_global, excludes=self.excluded_fields
        )

    def _get_company_id(self, appstruct):
        raise NotImplementedError()

    def filter_date(self, query, appstruct):
        period = appstruct.get("period", {})
        if period.get("start") not in (colander.null, None):
            start = period.get("start")
            end = period.get("end")
            if end in (None, colander.null):
                end = datetime.date.today()
            logger.debug(f"  + Filtering by period : {start} -> {end}")
            query = query.filter(Task.date.between(start, end))
        else:
            year = appstruct.get("year")
            if year not in (None, colander.null, -1):
                logger.debug(f"  + Filtering by year : {year}")
                query = query.filter(extract("year", Estimation.date) == year)
        return query

    def filter_ttc(self, query, appstruct):
        ttc = appstruct.get("ttc", {})
        if ttc.get("start") not in (None, colander.null):
            logger.info("  + Filtering by ttc amount : %s" % ttc)
            start = ttc.get("start")
            end = ttc.get("end")
            if end in (None, colander.null):
                query = query.filter(Estimation.ttc >= start)
            else:
                query = query.filter(Estimation.ttc.between(start, end))
        return query

    def filter_company(self, query, appstruct):
        company_id = self._get_company_id(appstruct)
        if company_id not in (None, colander.null):
            logger.info("  + Filtering on the company id : %s" % company_id)
            query = query.filter(Task.company_id == company_id)
        return query

    def filter_customer(self, query, appstruct):
        """
        filter estimations by customer
        """
        customer_id = appstruct.get("customer_id")
        if customer_id not in (None, colander.null):
            logger.info("  + Filtering on the customer id : %s" % customer_id)
            query = query.filter(Estimation.customer_id == customer_id)
        return query

    def filter_signed_status(self, query, appstruct):
        """
        Filter estimations by signed status
        """
        status = appstruct["signed_status"]
        logger.info("  + Signed status filtering : %s" % status)
        if status == "geninv":
            query = query.filter(Estimation.geninv == True)  # noqa: E712
        elif status == "noinv":
            query = query.filter(Estimation.geninv == False)
            query = query.filter(Estimation.signed_status == "signed")
        elif status != "all":
            query = query.filter(Estimation.signed_status == status)

        return query

    def filter_status(self, query, appstruct):
        """
        Filter the estimations by status
        """
        query = query.filter(Estimation.status == "valid")
        return query

    def filter_doctype(self, query, appstruct):
        """
        Filter the estimations by doc types
        """
        type_ = appstruct.get("doctype")
        if type_ != "both":
            query = query.filter(Estimation.type_ == type_)
        return query

    def filter_auto_validated(self, query, appstruct):
        """
        Filter the estimations by doc types
        """
        auto_validated = appstruct.get("auto_validated")
        if auto_validated:
            query = query.filter(Estimation.auto_validated == 1)
        return query

    def filter_business_type_id(self, query, appstruct):
        business_type_id = appstruct.get("business_type_id")
        if business_type_id not in ("all", None):
            query = query.filter(Estimation.business_type_id == business_type_id)
        return query

    def filter_internal_number(self, query, appstruct):
        number = appstruct.get("search")
        if number:
            logger.debug("    Filtering by official_number : %s" % number)
            query = query.filter(Task.internal_number.like("%" + number + "%"))
        return query


class GlobalEstimationList(GlobalEstimationListTools, BaseListView):
    title = "Devis de la CAE"
    add_template_vars = (
        "title",
        "is_admin",
        "with_draft",
        "stream_main_actions",
        "stream_more_actions",
    )
    sort_columns = dict(
        date=Estimation.date,
        customer=Customer.label,
        company=Company.name,
    )
    default_sort = "date"
    default_direction = "desc"
    is_admin = True
    with_draft = False

    def query(self):
        query = self.request.dbsession.query(Estimation)
        query = query.outerjoin(Task.company)
        query = query.outerjoin(Task.customer)
        query = query.options(
            contains_eager(Task.customer).load_only(
                Customer.id,
                Customer.label,
            )
        )
        query = query.options(
            contains_eager(Task.company).load_only(Company.id, Company.name)
        )
        query = query.options(
            load_only(
                "name",
                "internal_number",
                "status",
                Estimation.signed_status,
                Estimation.geninv,
                "date",
                "description",
                "ht",
                "tva",
                "ttc",
            )
        )
        return query

    def _get_company_id(self, appstruct):
        return appstruct.get("company_id")

    def stream_actions(self, document):
        return [
            Link(
                self.request.route_path(ESTIMATION_ITEM_ROUTE, id=document.id),
                "Voir",
                title="Voir ce devis",
                icon="arrow-right",
                css="btn icon only",
            ),
            Link(
                self.request.route_path("/estimations/{id}.pdf", id=document.id),
                "Télécharger la version PDF",
                title="Télécharger la version PDF",
                icon="file-pdf",
                css="btn icon only",
            ),
        ]

    def get_export_path(self, extension, details=False):
        return self.request.route_path(
            "estimations{}_export".format("_details" if details else ""),
            extension=extension,
            _query=self.request.GET,
        )

    def stream_main_actions(self):
        return []

    def stream_more_actions(self):
        yield Link(
            self.get_export_path(extension="xls"),
            icon="file-excel",
            label="Liste des devis (Excel)",
            css="btn icon_only mobile",
            popup=True,
            title="Générer un export excel des devis de la liste",
        )
        yield Link(
            self.get_export_path(extension="ods"),
            icon="file-spreadsheet",
            label="Liste des devis (ODS)",
            css="btn icon_only mobile",
            popup=True,
            title="Générer un export ODS des devis de la liste",
        )
        yield Link(
            self.get_export_path(extension="csv"),
            icon="file-csv",
            label="Liste des devis (CSV)",
            css="btn icon_only mobile",
            popup=True,
            title="Générer un export CSV des devis de la liste",
        )
        yield Link(
            self.get_export_path(extension="xls", details=True),
            icon="file-excel",
            label="Détail des devis (Excel)",
            css="btn icon_only mobile",
            popup=True,
            title="Générer un export excel du détail des devis de la liste",
        )
        yield Link(
            self.get_export_path(extension="ods", details=True),
            icon="file-spreadsheet",
            label="Détail des devis (ODS)",
            css="btn icon_only mobile",
            popup=True,
            title="Générer un export ODS du détail des devis de la liste",
        )
        yield Link(
            self.get_export_path(extension="csv", details=True),
            icon="file-csv",
            label="Détail des devis (CSV)",
            css="btn icon_only mobile",
            popup=True,
            title="Générer un export CSV du détail des devis de la liste",
        )


class CompanyEstimationList(GlobalEstimationList):
    is_admin = False
    is_global = False
    excluded_fields = ("auto_validated",)
    with_draft = True

    @property
    def title(self):
        return "Devis de l'enseigne {0}".format(self.request.context.name)

    def _get_company_id(self, appstruct=None):
        """
        Return the current context's company id
        """
        return self.request.context.id

    def get_export_path(self, extension, details=False):
        return self.request.route_path(
            "company_estimations{}_export".format("_details" if details else ""),
            id=self._get_company_id(),
            extension=extension,
            _query=self.request.GET,
        )

    def filter_status(self, query, appstruct):
        """
        Filter the estimations by status
        """
        status = appstruct.get("status", "all")
        logger.info("  + Status filtering : %s" % status)
        if status != "all":
            query = query.filter(Estimation.status == status)

        return query

    def stream_main_actions(self):
        result = []
        if self.request.has_permission(PERMISSIONS["context.add_estimation"]):
            result.append(
                Link(
                    self.request.route_path(
                        COMPANY_ESTIMATION_ADD_ROUTE, id=self.context.id
                    ),
                    "Ajouter un devis",
                    icon="plus",
                    css="icon btn-primary",
                )
            )
        return result


def add_views(config):
    """
    Add the views defined in this module
    """
    # Estimation list related views
    config.add_view(
        GlobalEstimationList,
        route_name=ESTIMATION_COLLECTION_ROUTE,
        renderer="estimations.mako",
        permission=PERMISSIONS["global.list_estimations"],
    )
    config.add_view(
        CompanyEstimationList,
        route_name=COMPANY_ESTIMATIONS_ROUTE,
        renderer="estimations.mako",
        permission=PERMISSIONS["company.view"],
    )


def includeme(config):
    add_views(config)
    config.add_admin_menu(
        parent="sale",
        order=0,
        label="Devis",
        href=ESTIMATION_COLLECTION_ROUTE,
        permission=PERMISSIONS["global.list_estimations"],
    )
    config.add_company_menu(
        parent="sale",
        order=1,
        label="Devis",
        route_name=COMPANY_ESTIMATIONS_ROUTE,
        route_id_key="company_id",
    )
