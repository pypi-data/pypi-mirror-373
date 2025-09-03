"""
Competence evaluation module

1- Choose a deadline (if manager choose also a contractor)
2- Fill the displayed grid
3- Display a printable version
"""
import logging
import colander
from pyramid.httpexceptions import HTTPFound
from sqlalchemy import func

from colanderalchemy import SQLAlchemySchemaNode

from caerp.consts.permissions import PERMISSIONS
from caerp.models.user.user import User
from caerp.utils import widgets
from caerp.forms.user import (
    get_users_options,
)
from caerp.models.competence import (
    CompetenceDeadline,
    CompetenceScale,
    CompetenceOption,
    CompetenceGrid,
    CompetenceGridItem,
    CompetenceGridSubItem,
)
from caerp.resources import (
    competence_js,
    competence_radar_js,
)
from caerp.forms.competence import CompetenceGridQuerySchema
from caerp.views import (
    BaseView,
    BaseRestView,
)


logger = logging.getLogger(__name__)


def get_competence_grid(request, contractor_id, deadline_id):
    """
    Return a competence grid record for the given user and deadline
    """
    query = CompetenceGrid.query()
    query = query.filter_by(
        contractor_id=contractor_id,
        deadline_id=deadline_id,
    )

    grid = query.first()
    options = CompetenceOption.query()

    if grid is None:
        grid = CompetenceGrid(
            contractor_id=contractor_id,
            deadline_id=deadline_id,
        )

        request.dbsession.add(grid)

    for option in options:
        grid.ensure_item(option)

    return grid


def redirect_to_competence_grid(request, appstruct):
    """
    Redirect to the appropriate competence grid
    """
    # On récupère l'id du user pour l'évaluation
    contractor_id = appstruct["contractor_id"]
    # L'id de la période d'évaluation
    deadline_id = appstruct["deadline"]
    # On redirige vers la page appropriée
    grid = get_competence_grid(request, contractor_id, deadline_id)
    url = request.route_path("competence_grid", id=grid.id)
    return HTTPFound(url)


def validate_competence_grid_query(request):
    """
    Validate datas posted to access a competence grid

    :param obj request: The pyramid request
    """
    schema = CompetenceGridQuerySchema.bind(request=request)
    try:
        appstruct = schema.deserialize(request.POST)
    except colander.Invalid:
        logger.exception(
            "Erreur dans le routage de la page de \
compétences : POSSIBLE BREAK IN ATTEMPT"
        )
    else:
        return appstruct
    return None


def competence_index_view(context, request):
    """
    Index view to go to a competence grid

    Both admin and user view

    :param obj request: The pyramid request
    """
    competence_js.need()
    # Don't return list of users to the template if we come here through the
    # user menu
    if not request.has_permission(PERMISSIONS["global.manage_competence"]):
        user_options = []
    else:
        user_options = get_users_options()

    deadlines = CompetenceDeadline.query().all()
    if "deadline" in request.POST:
        logger.debug(request.POST)
        appstruct = validate_competence_grid_query(request)
        if appstruct is not None:
            return redirect_to_competence_grid(request, appstruct)

    return {
        "title": "Évaluation des compétences",
        "user_options": user_options,
        "deadlines": deadlines,
    }


def competence_grid_view(context, request):
    """
    The competence grid base view
    """
    request.actionmenu.add(
        widgets.ViewLink(
            "Page précédente",
            "global.manage_competence",
            path="competences",
        )
    )
    competence_js.need()
    # loadurl : The url to load the options
    loadurl = request.route_path(
        "competence_grid",
        id=context.id,
        _query=dict(action="options"),
    )
    # contexturl : The url to load datas about the context in json format
    contexturl = request.current_route_path()

    title = "Évaluation des compétences de {0} pour l’échéance « {1} »".format(
        context.contractor.label, context.deadline.label
    )

    return {"title": title, "loadurl": loadurl, "contexturl": contexturl}


def competence_form_options(context, request):
    """
    Returns datas used to build the competence form page
    """
    return dict(
        grid=context,
        grid_edit_url=request.route_path(
            "competence_grid", id=context.id, _query=dict(action="edit")
        ),
        item_root_url=request.route_path(
            "competence_grid_items",
            id=context.id,
        ),
        deadlines=CompetenceDeadline.query().all(),
        scales=CompetenceScale.query().all(),
    )


def competence_radar_chart_view(context, request):
    """
    Competence radar chart view

    :param obj context: a user model
    """
    request.actionmenu.add(
        widgets.ViewLink(
            "Revenir au formulaire",
            "context.view_competence",
            path="competence_grid",
            id=context.id,
        )
    )
    competence_radar_js.need()
    loadurl = request.route_path(
        "competence_grid",
        id=context.id,
        _query=dict(action="radar"),
    )
    title = f"Profil des compétences entrepreneuriales {context.deadline.label}"

    grids = []
    # On récupère les grilles de compétences précédent la courant
    deadlines = CompetenceDeadline.query()
    deadlines = deadlines.filter(
        CompetenceDeadline.order <= context.deadline.order
    ).all()
    scales = CompetenceScale.query().all()
    for deadline in deadlines:
        grid = get_competence_grid(request, context.contractor_id, deadline.id)
        grids.append(grid)

    return dict(
        title=title,
        loadurl=loadurl,
        grids=grids,
        deadlines=deadlines,
        scales=scales,
    )


def competence_radar_chart_datas(context, request):
    """
    Return the datas used to show a radar / spider chart of a user's
    competences
    context : CompetenceGrid
    """
    datas = []
    legend = []

    deadlines = CompetenceDeadline.query()
    deadlines = deadlines.filter(CompetenceDeadline.order <= context.deadline.order)
    for deadline in deadlines:
        grid = get_competence_grid(request, context.contractor_id, deadline.id)
        datas.append(grid.__radar_datas__())
        legend.append("Profil {0}".format(deadline.label))

    datas.append(CompetenceOption.__radar_datas__(context.deadline_id))
    legend.append("Profil de référence")

    config = {}
    config["levels"] = CompetenceScale.query().count()
    max_value = request.dbsession.query(func.max(CompetenceScale.value)).all()[0][0]

    config["maxValue"] = max_value

    return {"datas": datas, "legend": legend, "config": config}


class RestCompetenceGrid(BaseView):
    """
    Json api for competence grid handling
    """

    def get(self):
        return {
            "grid": self.context,
            "items": [item for item in self.context.items if item.option.active],
        }


class RestCompetenceGridItem(BaseRestView):
    """
    Rest view for Item handling

    Provides :

        * get collection
        * edit element
    """

    @property
    def schema(self):
        return SQLAlchemySchemaNode(CompetenceGridItem, includes=("progress", "id"))

    def collection_get(self):
        """
        Return list of items for a given grid
        context is a grid
        """
        return self.context.items


class RestCompetenceGridSubItem(BaseRestView):
    """
    Rest view for Sub item handling:

    Provides:

        * get collection
        * edit element
    """

    @property
    def schema(self):
        return SQLAlchemySchemaNode(
            CompetenceGridSubItem,
            includes=(
                "evaluation",
                "id",
                "comments",
            ),
        )

    def collection_get(self):
        """
        Return list of subitems for a given item
        context is an item
        """
        return self.context.subitems


def add_routes(config):
    """
    Add module related routes
    """
    config.add_route("competences", "/competences")
    config.add_route(
        "user_competences",
        "/users/{id}/competences/",
        traverse="/users/{id}",
    )
    config.add_route(
        "competence_grid",
        "/competences/{id}",
        traverse="/competences/{id}",
    )

    config.add_route(
        "competence_grid_items",
        "/competences/{id}/items",
        traverse="/competences/{id}",
    )

    config.add_route(
        "competence_grid_item",
        "/competences/{id}/items/{iid:\d+}",
        traverse="/competence_items/{iid}",
    )

    config.add_route(
        "competence_grid_subitems",
        "/competences/{id}/items/{iid:\d+}/subitems",
        traverse="/competence_items/{iid}",
    )

    config.add_route(
        "competence_grid_subitem",
        "/competences/{id}/items/{iid:\d+}/subitems/{sid:\d+}",
        traverse="/competence_subitems/{sid}",
    )


def includeme(config):
    """
    Pyramid's inclusion mechanism
    """

    def add_json_view(obj, **kw):
        kw["renderer"] = "json"
        kw["xhr"] = True
        kw.setdefault("permission", PERMISSIONS["context.edit_competence"])
        config.add_view(obj, **kw)

    add_routes(config)
    # Same view for user and admin but with different routes and permissions
    config.add_view(
        competence_index_view,
        route_name="competences",
        renderer="/accompagnement/competences.mako",
        permission=PERMISSIONS["global.manage_competence"],
    )

    config.add_view(
        competence_index_view,
        route_name="user_competences",
        renderer="/accompagnement/competences.mako",
        context=User,
        permission=PERMISSIONS["context.list_competences"],
    )

    config.add_view(
        competence_grid_view,
        route_name="competence_grid",
        renderer="/accompagnement/competence.mako",
        context=CompetenceGrid,
        permission=PERMISSIONS["context.edit_competence"],
    )
    config.add_view(
        competence_radar_chart_view,
        route_name="competence_grid",
        renderer="/accompagnement/competence_resume.mako",
        request_param="action=radar",
        context=CompetenceGrid,
        permission=PERMISSIONS["context.view_competence"],
    )

    add_json_view(
        RestCompetenceGrid,
        attr="get",
        route_name="competence_grid",
        request_method="GET",
        context=CompetenceGrid,
        permission=PERMISSIONS["context.view_competence"],
    )

    add_json_view(
        RestCompetenceGridItem,
        attr="collection_get",
        route_name="competence_grid_items",
        request_method="GET",
        context=CompetenceGridItem,
        permission=PERMISSIONS["context.view_competence"],
    )

    add_json_view(
        RestCompetenceGridSubItem,
        attr="collection_get",
        route_name="competence_grid_subitems",
        request_method="GET",
        context=CompetenceGridItem,
        permission=PERMISSIONS["context.view_competence"],
    )

    add_json_view(
        RestCompetenceGridItem,
        attr="put",
        route_name="competence_grid_item",
        request_method="PUT",
        context=CompetenceGridItem,
        permission=PERMISSIONS["context.edit_competence"],
    )

    add_json_view(
        RestCompetenceGridSubItem,
        attr="put",
        route_name="competence_grid_subitem",
        request_method="PUT",
        context=CompetenceGridSubItem,
        permission=PERMISSIONS["context.edit_competence"],
    )

    add_json_view(
        competence_form_options,
        route_name="competence_grid",
        request_method="GET",
        request_param="action=options",
        context=CompetenceGrid,
        permission=PERMISSIONS["context.view_competence"],
    )
    add_json_view(
        competence_radar_chart_datas,
        route_name="competence_grid",
        request_param="action=radar",
        context=CompetenceGrid,
        permission=PERMISSIONS["context.view_competence"],
    )

    config.add_admin_menu(
        parent="accompagnement",
        order=3,
        label="Compétences",
        href="/competences",
        permission=PERMISSIONS["global.manage_competence"],
    )

    def deferred_is_user_company(self, kw):
        return kw["is_user_company"]

    config.add_company_menu(
        parent="accompagnement",
        order=3,
        label="Compétences",
        route_name="user_competences",
        route_id_key="user_id",
        permission=deferred_is_user_company,
    )
