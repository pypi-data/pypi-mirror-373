from sqlalchemy import func

from caerp_base.models.base import DBSESSION
from caerp.compute.math_utils import integer_to_amount
from caerp.models.task import Task, Payment
from caerp.dataqueries.base import BaseDataQuery
from caerp.utils.dataqueries import dataquery_class


@dataquery_class()
class ClientsFacturesQuery(BaseDataQuery):

    name = "clients_factures"
    label = "Liste des clients facturés sur une période"
    description = """
    Liste de tous les clients facturés sur la période choisie avec leurs coordonnées 
    (mail, tél, adresse postale) et les montants totaux facturés et encaissés sur la 
    période.
    """

    def default_dates(self):
        self.start_date = self.date_tools.year_start()
        self.end_date = self.date_tools.year_end()

    def headers(self):
        headers = [
            "Enseigne",
            "Code analytique",
            "Client",
            "Numéro d'immatriculation",
            "Contact principal",
            "Adresse e-mail",
            "Téléphone portable",
            "Téléphone fixe",
            "Adresse",
            "Complément d'adresse",
            "Code postal",
            "Ville",
            "Total facturé",
            "Total encaissé",
        ]
        return headers

    def data(self):
        data = []
        customers = []
        invoiced_amount = {}
        invoices = (
            DBSESSION()
            .query(Task)
            .filter(Task.status == "valid")
            .filter(Task.type_.in_(("invoice", "cancelinvoice")))
            .filter(Task.date.between(self.start_date, self.end_date))
        )
        for inv in invoices:
            if inv.customer not in customers:
                customers.append(inv.customer)
                invoiced_amount[inv.customer_id] = 0
            invoiced_amount[inv.customer_id] += inv.ttc
        for c in customers:
            paid_amount = (
                DBSESSION()
                .query(func.sum(Payment.amount))
                .join(Task)
                .filter(Task.customer_id == c.id)
                .filter(Payment.date.between(self.start_date, self.end_date))
                .scalar()
            )
            if not paid_amount:
                paid_amount = 0
            customer_data = [
                c.company.name,
                c.company.code_compta,
                c.label,
                c.registration,
                c.get_name() if c.type == "company" else "",
                c.email,
                c.mobile,
                c.phone,
                c.address,
                c.additional_address,
                c.zip_code,
                c.city,
                integer_to_amount(invoiced_amount[c.id], precision=5, default=0),
                integer_to_amount(paid_amount, precision=5, default=0),
            ]
            data.append(customer_data)
        data.sort(key=lambda i: (i[0], i[1]))
        return data
