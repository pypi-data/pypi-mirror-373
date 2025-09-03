from caerp.models.task import Invoice
from caerp.consts.permissions import PERMISSIONS

from caerp.utils.widgets import Link, Column, POSTButton

from caerp.views.task.utils import (
    get_task_url,
    get_task_view_type,
)
from caerp.views.company.tools import get_company_url
from caerp.views.third_party.customer.routes import CUSTOMER_ITEM_ROUTE


class TaskListPanel:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _stream_main_actions(self, item):
        """
        Yield common actions
        """
        yield Link(
            get_task_url(self.request, item, suffix=".pdf"),
            "PDF",
            icon="file-pdf",
            css="icon",
            popup=True,
        )
        yield Link(
            get_task_url(self.request, item),
            "Voir le document",
            icon="arrow-right",
            css="icon",
        )
        if self.request.has_permission(PERMISSIONS["context.add_file"], item):
            yield Link(
                get_task_url(self.request, item, suffix="/addfile"),
                "Ajouter un fichier",
                icon="paperclip",
                css="icon",
                popup=True,
            )
        if self.is_admin_view:
            yield Link(
                get_company_url(self.request, item.company),
                "Voir l'enseigne %s" % item.company.name,
                icon="building",
                css="icon",
            )
        yield Link(
            self.request.route_path(CUSTOMER_ITEM_ROUTE, id=item.customer_id),
            "Voir le client %s" % item.customer.label,
            icon="info-circle",
            css="icon",
        )
        task_type = get_task_view_type(item)
        if self.request.has_permission(
            PERMISSIONS[f"context.delete_{task_type}"], item
        ):
            yield POSTButton(
                get_task_url(self.request, item, suffix="/delete"),
                "Supprimer",
                icon="trash-alt",
                css="icon negative",
                confirm="Êtes-vous sûr de vouloir supprimer ce document ?",
            )

    def _stream_invoice_actions(self, item):
        """
        Stream actions available for invoices

        :param obj request: The Pyramid request object
        :param obj item: The Invoice or CancelInvoice instance
        """
        for link in self._stream_main_actions(item):
            yield link

        if isinstance(item, Invoice):

            if self.request.has_permission(
                PERMISSIONS["context.duplicate_invoice"], item
            ):
                yield Link(
                    get_task_url(self.request, item, suffix="/duplicate"),
                    "Dupliquer cette facture",
                    icon="copy",
                    css="icon",
                )
            if len(item.payments) > 0:
                yield Link(
                    get_task_url(self.request, item, suffix="/payment"),
                    "Voir les encaissements",
                    icon="euro-circle",
                    css="icon",
                )

            if self.request.has_permission(
                PERMISSIONS["context.add_payment_invoice"], item
            ):

                yield Link(
                    get_task_url(self.request, item, suffix="/addpayment"),
                    "Enregistrer un encaissement",
                    icon="plus-circle",
                    css="icon",
                    popup=True,
                )

    def _stream_estimation_actions(self, item):
        """
        Stream actions available for estimations

        :param obj request: The Pyramid request object
        :param obj item: The Invoice or CancelInvoice instance
        """
        for link in self._stream_main_actions(item):
            yield link

        if self.request.has_permission(
            PERMISSIONS["context.duplicate_estimation"], item
        ):
            yield Link(
                get_task_url(self.request, item, suffix="/duplicate"),
                "Dupliquer ce devis",
                icon="copy",
                css="icon",
            )

    def _invoice_columns(self):
        """
        Columns used to display an invoice list
        """
        result = []
        result.append(Column("&nbsp;"))
        result.append(Column("Numéro de facture", "official_number", "col_text", "N°"))
        if self.is_admin_view:
            result.append(Column("Enseigne", "company", "col_text"))
        result.append(Column("Date d’émission", "date", "col_date", "Émise le"))
        result.append(Column("Nom de la facture", "internal_number", "col_text"))
        result.append(Column("Client", "customer", "col_text"))
        if not self.tva_on_margin_display:
            result.append(Column("Montant Hors Taxes", "ht", "col_number", "HT"))
            result.append(Column("Montant de TVA", "tva", "col_number", "TVA"))
        result.append(Column("Montant TTC", "ttc", "col_number", "TTC"))
        result.append(Column("Paiement", "payment", "col_text"))
        result.append(
            Column("Fichiers attachés à la facture", None, "col_text", "Fichiers")
        )
        return result

    def _estimation_columns(self):
        """
        Columns used to display an invoice list
        """
        result = []
        result.append(Column("&nbsp;"))
        if self.is_admin_view:
            result.append(Column("Enseigne", "company", "col_text"))
        result.append(Column("Date d’émission", "date", "col_date", "Émis le"))
        result.append(Column("Description", "description", "col_text"))
        result.append(Column("Client", "customer", "col_text"))
        if not self.tva_on_margin_display:
            result.append(Column("Montant Hors Taxes", "ht", "col_number", "HT"))
            result.append(Column("Montant de TVA", "tva", "col_number", "TVA"))
        result.append(Column("Montant TTC", "ttc", "col_number", "TTC"))
        return result

    def __call__(
        self,
        records,
        datatype="invoice",
        is_admin_view=False,
        is_project_view=False,
        is_business_view=False,
        tva_on_margin_display=False,
    ):
        """
        datas used to render a list of tasks (estimations/invoices)
        """
        self.is_admin_view = is_admin_view
        self.is_project_view = is_project_view
        self.is_business_view = is_business_view
        self.tva_on_margin_display = tva_on_margin_display
        ret_dict = dict(
            datatype=datatype,
            records=records,
            is_admin_view=is_admin_view,
            is_project_view=is_project_view,
            is_business_view=is_business_view,
            is_invoice_list=not (is_business_view or is_project_view),
            tva_on_margin_display=tva_on_margin_display,
        )
        if datatype == "invoice":
            ret_dict["stream_actions"] = self._stream_invoice_actions
            ret_dict["columns"] = self._invoice_columns()
        elif datatype == "estimation":
            ret_dict["stream_actions"] = self._stream_estimation_actions
            ret_dict["columns"] = self._estimation_columns()
        else:
            raise Exception("Only invoices are supported")
        ret_dict["totalht"] = sum(r.ht for r in records)
        ret_dict["totaltva"] = sum(r.tva for r in records)
        ret_dict["totalttc"] = sum(r.ttc for r in records)
        return ret_dict


def includeme(config):
    """
    Pyramid's inclusion mechanism
    """
    config.add_panel(
        TaskListPanel,
        "task_list",
        renderer="panels/task/task_list.mako",
    )
