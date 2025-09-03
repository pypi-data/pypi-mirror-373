import logging

from caerp.consts.permissions import PERMISSIONS
from collections import OrderedDict

from caerp.interfaces import ITreasuryProducer, ITreasuryExpensePaymentWriter
from caerp.models.export.accounting_export_log import (
    ExpensePaymentAccountingExportLogEntry,
)
from caerp.models.expense.payment import ExpensePayment
from caerp.models.expense.sheet import ExpenseSheet
from caerp.models.user.user import User
from caerp.models.user.userdatas import UserDatas
from caerp.utils import strings
from caerp.utils.accounting import (
    check_company_accounting_configuration,
    check_user_accounting_configuration,
    check_waiver_accounting_configuration,
)
from caerp.utils.files import get_timestamped_filename
from caerp.utils.widgets import Link, ViewLink
from caerp.views.admin.expense.accounting import (
    EXPENSE_PAYMENT_ACCOUNTING_URL,
)
from caerp.views.export.utils import (
    get_expense_payment_period_form,
    get_expense_payment_all_form,
    get_expense_number_form,
    ACCOUNTING_EXPORT_TYPE_EXPENSE_PAYMENTS,
)
from caerp.views.export import BaseExportView
from caerp.views.company.tools import get_company_url
from caerp.views.user.routes import USER_ACCOUNTING_URL


logger = logging.getLogger(__name__)


ERR_COMPANY_CONFIG = """Un paiement de la note de dépenses {0}
n'est pas exportable : Le code analytique de l'enseigne {1} n'a pas été
configuré : 
<a onclick="window.openPopup('{2}');" href='#' title="La fiche de l’enseigne s’ouvrira dans une nouvelle fenêtre" aria-label="La fiche de l’enseigne s’ouvrira dans une nouvelle fenêtre">Voir l’enseigne</a>"""
ERR_USER_CONFIG = """Un paiement de la note de dépense {0}
n'est pas exportable : Le compte tiers de l'entrepreneur {1} n'a pas été
configuré : 
<a onclick="window.openPopup('{2}');" href='#' title="La fiche de l’entrepreneur s’ouvrira dans une nouvelle fenêtre" aria-label="La fiche de l’entrepreneur s’ouvrira dans une nouvelle fenêtre">Voir l’entrepreneur</a>"""

ERR_BANK_CONFIG = """Un paiement de la note de dépense {0}
n'est pas exportable : Le paiement n'est associé à aucune banque
<a onclick="window.openPopup('{1}');" href='#' title="Le détail du paiement s’ouvrira dans une nouvelle fenêtre" aria-label="Le détail du paiement s’ouvrira dans une nouvelle fenêtre">Voir le paiement</a>"""
ERR_WAIVER_CONFIG = """Le compte pour les abandons de créances n'a pas
été configuré : 
<a onclick="window.openPopup('{}');" href='#' title="La configuration du compte s’ouvrira dans une nouvelle fenêtre" aria-label="La configuration du compte s’ouvrira dans une nouvelle fenêtre">vous pouvez le configurer ici</a>
"""


class SingleExpensePaymentExportPage(BaseExportView):
    """
    Provide an expense payment export page for a single expense payment
    """

    admin_route_name = EXPENSE_PAYMENT_ACCOUNTING_URL
    writer_interface = ITreasuryExpensePaymentWriter

    @property
    def title(self):
        return (
            f"Exporter les écritures d'un paiement de la "
            f"note de dépenses {self.context.expense.official_number}"
        )

    def _populate_action_menu(self):
        if "come_from" in self.request.params:
            url = self.request.params["come_from"]
            title = "Retour à la page précédente"
        else:
            url = self.request.route_path("expense_payment", id=self.context.id)
            title = "Retour au paiement"

        self.request.actionmenu.add(
            Link(
                url=url,
                label="Retour",
                title=title,
                icon=None,
                css="",
            )
        )

    def before(self):
        self._populate_action_menu()

    def validate_form(self, forms):
        return "", {}

    def query(self, appstruct, form_name):
        force = self.request.params.get("force", False)
        query = ExpensePayment.query().filter(ExpensePayment.id == self.context.id)
        if not force:
            query = query.filter(ExpensePayment.exported == 0)
        return query

    def _check_bank(self, payment):
        if not payment.bank and not payment.waiver:
            return False
        return True

    def check(self, payments):
        """
        Check that the given expense_payments can be exported

        :param obj payments: A SQLA query of ExpensePayment objects
        """
        count = payments.count()
        if count == 0:
            title = "Il n'y a aucun paiement à exporter"
            res = {
                "title": title,
                "errors": [],
            }
            return False, res

        title = "Vous vous apprêtez à exporter {0} paiements".format(count)
        res = {"title": title, "errors": []}

        for payment in payments:
            expense = payment.expense
            if expense == None:
                res["errors"].append(
                    "Le paiement de note de dépense n°"
                    + str(payment.id)
                    + " n'est pas associé à une note de"
                    "dépense, l'export ne peut aboutir."
                )
                continue

            # CHECK COMPANY
            company = expense.company
            if not check_company_accounting_configuration(company):
                company_url = get_company_url(self.request, company, action="edit")
                message = ERR_COMPANY_CONFIG.format(
                    expense.id,
                    company.name,
                    company_url,
                )
                res["errors"].append(message)
                continue

            # CHECK USER
            user = expense.user
            if not check_user_accounting_configuration(self.request, user):
                user_url = self.request.route_path(
                    USER_ACCOUNTING_URL,
                    id=user.id,
                    _query={"action": "edit"},
                )
                message = ERR_USER_CONFIG.format(
                    expense.id,
                    strings.format_account(user),
                    user_url,
                )
                res["errors"].append(message)
                continue

            # CHECK BANK
            if not self._check_bank(payment):
                payment_url = self.request.route_path(
                    "expense_payment", id=payment.id, _query={"action": "edit"}
                )
                message = ERR_BANK_CONFIG.format(expense.id, payment_url)
                res["errors"].append(message)
                continue

            # CHECK WAIVER
            if payment.waiver and not check_waiver_accounting_configuration(
                self.request
            ):
                admin_url = self.request.route_path(self.admin_route_name)
                message = ERR_WAIVER_CONFIG.format(admin_url)
                res["errors"].append(message)
                continue

        return len(res["errors"]) == 0, res

    def record_exported(self, payments, form_name, appstruct):
        """
        Record that those payments have already been exported
        """
        for payment in payments:
            logger.info(
                f"The payment id : {payment.id} (for expense id "
                f"{payment.expense.id} / official number "
                f"{payment.expense.official_number}) has been exported"
            )
            payment.exported = True
            self.request.dbsession.merge(payment)

    def _collect_export_data(self, expense_payments, appstruct=None):
        exporter_class = self.request.find_service_factory(
            ITreasuryProducer, context=ExpensePayment
        )
        exporter = exporter_class(self.context, self.request)
        return exporter.get_book_entries(expense_payments)

    def record_export(self, expense_payments, form_name, appstruct, export_file):
        export = ExpensePaymentAccountingExportLogEntry()
        export.user_id = self.request.identity.id
        export.export_file_id = export_file.id
        export.export_type = ACCOUNTING_EXPORT_TYPE_EXPENSE_PAYMENTS

        for expense_payment in expense_payments:
            export.exported_expense_payments.append(expense_payment)

        self.request.dbsession.add(export)
        self.request.dbsession.flush()

    def get_filename(self, writer):
        return get_timestamped_filename("export_paiement_ndf", writer.extension)


class ExpensePaymentExportPage(SingleExpensePaymentExportPage):
    """
    Provide an expense payment export page
    """

    @property
    def title(self):
        return "Exporter les écritures des paiements de notes de dépenses"

    def _populate_action_menu(self):
        self.request.actionmenu.add(
            ViewLink(
                label="Liste des notes de dépenses",
                path="expenses",
            )
        )

    def get_forms(self):
        """
        Implement parent get_forms method
        """
        result = OrderedDict()
        period_form = get_expense_payment_period_form(self.request)
        expense_id_form = get_expense_number_form(
            self.request,
            period_form.counter,
            title="Exporter les paiements correspondant à une note de dépense",
        )
        all_form = get_expense_payment_all_form(
            self.request,
            period_form.counter,
        )
        for form in (
            all_form,
            expense_id_form,
            period_form,
        ):
            result[form.formid] = {"form": form, "title": form.schema.title}
        return result

    def _filter_date(self, query, start_date, end_date):
        return query.filter(ExpensePayment.date.between(start_date, end_date))

    def _filter_number(self, query, official_number):
        query = query.join(ExpensePayment.expense)
        return query.filter(ExpenseSheet.official_number == official_number)

    def _filter_by_issuer(self, query, query_params_dict):
        if "issuer_id" in query_params_dict:
            query = query.filter(
                ExpensePayment.user_id == query_params_dict["issuer_id"]
            )

        return query

    def _filter_by_antenne(self, query, query_params_dict):
        """
        Filter regarding the antenne of the User associated to the company
        that created the document. If no user associated to the company or
        multiple user it's not taken int account
        """
        if "antenne_id" not in query_params_dict:
            return query

        antenne_id = query_params_dict["antenne_id"]
        # -2 means situation_antenne_id = NULL
        if antenne_id == -2:
            antenne_id = None

        query = query.join(ExpensePayment.expense)
        query = query.outerjoin(User, ExpenseSheet.user)
        query = query.outerjoin(User.userdatas)
        query = query.filter(UserDatas.situation_antenne_id == antenne_id)

        return query

    def _filter_by_follower(self, query, query_params_dict):
        """
        Filter regarding the follower of the User associated to the company
        that created the document. If no user associated to the company or
        multiple user it's not taken int account
        """
        if "follower_id" not in query_params_dict:
            return query

        follower_id = query_params_dict["follower_id"]
        # -2 means situation_follower_id = NULL
        if follower_id == -2:
            follower_id = None

        query = query.join(ExpensePayment.expense)
        query = query.outerjoin(User, ExpenseSheet.user)
        query = query.outerjoin(User.userdatas)
        query = query.filter(UserDatas.situation_follower_id == follower_id)

        return query

    def _filter_by_mode(self, query, query_params_dict):
        if "mode" in query_params_dict:
            query = query.filter(ExpensePayment.mode == query_params_dict["mode"])
        return query

    def _filter_by_bank_account(self, query, query_params_dict):
        if "bank_account" in query_params_dict:
            if query_params_dict["bank_account"] > 0:
                logger.debug(
                    "Filtering by bank_account: %s", query_params_dict["bank_account"]
                )
                query = query.filter(
                    ExpensePayment.bank_id == query_params_dict["bank_account"]
                )
        return query

    def query(self, query_params_dict, form_name):
        """
        Retrieve the exports we want to export
        """
        query = ExpensePayment.query()

        if form_name == "period_form":
            start_date = query_params_dict["start_date"]
            end_date = query_params_dict["end_date"]
            query = self._filter_date(query, start_date, end_date)

        elif form_name == "expense_number_form":
            official_number = query_params_dict["official_number"]
            query = self._filter_number(query, official_number)

        if "exported" not in query_params_dict or not query_params_dict.get("exported"):
            query = query.filter(ExpensePayment.exported == False)  # noqa:E712

        query = self._filter_by_issuer(query, query_params_dict)
        query = self._filter_by_antenne(query, query_params_dict)
        query = self._filter_by_follower(query, query_params_dict)
        query = self._filter_by_mode(query, query_params_dict)
        query = self._filter_by_bank_account(query, query_params_dict)
        return query

    def validate_form(self, forms):
        return BaseExportView.validate_form(self, forms)


def add_routes(config):
    config.add_route(
        "/export/treasury/expense_payments", "/export/treasury/expense_payments"
    )
    config.add_route(
        "/export/treasury/expense_payments/{id}",
        "/export/treasury/expense_payments/{id}",
        traverse="/expense_payments/{id}",
    )


def add_views(config):
    config.add_view(
        SingleExpensePaymentExportPage,
        route_name="/export/treasury/expense_payments/{id}",
        renderer="/export/single.mako",
        permission=PERMISSIONS["global.manage_accounting"],
    )
    config.add_view(
        ExpensePaymentExportPage,
        route_name="/export/treasury/expense_payments",
        renderer="/export/main.mako",
        permission=PERMISSIONS["global.manage_accounting"],
    )


def includeme(config):
    add_routes(config)
    add_views(config)
    config.add_admin_menu(
        parent="accounting",
        order=3,
        label="Export des paiements de dépense",
        href="/export/treasury/expense_payments",
        permission=PERMISSIONS["global.manage_accounting"],
    )
