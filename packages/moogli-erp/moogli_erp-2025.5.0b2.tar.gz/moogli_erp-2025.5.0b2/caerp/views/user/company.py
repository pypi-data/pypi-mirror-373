import logging
from caerp.consts.permissions import PERMISSIONS
from pyramid.httpexceptions import HTTPFound

from caerp.models.company import Company

from caerp.utils.widgets import (
    Link,
    POSTButton,
)
from caerp.utils.strings import format_account
from caerp.forms.user.company import get_company_association_schema
from caerp.views import (
    BaseView,
    BaseFormView,
)
from caerp.views.company.tools import get_company_url


logger = logging.getLogger(__name__)


class UserCompaniesView(BaseView):
    """
    Collect datas for the company display view
    """

    title = "Enseignes de l'utilisateur"

    @property
    def current_user(self):
        return self.context

    def _stream_actions(self, item):
        """
        Stream actions available for the given item

        :param obj item: The company instance
        """
        yield Link(
            get_company_url(self.request, item),
            "Voir",
            title="Voir l’enseigne",
            icon="building",
            css="icon",
        )
        if self.request.has_permission(PERMISSIONS["context.edit_company"], item):
            yield Link(
                get_company_url(self.request, item, action="edit"),
                "Modifier",
                title="Modifier les informations relatives à l’enseigne",
                icon="pen",
                css="icon",
            )
        if self.request.has_permission(PERMISSIONS["global.create_company"]):
            if len(item.employees) > 1:
                yield POSTButton(
                    get_company_url(
                        self.request, item, action="remove", uid=self.current_user.id
                    ),
                    "Retirer",
                    title="Retirer l’entrepreneur de cette enseigne",
                    icon="lock",
                    css="icon",
                    confirm="{} n’aura plus accès aux données de cette "
                    "l’enseigne {}. Êtes-vous sûr de vouloir continuer "
                    "?".format(format_account(self.current_user), item.name),
                )

            if item.active:
                yield POSTButton(
                    get_company_url(self.request, item, action="disable"),
                    "Désactiver",
                    title="Désactiver cette enseigne",
                    icon="lock",
                    css="icon",
                    confirm="L’enseigne {} ne sera plus accessible et "
                    "n’apparaîtra plus dans les listes (factures, notes de "
                    "dépenses…). "
                    "Les comptes associés à cette enseigne seront désactivés."
                    " Êtes-vous sûr de vouloir continuer "
                    "?".format(item.name),
                )
            else:
                yield POSTButton(
                    get_company_url(self.request, item, action="disable"),
                    "Activer",
                    title="Ré-activer cette enseigne",
                    icon="lock-open",
                    css="icon",
                )

    def __call__(self):
        companies = self.current_user.companies
        return dict(
            title=self.title,
            companies=companies,
            user=self.current_user,
            stream_actions=self._stream_actions,
        )


class CompanyAssociationView(BaseFormView):
    """
    Associate a user with a company
    """

    title = "Associer un utilisateur à une ou plusieurs enseigne(s)"
    schema = get_company_association_schema()

    @property
    def current_user(self):
        return self.context

    def submit_success(self, appstruct):
        for name in appstruct.get("companies", []):
            company = Company.query().filter(Company.name == name).first()
            if company is not None and company not in self.current_user.companies:
                self.current_user.companies.append(company)
                self.request.dbsession.merge(self.current_user)

        url = self.request.route_path(
            "/users/{id}/companies",
            id=self.current_user.id,
        )
        return HTTPFound(url)


def add_routes(config):
    config.add_route(
        "/users/{id}/companies",
        "/users/{id}/companies",
        traverse="/users/{id}",
    )
    for action in ("associate",):
        config.add_route(
            "/users/{id}/companies/%s" % action,
            "/users/{id}/companies/%s" % action,
            traverse="/users/{id}",
        )


def add_views(config):
    config.add_view(
        UserCompaniesView,
        route_name="/users/{id}/companies",
        layout="user",
        permission=PERMISSIONS["global.company_view"],
        renderer="caerp:templates/user/companies.mako",
    )
    config.add_view(
        CompanyAssociationView,
        route_name="/users/{id}/companies/associate",
        renderer="caerp:templates/base/formpage.mako",
        permission=PERMISSIONS["global.create_company"],
        layout="default",
    )


def includeme(config):
    add_routes(config)
    add_views(config)
