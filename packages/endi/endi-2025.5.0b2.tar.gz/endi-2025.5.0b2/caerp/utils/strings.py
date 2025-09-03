"""
Common translation strings
"""

import calendar
import locale
import re
import secrets
import string
import unicodedata
from typing import List, Optional

from webhelpers2.html import literal

from caerp.compute import math_utils
from caerp.utils.ascii import force_ascii
from caerp.utils.datetimes import format_date

SINGLE_STATUS_LABELS = {
    "draft": "Brouillon",
    "wait": "En attente de validation",
    "valid": "Validé{genre}",
    "invalid": "Invalidé{genre}",
}

DEF_STATUS = "Statut inconnu"

STATUS = dict(
    (
        (
            "draft",
            "Repassé en brouillon",
        ),
        (
            "wait",
            "Validation demandée",
        ),
        ("valid", "Validé{genre}"),
        (
            "invalid",
            "Invalidé{genre}",
        ),
        # Legacy messages of Expense (Communication class)
        ("unknown", ""),
    )
)

STATUS_SENTENCES = dict(
    (
        (
            "draft",
            "est un brouillon",
        ),
        (
            "wait",
            "est en attente de validation",
        ),
        ("valid", "a été validée"),
        ("invalid", "est invalide"),
    )
)
DEF_STATUS_SENTENCE = "est dans un état inconnu"

ESTIMATION_STATUS = dict(
    (
        (
            "aborted",
            "Sans suite",
        ),
        (
            "sent",
            "Envoyé",
        ),
        (
            "signed",
            "Signé",
        ),
        ("waiting", "En attente de réponse"),
        ("geninv", "Factures générées"),
    )
)

INVOICE_STATUS = dict(
    (
        (
            "paid",
            "Payée partiellement",
        ),
        (
            "resulted",
            "Soldée",
        ),
    )
)

JUSTIFIED_STATUS = dict(
    (
        ("waiting", "En attente de justificatifs"),
        ("justified", "Justificatifs reçus"),
    )
)

PAID_STATUS = dict(
    (
        ("paid", "Payée partiellement"),
        ("resulted", "Payée intégralement"),
        ("justified", "Justificatifs reçus"),
    )
)

ACTIVITY_STATUS = dict(
    (
        (
            "closed",
            "Terminée",
        ),
        (
            "planned",
            "Planifiée",
        ),
    )
)

URSSAF3P_REGISTRATION_STATUS = dict(
    (
        ("disabled", "URSSAF : désactivé"),
        ("wait", "URSSAF : validation requise"),
        ("valid", "URSSAF : validé"),
    )
)

INDICATOR_STATUS_LABELS = {
    "danger": "Obligation non satisfaite",
    "warning": "Recommandation non satisfaite",
    "success": "Recommandation/obligation validée",
}
INDICATOR_VALIDATION_STATUS_LABELS = {
    "valid": "Validé",
    "invalid": "Invalidé par l'équipe d'appui",
    "wait": "En attente de validation",
    "none": "N'est pas soumis à validation",
}

TASKTYPES_LABEL = dict(
    invoice="Facture",
    internalinvoice="Facture interne",
    estimation="Devis",
    internalestimation="Devis interne",
    cancelinvoice="Avoir",
    internalcancelinvoice="Avoir interne",
)

# Intended as the big dictionary of strings relative to app models
# uses class name as key, because not everyone has a type_ column
# MODEL_STRINGS[model.__class__.__name__]
MODELS_STRINGS = dict(
    Invoice=dict(
        label="Facture",
    ),
    InternalInvoice=dict(
        label="Facture interne",
    ),
    Estimation=dict(
        label="Devis",
    ),
    InternalEstimation=dict(
        label="Devis interne",
    ),
    CancelInvoice=dict(
        label="Avoir",
    ),
    ExpenseSheet=dict(
        label="Note de dépenses",
        sentence_start="Cette note de dépenses",
    ),
    SupplierOrder=dict(
        label="Commande fournisseur",
        sentence_start="Cette commande fournisseur",
    ),
    InternalSupplierOrder=dict(
        label="Commande fournisseur interne",
        sentence_start="Cette commande fournisseur interne",
    ),
    SupplierInvoice=dict(
        label="Facture fournisseur",
        sentence_start="Cette facture fournisseur",
    ),
    InternalSupplierInvoice=dict(
        label="Facture fournisseur interne",
        sentence_start="Cette facture fournisseur interne",
    ),
)


def format_status_string(status: "StatusLogEntry", genre=""):
    """
    Return a label for the given status

    :param str code: StatusLogEntry
    :param str genre: '' or 'e'
    """
    code = status.status

    if status.state_manager_key == "justified_status":
        result = JUSTIFIED_STATUS[code]
    elif status.state_manager_key == "urssaf3p_registration_status":
        result = URSSAF3P_REGISTRATION_STATUS[code]
    elif code in ESTIMATION_STATUS:
        result = ESTIMATION_STATUS[code]
    elif code in INVOICE_STATUS:
        result = INVOICE_STATUS[code]
    else:
        result = STATUS.get(code, code)

    return result.format(genre=genre)


def get_genre(obj):
    if obj.type_ in (
        "invoice",
        "expensesheet",
        "internalinvoice",
        "supplier_invoice",
        "supplier_order",
        "internalsupplier_invoice",
        "internalsupplier_order",
    ):
        genre = "e"
    else:
        genre = ""
    return genre


def format_main_status(obj, full=True):
    """
    return a formatted status string
    """
    status = obj.status

    genre = get_genre(obj)

    if full:
        user = obj.status_user

        status_str = STATUS.get(status, DEF_STATUS).format(genre=genre)
        suffix = " par {0} le {1}".format(
            format_account(user), format_date(obj.status_date)
        )
        status_str += suffix
    else:
        status_str = SINGLE_STATUS_LABELS.get(status, DEF_STATUS).format(genre=genre)

    return status_str


def format_estimation_status(estimation, full=True):
    """
    Return a formatted string for estimation specific status
    """
    if estimation.geninv:
        return ESTIMATION_STATUS.get("geninv")
    elif estimation.signed_status in ("sent", "aborted", "signed"):
        return ESTIMATION_STATUS.get(estimation.signed_status)
    else:
        return format_main_status(estimation, full)


def format_invoice_status(invoice, full=True):
    """
    Return a formatted string for invoice specific status

    :param obj invoice: An invoice instance
    """
    if invoice.paid_status in ("paid", "resulted"):
        return INVOICE_STATUS.get(invoice.paid_status)
    else:
        return format_main_status(invoice, full)


def format_cancelinvoice_status(cinvoice, full=True):
    """
    Return a string representing the state of this cancelinvoice

    :param obj cinvoice: A CancelInvoice instance
    """
    return format_main_status(cinvoice, full)


def format_sent_by_email_status(task, last_smtp_history):
    if not last_smtp_history:
        return ""
    genre = get_genre(task)
    date = format_date(last_smtp_history.created_at)
    return f"Envoyé{genre} par e-mail au client le {date}"


def _format_payable_status(obj, full=True):
    """
    Return a single status string for an obj with paid+validation status status
    and a paid status.
    """
    if obj.paid_status in ("paid", "resulted"):
        status_str = PAID_STATUS.get(obj.paid_status)
    else:
        status_str = STATUS.get(obj.status, DEF_STATUS).format(genre="e")
        if full:
            if obj.status_user:
                account = format_account(obj.status_user)
            elif hasattr(obj, "user") and obj.user is not None:
                account = format_account(obj.user)
            else:
                account = None
            date = format_date(obj.status_date)

            if account:
                status_str += " par {}".format(account)

            status_str += " le {}".format(date)

    return status_str


def format_expense_status(expense, full=True):
    return _format_payable_status(expense, full)


def format_supplier_invoice_status(supplier_invoice, full=True):
    return _format_payable_status(supplier_invoice, full)


def format_supplier_order_status(supplier_order, full=True):
    if supplier_order.supplier_invoice:
        return f"{format_main_status(supplier_order)} ; Attaché à une facture"
    else:
        return format_main_status(supplier_order)


def format_status(element, full=True):
    if element.type_ in ("supplier_order", "internalsupplier_order"):
        return format_supplier_order_status(element, full)
    elif element.type_ in ("supplier_invoice", "internalsupplier_invoice"):
        return format_supplier_invoice_status(element, full)
    elif element.type_ in ("estimation", "internalestimation"):
        return format_estimation_status(element, full)
    elif element.type_ in ("invoice", "internalinvoice"):
        return format_invoice_status(element, full)
    elif element.type_ in ["cancelinvoice", "internalcancelinvoice"]:
        return format_cancelinvoice_status(element, full)
    elif element.type_ == "expensesheet":
        return format_expense_status(element, full)


def format_expense_status_sentence(expense):
    if expense.paid_status == "resulted":
        return "a été intégralement payée"
    elif expense.paid_status == "paid":
        return "a été partiellement payée"
    else:
        return STATUS_SENTENCES[expense.status]


def format_status_sentence(element):
    """
    Same as format status but with a full sentence.

    E.g.: « Cette note de dépenses a été validée. »
    """
    try:
        prefix = MODELS_STRINGS[element.__class__.__name__]["sentence_start"]
    except KeyError:
        prefix = "Ce document "

    try:
        if element.__class__.__name__ == "ExpenseSheet":
            status_sentence = format_expense_status_sentence(element)
        else:
            status_sentence = STATUS_SENTENCES[element.status]
    except KeyError:
        status_sentence = DEF_STATUS_SENTENCE

    return "{} {}".format(prefix, status_sentence)


def format_valid_status_message(request, element):
    el = element
    action = "a bien été validé"

    if el.type_ in ("supplier_order", "internalsupplier_order"):
        str = f"La commande fournisseur '{el.name}' {action}e !"
        el_url = request.route_path("/supplier_orders/{id}", id=el.id)
        pdf_url = None
    elif el.type_ in ("supplier_invoice", "internalsupplier_invoice"):
        str = f"La facture fournisseur {el.official_number} {action}e !"
        el_url = request.route_path("/supplier_invoices/{id}", id=el.id)
        pdf_url = None
    elif el.type_ in ("estimation", "internalestimation"):
        str = f"Le devis '{el.name}' ({el.get_short_internal_number()}) {action} !"
        el_url = request.route_path("/estimations/{id}", id=el.id)
        pdf_url = el_url + ".pdf"
    elif el.type_ in ("invoice", "internalinvoice"):
        str = f"La facture {el.official_number} {action}e !"
        el_url = request.route_path("/invoices/{id}", id=el.id)
        pdf_url = el_url + ".pdf"
    elif el.type_ in ("cancelinvoice", "internalcancelinvoice"):
        str = f"L'avoir {el.official_number} {action} !"
        el_url = request.route_path("/cancelinvoices/{id}", id=el.id)
        pdf_url = el_url + ".pdf"
    elif el.type_ == "expensesheet":
        str = "La note de dépenses {} de {} sur {} {} {}e !".format(
            el.official_number,
            el.user.label,
            month_name(el.month),
            el.year,
            action,
        )
        el_url = request.route_path("/expenses/{id}", id=el.id)
        pdf_url = None
    else:
        return None

    validation_message = str
    if el_url:
        validation_message += f"""
        &nbsp; <a href='{el_url}' class='btn' target='_blank'>
            Voir le document
        </a>"""
    if pdf_url:
        validation_message += f"""
        &nbsp; <a href='{pdf_url}' class='btn' download>
            Télécharger le PDF
        </a>"""
    return validation_message


def estimation_get_major_status(estimation):
    """
    Return the most significant status for the given task
    """
    res = "draft"
    if estimation.geninv:
        res = "geninv"
    elif estimation.signed_status != "waiting":
        res = estimation.signed_status
    else:
        res = estimation.status
    return res


def invoice_get_major_status(invoice):
    """
    Return the most significant status for the given task
    """
    res = "draft"
    if invoice.paid_status != "waiting":
        res = invoice.paid_status
    else:
        res = invoice.status
    return res


def cancelinvoice_get_major_status(cinvoice):
    """
    Return the most significant status for the given task
    """
    return cinvoice.status


def expense_get_major_status(expense):
    if expense.paid_status != "waiting":
        return expense.paid_status
    elif expense.status == "waiting" and expense.justified:
        return "justified"
    else:
        return expense.status


def supplier_order_get_major_status(order):
    return order.status


def supplier_invoice_get_major_status(invoice):
    return invoice.status


def major_status(element):
    if element.type_ in ("estimation", "internalestimation"):
        return estimation_get_major_status(element)
    elif element.type_ in ("invoice", "internalinvoice"):
        return invoice_get_major_status(element)
    elif element.type_ in ("cancelinvoice", "internalcancelinvoice"):
        return cancelinvoice_get_major_status(element)
    elif element.type_ == "expensesheet":
        return expense_get_major_status(element)
    elif element.type_ in ("supplier_order", "internalsupplier_order"):
        return supplier_order_get_major_status(element)
    elif element.type_ in ("supplier_invoice", "internalsupplier_invoice"):
        return supplier_invoice_get_major_status(element)


def format_activity_status(activity):
    """
    Return a formatted status string for the given activity
    """
    status_str = ACTIVITY_STATUS.get(activity.status, DEF_STATUS)
    return status_str


def format_indicator_status(status: str) -> str:
    """
    Return a formatted status string for the given indicator
    """
    return INDICATOR_STATUS_LABELS.get(status, "inconnu")


def format_indicator_main_status(indicator) -> str:
    """Returns the main status of the given status"""
    status = ""
    if getattr(indicator, "validation", False):
        status = INDICATOR_VALIDATION_STATUS_LABELS.get(
            indicator.validation_status, "Inconnu"
        )
    else:
        status = format_indicator_status(indicator.status)
    return status


def format_account(account, reverse=True, upper=True):
    """
    return {firstname} {lastname}
    """
    if hasattr(account, "firstname"):
        firstname = account.firstname
        lastname = account.lastname
    elif hasattr(account, "coordonnees_firstname"):
        firstname = account.coordonnees_firstname
        lastname = account.coordonnees_lastname
    else:
        firstname = "Inconnu"
        lastname = ""
    return format_name(firstname, lastname, reverse, upper)


def format_name(firstname, lastname, reverse=True, upper=True):
    """
    format firstname and lastname in a common format
    """
    if firstname is None:
        firstname = ""
    if lastname is None:
        lastname = ""
    firstname = firstname.capitalize()
    if upper:
        lastname = lastname.upper()
    else:
        lastname = lastname.capitalize()
    if reverse:
        return "{0} {1}".format(lastname, firstname)
    else:
        return "{0} {1}".format(firstname, lastname)


def add_trailing_zeros(amount):
    """
    Ensure an amount has sufficient trailing zeros
    """
    if "," in amount:
        dec = len(amount) - (amount.index(",") + 1)
        if dec <= 2:
            for i in range(0, 2 - dec):
                amount += "0"
    return amount


def remove_kms_training_zeros(amount):
    """
    Removed unnecessary kms amount training zeros
    :param amount:
    :return: amount
    """
    if "," in amount:
        dec = len(amount) - amount.index(",")
        ints = [i for i in list(amount[-dec:]) if i != "," and i != "0"]
        if len(ints) == 0:
            amount = amount[:-dec]
    return amount


def integer_to_decimal_string(
    integer: int,
    precision: int = 2,
    separator: str = ".",
) -> str:
    """
    Convert an integer to a decimal string without locale or grouping specific

    :param int integer: The integer to convert
    :param int precision: The decimal precision the integer represents
    :param str separator: The decimal separator
    """
    int_string = str(integer)
    if len(int_string) <= precision:
        return "0." + int_string.zfill(precision)
    else:
        return f"{int_string[:-precision]}{separator}{int_string[-precision:]}"


def format_amount(
    amount,
    trim=True,
    grouping=True,
    precision=2,
    display_precision=None,
    html=True,
    currency=False,
):
    """
    return a pretty printable amount

    :param int amount: The amount to display
    :param bool trim: Should the amount be trimmed
    :param bool grouping: Should the amount be grouped (grouping form depends
    on locales)
    :param int precision: The decimal precision to convert the amount to
    (Decimal amounts are stored as BigInteger in the database to avoid float
    precision conflicts and facilitate computation, here precision indicates
    with which 10**precision the conversion is made)
    :param int display_precision: The precision used to display the amount
    (trimming strategy)
    """
    resp = ""
    if amount is not None:
        dividor = 10.0**precision
        # Set a default display precision
        if display_precision is None:
            display_precision = precision

        # Limit to 2 trailing zeros
        if isinstance(amount, float) and precision <= 2:
            if amount == int(amount):
                trim = True
        elif precision > 2:
            if (
                math_utils.floor_to_precision(
                    amount, precision=2, dialect_precision=precision
                )
                == amount
            ):
                trim = True

        if trim:
            formatter = "%.2f"
            amount = int(amount) / dividor
            resp = locale.format_string(formatter, amount, grouping=grouping)
        else:
            formatter = "%.{0}f".format(display_precision)
            amount = amount / dividor
            resp = locale.format_string(formatter, amount, grouping=grouping)
            resp = resp.rstrip("0")
            resp = add_trailing_zeros(resp)

        if grouping and html:
            resp = resp.replace(" ", "&nbsp;")
            resp = resp.replace("\u202f", "&nbsp;")

        if currency:
            if html:
                resp = resp + "&nbsp;$euro;"
            else:
                resp = resp + " €"

    # Turn of escaping, otherwise, &nbsp appers verbatim
    return literal(resp)


RE_DECIMAL_PART = re.compile(
    r"{locale_decimal_separator}\d+".format(
        locale_decimal_separator=locale.localeconv()["decimal_point"]
    )
)


def format_float(value, precision=None, grouping=True, html=True, wrap_decimals=False):
    """
    Format a float value :
        * Localized version with grouped values
        * trim datas to precision if asked for

    :param float value: The value to format
    :param int precision: If set, the value will be trimmed to that precision
    :param bool grouping: Should the datas be grouped (by thousands)
    :param bool html: Should the resulting string be html-friendly (using
    &nbsp;)
    :returns: A formatted string that can be used in html outputs
    :rtype: str
    """
    # En python la valeur -0.0 existe et donne une sortie visuellement
    # indésirable
    if value == 0:
        value = 0.0
    if isinstance(value, (float, int)):
        if precision is not None:
            formatter = "%.{0}f".format(precision)
        else:
            formatter = "%s"
        value = locale.format_string(formatter, value, grouping=grouping)

        # des versions de locale fourniss
        if html:
            value = value.replace(" ", "&nbsp;")
            value = value.replace("\u202f", "&nbsp;")
            if wrap_decimals:
                # wrap decimal part in a span
                value = RE_DECIMAL_PART.sub(
                    r'<span class="decimal-part">\g<0></span>', value
                )

    # Turn of escaping, otherwise, &nbsp appers verbatim
    return literal(value)


def format_paymentmode(paymentmode):
    """
    format payment modes for display
    Since #662 ( Permettre la configuration des modes de paiement )
    no formatting is necessary
    """
    return paymentmode


def month_name(index, capitalize=False):
    """
    Return the name of the month number "index"
    """
    result = ""
    if not isinstance(index, int):
        try:
            index = int(index)
        except ValueError:
            return ""

    if index in range(1, 13):
        result = calendar.month_name[index]

    if capitalize:
        result = result.capitalize()

    return result


def short_month_name(index):
    """
    Return the short name of the month number "index"
    """
    result = ""
    if not isinstance(index, int):
        try:
            index = int(index)
        except ValueError:
            return ""

    if index in range(1, 13):
        result = calendar.month_abbr[index]

    return result


def human_readable_filesize(size):
    """
    Return a human readable file size
    """
    result = "Inconnu"
    try:
        size = float(size)
        for x in ["bytes", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                result = "%3.1f %s" % (size, x)
                break
            size /= 1024.0
    except (ValueError, TypeError):
        pass
    return result


def format_task_type(task):
    return TASKTYPES_LABEL.get(task.type_)


def format_civilite(civilite_str):
    """
    Shorten the civilite string

    :param str civilite_str: Monsieur/Madame
    :returns: Mr/Mme
    :rtype: str
    """
    res = civilite_str
    if civilite_str.lower() == "monsieur":
        res = "M."
    elif civilite_str.lower() == "madame":
        res = "Mme"
    elif civilite_str.lower() == "mr&mme":
        res = "M. et Mme"
    return res


def strip_civilite(str_with_civilite) -> str:
    """
    Remove the civilite from the given string if any

    :param str str_with_civilite: string that may have civilite
    :returns: the string without the civilite
    """
    from caerp.forms.third_party.customer import CIVILITE_OPTIONS

    res = str_with_civilite

    all_civ = []
    for short_civ, long_civ in CIVILITE_OPTIONS:
        all_civ.append(short_civ)
        all_civ.append(long_civ)
    all_civ.append("M.")
    all_civ.append("Mme")
    all_civ = sorted(all_civ, key=lambda x: (-len(x), x))

    for civ in all_civ:
        res = res.replace(civ, "")

    return res.replace("  ", " ").strip()


def format_lower_ascii(original_str):
    """
    Generate a lower ascii only string from the original one
    :param str original_str: The string to modify
    :returns: A modified string
    :rtype: str
    """
    result = original_str.lower()
    result = force_ascii(result)
    result = result.replace(" ", "_")
    return result


RE_NONLETTER = re.compile(r"[^a-zA-Z]")


def strip_nonletters(s: str) -> str:
    return RE_NONLETTER.sub("", s)


def safe_ascii_str(value):
    """
    Replace special chars to their ascii counterpart.

    This does modify the string (remove accents…) and is only intended for
    non-human-facing strings.

    :param str value: The value to convert
    :rtype: str
    """
    normalized = unicodedata.normalize("NFKD", value)
    return normalized.encode("ascii", "ignore").decode("utf-8")


def compile_template_str(template_string, template_context):
    """
    Compile the template string and merge the context

    :param str template_string: The string to templatize
    :param dict template: templating context
    :rtype: str
    """
    return template_string.format(**template_context)


def pluralize(collection, plural_mark="s", singular_mark=""):
    """
    Helps handling the singular/plural forms of a word

    >>> 'Simpson' + pluralize(['bart'])
    'Simpson'
    >>> 'Simpson' + pluralize(['homer', 'bart'])
    'Simpsons'

    >>> pluralize(['Jolly Jumper'], 'chevaux', 'cheval')
    'cheval'

    >>> 'chou' + 'pluralize(['rave'], 'x')
    'chou'


    :param collection: list-like object
    """
    count = len(collection)

    if count > 1:
        return plural_mark
    else:
        return singular_mark


HOUR_UNITS = ("h", "hs", "hrs")


def is_hours(unit) -> bool:
    """
    Test if the given unit is in hours
    """
    result = False
    if unit:
        unit_lc = unit.lower()
        result = unit_lc.startswith("heure") or unit_lc in HOUR_UNITS
    return result


def remove_newlines(s: str) -> str:
    """
    Remove new line character

    Replace them by space, in case they were used as a separator
    """
    if s:
        # windows newlines
        s = s.replace("\r\n", " ")
        s = s.replace("\n", " ")
    return s


def format_quantity(quantity):
    """
    format the quantity
    """
    if quantity is not None:
        result = locale.format_string("%g", quantity, grouping=True)
        if isinstance(result, bytes):
            result = result.decode("utf-8")
        return result
    else:
        return ""


def _string_or_int(text):
    """Return an int if text is an int else return the text"""
    return int(text) if text.isdigit() else text


def sort_string_with_numbers(text):
    """
    Allow to sort list of string with numbers in human order

    >>> l = [ "b1", "a1", "a10", "a11", "a2",]
    >>> l.sort(key=sort_string_with_numbers)
    >>> assert l == ["a1", "a2", "a10", "a11", "b1"]

    Inspired by :
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    """
    return [_string_or_int(c) for c in re.split(r"(\d+)", text)]


def get_keys_from_template(template: str) -> List[str]:
    """
    Collect string formatting variables used in template (string.format style)

    raises ValueError in case of string formating language syntax error.
    :param str template: The template string
    """
    fmt = string.Formatter()
    # parse returns tuples
    # In [4]: list(string.Formatter().parse(a))
    # Out[4]: [('', 'SEQYEAR', '', None), (' ', 'YYYY', '', None)]
    return [i[1] for i in fmt.parse(template) if i[1] is not None]


def convert_to_string(value):
    """
    Convertit une valeur en chaîne de caractères sauf None -> ""
    """
    if value is None:
        return ""
    else:
        return str(value)


def boolean_to_string(value: bool) -> str:
    """
    Retourn une représentation en chaîne de caractères d'un booléen (Oui/Non)
    """
    return "Oui" if value else "Non"


def get_random_string(length: Optional[int] = 10) -> str:
    """
    Generate a random string of given length

    :param int length: Length of the random string
    :return: Random string
    :rtype: str
    """
    return "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(length)
    )
