import colander
import logging

from pyramid.httpexceptions import HTTPFound
from sqla_inspect.csv import CsvExporter

from caerp.consts.permissions import PERMISSIONS
from caerp.export.sage import SAGE_COMPATIBLE_ENCODING
from caerp.export.utils import write_file_to_request
from caerp.forms.bank_remittance import (
    get_bank_remittances_list_schema,
    RemittanceDateSchema,
)
from caerp.models.company import Company
from caerp.models.task import Task
from caerp.models.task.payment import (
    Payment,
    BankRemittance,
)
from caerp.models.third_party import Customer
from caerp.utils.datetimes import format_date
from caerp.utils.pdf import (
    render_html,
    write_html_as_pdf_response,
)
from caerp.utils.strings import format_amount
from caerp.utils.widgets import (
    Link,
    ViewLink,
    POSTButton,
)
from caerp.views import (
    BaseView,
    BaseListView,
)
from caerp.views.accounting.routes import (
    BANK_REMITTANCE_ROUTE,
    BANK_REMITTANCE_ITEM_ROUTE,
)


logger = log = logging.getLogger(__name__)


class BankRemittanceListView(BaseListView):
    """
    Bank Remittances listing view
    """

    title = "Liste des remises en banque"
    schema = get_bank_remittances_list_schema()
    sort_columns = {
        "id": BankRemittance.id,
        "created_at": BankRemittance.created_at,
        "remittance_date": BankRemittance.remittance_date,
    }
    default_sort = "created_at"
    default_direction = "desc"

    def query(self):
        return BankRemittance.query()

    def filter_remittance_id(self, query, appstruct):
        search = appstruct.get("search", None)
        if search:
            query = query.filter(BankRemittance.id.like("%" + search + "%"))
        return query

    def filter_payment_mode(self, query, appstruct):
        payment_mode = appstruct.get("payment_mode")
        if payment_mode:
            query = query.filter(BankRemittance.payment_mode == payment_mode)
        return query

    def filter_bank(self, query, appstruct):
        bank = appstruct.get("bank_id")
        if bank:
            query = query.filter(BankRemittance.bank_id == bank)
        return query

    def filter_closed(self, query, appstruct):
        closed = appstruct.get("closed", True)
        if closed in (False, colander.null, "false"):
            query = query.filter_by(closed=False)
        return query


class BankRemittanceView(BaseListView):
    """
    Bank Remittance detail view
    """

    schema = None
    add_template_vars = ("stream_main_actions",)
    sort_columns = {
        "date": Payment.date,
        "company": Company.name,
        "customer": Customer.label,
        "invoice": Task.official_number,
        "amount": Payment.amount,
    }
    default_sort = "date"
    default_direction = "desc"

    @property
    def title(self):
        return "Détail de la remise en banque {0}".format(self.context.id)

    def populate_actionmenu(self, appstruct):
        self.request.actionmenu.add(
            ViewLink(
                "Liste des remises en banque",
                path="/accounting/bank_remittances",
            )
        )

    def query(self):
        return (
            Payment.query()
            .join(Task)
            .join(Task.company)
            .join(Task.customer)
            .filter(Payment.bank_remittance_id == self.context.id)
        )

    def stream_main_actions(self):
        if self.context.closed:
            confirm_msg = None
            if self.context.is_exported():
                confirm_msg = "Cette remise en banque a déjà été exportée en \
comptabilité.\n\nEtes vous sûr de vouloir la rouvrir ?"
            yield POSTButton(
                self.request.route_path(
                    BANK_REMITTANCE_ITEM_ROUTE,
                    id=self.context.id,
                    _query=dict(action="open"),
                ),
                "Rouvrir",
                title="Rouvrir cette remise en banque",
                icon="lock-open",
                css="icon btn-primary",
                confirm=confirm_msg,
            )
            yield Link(
                self.request.route_path("bank_remittance.pdf", id=self.context.id),
                "PDF",
                title="Editer le borderau de remise",
                icon="file-pdf",
                css="icon",
            )
            yield Link(
                self.request.route_path("bank_remittance.csv", id=self.context.id),
                "CSV",
                title="Export au format CSV",
                icon="file-csv",
                css="icon",
            )
        else:
            yield Link(
                self.request.route_path(
                    BANK_REMITTANCE_ITEM_ROUTE,
                    id=self.context.id,
                    _query=dict(action="close"),
                ),
                "Clôturer",
                title="Clôturer cette remise en banque",
                icon="lock",
                css="icon btn-primary",
                js="toggleModal('remittance_close_form'); return false;",
            )


class BankRemittanceCloseView(BaseView):
    """
    View to close bank remittance
    """

    def __call__(self):
        schema = RemittanceDateSchema()
        schema = schema.deserialize(self.request.POST)
        self.context.closed = True
        self.context.remittance_date = schema["remittance_date"]
        self.dbsession.merge(self.context)
        self.session.flash(
            "La remise en banque {} est maintenant fermée".format(self.context.id)
        )
        return HTTPFound(self.request.referrer)


class BankRemittanceOpenView(BaseView):
    """
    View to reopen bank remittance
    """

    def __call__(self):
        self.context.closed = False
        self.context.remittance_date = None
        self.dbsession.merge(self.context)
        self.request.session.flash(
            "La remise en banque {} est maintenant ouverte".format(self.context.id)
        )
        return HTTPFound(self.request.referrer)


def BankRemittancePdfView(context, request):
    """
    Return a pdf output of the bank remittance
    """
    filename = "remise_{}.pdf".format(context.id)
    template = "caerp:templates/accounting/bank_remittance_pdf.mako"
    datas = dict(bank_remittance=context)
    html_str = render_html(request, template, datas)
    write_html_as_pdf_response(request, filename, html_str)
    return request.response


def BankRemittanceCsvView(context, request):
    """
    Return a csv output of the bank remittance
    """
    writer = CsvExporter()
    writer.headers = (
        {
            "name": "date",
            "label": "Date",
        },
        {"name": "bank_label", "label": "Banque"},
        {"name": "issuer", "label": "Emetteur"},
        {"name": "check_number", "label": "Num. chèque"},
        {"name": "invoice_ref", "label": "Réf. facture"},
        {"name": "code_compta", "label": "Code interne"},
        {"name": "amount", "label": "Montant"},
    )
    br_datas = []
    for payment in context.get_grouped_payments():
        row = {
            "date": format_date(payment["date"]),
            "bank_label": payment["bank_label"],
            "issuer": payment["issuer"],
            "check_number": payment["check_number"],
            "invoice_ref": payment["invoice_ref"],
            "code_compta": payment["code_compta"],
            "amount": format_amount(payment["amount"], grouping=False, precision=5),
        }
        br_datas.append(row)
    writer.set_datas(br_datas)
    write_file_to_request(
        request,
        "remise_{}.csv".format(context.id),
        writer.render(),
        "application/csv",
        encoding=SAGE_COMPATIBLE_ENCODING,
    )
    return request.response


def includeme(config):
    """
    Add module's views
    """
    config.add_view(
        BankRemittanceListView,
        route_name=BANK_REMITTANCE_ROUTE,
        renderer="/accounting/bank_remittances.mako",
        permission=PERMISSIONS["global.manage_accounting"],
    )
    config.add_view(
        BankRemittanceView,
        route_name=BANK_REMITTANCE_ITEM_ROUTE,
        renderer="/accounting/bank_remittance.mako",
        permission=PERMISSIONS["global.manage_accounting"],
    )
    config.add_view(
        BankRemittanceCloseView,
        route_name=BANK_REMITTANCE_ITEM_ROUTE,
        request_param="action=close",
        permission=PERMISSIONS["global.manage_accounting"],
    )
    config.add_view(
        BankRemittanceOpenView,
        route_name=BANK_REMITTANCE_ITEM_ROUTE,
        request_param="action=open",
        permission=PERMISSIONS["global.manage_accounting"],
        require_csrf=True,
        request_method="POST",
    )
    config.add_view(
        BankRemittancePdfView,
        route_name="bank_remittance.pdf",
        permission=PERMISSIONS["global.manage_accounting"],
    )
    config.add_view(
        BankRemittanceCsvView,
        route_name="bank_remittance.csv",
        permission=PERMISSIONS["global.manage_accounting"],
    )
    config.add_admin_menu(
        parent="accounting",
        order=8,
        label="Remises en banque",
        permission=PERMISSIONS["global.manage_accounting"],
        href=BANK_REMITTANCE_ROUTE,
        routes_prefixes=[
            BANK_REMITTANCE_ITEM_ROUTE,
        ],
    )
