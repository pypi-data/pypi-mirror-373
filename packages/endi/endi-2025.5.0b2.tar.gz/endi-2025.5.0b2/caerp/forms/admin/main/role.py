import functools
import deform
import colander
import deform_extensions
from typing import Optional
from sqlalchemy import select
from colanderalchemy import SQLAlchemySchemaNode

from caerp.consts.users import ACCOUNT_TYPES_LABELS
from caerp.models.user import Group
from caerp.forms import (
    customize_field,
    get_sequence_child_item,
    get_deferred_model_select_checkbox,
)
from caerp.models.user.access_right import AccessRight
from caerp.views.render_api import build_icon_str


def get_right_label(access_right: AccessRight, request):
    label: str = access_right.label
    for tag in access_right.tags:
        label += f"&nbsp;<span class='icon tag neutral'>{tag}</span>"
    if access_right.rgpd:
        label += "&nbsp;<span class='icon tag caution'>RGPD</span>"
    label += """
        &nbsp;
        <span class="icon" title="{0}">
            {1} <span class="screen-reader-text">{0}</span>
        </span>
    """.format(
        access_right.description, build_icon_str(request, "question-circle")
    )
    return label


def query_access_rights_by_account_type(
    bind_params: dict, account_type: Optional[str] = None
):
    """
    Query builder for AccessRight model
    """
    request = bind_params["request"]
    query = select(AccessRight)
    result = request.dbsession.execute(query).scalars().all()
    if account_type and account_type != "all" and account_type != "hybride":
        # Si on édite un compte equipe_appui ou entrepreneur,
        # on filtre les access_rights
        result = [
            right
            for right in result
            if right.account_type == account_type or right.account_type == "all"
        ]
    result.sort(key=lambda r: r.label)
    return result


def customize_schema_for_add(schema, request):
    customize = functools.partial(customize_field, schema)
    # On a trois listes de checkboxes avec des droits.
    # Une avec tous les droits
    # Une avec les droits spécifiques aux entrepreneurs
    # Une avec les droits spécifiques à l'équipe d'appui
    # Le radio ci-dessous (account_type) switche l'affichage de l'une des trois
    if "account_type" in schema:
        values = tuple(
            (key, value)
            for key, value in ACCOUNT_TYPES_LABELS.items()
            if key != "hybride"
        )
        # On rajoute un troisième item prenant la key de l'account_type
        # Cela permet au widget d'afficher/masquer les champs lié au type
        # de compte
        values = [value + (f"access_rights_{value[0]}",) for value in values]
        values += (("all", "Les deux", "access_rights"),)
        customize(
            "account_type",
            widget=deform_extensions.RadioChoiceToggleWidget(values=values),
        )

    if "name" in schema:
        customize(
            "name",
            title="Nom du rôle",
            validator=colander.Regex(
                r"^[a-z\-]+$",
                "Nom incorrect (ne doit contenir que des caractères alphabétiques en minuscules ou des tirets)",
            ),
        )

    if "access_rights" in schema:
        get_label = functools.partial(get_right_label, request=request)

        customize(
            "access_rights",
            title="Droits des utilisateurs ayant ce rôle",
            children=get_sequence_child_item(AccessRight),
            widget=get_deferred_model_select_checkbox(
                AccessRight,
                keys=("id", get_label),
                query_builder=query_access_rights_by_account_type,
            ),
        )

        schema["access_rights_entrepreneur"] = schema["access_rights"].clone()
        schema["access_rights_equipe_appui"] = schema["access_rights"].clone()

        customize(
            "access_rights_entrepreneur",
            title="Droits des entrepreneurs ayant ce rôle",
            widget=get_deferred_model_select_checkbox(
                AccessRight,
                keys=("id", get_label),
                query_builder=functools.partial(
                    query_access_rights_by_account_type, account_type="entrepreneur"
                ),
            ),
        )
        customize(
            "access_rights_equipe_appui",
            title="Droits des membres de l'équipe d'appui ayant ce rôle",
            widget=get_deferred_model_select_checkbox(
                AccessRight,
                keys=("id", get_label),
                query_builder=functools.partial(
                    query_access_rights_by_account_type, account_type="equipe_appui"
                ),
            ),
        )


def customize_schema_for_edit(schema, request):
    customize = functools.partial(customize_field, schema)
    if "name" in schema:
        customize(
            "name",
            title="Nom du rôle",
            validator=colander.Regex(
                r"^[a-z\-]+$",
                "Nom incorrect (ne doit contenir que des caractères alphabétiques en minuscules ou des tirets)",
            ),
        )
    account_type_label = ACCOUNT_TYPES_LABELS.get(
        request.context.account_type, "entrepreneurs et équipe d'appui"
    )
    customize(
        "default_for_account_type",
        title=(
            f"Rôle associé par défaut aux "
            f'nouveaux comptes de type "{account_type_label}" ?'
        ),
    )
    values = tuple(
        (key, value) for key, value in ACCOUNT_TYPES_LABELS.items() if key != "hybride"
    )
    values += (
        (
            "all",
            "Les deux",
        ),
    )
    customize(
        "account_type",
        widget=deform.widget.RadioChoiceWidget(values=values, readonly=True),
    )

    if "access_rights" in schema:
        get_label = functools.partial(get_right_label, request=request)

        customize(
            "access_rights",
            title="Droits des utilisateurs ayant ce rôle",
            children=get_sequence_child_item(AccessRight),
            widget=get_deferred_model_select_checkbox(
                AccessRight,
                keys=("id", get_label),
                query_builder=functools.partial(
                    query_access_rights_by_account_type,
                    account_type=request.context.account_type,
                ),
            ),
        )


def get_add_edit_group_schema(request, edit=False):
    excludes = (
        "id",
        "users",
    )
    schema = SQLAlchemySchemaNode(Group, excludes=excludes)
    if edit:
        customize_schema_for_edit(schema, request=request)
    else:
        customize_schema_for_add(schema, request=request)
    return schema
