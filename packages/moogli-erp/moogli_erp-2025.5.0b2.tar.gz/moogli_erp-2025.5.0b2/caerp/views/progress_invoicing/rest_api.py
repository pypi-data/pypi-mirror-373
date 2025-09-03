import logging
from pyramid.httpexceptions import (
    HTTPForbidden,
)
from caerp.consts.permissions import PERMISSIONS
from caerp.models.progress_invoicing import (
    ProgressInvoicingChapter,
    ProgressInvoicingPlan,
    ProgressInvoicingWorkItem,
    ProgressInvoicingBaseProduct,
)
from caerp.views import BaseRestView
from caerp.models.progress_invoicing import (
    ProgressInvoicingWork,
)
from caerp.forms.progress_invoicing import (
    get_edit_product_schema,
    get_edit_work_schema,
    get_edit_workitem_schema,
)

from .routes import (
    PLAN_ITEM_API_ROUTE,
    CHAPTER_API_ROUTE,
    CHAPTER_ITEM_API_ROUTE,
    PRODUCT_API_ROUTE,
    PRODUCT_ITEM_API_ROUTE,
    WORK_ITEMS_API_ROUTE,
    WORK_ITEMS_ITEM_API_ROUTE,
)


logger = logging.getLogger(__name__)


# class ProgressInvoicingRestView(BaseRestView):
#     """
#     Rest api for progress invoicing configuration
#     """

#     schema = get_edit_schema()

#     def collection_get(self):
#         business = self.context.business
#         result = [
#             AbstractProgressTaskLineGroup(group_status, self.context.id)
#             for group_status in business.progress_invoicing_group_statuses
#         ]
#         return [group for group in result if group.current_element]

#     def _get_current_status(self):
#         group_id = self.request.matchdict["group_id"]
#         group_status = ProgressInvoicingGroupStatus.get(group_id)
#         if not group_status:
#             raise HTTPNotFound()
#         return group_status

#     def get(self):
#         group_status = self._get_current_status()
#         return AbstractProgressTaskLineGroup(group_status, self.context.id)

#     def put(self):
#         self.logger.info("PUT request")
#         submitted = self.request.json_body
#         logger.debug(submitted)
#         schema = self.schema.bind(request=self.request)

#         try:
#             attributes = schema.deserialize(submitted)
#         except colander.Invalid as err:
#             self.logger.exception("  - Erreur")
#             self.logger.exception(submitted)
#             raise rest.RestError(err.asdict(), 400)

#         line_config = {}
#         for line in attributes["lines"]:
#             line_config[line["id"]] = line["current_percent"]
#         group_status = self._get_current_status()
#         group_status.get_or_generate(line_config, self.context.id)
#         return AbstractProgressTaskLineGroup(group_status, self.context.id)


class ProgressInvoicingPlanRestView(BaseRestView):
    # Pas de requête pour récupérer tous les plans
    route = None
    item_route = PLAN_ITEM_API_ROUTE

    def post(self):
        return HTTPForbidden()

    def put(self):
        return HTTPForbidden()

    def delete(self):
        return HTTPForbidden()


class ProgressInvoicingChapterRestView(BaseRestView):
    route = CHAPTER_API_ROUTE
    item_route = CHAPTER_ITEM_API_ROUTE

    def collection_get(self):
        return self.context.chapters

    def put(self):
        return HTTPForbidden()

    def post(self):
        return HTTPForbidden()

    def delete(self):
        return HTTPForbidden()


class ProgressInvoicingProductRestView(BaseRestView):
    route = PRODUCT_API_ROUTE
    item_route = PRODUCT_ITEM_API_ROUTE

    def collection_get(self):
        return self.context.products

    def get_schema(self, submitted):
        if isinstance(self.context, ProgressInvoicingWork):
            return get_edit_work_schema()
        else:
            return get_edit_product_schema()

    def after_flush(self, entry, edit, attributes):
        entry.on_before_commit(self.request, "update", attributes)
        return super().after_flush(entry, edit, attributes)

    def post(self):
        return HTTPForbidden()

    def delete(self):
        return HTTPForbidden()


class ProgressInvoicingWorkItemRestView(BaseRestView):
    route = WORK_ITEMS_API_ROUTE
    item_route = WORK_ITEMS_ITEM_API_ROUTE
    schema = get_edit_workitem_schema()

    def collection_get(self):
        if isinstance(self.context, ProgressInvoicingWork):
            return self.context.items
        return []

    def pre_format(self, datas, edit=False):
        if "percentage" in datas:
            datas["_percentage"] = datas["percentage"]
        return super().pre_format(datas, edit)

    def after_flush(self, entry, edit, attributes):
        entry.on_before_commit(self.request, "update", attributes)
        return super().after_flush(entry, edit, attributes)

    def post(self):
        return HTTPForbidden()

    def delete(self):
        return HTTPForbidden()


def includeme(config):
    for view, collection_context, context in (
        (ProgressInvoicingPlanRestView, None, ProgressInvoicingPlan),
        (
            ProgressInvoicingChapterRestView,
            ProgressInvoicingPlan,
            ProgressInvoicingChapter,
        ),
        (
            ProgressInvoicingProductRestView,
            ProgressInvoicingChapter,
            ProgressInvoicingBaseProduct,
        ),
        (
            ProgressInvoicingWorkItemRestView,
            ProgressInvoicingWork,
            ProgressInvoicingWorkItem,
        ),
    ):
        config.add_rest_service(
            view,
            view.item_route,
            collection_route_name=view.route,
            collection_context=collection_context,
            context=context,
            collection_view_rights=PERMISSIONS["company.view"],
            view_rights=PERMISSIONS["company.view"],
            add_rights=PERMISSIONS["context.edit_progress_invoicing_plan"],
            edit_rights=PERMISSIONS["context.edit_progress_invoicing_plan"],
            delete_rights=PERMISSIONS["context.edit_progress_invoicing_plan"],
        )
