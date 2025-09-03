"""
Base Task views
"""
import datetime
import logging

from typing import List

from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from sqlalchemy import inspect

from caerp.consts.permissions import PERMISSIONS
from caerp.forms.files import get_file_upload_schema
from caerp.interfaces import ITaskPdfRenderingService

from caerp.services.smtp.task import get_last_sent_node_smtp_history
from caerp.utils.image import ImageResizer
from caerp.utils.widgets import ViewLink, Link

from caerp.models.files import File
from caerp.models.third_party.customer import Customer
from caerp.models.company import Company
from caerp.models.project import (
    Phase,
    Project,
)
from caerp.models.task import Task, TaskLine, Estimation, Invoice

from caerp.forms.tasks.base import (
    get_duplicate_schema,
    get_task_metadatas_edit_schema,
)
from caerp.forms.tasks.invoice import SetProductsSchema

from caerp.export.utils import write_file_to_request
from caerp.export.task_pdf import ensure_task_pdf_persisted

from caerp.resources import (
    task_resources,
    task_add_js,
    task_duplicate_js,
    node_view_only_js,
    pdf_preview_js,
)
from caerp.controllers.state_managers import (
    check_validation_allowed,
    set_validation_status,
)
from caerp.views import (
    BaseView,
    BaseFormView,
    DeleteView,
    TreeMixin,
    JsAppViewMixin,
    submit_btn,
    cancel_btn,
)
from caerp.views.business.routes import BUSINESS_ITEM_ROUTE
from caerp.views.files.views import BaseZipFileView, FileUploadView
from caerp.views.indicators.routes import INDICATOR_NODE_COLLECTION_API_ROUTE
from caerp.views.project.files import ProjectFilesView
from caerp.views.sale_product.routes import CATALOG_API_ROUTE
from caerp.views.project.routes import (
    PROJECT_ITEM_PHASE_ROUTE,
    PROJECT_ITEM_ROUTE,
)
from caerp.views.third_party.customer.routes import CUSTOMER_ITEM_ROUTE
from caerp.views.price_study.utils import get_price_study_api_urls
from caerp.views.progress_invoicing.utils import get_progress_invoicing_plan_url
from caerp.views.status import StatusView
from .utils import (
    get_task_url,
    get_task_parent_url,
    get_task_view_type,
)

logger = logging.getLogger(__name__)


def get_project_redirect_btn(request, id_):
    """
    Button for "go back to project" link
    """
    return Link(request.route_path(PROJECT_ITEM_ROUTE, id=id_), "Revenir au dossier")


def get_customer_redirect_btn(request, id_):
    """
    Button for "go back to customer" link
    """
    return Link(request.route_path(CUSTOMER_ITEM_ROUTE, id=id_), "Revenir au client")


class TaskAddView(BaseView):
    title = "*** Titre à modifier ***"

    def _get_company_id(self) -> int:
        if isinstance(self.context, Company):
            return self.context.id
        elif hasattr(self.context, "company_id"):
            return self.context.company_id
        else:
            raise Exception("Can't find the company id")

    def __call__(self) -> dict:
        task_add_js.need()
        self.populate_navigation()

        initial_data = {"company_id": self._get_company_id()}
        if "customer_id" in self.request.GET:
            initial_data["customer_id"] = int(self.request.GET["customer_id"])

        if "project_id" in self.request.GET:
            initial_data["project_id"] = int(self.request.GET["project_id"])

        if "phase_id" in self.request.GET:
            phase_id = int(self.request.GET["phase_id"])
            phase = Phase.get(phase_id)
            if phase:
                initial_data["project_id"] = phase.project_id
                initial_data["phase_id"] = phase_id

        result = {
            "title": self.title,
            "js_app_options": {
                "context_url": self.request.current_route_path(_query={}),
                "form_config_url": self.get_api_url(
                    _query=dict(form_config="1", **initial_data)
                ),
                "api_url": self.get_api_url(_query=initial_data),
                "initial_data": initial_data,
            },
        }
        return result

    def get_api_url(self, _query: dict = {}) -> str:
        raise NotImplementedError("Url manquante")

    def get_list_url(self) -> str:
        raise NotImplementedError("Url manquante")

    def get_parent_link(self):
        res = None
        if "project_id" in self.request.GET:
            res = get_project_redirect_btn(self.request, self.request.GET["project_id"])
        elif "customer_id" in self.request.GET:
            res = get_customer_redirect_btn(
                self.request, self.request.GET["customer_id"]
            )

        return res

    def populate_navigation(self):
        """
        Add buttons in the request actionmenu attribute
        """
        result = self.get_parent_link()
        if result:
            logger.debug(f"Pushing link {result.url} into breadcrumb")
            self.request.navigation.breadcrumb.append(result)

        self.request.navigation.breadcrumb.append(Link("", self.title))


class TaskJsAppViewMixin(JsAppViewMixin):
    def context_url(self, _query={}):
        return get_task_url(self.request, _query=_query, api=True)


class TaskEditView(BaseView, TreeMixin, TaskJsAppViewMixin):
    def title(self):
        return "Modification du document {task.name}".format(task=self.context)

    def catalog_tree_url(self):
        return self.request.route_path(
            CATALOG_API_ROUTE,
            id=self.context.company_id,
        )

    def task_line_group_api_url(self):
        return get_task_url(self.request, suffix="/task_line_groups", api=True)

    def get_js_app_options(self) -> dict:
        options = super().get_js_app_options().copy()
        options.update(
            {
                "catalog_tree_url": self.catalog_tree_url(),
                "file_upload_url": get_task_url(self.request, suffix="/addfile"),
                "file_requirement_url": self.request.route_path(
                    INDICATOR_NODE_COLLECTION_API_ROUTE, id=self.context.id
                ),
                "file_attachment_url": get_task_url(
                    self.request,
                    _query={"fields": "attachments"},
                    api=True,
                ),
                "total_url": get_task_url(self.request, suffix="/total", api=True),
            }
        )
        if self.context.has_price_study():
            logger.debug("Has a price study")
            options.update(
                get_price_study_api_urls(self.request, self.context.price_study)
            )
        elif self.context.has_progress_invoicing_plan():
            logger.debug("Has a progress invoicing plan")
            options.update(
                get_progress_invoicing_plan_url(
                    self.request, self.context.progress_invoicing_plan
                )
            )
        else:
            options["task_line_group_api_url"] = self.task_line_group_api_url()

        return options

    def __call__(self):
        task_type = get_task_view_type(self.context)
        if not self.request.has_permission(PERMISSIONS[f"context.edit_{task_type}"]):
            url = get_task_url(self.request, suffix="/general", _query=self.request.GET)
            return HTTPFound(url)

        if hasattr(self, "_before"):
            self._before()

        self.populate_navigation()

        task_resources.need()
        result = dict(
            context=self.context,
            title=self.title,
            js_app_options=self.get_js_app_options(),
        )
        return result


class TaskDeleteView(DeleteView):
    """
    Base task deletion view
    """

    msg = "Le document {context.name} a bien été supprimé."

    @property
    def delete_msg(self):
        return self.msg.format(context=self.context)

    def on_before_delete(self):
        # Force le chargement du contexte dans la session courante avant suppression
        self.business = self.context.business
        self.project = self.context.project

    def on_delete(self):
        self.context.on_before_commit(self.request, "delete")

    def redirect(self):
        """
        Return a redirect url after task deletion
        """
        if self.business.visible:
            # l'affaire peut avoir été supprimée mais l'objet existe encore
            # On récupère le statut sqlalchemy de l'objet
            object_status = inspect(self.business)
            if not object_status.deleted:
                return HTTPFound(
                    self.request.route_path(BUSINESS_ITEM_ROUTE, id=self.business.id)
                )
        return HTTPFound(
            self.request.route_path(PROJECT_ITEM_ROUTE, id=self.project.id)
        )


class TaskDuplicateView(BaseFormView):
    """
    Task duplication view
    """

    schema = get_duplicate_schema()

    @property
    def title(self):
        return "Dupliquer {0} {1}".format(self.label, self.context.name)

    def before(self, form):
        BaseFormView.before(self, form)
        task_duplicate_js.need()

    def _after_task_duplicate(self, task, appstruct):
        """
        A function that is called after a task is duplicated.

        Args:
            task (Task): The duplicated task.
            appstruct (dict): The appstruct used to create the task.
        """
        pass

    def submit_success(self, appstruct):
        logger.debug("# Duplicating a document #")
        logger.debug(appstruct)

        project_id = appstruct.pop("project_id")
        appstruct["project"] = Project.get(project_id)

        customer_id = appstruct.pop("customer_id")
        appstruct["customer"] = Customer.get(customer_id)

        task = self.context.duplicate(
            self.request, user=self.request.identity, **appstruct
        )

        self._after_task_duplicate(task, appstruct)

        self.dbsession.add(task)
        self.dbsession.flush()
        logger.debug(
            "The {t.type_} {t.id} has been duplicated to {new_t.id}".format(
                t=self.context, new_t=task
            )
        )
        return HTTPFound(get_task_url(self.request, task))


class TaskMoveToPhaseView(BaseView):
    """
    View used to move a document to a specific directory/phase

    expects a get arg "phase" containing the destination phase_id
    """

    def __call__(self):
        phase_id = self.request.params.get("phase")
        if phase_id:
            phase = Phase.get(phase_id)
            if phase in self.context.project.phases:
                self.context.phase_id = phase_id
                self.request.dbsession.merge(self.context)

        return HTTPFound(
            self.request.route_path(
                PROJECT_ITEM_PHASE_ROUTE,
                id=self.context.project_id,
                _query={"phase": phase_id},
            )
        )


class TaskPdfView(BaseView):
    """
    Return A pdf representation of the current context
    """

    def __call__(self):
        rendering_service = self.request.find_service(
            ITaskPdfRenderingService,
            context=self.context,
        )
        filename = rendering_service.filename()
        pdf_buffer = ensure_task_pdf_persisted(self.context, self.request)
        write_file_to_request(self.request, filename, pdf_buffer, "application/pdf")
        return self.request.response


class TaskPdfDevView(BaseView):
    """
    Return the html structure used in pdf generation
    """

    def __call__(self):
        from caerp.resources import pdf_css

        pdf_css.need()
        return dict(task=self.context)


class TaskSetMetadatasView(BaseFormView):
    schema = get_task_metadatas_edit_schema()
    buttons = (submit_btn, cancel_btn)

    @property
    def title(self):
        return "Modification du document {task.name}".format(task=self.context)

    def before(self, form):
        task_add_js.need()
        self.request.actionmenu.add(
            ViewLink(
                "Revenir au document", url=get_task_url(self.request, suffix="/general")
            ),
        )
        appstruct = {
            "name": self.context.name,
            "customer_id": self.context.customer_id,
            "project_id": self.context.project_id,
        }
        if self.context.phase_id:
            appstruct["phase_id"] = self.context.phase_id

        form.set_appstruct(appstruct)

    def redirect(self):
        url = get_task_url(self.request)
        return HTTPFound(url)

    def _get_related_elements(self):
        """
        List elements related to the current estimation
        Produce a list of visible elements that will be moved
        and a list of all elements that will be moved

        :returns: a 2-uple (visible elements, list of elements to be moved)
        :rtype: tuple
        """
        all_items = []
        visible_items = []
        business = self.context.business
        if business:
            if business.visible:
                visible_items.append(business)
            all_items.append(business)

            all_items.extend(business.invoices)
            visible_items.extend(business.invoices)
            for estimation in business.estimations:
                if estimation != self.context:
                    visible_items.append(estimation)
                    all_items.append(estimation)
        return visible_items, all_items

    def _handle_move_to_project(self, appstruct):
        """
        Handle the specific case where a document is moved to another project

        :param dict appstruct: The appstruct returned after form validation
        """
        visible_items, all_items = self._get_related_elements()
        if visible_items:
            logger.debug("We want the user to confirm the Move to project action")

        self._apply_modifications(appstruct)
        # We move all elements to the other project
        for element in all_items:
            element.project_id = appstruct["project_id"]
            if hasattr(element, "phase_id") and "phase_id" in appstruct:
                element.phase_id = appstruct["phase_id"]
            self.dbsession.merge(element)

        result = self.redirect()

        return result

    def _apply_modifications(self, appstruct):
        """
        Apply the modification described by appstruct to the current context

        :param dict appstruct: The appstruct returned after form validation
        """
        if "customer_id" in appstruct:
            # Dans le cas où le document peut être déplacé d'un dossier à un
            # autre, on a aussi besoin du customer_id dans le formulaire pour
            # que la partie js fonctionne, mais on ne veut pas pour autant
            # qu'il soit modifiable
            # Donc si il est présent, on l'enlève
            appstruct.pop("customer_id")
        for key, value in appstruct.items():
            setattr(self.context, key, value)
        return self.request.dbsession.merge(self.context)

    def submit_success(self, appstruct):
        """
        Handle successfull modification

        :param dict appstruct: The appstruct returned after form validation
        :rtype: HTTPFound
        """
        logger.debug("TaskSetMetadatasView.submit_success : %s" % appstruct)
        project_id = appstruct.get("project_id")

        if project_id not in (None, self.context.project_id):
            result = self._handle_move_to_project(appstruct)
        else:
            self._apply_modifications(appstruct)
            result = self.redirect()

        return result

    def cancel_success(self, appstruct):
        return self.redirect()

    cancel_failure = cancel_success


class TaskSetProductsView(BaseFormView):
    """
    Base view for setting product codes (on invoices and cancelinvoices)

    context

        invoice or cancelinvoice
    """

    schema = SetProductsSchema()

    def before(self, form):
        form.set_appstruct(
            {"lines": [line.appstruct() for line in self.context.all_lines]}
        )
        self.request.actionmenu.add(
            ViewLink(
                "Revenir au document",
                url=get_task_url(self.request, suffix="/general"),
            )
        )

    def submit_success(self, appstruct):
        for line in appstruct["lines"]:
            line_id = line.get("id")
            product_id = line.get("product_id")
            if line_id is not None and product_id is not None:
                taskline = TaskLine.get(line_id)
                if taskline.task == self.context:
                    taskline.product_id = product_id
                    self.request.dbsession.merge(taskline)
                else:
                    logger.error(
                        "Possible break in attempt: trying to set product id "
                        "on the wrong task line (not belonging to this task)"
                    )
        return HTTPFound(get_task_url(self.request))


class TaskSetDraftView(BaseView):
    """
    Set the current task status to draft
    """

    def __call__(self):
        set_validation_status(self.request, self.context, "draft")
        # This view offers no input for comment
        self.context.status_comment = ""
        return HTTPFound(get_task_url(self.request))


class TaskStatusView(StatusView):
    """
    View handling base status for tasks (estimation/invoice/cancelinvoice)

    Status related views should implement

    - the validate function to ensure data
      integrity

    - state_manager_key (str) to where the status is stored on document model
    """

    def validate(self):
        raise NotImplementedError()

    def check_allowed(self, status):
        check_validation_allowed(self.request, self.context, status)

    def get_parent_url(self):
        return get_task_parent_url(self.request)

    def get_redirect_url(self):
        return get_task_url(self.request)

    def pre_status_process(self, status, params):
        if "comment" in params:
            self.context.status_comment = params.get("comment")
            logger.debug(self.context.status_comment)

        if "change_date" in params and params["change_date"] in ("1", 1):
            logger.debug("Forcing the document's date to today")
            self.context.date = datetime.date.today()
        elif (
            self.context.type_ in Task.invoice_types
            and not self.request.config.get_value(
                "allow_unchronological_invoice_sequence", False, bool
            )
        ):
            logger.debug("Setting the document's date to today")
            self.context.date = datetime.date.today()

        return StatusView.pre_status_process(self, status, params)

    def pre_wait_process(self, status, params):
        """
        Launched before the wait status is set

        :param str status: The new status that should be affected
        :param dict params: The params that were transmitted by the associated
        State's callback
        """
        self.validate()
        return params

    def pre_valid_process(self, status, params):
        """
        Launched before the valid status is set

        :param str status: The new status that should be affected
        :param dict params: The params that were transmitted by the associated
        State's callback
        """
        self.validate()
        return params

    def post_valid_process(self, status, params):
        """
        Launched after the status is set to valid

        :param str status: The new status that should be affected
        :param dict params: The params that were transmitted by the associated
        State's callback
        """
        # Check if document was auto validated (for invoices and estimations)
        if isinstance(self.context, (Estimation, Invoice)):
            user = self.request.identity
            user_companies = [company.id for company in user.companies]
            task_company = self.context.company_id

            if task_company in user_companies:
                self.context.set_auto_validated()


class BaseTaskHtmlTreeMixin(TreeMixin):
    request = None
    context = None

    @property
    def title(self):
        return "TITLE NOT SET"

    @property
    def tree_url(self):
        task = self.current()
        return self.request.route_path(
            self.route_name,
            id=task.id,
        )

    def current(self):
        if isinstance(self.context, Task):
            return self.context
        elif hasattr(self.context, "task"):
            return self.context.task
        else:
            logger.error("Can't find the current task")
            raise HTTPNotFound()


class TaskGeneralView(BaseView, BaseTaskHtmlTreeMixin, TaskJsAppViewMixin):
    """
    Base Class For the General tab of the Task html view

    Subclasses should set

        - A title (str) attribute or property
        - A file_route_name (str) attribute or property pointing to the
        file tab route
        - A route_name (str) : route presenting the current view
    """

    file_route_name: str = ""
    route_name: str = ""

    def _collect_file_indicators(self):
        """
        Collect file requirements attached to the given context
        """
        return self.context.get_file_requirements(scoped=False)

    def _get_file_tab_link(self):
        """
        Return the link to the file tab
        """
        return Link(
            self.request.route_path(
                self.file_route_name,
                id=self.context.id,
            ),
            "",
            title="Voir le détail des fichiers",
            icon="arrow-right",
            css="btn icon only",
        )

    def __call__(self):
        self.populate_navigation()
        # Code JS des Mémos
        node_view_only_js.need()

        task_type = get_task_view_type(self.context)
        # If the task is editable, we go the edit page
        if self.request.has_permission(PERMISSIONS[f"context.edit_{task_type}"]):
            return HTTPFound(get_task_url(self.request))

        return dict(
            title=self.title,
            indicators=self._collect_file_indicators(),
            js_app_options=self.get_js_app_options(),
            file_tab_link=self._get_file_tab_link(),
            task=self.context,
            last_smtp_history=get_last_sent_node_smtp_history(
                self.request, self.context
            ),
        )


class TaskPreviewView(BaseView, BaseTaskHtmlTreeMixin):
    route_name = ""

    def __call__(self):
        pdf_preview_js.need()
        self.populate_navigation()
        return {"title": self.title, "url": get_task_url(self.request, suffix=".pdf")}


class TaskZipFileView(BaseZipFileView):
    def filename(self):
        return f"{self.context.name}_archive.zip"

    def collect_files(self) -> List[File]:
        files = []
        if self.context.status == "valid":
            if self.context.pdf_file is None:
                ensure_task_pdf_persisted(self.context, self.request)
            files.append(self.context.pdf_file)

        files.extend(self.context.files)
        return files


class TaskFilesView(ProjectFilesView, BaseTaskHtmlTreeMixin):
    route_name = ""

    @property
    def title(self):
        return "Fichiers attachés au dossier {0}".format(self.context.project.name)

    def get_project_id(self):
        return self.context.project_id

    def _get_js_app_options(self):
        result = super()._get_js_app_options()
        if self.context.business_id is not None:
            result["business_id"] = self.context.business_id
        result["task_id"] = self.context.id
        result["title"] = self.title
        return result


class TaskFileUploadView(FileUploadView):
    def get_schema(self):
        return get_file_upload_schema([ImageResizer(1600, 1600, "PDF")])
