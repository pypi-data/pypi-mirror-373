import datetime

from paginate_sqlalchemy import SqlalchemyOrmPage
from sqlalchemy import or_

from caerp import resources
from caerp.models.activity import Attendance
from caerp.models.workshop import Workshop
from caerp.panels.company_index import utils


def coming_workshops_panel(context, request):
    """
    Return the list of the upcoming CAE workshops
    where the user is or can ben registered
    """
    if not request.is_xhr:
        resources.event_list_js.need()

    title = "Prochains ateliers de la CAE"
    current_user = request.identity

    query = Workshop.query()
    query = query.filter(Workshop.datetime >= datetime.datetime.now())
    query = query.filter(
        or_(
            Workshop.attendances.any(Attendance.account_id == current_user.id),
            Workshop.signup_mode == "open",
        )
    )
    query = query.order_by(Workshop.datetime)

    page_nb = utils.get_page_number(request, "workshops_page_nb")
    items_per_page = utils.get_items_per_page(request, "workshops_per_page")

    paginated_workshops = SqlalchemyOrmPage(
        query,
        page_nb,
        items_per_page=items_per_page,
        url_maker=utils.make_get_list_url("workshops"),
    )

    result_data = {"workshops": paginated_workshops, "title": title}
    return result_data


def includeme(config):
    config.add_panel(
        coming_workshops_panel,
        "cae_coming_workshops",
        renderer="panels/company_index/coming_workshops.mako",
    )
