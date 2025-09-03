"""
Accounting module related schemas
"""
import datetime
import logging
import re

import colander
import deform
import deform_extensions
from colanderalchemy import SQLAlchemySchemaNode
from sqlalchemy import distinct, select

from caerp import forms
from caerp.compute.parser import NumericStringParser
from caerp.forms.custom_types import CsvTuple, QuantityType
from caerp.forms.fields import YearPeriodSchema
from caerp.forms.lists import BaseListsSchema
from caerp.forms.widgets import CleanMappingWidget
from caerp.models.accounting.accounting_closures import AccountingClosure
from caerp.models.accounting.balance_sheet_measures import (
    ActiveBalanceSheetMeasureType,
    BalanceSheetMeasureGrid,
    PassiveBalanceSheetMeasureType,
)
from caerp.models.accounting.income_statement_measures import (
    IncomeStatementMeasureGrid,
    IncomeStatementMeasureType,
    IncomeStatementMeasureTypeCategory,
)
from caerp.models.accounting.operations import AccountingOperation
from caerp.models.accounting.treasury_measures import (
    TreasuryMeasureGrid,
    TreasuryMeasureType,
    TreasuryMeasureTypeCategory,
)
from caerp.models.company import Company
from caerp.utils.accounting import get_current_financial_year_value

logger = logging.getLogger(__name__)


class PeriodSchema(colander.MappingSchema):
    """
    A form used to select a period
    """

    is_range = True

    start = colander.SchemaNode(
        colander.Date(),
        title="Remontées entre le",
        description="",
        default=datetime.date(datetime.date.today().year, 1, 1),
        missing=colander.drop,
    )
    end = colander.SchemaNode(
        colander.Date(),
        title="et le",
        description="",
        default=None,
        missing=colander.drop,
    )


class DebitAmountRangeSchema(colander.MappingSchema):
    """
    Used to filter on a range of debit amount
    """

    is_range = True

    start = colander.SchemaNode(
        colander.Float(),
        title="Montant au débit entre",
        missing=colander.drop,
        description="",
    )
    end = colander.SchemaNode(
        colander.Float(),
        title="et",
        missing=colander.drop,
        description="",
    )


class CreditAmountRangeSchema(colander.MappingSchema):
    """
    Used to filter on a range of credit amount
    """

    is_range = True

    start = colander.SchemaNode(
        colander.Float(),
        title="Montant au crédit entre",
        missing=colander.drop,
        description="",
    )
    end = colander.SchemaNode(
        colander.Float(),
        title="et",
        missing=colander.drop,
        description="",
    )


COMPLEX_TOTAL_HELP = """
    Combiner plusieurs catégories et indicateurs au travers d’opérations
    arithmétiques.
    Les noms des variables (catégories ou indicateurs) doivent être encadrés 
 de {}.<br />
    Exemple : {Salaires et Cotisations} + {Charges} / 100.
    <br ><strong>Liste des catégories :</strong><br /> %s <br /><strong>Liste 
 des indicateurs :</strong><br /> %s"""


def get_upload_list_schema():
    """
    Build a schema for Accounting Operation upload listing
    """
    schema = BaseListsSchema().clone()
    del schema["search"]

    schema.insert(
        0,
        colander.SchemaNode(
            colander.String(),
            name="filetype",
            title="Type de fichier",
            widget=deform.widget.SelectWidget(
                values=(
                    ("all", "Tous"),
                    ("general_ledger", "Grand livre"),
                    ("analytical_balance", "Balance analytique"),
                )
            ),
            default="all",
            missing=colander.drop,
        ),
    )
    schema.insert(
        0,
        YearPeriodSchema(
            name="period",
            title="",
            widget=CleanMappingWidget(),
            missing=colander.drop,
        ),
    )
    return schema


@colander.deferred
def deferred_analytical_account_widget(node, kw):
    """
    Defer analytical widget
    """
    query = select(distinct(AccountingOperation.analytical_account)).order_by(
        AccountingOperation.analytical_account
    )

    data = kw["request"].dbsession.execute(query).scalars().all()
    values = list(zip(data, data))
    default_option = ("", "Tous")
    values.insert(0, default_option)
    # Use of placeholder arg is mandatory with Select2 ; otherwise, the
    # clear button crashes. https://github.com/select2/select2/issues/5725
    return deform.widget.Select2Widget(
        values=values,
        placeholder=default_option[1],
    )


@colander.deferred
def deferred_general_account_widget(node, kw):
    """
    Defer analytical widget
    """
    query = select(distinct(AccountingOperation.general_account)).order_by(
        AccountingOperation.general_account
    )

    data = kw["request"].dbsession.execute(query).scalars().all()

    values = list(zip(data, data))
    default_option = ("", "Tous")
    values.insert(0, default_option)
    # Use of placeholder arg is mandatory with Select2 ; otherwise, the
    # clear button crashes. https://github.com/select2/select2/issues/5725
    return deform.widget.Select2Widget(
        values=values,
        placeholder=default_option[1],
    )


def _get_company_id_filter(node, kw):
    """
    Defer the company id selection widget
    """
    query = select(distinct(AccountingOperation.company_id))
    company_ids = kw["request"].dbsession.execute(query).scalars().all()
    return Company.id.in_(company_ids)


def get_operation_list_schema():
    """
    Build a schema listing operations
    """
    schema = BaseListsSchema().clone()
    del schema["search"]
    schema.insert(
        0,
        colander.SchemaNode(
            colander.Boolean(),
            name="include_associated",
            title="",
            label="Inclure les opérations associées à une enseigne",
            default=True,
            missing=colander.drop,
        ),
    )
    schema.insert(
        0,
        colander.SchemaNode(
            colander.String(),
            name="analytical_account",
            title="Compte analytique",
            widget=deferred_analytical_account_widget,
            missing=colander.drop,
        ),
    )
    schema.insert(
        0,
        colander.SchemaNode(
            colander.String(),
            name="general_account",
            title="Compte général",
            widget=deferred_general_account_widget,
            missing=colander.drop,
        ),
    )
    schema.insert(
        0,
        colander.SchemaNode(
            colander.Integer(),
            name="company_id",
            title="Enseigne",
            widget=forms.get_deferred_model_select(
                Company,
                filters=(_get_company_id_filter,),
                keys=("id", "name"),
                empty_filter_msg="Toutes",
                widget_class=deform.widget.Select2Widget,
            ),
            missing=colander.drop,
        ),
    )

    return schema


def get_company_general_ledger_operations_list_schema():
    """
    Build a schema for company general ledger listing operations
    """
    schema = BaseListsSchema().clone()
    del schema["search"]
    schema.insert(
        0,
        colander.SchemaNode(
            colander.String(),
            name="general_account",
            title="Compte général",
            widget=deferred_general_account_widget,
            missing=colander.drop,
        ),
    )
    schema.insert(
        1,
        PeriodSchema(
            name="period",
            title="",
            validator=colander.Function(
                forms.range_validator,
                msg="La date de début doit précéder la date de fin",
            ),
            widget=CleanMappingWidget(),
            missing=colander.drop,
        ),
    )
    schema.insert(
        2,
        DebitAmountRangeSchema(
            name="debit",
            title="",
            validator=colander.Function(
                forms.range_validator,
                msg=("Le montant minimal doit être inférieur ou égal au maximum"),
            ),
            widget=CleanMappingWidget(),
            missing=colander.drop,
        ),
    )
    schema.insert(
        3,
        CreditAmountRangeSchema(
            name="credit",
            title="",
            validator=colander.Function(
                forms.range_validator,
                msg=("Le montant minimal doit être inférieur ou égal au maximum"),
            ),
            widget=CleanMappingWidget(),
            missing=colander.drop,
        ),
    )

    return schema


def get_upload_treasury_list_schema():
    """
    Build the schema used to list treasury measure grids by upload
    """
    schema = BaseListsSchema().clone()
    del schema["search"]
    schema.insert(
        0,
        colander.SchemaNode(
            colander.Integer(),
            name="company_id",
            title="Enseigne",
            widget=forms.get_deferred_model_select(
                Company,
                filters=(_get_company_id_filter,),
                keys=("id", "name"),
                empty_filter_msg="Toutes",
                widget_class=deform.widget.Select2Widget,
            ),
            missing=colander.drop,
        ),
    )
    return schema


def get_treasury_measures_list_schema(company_id=None):
    """
    Build the schema used to list treasury measures

    :returns: A form schema
    :rtype: colander.Schema
    """
    schema = BaseListsSchema().clone()
    del schema["search"]

    def get_year_options(kw):
        context = kw["request"].context
        if isinstance(context, TreasuryMeasureGrid):
            cid = TreasuryMeasureGrid.company_id
        else:
            cid = context.id
        cid = company_id or cid
        return TreasuryMeasureGrid.get_years(cid)

    node = forms.year_filter_node(
        name="year",
        query_func=get_year_options,
        title="Année de dépôt",
    )

    schema.insert(0, node)
    return schema


def get_income_statement_measures_list_schema(company_id=None):
    """
    Build the schema used to list income statement measures

    :returns: A form schema
    :rtype: colander.Schema
    """
    schema = BaseListsSchema().clone()
    del schema["search"]
    del schema["page"]
    del schema["items_per_page"]

    def get_year_options(kw):
        cid = company_id or kw["request"].context.get_company_id()
        years = IncomeStatementMeasureGrid.get_years(company_id=cid)
        current_year = datetime.date.today().year
        next_year = current_year + 1
        if current_year not in years:
            years.append(current_year)
        if next_year not in years:
            years.append(next_year)
        return years

    def _defered_config_bool(key):
        @colander.deferred
        def f(node, kw):
            result = False
            if kw["request"].config.get_value(key, type_=bool, default=True):
                result = True

            return result

        return f

    def _defered_default_financial_year_value():
        @colander.deferred
        def f(node, kw):
            return get_current_financial_year_value()

        return f

    schema.insert(
        0,
        colander.SchemaNode(
            colander.Boolean(),
            name="show_zero_rows",
            title="",
            label="Afficher les lignes à zéro",
            missing=colander.drop,
            default=_defered_config_bool("income_statement_default_show_zero_rows"),
            widget=deform.widget.CheckboxWidget(toggle=True),
        ),
    )
    schema.insert(
        0,
        colander.SchemaNode(
            colander.Boolean(),
            name="show_decimals",
            title="",
            label="Afficher les décimales",
            default=_defered_config_bool("income_statement_default_show_decimals"),
            missing=colander.drop,
            widget=deform.widget.CheckboxWidget(toggle=True),
        ),
    )

    schema.insert(
        0,
        forms.year_select_node(
            name="year",
            query_func=get_year_options,
            title="Année",
            default=_defered_default_financial_year_value(),
        ),
    )

    return schema


def get_balance_sheet_measures_list_schema(company_id=None):
    """
    Build the schema used to list balance sheet measures

    :returns: A form schema
    :rtype: colander.Schema
    """
    schema = BaseListsSchema().clone()
    del schema["search"]
    del schema["page"]
    del schema["items_per_page"]

    def get_year_options(kw):
        cid = company_id or kw["request"].context.get_company_id()
        years = BalanceSheetMeasureGrid.get_years(company_id=cid)
        return years

    node = forms.year_select_node(
        name="year", query_func=get_year_options, title="Année"
    )

    schema.insert(0, node)

    return schema


def get_deferred_widget_categories(category_class):
    """
    Returns a deferred widget used to select one or more categories
    """

    @colander.deferred
    def deferred_categories_widget(node, kw):
        query = select(category_class.label).where(category_class.active == True)

        data = kw["request"].dbsession.execute(query).scalars().all()
        choices = zip(data, data)
        return deform.widget.CheckboxChoiceWidget(values=choices)

    return deferred_categories_widget


def get_deferred_complex_total_description(category_class, type_class):
    """
    Returns a deferred description for the complex total configuration
    """

    @colander.deferred
    def deferred_description(node, kw):
        categories = "<br />".join(
            (f"- {i.label}" for i in category_class.get_categories(keys=("label",)))
        )
        types = "<br />".join(
            (f"- {i.label}" for i in type_class.get_types(keys=("label",)))
        )

        return COMPLEX_TOTAL_HELP % (categories, types)

    return deferred_description


def accounting_closure_year_validator(node, year):
    year_closure = AccountingClosure.query().filter_by(year=year).all()

    if year_closure:
        raise colander.Invalid(node, "L’année de clôture existe déjà.")


def get_deferred_label_validator(measure_class, is_edit):
    @colander.deferred
    def deferred_label_validator(node, kw):
        """
        Check whether a type or a category already has the same label
        """
        context = kw["request"].context
        dbsession = kw["request"].dbsession

        checked_classes = []
        income_classes = [
            IncomeStatementMeasureTypeCategory,
            IncomeStatementMeasureType,
        ]
        treasury_classes = [
            TreasuryMeasureTypeCategory,
            TreasuryMeasureType,
        ]

        if measure_class in income_classes:
            checked_classes = income_classes
        if measure_class in treasury_classes:
            checked_classes = treasury_classes

        accounting_labels = []
        for class_ in checked_classes:
            query = dbsession.query(class_.label)
            query = query.filter_by(active=True)
            if is_edit and isinstance(context, class_):
                query = query.filter(class_.id != context.id)
            accounting_labels += [i[0] for i in query]

        def label_validator(node, value):
            forbidden_chars = [":", "!", ",", "."]
            if any([char in value for char in forbidden_chars]):
                raise colander.Invalid(
                    node,
                    "Erreur de syntaxe (les caractères ':', '!', '.' et ',' sont interdits)",
                )
            if value in accounting_labels:
                raise colander.Invalid(
                    node,
                    "Une catégorie ou un indicateur porte déjà ce nom",
                )

        return label_validator

    return deferred_label_validator


BRACES_REGEX = re.compile(r"\{([^}]+)\}\s?")


def complex_total_validator(node, value):
    """
    Validate the complex total syntax
    """
    if len(value) > 254:
        raise colander.Invalid(node, "Ce champ est limité à 255 caractères")

    if value.count("{") != value.count("}"):
        raise colander.Invalid(node, "Erreur de syntaxe")

    fields = BRACES_REGEX.findall(value)

    format_dict = dict((field, 1) for field in fields)
    try:
        temp = value.format(**format_dict)
    except Exception as err:
        raise colander.Invalid(node, "Erreur de syntaxe : {0}".format(err))

    parser = NumericStringParser()
    try:
        parser.parse(temp)
    except Exception as err:
        raise colander.Invalid(node, "Erreur de syntaxe : {0}".format(err))


def get_admin_accounting_measure_type_schema(subclass, is_edit, total=False):
    """
    Build the schema for accounting measure type edit/add

    Total types are more complex and can be :

        * The sum of categories
        * A list of account prefix (like the common type of measure_types)

    :param class subclass: The child class we want to edit
    (IncomeStatementMeasureTypeCategory or TreasuryMeasureTypeCategory)
    :param bool total: Are we editing a total type ?
    """
    if total:
        if subclass == IncomeStatementMeasureType:
            category_class = IncomeStatementMeasureTypeCategory
        else:
            category_class = TreasuryMeasureTypeCategory

        schema = SQLAlchemySchemaNode(
            subclass,
            includes=(
                "category_id",
                "label",
                "account_prefix",
                "is_total",
                "order",
                "invert_default_cd_or_dc",
            ),
        )
        schema["label"].validator = get_deferred_label_validator(subclass, is_edit)
        schema["is_total"].widget = deform.widget.HiddenWidget()
        schema.add_before(
            "account_prefix",
            colander.SchemaNode(
                colander.String(),
                name="total_type",
                title="Cet indicateur est il défini comme :",
                widget=deform_extensions.RadioChoiceToggleWidget(
                    values=(
                        (
                            "categories",
                            "La somme des indicateurs de une ou plusieurs "
                            "catégories ?",
                            "categories",
                        ),
                        (
                            "account_prefix",
                            "Un groupement d’écritures ?",
                            "account_prefix",
                        ),
                        (
                            "complex_total",
                            "Le résultat d’une formule arithmétique basée sur "
                            "les catégories et les indicateurs ?",
                            "complex_total",
                        ),
                    )
                ),
                missing=colander.drop,
            ),
        )
        schema["account_prefix"].missing = ""

        deferred_description = get_deferred_complex_total_description(
            category_class, subclass
        )
        schema.add(
            colander.SchemaNode(
                colander.String(),
                name="complex_total",
                title="Combinaison complexe de catégories et d’indicateurs",
                description=deferred_description,
                validator=complex_total_validator,
                missing="",
            )
        )

        if (
            subclass == ActiveBalanceSheetMeasureType
            or subclass == PassiveBalanceSheetMeasureType
        ):
            deferred_widget = deform.widget.CheckboxChoiceWidget(
                values=(("active", "Actif"), ("passive", "Passif"))
            )
        else:
            deferred_widget = get_deferred_widget_categories(category_class)

        schema.add(
            colander.SchemaNode(
                CsvTuple(),
                name="categories",
                title="Somme des catégories",
                description="Représentera la somme des catégories " "sélectionnées",
                widget=deferred_widget,
            )
        )

        default_wording = "Non inversé"
        not_default_wording = "Inversé"

    else:
        schema = SQLAlchemySchemaNode(subclass, excludes=("is_total", "categories"))
        schema["label"].validator = get_deferred_label_validator(subclass, is_edit)
        if subclass == IncomeStatementMeasureType:
            default_wording = "Crédit - Débit"
            not_default_wording = "Débit - Crédit"
        else:
            default_wording = "Débit - Crédit"
            not_default_wording = "Crédit - Débit"

    schema.add(
        colander.SchemaNode(
            colander.Int(),
            name="invert_default_cd_or_dc",
            title="Convention de signe :",
            missing=0,
            default=0,
            widget=deform.widget.RadioChoiceWidget(
                values=(
                    (
                        0,
                        default_wording,
                    ),
                    (
                        1,
                        not_default_wording,
                    ),
                )
            ),
        ),
    )

    return schema


def get_admin_accounting_type_category_schema(subclass, is_edit):
    """
    Build the schema for accounting type category add/edit

    :param class subclass: The child class we want to edit
    (IncomeStatementMeasureTypeCategory or TreasuryMeasureTypeCategory)
    """
    schema = SQLAlchemySchemaNode(subclass, includes=("label", "order"))
    schema["label"].validator = get_deferred_label_validator(subclass, is_edit)
    return schema


def get_admin_accounting_closure_schema(subclass):
    """
    Build the schema for accounting closure add

    :param class subclass: The child class we want to edit
    (AcccountingClosure)
    """
    schema = SQLAlchemySchemaNode(subclass, includes=("year", "active"))
    schema["year"].validator = accounting_closure_year_validator
    return schema


def get_admin_general_ledger_account_wording_schema(subclass):
    """
    Build the schema for account wording add

    :param class subclass: The child class we want to edit
    (AcccountingClosure)
    """
    schema = SQLAlchemySchemaNode(subclass)
    return schema


def get_add_edit_accounting_operation_schema():
    """
    Build a schema for AccountingOperation add/edit
    """
    excludes = ("id", "upload_id", "company_id")

    schema = SQLAlchemySchemaNode(AccountingOperation, excludes=excludes)
    forms.customize_field(schema, "label", preparer=forms.truncate_preparer(80))
    for field in "debit", "credit", "balance":
        forms.customize_field(schema, field, typ=QuantityType())
    return schema
