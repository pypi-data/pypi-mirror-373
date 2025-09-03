"""
Workshop related views
"""
import colander
import colanderalchemy
import datetime
import logging
import peppercorn

from js.deform import auto_need
from js.jquery_timepicker_addon import timepicker_fr
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPForbidden,
)
from typing import Union

from caerp.consts.permissions import PERMISSIONS
from caerp.export.workshop_pdf import workshop_pdf
from caerp.export.utils import write_file_to_request
from caerp.forms import merge_session_with_post
from caerp.forms.workshop import (
    ATTENDANCE_STATUS,
    Attendances as AttendanceSchema,
    get_workshop_schema,
)
from caerp.models.activity import Attendance
from caerp.models.company import Company
from caerp.models.user.user import User
from caerp.models.user.userdatas import AntenneOption
from caerp.models.workshop import (
    WorkshopTagOption,
    Workshop,
    Timeslot,
)
from caerp.panels.workshop import pdf_content_panel
from caerp.utils.navigation import NavigationHandler
from caerp.utils.widgets import Link, POSTButton
from caerp.utils.datetimes import (
    format_date,
    format_datetime,
)
from caerp.views import (
    BaseFormView,
    DuplicateView,
)
from caerp.views.files.views import FileUploadView


logger = log = logging.getLogger(__name__)


NAVIGATION_KEY = "/workshops"

WORKSHOP_SUCCESS_MSG = "L'atelier a bien été programmée : \
<a href='{0}'>Voir</a>"


def get_new_datetime(now, hour, minute=0):
    """
    Return a new datetime object based on the 'now' element

        hour

            The hour we'd like to set

        minute

            The minute value we want to set (default 0)
    """
    return now.replace(hour=hour, minute=minute, second=0, microsecond=0)


def get_default_timeslots():
    """
    Return default timeslots for workshop creation
    """
    now = datetime.datetime.now()
    morning = {
        "name": "Matinée",
        "start_time": get_new_datetime(now, 9),
        "end_time": get_new_datetime(now, 12, 30),
    }
    afternoon = {
        "name": "Après-midi",
        "start_time": get_new_datetime(now, 14),
        "end_time": get_new_datetime(now, 18),
    }
    return [morning, afternoon]


class WorkshopAddView(BaseFormView):
    """
    View for adding workshop
    """

    title = "Créer un nouvel atelier"

    def get_schema(
        self,
    ) -> Union[colander.Schema, colanderalchemy.SQLAlchemySchemaNode]:
        return get_workshop_schema()

    def before(self, form):
        auto_need(form)
        timepicker_fr.need()
        default_timeslots = get_default_timeslots()
        if self.request.has_permission(PERMISSIONS["global.manage_workshop"]):
            if self.context.__name__ == "company":
                form.set_appstruct(
                    {
                        "timeslots": default_timeslots,
                        "company_manager_id": self.context.id,
                    }
                )
            else:
                form.set_appstruct(
                    {
                        "timeslots": default_timeslots,
                    }
                )
        else:
            form.set_appstruct(
                {
                    "timeslots": default_timeslots,
                    "company_manager_id": self.context.id,
                    "trainers": [self.request.identity.id],
                }
            )

    def submit_success(self, appstruct):
        """
        Create a new workshop
        """
        come_from = appstruct.pop("come_from")

        timeslots_datas = appstruct.pop("timeslots")
        for i in timeslots_datas:
            i.pop("id", None)

        timeslots_datas.sort(key=lambda val: val["start_time"])

        appstruct["datetime"] = timeslots_datas[0]["start_time"]
        appstruct["timeslots"] = [Timeslot(**data) for data in timeslots_datas]

        participants_ids = set(appstruct.pop("participants", []))
        appstruct["participants"] = [User.get(id_) for id_ in participants_ids]

        for timeslot in appstruct["timeslots"]:
            timeslot.participants = appstruct["participants"]

        trainers_ids = set(appstruct.pop("trainers", []))
        appstruct["trainers"] = [User.get(id_) for id_ in trainers_ids]

        workshop_tags_ids = set(appstruct.pop("tags", []))
        appstruct["tags"] = [WorkshopTagOption.get(id_) for id_ in workshop_tags_ids]

        if self.context is not None:
            if self.context.__name__ == "company":
                appstruct["company_manager_id"] = self.context.id
            else:
                appstruct["company_manager_id"] = None

        if self.request.identity is not None:
            if self.request.identity.id is not None:
                appstruct["owner"] = User.get(self.request.identity.id)

        workshop_obj = Workshop(**appstruct)

        workshop_obj = merge_session_with_post(
            workshop_obj,
            appstruct,
            remove_empty_values=False,
        )
        self.dbsession.add(workshop_obj)
        self.dbsession.flush()

        workshop_url = self.request.route_path(
            "workshop", id=workshop_obj.id, _query=dict(action="edit")
        )

        if not come_from:
            redirect = workshop_url
        else:
            msg = WORKSHOP_SUCCESS_MSG.format(workshop_url)
            self.session.flash(msg)
            redirect = come_from
        return HTTPFound(redirect)


class WorkshopEditView(BaseFormView):
    """
    Workshop edition view

    Provide edition functionnality and display a form for attendance recording
    """

    add_template_vars = (
        "title",
        "available_status",
        "is_multi_antenna_server",
    )

    def get_schema(
        self,
    ) -> Union[colander.Schema, colanderalchemy.SQLAlchemySchemaNode]:
        return get_workshop_schema()

    @property
    def title(self):
        return self.context.title

    @property
    def available_status(self):
        return ATTENDANCE_STATUS

    @property
    def is_multi_antenna_server(self):
        return AntenneOption.query().count() > 1

    def before(self, form):
        """
        Populate the form before rendering

            form

                The deform form object used in this form view (see parent class
                in pyramid_deform)
        """
        add_tree_to_navigation(self.request)
        self.request.navigation.breadcrumb.append(Link("", self.title))

        auto_need(form)
        timepicker_fr.need()

        appstruct = self.context.appstruct()
        participants = self.context.participants
        appstruct["participants"] = [p.id for p in participants]

        trainers = self.context.trainers
        appstruct["trainers"] = [p.id for p in trainers]

        appstruct["tags"] = [a.id for a in self.request.context.tags]

        timeslots = self.context.timeslots
        appstruct["timeslots"] = [t.appstruct() for t in timeslots]

        form.set_appstruct(appstruct)

        from deform_extensions import GridFormWidget

        WORKSHOP_EDIT_GRID_FORM = (
            [["name", 12]],
            [["company_manager_id", 12]],
            [["trainers", 12]],
            [["tags", 12]],
            [["signup_mode", 12]],
            [["description", 12]],
            [["place", 12]],
            [["info1_id", 12]],
            [["info2_id", 12]],
            [["info3_id", 12]],
            [["max_participants", 12]],
            [["participants", 12]],
            [["timeslots", 12]],
        )

        form.widget = GridFormWidget(named_grid=(WORKSHOP_EDIT_GRID_FORM))

        return form

    def _retrieve_workshop_timeslot(self, id_):
        """
        Retrieve an existing workshop model from the current context
        """
        for timeslot in self.context.timeslots:
            if timeslot.id == id_:
                return timeslot
        log.warn(
            "Possible break in attempt : On essaye d'éditer un timeslot \
qui n'appartient pas au contexte courant !!!!"
        )
        raise HTTPForbidden()

    def _get_timeslots(self, appstruct):
        datas = appstruct.pop("timeslots")
        objects = []
        datas.sort(key=lambda val: val["start_time"])

        for data in datas:
            id_ = data.pop("id", None)
            if id_ is None:
                # New timeslots
                objects.append(Timeslot(**data))
            else:
                # existing timeslots
                obj = self._retrieve_workshop_timeslot(id_)
                merge_session_with_post(obj, data)
                objects.append(obj)

        return objects

    def submit_success(self, appstruct):
        """
        Handle successfull submission of our edition form
        """
        logger.info("Submitting workshop edit")
        logger.info(appstruct)
        come_from = appstruct.pop("come_from")
        appstruct["timeslots"] = self._get_timeslots(appstruct)
        appstruct["datetime"] = appstruct["timeslots"][0].start_time

        participants_ids = set(appstruct.pop("participants", []))
        appstruct["participants"] = [User.get(id_) for id_ in participants_ids]

        for timeslot in appstruct["timeslots"]:
            timeslot.participants = appstruct["participants"]

        trainers_ids = set(appstruct.pop("trainers", []))
        appstruct["trainers"] = [User.get(id_) for id_ in trainers_ids]

        workshop_tags_ids = set(appstruct.pop("tags", []))
        appstruct["tags"] = [WorkshopTagOption.get(id_) for id_ in workshop_tags_ids]

        if "company_manager_id" in appstruct:
            if appstruct["company_manager_id"] == -1:
                appstruct["company_manager_id"] = None

        if self.request.identity is not None:
            if self.request.identity.id is not None:
                appstruct["owner"] = User.get(self.request.identity.id)

        merge_session_with_post(
            self.context,
            appstruct,
            remove_empty_values=False,
        )
        self.dbsession.merge(self.context)

        workshop_url = self.request.route_path(
            "workshop", id=self.context.id, _query=dict(action="edit")
        )

        if not come_from:
            redirect = workshop_url
        else:
            msg = WORKSHOP_SUCCESS_MSG.format(workshop_url)
            self.session.flash(msg)
            redirect = come_from

        return HTTPFound(redirect)


def record_attendances_view(context, request):
    """
    Record attendances for the given context (workshop)

    Special Note : Since we need a special layout in the form (with tabs and
    lines with the username as header, we can't render it with deform.  We use
    peppercorn's parser and we build an appropriate form in the template
    """
    schema = AttendanceSchema().bind(request=request)
    if "submit" in request.params:
        controls = list(request.params.items())
        values = peppercorn.parse(controls)
        try:
            appstruct = schema.deserialize(values)
        except colander.Invalid as e:
            log.error("Error while validating workshop attendance")
            log.error(e)
        else:
            for datas in appstruct["attendances"]:
                account_id = datas["account_id"]
                timeslot_id = datas["timeslot_id"]
                obj = Attendance.get((account_id, timeslot_id))
                obj.status = datas["status"]
                request.dbsession.merge(obj)
            request.session.flash("L'émargement a bien été enregistré")

    url = request.route_path(
        "workshop",
        id=context.id,
        _query=dict(action="edit"),
    )

    return HTTPFound(url)


def timeslots_pdf_output(timeslots, workshop, request):
    """
    write the pdf output of an attendance sheet to the current request response

        timeslots

            The timeslots to render in the attendance sheet (one timeslot = one
            column)

        workshop

            The workshop object

        request

            The current request object
    """
    if not hasattr(timeslots, "__iter__"):
        timeslots = [timeslots]

    date = workshop.datetime.strftime("%e_%m_%Y")
    filename = "atelier_{0}_{1}.pdf".format(date, workshop.id)

    pdf_buffer = workshop_pdf(workshop, timeslots, request)

    write_file_to_request(request, filename, pdf_buffer, "application/pdf")
    return request.response


def timeslot_pdf_view(timeslot, request):
    """
    Return a pdf attendance sheet for the given timeslot

        timeslot

            A timeslot object returned as a current context by traversal
    """
    return timeslots_pdf_output(timeslot, timeslot.workshop, request)


def workshop_pdf_view(workshop, request):
    """
    Return a pdf attendance sheet for all the timeslots of the given workshop

        workshop

            A workshop object returned as a current context by traversal
    """
    return timeslots_pdf_output(workshop.timeslots, workshop, request)


def workshop_pdf_html_view(workshop, request):
    """
    Debug view to debug generated HTML
    """
    from caerp.resources import pdf_css

    pdf_css.need()
    return pdf_content_panel(workshop, request, workshop.timeslots)


def workshop_view(workshop, request):
    """
    Workshop view_only view

        workshop

            the context returned by the traversal tree
    """
    if request.has_permission(PERMISSIONS["context.edit_workshop"]):
        url = request.route_path(
            "workshop",
            id=workshop.id,
            _query=dict(action="edit"),
        )
        return HTTPFound(url)
    add_tree_to_navigation(request)
    request.navigation.breadcrumb.append(Link("", workshop.title))

    timeslots_datas = []
    for timeslot in workshop.timeslots:
        if timeslot.start_time.day == timeslot.end_time.day:
            time_str = "le {0} de {1} à {2}".format(
                format_date(timeslot.start_time),
                format_datetime(timeslot.start_time, timeonly=True),
                format_datetime(timeslot.end_time, timeonly=True),
            )
        else:
            time_str = "du {0} au {1}".format(
                format_datetime(timeslot.start_time), format_datetime(timeslot.end_time)
            )
        status = timeslot.user_status(request.identity.id)
        timeslots_datas.append((timeslot.name, time_str, status))

    action_buttons = []
    current_user_id = request.identity.id
    if request.has_permission(PERMISSIONS["context.signup_workshop"], workshop):
        if workshop.is_participant(current_user_id):
            action_buttons.append(
                POSTButton(
                    request.route_path(
                        "workshop",
                        id=workshop.id,
                        _query=dict(action="signout", user_id=current_user_id),
                    ),
                    "Me désinscrire de cet atelier",
                    "Me désinscrire de cet atelier",
                    icon="times",
                    css="icon negative",
                )
            )
        else:
            action_buttons.append(
                POSTButton(
                    request.route_path(
                        "workshop",
                        id=workshop.id,
                        _query=dict(action="signup", user_id=current_user_id),
                    ),
                    "M'inscrire à cet atelier",
                    "M'inscrire à cet atelier",
                    icon="calendar-alt",
                    css="btn-primary icon",
                )
            )

    return dict(
        title=workshop.title,
        action_buttons=action_buttons,
        timeslots_datas=timeslots_datas,
    )


def workshop_delete_view(workshop, request):
    """
    Workshop deletion view
    """
    url = request.referer
    request.dbsession.delete(workshop)
    request.session.flash("L'atelier a bien été supprimé")
    if not url:
        url = request.route_path("workshops")
    return HTTPFound(url)


def workshop_signup_view(workshop, request):
    """
    User signup service

    Current user subscribe to a workshop (himself or user_id argument)
    """
    url = request.referer

    if not url:
        url = request.route_path("workshops")

    if (
        request.has_permission(PERMISSIONS["context.edit_workshop"])
        and "user_id" in request.params
        and int(request.params["user_id"]) != request.identity.id
    ):

        user = User.get(request.params["user_id"])
        msg = "{} est inscrit à « {} ».".format(user.label, workshop.title)
    else:
        user = request.identity
        msg = "Vous êtes inscrit à « {} ».".format(workshop.title)

    # check max_participants is not reached
    if (workshop.max_participants > 0) and (
        len(workshop.participants) >= workshop.max_participants
    ):
        request.session.flash("L'atelier est déjà complet", queue="error")
        return HTTPFound(url)

    if user not in workshop.participants:
        workshop.participants.append(user)

        for timeslot in workshop.timeslots:
            timeslot.participants.append(user)

        request.dbsession.merge(workshop)
    request.session.flash(msg)
    return HTTPFound(url)


def workshop_signout_view(workshop, request):
    """
    Self-service user signout from a workshop.
    """
    url = request.referer

    if (
        request.has_permission(PERMISSIONS["context.edit_workshop"])
        and "user_id" in request.params
        and int(request.params["user_id"]) != request.identity.id
    ):
        user = User.get(request.params["user_id"])
        msg = "{} est désinscrit de « {} ».".format(user.label, workshop.title)
    else:
        user = request.identity
        msg = "Vous êtes désinscrit de « {} ».".format(workshop.title)

    if user in workshop.participants:
        workshop.participants.remove(user)

        for timeslot in workshop.timeslots:
            timeslot.participants.remove(user)

        request.dbsession.merge(workshop)
    request.session.flash(msg)
    if not url:
        url = request.route_path("workshops")
    return HTTPFound(url)


class WorkShopDuplicateView(DuplicateView):
    """
    Workshop duplication view
    """

    message = "Vous avez été redirigé vers le nouvel atelier"
    route_name = "workshop"


def add_tree_to_navigation(request):
    """
    Add elements in the actionmenu regarding the current context
    """
    handler = NavigationHandler(request, NAVIGATION_KEY)
    last = handler.last()

    if last is not None:
        link = Link(last, "Liste des ateliers")
        request.navigation.breadcrumb.append(link)


def add_views(config):
    config.add_view(
        WorkshopAddView,
        route_name="workshops",
        request_param="action=new",
        renderer="/base/formpage.mako",
        permission=PERMISSIONS["global.manage_workshop"],
    )

    config.add_view(
        WorkshopAddView,
        route_name="company_workshops",
        request_param="action=new",
        renderer="/base/formpage.mako",
        context=Company,
        permission=PERMISSIONS["context.add_training"],
    )

    config.add_view(
        WorkshopEditView,
        route_name="workshop",
        request_param="action=edit",
        renderer="/workshops/workshop_edit.mako",
        context=Workshop,
        permission=PERMISSIONS["context.edit_workshop"],
    )

    config.add_view(
        record_attendances_view,
        route_name="workshop",
        request_param="action=record",
        context=Workshop,
        permission=PERMISSIONS["context.edit_workshop"],
    )

    config.add_view(
        workshop_signup_view,
        route_name="workshop",
        request_param="action=signup",
        request_method="POST",
        require_csrf=True,
        context=Workshop,
        permission=PERMISSIONS["context.signup_workshop"],
    )
    config.add_view(
        workshop_signout_view,
        route_name="workshop",
        request_param="action=signout",
        request_method="POST",
        require_csrf=True,
        context=Workshop,
        permission=PERMISSIONS["context.signout_workshop"],
    )

    config.add_view(
        workshop_delete_view,
        route_name="workshop",
        request_param="action=delete",
        require_csrf=True,
        request_method="POST",
        context=Workshop,
        permission=PERMISSIONS["context.edit_workshop"],
    )

    config.add_view(
        WorkShopDuplicateView,
        route_name="workshop",
        request_param="action=duplicate",
        require_csrf=True,
        request_method="POST",
        context=Workshop,
        permission=PERMISSIONS["context.duplicate_workshop"],
    )

    config.add_view(
        workshop_view,
        route_name="workshop",
        renderer="/workshops/workshop_view.mako",
        context=Workshop,
        permission=PERMISSIONS["context.view_workshop"],
    )

    config.add_view(
        timeslot_pdf_view,
        route_name="timeslot.pdf",
        context=Timeslot,
        permission=PERMISSIONS["context.view_workshop"],
    )

    config.add_view(
        workshop_pdf_view,
        route_name="workshop.pdf",
        context=Workshop,
        permission=PERMISSIONS["context.view_workshop"],
    )

    config.add_view(
        workshop_pdf_html_view,
        renderer="panels/workshop/pdf_content.mako",
        context=Workshop,
        permission=PERMISSIONS["global.manage_workshop"],
    )

    config.add_view(
        FileUploadView,
        route_name="workshop",
        renderer="/base/formpage.mako",
        request_param="action=attach_file",
        context=Workshop,
        permission=PERMISSIONS["context.edit_workshop"],
    )


def includeme(config):
    """
    Add view to the pyramid registry
    """
    add_views(config)
    config.add_admin_menu(
        parent="accompagnement",
        order=1,
        label="Ateliers",
        route_name="cae_workshops",
        permission=PERMISSIONS["global.manage_workshop"],
    )
    config.add_admin_menu(
        parent="training",
        order=1,
        label="Ateliers",
        route_name="workshops",
        permission=PERMISSIONS["global.view_training"],
    )

    config.add_admin_menu(
        parent="accompagnement",
        order=2,
        label="Mes inscriptions",
        route_name="user_workshop_subscriptions",
        route_id_key="user_id",
    )

    config.add_company_menu(
        parent="accompagnement",
        order=1,
        label="Ateliers",
        route_name="company_workshops_subscribed",
        route_id_key="company_id",
        permission=PERMISSIONS["global.manage_workshop"],
    )

    def deferred_is_user_company(self, kw):
        return kw["is_user_company"]

    config.add_company_menu(
        parent="accompagnement",
        order=2,
        label="Inscription aux ateliers",
        route_name="user_workshop_subscriptions",
        route_id_key="user_id",
        permission=deferred_is_user_company,
    )

    def deferred_permission(self, kw):
        return kw["request"].has_permission(
            PERMISSIONS["context.view_training"], kw["company"]
        )

    config.add_company_menu(
        parent="worktools",
        order=1,
        label="Organisation d'ateliers",
        route_name="company_workshops",
        route_id_key="company_id",
        permission=deferred_permission,
    )
