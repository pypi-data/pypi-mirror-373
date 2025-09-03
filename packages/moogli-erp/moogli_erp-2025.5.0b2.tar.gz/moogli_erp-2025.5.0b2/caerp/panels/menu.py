"""
    Panels for the top main menus

    A common user has his company menu with customers, projects ...
    A manager or an admin has an admin menu and eventually a usermenu if he's
    consulting a company's account

    each user has his own menu with preferences, logout, holidays declaration
"""
import logging
from sqlalchemy import or_
from webhelpers2.html import tags
from webhelpers2.html import HTML
from caerp.models.company import Company
from caerp.models.services.user import UserPrefsService
from caerp.services.company import find_company_id_from_model
from caerp.utils.menu import HtmlAppMenuItem
from caerp.consts.permissions import PERMISSIONS

logger = logging.getLogger(__name__)


def get_current_company(request, submenu=False, is_user_company=True):
    """Extract the current company from the request

    - If already retrieved -> request.current_company
    - If company-context request → request.context
    - If non-admin and single-company → that company
    - If non-admin and multi-company and not a company-context request:
       → latest used company

    :param obj request: the pyramid request
    :param bool submenu: Do we ask this for the submenu ?
    """
    if request.dbsession.query(Company.id).count() == 1:
        return request.dbsession.query(Company).first()
    # Try to get the current company object from cache
    company = getattr(request, "current_company", None)
    if company is None:
        # Pas un manager et une seule enseigne
        if len(request.identity.active_companies) == 1 and not submenu:
            company = request.identity.active_companies[0]

        # On tente de récupérer l'enseigne depuis le contexte
        elif hasattr(request, "context"):
            cid = find_company_id_from_model(request, request.context)
            if cid is not None:  # case Workshops interne CAE
                company = Company.get(cid)

        # Pour les non admins qui ont plusieurs ensignes,
        # on stocke la last_used_company
        # pour afficher le menu même si on a pas pu la récupérer
        # depuis le contexte
        if not submenu:
            if company is not None:
                UserPrefsService.set(request, "last_used_company", company.id)
            else:
                cid = UserPrefsService.get(request, "last_used_company")
                if cid is not None:  # Prevent empty last_used_company
                    company = Company.get(cid)

            # fallback on prend la première qu'on trouve
            if company is None and len(request.identity.active_companies):
                company = request.identity.active_companies[0]

        # Place the current company in cache (only for the request's lifecycle)
        request.current_company = company
    return company


def get_companies(request, company=None):
    """
    Retrieve the companies the current user has access to

    :param obj request: The current pyramid request
    :param obj company: The current company
    :returns: The list of companies
    :rtype: list
    """
    companies = []
    if request.has_permission(PERMISSIONS["global.company_view"]):
        if company is not None:
            companies = (
                Company.label_datas_query(request)
                .filter(
                    or_(
                        Company.active == True,  # noqa: E712
                        Company.id == company.id,
                    )
                )
                .all()
            )
        else:
            companies = Company.label_datas_query(request, only_active=True).all()
    else:
        companies = request.identity.active_companies
    return companies


def get_company_menu(request, company, css=None, submenu=True, is_user_company=True):
    """
    Build the Company related menu
    """
    menu_builder = request.registry.company_menu
    menu = menu_builder.build(
        request,
        context=company,
        user_id=request.identity.id,
        company_id=company.id,
        submenu=submenu,
        is_user_company=is_user_company,
        company=company,
    )
    menu["css"] = css
    return menu


def get_admin_menus(request):
    """
    Build the admin menu
    """
    menu_builder = request.registry.admin_menu
    menu = menu_builder.build(request, user_id=request.identity.id)
    return menu


def company_choice(request, companies, current_company=None):
    """
    Add the company choose menu
    """
    from caerp.views.company.routes import ITEM_ROUTE as COMPANY_ROUTE

    options = tags.Options()
    options.add_option("Sélectionner une enseigne...", "/")
    for company_datas in companies:
        if request.context.__name__ == "company":
            url = request.current_route_path(id=company_datas.id)
        else:
            url = request.route_path(COMPANY_ROUTE, id=company_datas.id)
        if request.has_permission(PERMISSIONS["global.company_view"]):
            label = Company.format_label_from_datas(
                company_datas, with_select_search_datas=True
            )
        else:
            label = company_datas.name
        options.add_option(label, url)
    if current_company is not None:
        if request.context.__name__ == "company":
            default = request.current_route_path(id=current_company.id)
        else:
            default = request.route_path(COMPANY_ROUTE, id=current_company.id)
    else:
        default = request.current_route_path()
    html_attrs = {
        "class": "company-search",
        "id": "company-select-menu",
        "accesskey": "E",
        "style": "color: transparent;",  # avoid full label visibility while JS loading
    }
    html_code = HTML.li(tags.select("companies", default, options, **html_attrs))
    return HtmlAppMenuItem(html=html_code).build()


def get_usermenu(request):
    """
    Return the user menu (My account, holidays ...)
    """
    menu_builder = request.registry.user_menu
    return menu_builder.build(request, user_id=request.identity.id)


def menu_panel(context, request):
    """
    Top menu panel

    Build the top menu dict representation

    :rtype: dict
    """
    # If we've no user in the current request, we don't return anything
    if not request.identity:
        return {}

    menu = None
    if request.has_permission(PERMISSIONS["global.access_ea"]):
        menu = get_admin_menus(request)
    else:
        current_company = get_current_company(request)
        if current_company:
            menu = get_company_menu(request, current_company, submenu=False)
            companies = get_companies(request, current_company)
            # If there is more than 1 company accessible for the current user,
            # we provide a usefull dropdown menu
            if len(companies) > 1:
                menu["items"].insert(
                    0, company_choice(request, companies, current_company)
                )

    usermenu = get_usermenu(request)

    return {
        "menu": menu,
        "usermenu": usermenu,
    }


def submenu_panel(context, request):
    """
    Submenu panel, build a dict representation of the submenu, if one is
    expected

    :rtype: dict
    """
    # If we've no user in the current request, we don't return anything
    if not request.identity:
        return {}

    # There are no submenus for non admins
    if not request.has_permission(PERMISSIONS["global.access_ea"]):
        return {}

    current_company = get_current_company(request, submenu=True)
    if not current_company:
        submenu = {"items": [company_choice(request, get_companies(request))]}
        return {"submenu": submenu}

    is_user_company = current_company.employs(request.identity.id)
    submenu = get_company_menu(
        request,
        current_company,
        css="nav-pills",
        is_user_company=is_user_company,
    )
    if submenu:
        companies = get_companies(request, current_company)
        # If there is more than 1 company accessible for the current user,
        # we provide a usefull dropdown menu
        if len(companies) > 1:
            submenu["items"].insert(
                0, company_choice(request, companies, current_company)
            )
    return {"submenu": submenu}


def includeme(config):
    """
    Pyramid's inclusion mechanism
    """
    config.add_panel(
        menu_panel,
        "menu",
        renderer="/panels/menu.mako",
    )
    config.add_panel(
        submenu_panel,
        "submenu",
        renderer="/panels/menu.mako",
    )
