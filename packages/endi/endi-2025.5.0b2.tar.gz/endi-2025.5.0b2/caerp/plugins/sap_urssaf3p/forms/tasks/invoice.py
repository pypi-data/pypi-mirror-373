from caerp import forms
from caerp.forms.tasks.invoice import get_list_schema


def get_urssaf3p_request_status_filter_options():
    options = [
        ("all", "Pas de filtre"),
        ("requested", "Toutes les factures en avance immédiate"),
    ]
    options.append(("error", "En erreur"))
    options.append(("waiting", "En attente"))
    options.append(("aborted", "Annulée"))
    options.append(("payment_issue", "En refus de prélèvement"))
    options.append(("resulted", "Payée"))
    return options


def get_urssaf3p_list_schema(request, is_global=False, excludes=()):
    schema = get_list_schema(request, is_global, excludes)
    schema.add_before(
        "auto_validated",
        forms.status_filter_node(
            get_urssaf3p_request_status_filter_options(),
            name="avance_immediate",
            title="Avance immédiate URSSAF",
        ),
    )
    return schema
