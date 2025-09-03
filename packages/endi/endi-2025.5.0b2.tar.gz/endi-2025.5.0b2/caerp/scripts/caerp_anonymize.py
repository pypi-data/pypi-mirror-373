"""
Script used to anonymize the content of the current database (
remove names,
customer personnal infos,
personnal datas ...)
"""

import argparse
import inspect
import itertools
import logging
import os
import random
import re
from collections import OrderedDict

import schwifty
import transaction
from caerp_base.models.base import DBSESSION
from sqlalchemy.orm import load_only

from caerp.models.listeners import SQLAListeners
from caerp.scripts.utils import argparse_command
from caerp.utils.image import build_header
from caerp.utils.sys_environment import resource_filename, resource_stream


def set_if_present(obj, field_name, value):
    if getattr(obj, field_name):
        setattr(obj, field_name, value)


class Anonymizer:
    def __init__(self, logger):
        try:
            from faker import Faker
        except ImportError:
            raise Exception(
                "You should install faker before being able to anonymize "
                "datas : "
                "pip install faker"
            )
        SQLAListeners.stop_listening()
        self.us_faker = Faker()
        self.faker = Faker("fr_FR")
        self.logger = logger
        self.session = DBSESSION()
        self.methods = self._load_an_methods()

    def _load_an_methods(self):
        methods = {}
        for method_name, method in inspect.getmembers(self, inspect.ismethod):
            if method_name.startswith("_an_"):
                methods[method_name] = method

        keys = list(methods.keys())
        keys.sort()
        result = OrderedDict()
        for key in keys:
            result[key] = methods[key]
        return result

    def _zipcode(self):
        if hasattr(self.faker, "zipcode"):
            return self.faker.zipcode()
        else:
            return self.faker.postcode()

    def _an_activity(self):
        from caerp.models.activity import Activity, ActivityType
        from caerp.models.workshop import Workshop

        for activity in self.session.query(Activity):
            for fieldname in ("point", "objectifs", "action", "documents", "notes"):
                setattr(activity, fieldname, self.faker.text())

        for workshop in self.session.query(Workshop).options(load_only("id")):
            workshop.description = self.faker.text()
            self.session.merge(workshop)

        type_labels = (
            "RV conseil",
            "RV suivi",
            "RV Gestion",
            "RV Admin",
            "RV RH",
            "RV Compta",
            "RV hebdo",
            "RV Mensuel",
        )

        for index, typ in enumerate(self.session.query(ActivityType).all()):
            typ.label = type_labels[index % 7]

    def _an_commercial(self):
        from caerp.models.commercial import TurnoverProjection

        for t in self.session.query(TurnoverProjection):
            t.comment = self.faker.text()

    def _anonymize_thirdparty_fields(self, thirdparty):
        """
        anonymize the fields factorized into models.third_party.ThirdParty
        (Supplier, Customer)
        """
        tp = thirdparty

        fields = [
            ("company_name", self.faker.company()),
            ("lastname", self.faker.last_name()),
            ("firstname", self.faker.first_name()),
            # civilite is not anonymized
            ("code", (tp.lastname + tp.company_name)[:4].upper()),
            # compte_cg is not anonymized
            ("compte_tiers", (tp.lastname + tp.company_name)[:4].upper()),
            ("registration", self.faker.siret()),
            # function is not anonymized
            ("address", self.faker.street_address()),
            ("additional_address", ""),
            ("zip_code", self._zipcode()),
            ("city", self.faker.city()),
            ("city_code", "123456"),
            # country is not anonymized
            ("email", self.faker.ascii_safe_email()),
            ("mobile", self.faker.phone_number()),
            ("phone", self.faker.phone_number()),
            ("fax", self.faker.phone_number()),
            ("tva_intracomm", ""),
            ("bank_account_iban", self.faker.iban()),
            ("bank_account_bic", self.faker.bic()),
            ("bank_account_owner", ""),
        ]

        # Logic is to keep blank what is blank
        for field_name, field_value in fields:
            if getattr(thirdparty, field_name):
                setattr(thirdparty, field_name, field_value)
        # .label and .name are be handled via signals
        # in models.thirt_party.third_party

    def _an_supplier(self):
        from caerp.models.third_party.supplier import Supplier

        for sup in self.session.query(Supplier):
            self._anonymize_thirdparty_fields(sup)

    def _an_company(self):
        from caerp.models.company import Company

        for comp in self.session.query(Company):
            comp.name = self.faker.company()
            comp.goal = self.faker.bs()
            comp.comments = self.faker.catch_phrase()
            comp.phone = self.faker.phone_number()
            comp.mobile = self.faker.phone_number()
            comp.email = self.faker.ascii_safe_email()
            set_if_present(
                comp, "code_compta", self.faker.unique.bothify(text="ANA-####")
            )
            set_if_present(comp, "address", self.faker.street_address())
            set_if_present(comp, "city", self.faker.city())
            set_if_present(comp, "zip_code", self._zipcode())
            if comp.country and comp.country != "France":
                comp.country = self.faker.country()
            if comp.header:
                header = build_header(
                    "{0}\n {1} - {2}".format(comp.name, comp.phone, comp.email)
                )
                comp.header = {"name": "header.png", "data": header}
            comp.cgv = ""

    def _an_competence(self):
        from caerp.models.competence import CompetenceGridItem, CompetenceGridSubItem

        for item in self.session.query(CompetenceGridItem):
            item.progress = self.faker.text()
        for item in self.session.query(CompetenceGridSubItem):
            item.comments = self.faker.text()

    def _an_config(self):
        from caerp.models.config import Config, ConfigFiles

        Config.set("cae_business_name", "CAE Démo")
        Config.set("cae_legal_status", "SARL SCOP")
        Config.set("cae_admin_mail", self.faker.ascii_safe_email())
        Config.set("cae_address", self.faker.street_address())
        Config.set("cae_zipcode", self._zipcode())
        Config.set("cae_city", self.faker.city())
        Config.set("cae_tel", self.faker.phone_number())
        Config.set("cae_contact_email", self.faker.ascii_safe_email())
        Config.set("cae_business_identification", self.faker.siret())
        Config.set("cae_intercommunity_vat", self.faker.vat_id())

        Config.set("welcome", self.faker.sentence(nb_words=15))
        ConfigFiles.set(
            "logo.png",
            {
                "data": resource_stream("static/img/caerp/logo.png"),
                "filename": "logo.jpg",
            },
        )
        Config.set("coop_cgv", self.faker.paragraph(nb_sentences=40))
        Config.set(
            "coop_pdffootertitle",
            """Une activité de ma CAE SARL SCOP à \
capital variable""",
        )
        Config.set(
            "coop_pdffootercourse",
            """Organisme de formation N° de déclaration \
d'activité au titre de la FPC : xx xx xxxxx. MA CAE est exonérée de TVA pour \
les activités s'inscrivant dans le cadre de la formation professionnelle \
conformément à l'art. L920-4 du Code du travail et de l'art. 202 C de \
l'annexe II du code général des impôts""",
        )
        footer = """RCS XXXX 000 000 000 00000 - SIRET 000 \
000 000 000 00 - Code naf 0000Z TVA INTRACOM : FR0000000. Siège social : 10 \
rue vieille 23200 Aubusson"""
        Config.set("coop_pdffootercontent", footer)
        Config.set("coop_pdffootertext", footer)
        Config.set("activity_footer", footer)

        Config.set("workshop_footer", footer)

        Config.set("sap_attestation_document_help", "")
        Config.set("sap_attestation_footer", footer)
        Config.set("sap_attestation_signee", "X")
        ConfigFiles.set("sap_attestation_header_img", {})
        ConfigFiles.set("sap_attestation_footer_img", {})

    def _an_customer(self):
        from caerp.models.third_party.customer import Customer

        for cust in self.session.query(Customer):
            self._anonymize_thirdparty_fields(cust)

    def _an_expense(self):
        from caerp.models.expense.sheet import (
            BaseExpenseLine,
            ExpenseKmLine,
            ExpenseSheet,
        )

        for sheet in self.session.query(ExpenseSheet):
            if sheet.status_comment:
                sheet.status_comment = self.faker.text()

        for line in self.session.query(BaseExpenseLine):
            line.description = self.faker.text()
        for line in self.session.query(ExpenseKmLine):
            line.start = self.faker.city()
            line.end = self.faker.city()

    def _an_node(self):
        from caerp.models.node import Node

        for node in self.session.query(Node):
            node.name = self.faker.sentence(nb_words=4, variable_nb_words=True)

    def _an_supplier_order(self):
        from caerp.models.supply import SupplierOrder, SupplierOrderLine

        for supplier_order in self.session.query(SupplierOrder):
            supplier_order.name = "Commande {}".format(
                self.faker.sentence(nb_words=3, variable_nb_words=True)
            )
            if supplier_order.status_comment:
                supplier_order.status_comment = self.faker.text()
        for line in self.session.query(SupplierOrderLine):
            line.description = self.faker.text()

    def _an_supplier_invoice(self):
        from caerp.models.supply import SupplierInvoice, SupplierInvoiceLine

        for supplier_invoice in self.session.query(SupplierInvoice):
            if supplier_invoice.name:
                supplier_invoice.name = "Facture {}".format(
                    self.faker.sentence(nb_words=3, variable_nb_words=True)
                )
            if supplier_invoice.status_comment:
                supplier_invoice.status_comment = self.faker.text()
        for line in self.session.query(SupplierInvoiceLine):
            line.description = self.faker.text()

    def _an_status_log_entry(self):
        from caerp.models.status import StatusLogEntry

        for entry in self.session.query(StatusLogEntry):
            if entry.comment:
                entry.comment = self.faker.sentence(nb_words=6)

    def _an_payment(self):
        from caerp.models.payments import BankAccount

        for b in self.session.query(BankAccount):
            b.label = "Banque : {0}".format(self.faker.company())
            b.iban = self.faker.iban()
            b.bic = "ABCDEFGHI01"
        from caerp.models.task.payment import Payment

        for p in self.session.query(Payment):
            p.issuer = self.faker.company()

    def _an_project(self):
        from caerp.models.project import Phase, Project

        for p in self.session.query(Project):
            p.name = self.faker.sentence(nb_words=5)
            p.definition = self.faker.text()
            if p.code:
                p.code = p.name[:3].upper()
            if p.description:
                p.description = self.faker.sentence(nb_words=8)

        for p in self.session.query(Phase):
            if not p.is_default():
                p.name = self.faker.sentence(nb_words=3)

    def _an_sale_product(self):
        from caerp.models.sale_product.base import (
            BaseSaleProduct,
            SaleProductStockOperation,
        )
        from caerp.models.sale_product.category import SaleProductCategory
        from caerp.models.sale_product.training import SaleProductTraining
        from caerp.models.sale_product.work import SaleProductWork
        from caerp.models.sale_product.work_item import WorkItem

        for cat in self.session.query(SaleProductCategory):
            cat.title = self.faker.sentence(nb_words=3)
            cat.description = self.faker.text()

        for prod in self.session.query(BaseSaleProduct):
            prod.label = self.faker.sentence(nb_words=2)
            prod.description = self.faker.text()
            if prod.notes:
                prod.notes = self.faker.text()

        for group in self.session.query(SaleProductWork):
            group.title = self.faker.sentence(nb_words=2)

        for item in self.session.query(SaleProductTraining):
            for field in (
                "goals",
                "prerequisites",
                "for_who",
                "content",
                "teaching_method",
                "logistics_mean",
                "more_stuff",
                "evaluation",
                "place",
                "free_one",
                "free_two",
                "free_three",
            ):
                setattr(item, field, self.faker.sentence(nb_words=3))

        for item in self.session.query(WorkItem):
            item._description = self.faker.sentence(nb_words=3)

        for op in self.session.query(SaleProductStockOperation):
            op.description = self.faker.text()

    def _an_statistic(self):
        from caerp.models.statistics import StatisticSheet

        for s in self.session.query(StatisticSheet):
            s.title = self.faker.sentence(nb_words=4)

    def _an_task(self):
        from caerp.models.task import DiscountLine, Task, TaskLine, TaskLineGroup

        RE_TASK_INTERNAL_NUM = re.compile(r"(.*) (\d{4}-\d{2} [FDA]I?\d+)")
        for task in self.session.query(Task):
            if task.status_comment:
                task.status_comment = self.faker.text()

            # If default name, keep it, else, pick something at random
            if task.name and task.name != task._name_tmpl.format(task.project_index):
                task.name = "{} {}".format(task.type_label, self.faker.word())

            if task.internal_number:
                m = RE_TASK_INTERNAL_NUM.match(task.internal_number)
                if m:
                    task.internal_number = f"{task.company.name} {m.group(2)}"
                else:
                    task.internal_number = (
                        f"{task.company.name} {task.date:%Y-%m} X{task.company_index}"
                    )

            task.description = self.faker.text()
            task.address = task.customer.full_address
            task.workplace = self.faker.address()
            task.payment_conditions = "Par chèque ou virement à réception de "
            "facture"
            if task.notes:
                task.notes = self.faker.text()
        for line in self.session.query(DiscountLine):
            line.description = self.faker.text()

        for line in self.session.query(TaskLine):
            line.description = self.faker.text()

        for group in self.session.query(TaskLineGroup):
            if group.title:
                group.title = self.faker.sentence(nb_words=4)
            if group.description:
                group.description = self.faker.text()

    def _an_task_config(self):
        from caerp.models.task import PaymentConditions

        self.session.query(PaymentConditions).delete()

        for index, label in enumerate(
            ["30 jours fin de mois", "À réception de facture"]
        ):
            condition = PaymentConditions(label=label)
            if index == 0:
                condition.default = True

            self.session.add(condition)

    def _an_task_mentions(self):
        from caerp.models.project.mentions import BusinessTypeTaskMention
        from caerp.models.task import Estimation, Task
        from caerp.models.task.mentions import (
            MANDATORY_TASK_MENTION,
            TASK_MENTION,
            TaskMention,
        )

        TASK_MENTION.delete().execute()
        MANDATORY_TASK_MENTION.delete().execute()
        self.session.query(BusinessTypeTaskMention).delete()

        for i in self.session.query(TaskMention):
            self.session.delete(i)

        invoice_mentions = []
        for label, title, full_text in (
            (
                "Informations de paiement pour les factures",
                "Conditions de paiement",
                """Par chèque libellé à l'ordre de : \
MA CAE/ {name}
à envoyer à l'adresse suivante :
MA CAE/ {name}
10 rue Vieille
23200 Aubusson

Ou par virement sur le compte de MA CAE/ {name}
MA BANQUE
RIB : xxxxx xxxx xxxxxxxxxxxxx
IBAN : xxxx xxxx xxxx xxxx xxxx xxxx xxx
BIC : MABAFRMACAXX
Merci d'indiquer le numéro de facture sur le libellé de votre virement ou \
dos de votre chèque.
""",
            ),
            (
                "Informations sur les retards de paiement ",
                "Retard de paiement",
                """Tout retard de paiement entraînera à titre de \
clause pénale, conformément à la loi 92.1442 du 31 décembre 1992, une \
pénalité égale à un taux d'intérêt équivalent à une fois et demi le taux \
d'intérêt légal en vigueur à cette échéance.
Une indemnité de 40 euros forfaitaire sera demandée en sus pour chaque \
facture payée après l’échéance fixée. Celle-ci n’est pas soumise à TVA.""",
            ),
        ):
            mention = TaskMention(label=label, title=title, full_text=full_text)
            self.session.add(mention)
            self.session.flush()
            invoice_mentions.append(mention)

        for invoice in (
            Task.query()
            .filter(Task.type_.in_(Task.invoice_types))
            .options(load_only("id"))
        ):
            invoice.mandatory_mentions = invoice_mentions
            self.session.merge(invoice)

        estimation_mentions = []
        for label, title, full_text in (
            (
                "Informations sur l'acceptation des devis",
                "Acceptation du devis",
                """Le paiement anticipé ne donne droit à aucun escompte.
Les acomptes demandés ne sont pas des arrhes et ne permettent pas de renoncer \
au marché.
Les clients particuliers ou professionnels de moins de 6 salariés bénéficient \
d'un délai de rétractation de 14 jours. Aucun acompte ne pourra être versé \
pendant cette période.""",
            ),
        ):
            mention = TaskMention(label=label, title=title, full_text=full_text)
            self.session.add(mention)
            self.session.flush()
            estimation_mentions.append(mention)

        for estimation in Estimation.query().options(load_only("id")):
            estimation.mandatory_mentions = estimation_mentions
            self.session.merge(estimation)

        from caerp.models.project.mentions import BusinessTypeTaskMention

        for rel in BusinessTypeTaskMention.query():
            self.session.delete(rel)

        from caerp.models.project.types import BusinessType

        for btype in BusinessType.query():
            for mention in invoice_mentions:
                for doctype in ("invoice", "cancelinvoice"):
                    self.session.add(
                        BusinessTypeTaskMention(
                            doctype=doctype,
                            task_mention_id=mention.id,
                            business_type_id=btype.id,
                            mandatory=True,
                        )
                    )

            for mention in estimation_mentions:
                for doctype in ["estimation"]:
                    self.session.add(
                        BusinessTypeTaskMention(
                            doctype=doctype,
                            task_mention_id=mention.id,
                            business_type_id=btype.id,
                            mandatory=True,
                        )
                    )

    def _an_user(self):
        from caerp.models.user.login import Login
        from caerp.models.user.user import User

        counter = itertools.count()
        found_contractor = False
        for u in (
            self.session.query(User)
            .outerjoin(Login)
            .order_by(
                Login.active.desc(),  # active accounts first
                Login.id,
            )
        ):
            index = next(counter)
            u.user_prefs = {}
            if u.login:
                if index == 1:
                    u.login.login = "admin1"
                    u.login.groups = ["admin"]

                elif index == 2:
                    u.login.login = "manager1"
                    u.login.groups = ["manager"]

                elif not found_contractor and "contractor" in u.login.groups:
                    u.login.login = "entrepreneur1"
                    found_contractor = True
                else:
                    u.login.login = "user_{0}".format(index)

            u.lastname = self.faker.last_name()
            u.firstname = self.faker.first_name()
            u.email = self.faker.ascii_safe_email()
            if u.compte_tiers:
                u.compte_tiers = "N{}{}{}".format(
                    u.id,
                    u.firstname[:1],
                    u.lastname[:1],
                ).upper()
            if u.login:
                u.login.set_password(u.login.login)
            if u.has_userdatas():
                u.userdatas.coordonnees_lastname = u.lastname
                u.userdatas.coordonnees_firstname = u.firstname
                u.userdatas.coordonnees_email1 = u.email

    def _an_userdatas(self):
        from caerp.models.user.userdatas import (
            AidOrganismsDatas,
            AntenneOption,
            BankAccountsDatas,
            CareContractsDatas,
            CompanyDatas,
            UserDatas,
        )

        for u in self.session.query(UserDatas):
            u.coordonnees_ladies_lastname = self.faker.last_name_female()
            u.coordonnees_email2 = self.faker.ascii_safe_email()
            u.coordonnees_tel = self.faker.phone_number()[:14]
            u.coordonnees_mobile = self.faker.phone_number()[:14]
            u.coordonnees_address = self.faker.street_address()
            u.coordonnees_zipcode = self._zipcode()
            u.coordonnees_city = self.faker.city()
            u.coordonnees_birthplace = self.faker.city()
            u.coordonnees_birthplace_zipcode = self._zipcode()
            u.coordonnees_secu = "0 00 00 000 000 00"
            u.coordonnees_emergency_name = self.faker.name()
            u.coordonnees_emergency_phone = self.faker.phone_number()[:14]
            u.parcours_prescripteur_name = self.faker.name()
            u.parcours_goals = self.faker.text()

        for datas in self.session.query(CompanyDatas):
            datas.title = self.faker.company()
            datas.name = self.faker.company()
            datas.website = self.faker.url()

        for a in AntenneOption.query():
            a.label = "Antenne : {0}".format(self.faker.city())

        for datas in self.session.query(BankAccountsDatas):
            datas.iban = self.faker.iban()
            datas.bic = "ABCDEFGHI01"

        for datas in self.session.query(CareContractsDatas):
            datas.details = self.faker.text()

        for datas in self.session.query(AidOrganismsDatas):
            datas.details = self.faker.text()

    def _an_files(self):
        from caerp.models.company import Company
        from caerp.models.files import File

        for file_ in File.query():
            if not isinstance(file_.parent, Company):
                self.session.delete(file_)

        from caerp.models.files import Template

        sample_tmpl_path = os.path.abspath(resource_filename("sample_templates"))
        for filename in os.listdir(sample_tmpl_path):
            filepath = os.path.join(sample_tmpl_path, filename)
            if os.path.isfile(filepath):
                with open(filepath, "rb") as fbuf:
                    tmpl = Template(name=filename, description=filename)
                    tmpl.data = fbuf.read()
                    self.session.add(tmpl)

    def _an_celery_jobs(self):
        from caerp_celery.models import CsvImportJob, FileGenerationJob, Job, MailingJob

        for factory in (
            CsvImportJob,
            MailingJob,
            FileGenerationJob,
            Job,
        ):
            self.session.query(factory).delete()
            self.session.flush()

    def _an_accounting(self):
        from caerp.models.accounting.operations import AccountingOperation

        self.session.query(AccountingOperation).delete()
        self.session.flush()

    def _an_smtp_settings(self):
        from caerp.models.smtp import NodeSmtpHistory, SmtpSettings

        self.session.query(SmtpSettings).delete()
        self.session.query(NodeSmtpHistory).delete()
        self.session.flush()

    def run_from(self, method_name):
        """
        Runs all anonymization methods following method_name

        :param str method_name: The name with or without the _an_ prefix
        """
        if not method_name.startswith("_an_"):
            method_name = "_an_%s" % method_name

        methods = list(self.methods.keys())
        if method_name in methods:
            methods = methods[methods.index(method_name) :]

        for method in methods:
            self.run_method(method)

    def run_method(self, method_name):
        """
        Runs a single anonymization method

        :param str method_name: The name with or without the _an_ prefix
        """
        if not method_name.startswith("_an_"):
            method_name = "_an_%s" % method_name
        if method_name in self.methods:
            self.logger.debug("Step : {0}".format(method_name))
            self.methods[method_name]()
            transaction.commit()
            transaction.begin()

    def run(self):
        for key in self.methods:
            self.run_method(key)


def run_command(args, env):
    """
    Run command, run one or more anonymization method
    """
    logger = logging.getLogger(__name__)

    manager = Anonymizer(logger)
    if args.from_method is not None:
        manager.run_from(args.from_method)
    elif args.method is not None:
        manager.run_method(args.method)
    else:
        manager.run()


def list_command(args, env):
    """
    List available methods
    """
    logger = logging.getLogger(__name__)
    manager = Anonymizer(logger)
    for method in manager.methods:
        print(method)


def anonymize_entry_point():
    parser = argparse.ArgumentParser(description="enDI database anonymization utility")
    parser.add_argument("config_uri")

    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    run_parser = subparsers.add_parser("run", description=run_command.__doc__.strip())
    run_parser.add_argument("--method")
    run_parser.add_argument("--from-method")  # abbreviatied "--from" also works
    run_parser.set_defaults(func=run_command)

    list_parser = subparsers.add_parser(
        "list", description=list_command.__doc__.strip()
    )
    list_parser.set_defaults(func=list_command)

    def callback(arguments, env):
        return arguments.func(arguments, env)

    try:
        return argparse_command(callback, parser)
    finally:
        pass
