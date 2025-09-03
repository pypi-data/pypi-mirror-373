import logging
import colander
import deform
from deform import widget as deform_widget

from caerp.consts.permissions import PERMISSIONS
from caerp.models.activity import ATTENDANCE_STATUS
from caerp.models.workshop import (
    WorkshopAction,
    WorkshopTagOption,
    get_workshop_years,
)
from caerp.models.company import Company
from caerp.models.activity import EVENT_SIGNUP_MODE
from caerp.forms.user import (
    user_node,
)
from caerp.forms.company import company_node
from caerp import forms
from caerp.forms import lists

logger = logging.getLogger(__name__)

participant_choice_node = forms.mk_choice_node_factory(
    user_node,
    resource_name="un participant",
    resource_name_plural="un ou plusieurs participant(s)",
)

participant_filter_node_factory = forms.mk_filter_node_factory(
    user_node,
    title="Participant",
    empty_filter_msg="Tous",
)

trainer_choice_node_factory = forms.mk_choice_node_factory(
    user_node,
    resource_name="une personne avec les droits « Formateur »",
    resource_name_plural="une ou plusieurs personnes avec les droits " "« Formateur »",
    access_rights=["es_trainer"],
)

trainer_filter_node_factory = forms.mk_filter_node_factory(
    user_node,
    title="Animateur/Animatrice(s)",
    empty_filter_msg="Tou(te)s",
    access_rights=["es_trainer"],
)

accompagnateur_filter_node_factory = forms.mk_filter_node_factory(
    user_node,
    title="Animateur/Animatrice(s)",
    empty_filter_msg="Tous",
    access_rights=["es_trainer", "global_accompagnement"],
)
accompagnateur_choice_node_factory = forms.mk_choice_node_factory(
    user_node,
    resource_name="un formateur ou un membre de l'équipe d'appui",
    resource_name_plural="un ou plusieurs formateurs ou membres de l'équipe d'appui",
    access_rights=["es_trainer", "global_accompagnement"],
)

company_manager_node_factory = forms.mk_choice_node_factory(
    company_node,
    widget_options={"query": Company.query_for_select_with_trainer},
    resource_name="Enseigne gestionnaire de l’atelier",
    description="Laisser ce champ vide si l’atelier est géré par la CAE.\r\n"
    "Enseignes avec d’un ou plusieurs employés ayant des droits "
    "de formateur.",
)


def get_info_field(title):
    """
    returns a simple node factorizing recurent datas
    """
    return colander.SchemaNode(
        colander.String(),
        validator=colander.Length(max=125),
        title=title,
        description="Utilisé dans la feuille d’émargement",
        missing="",
    )


def get_info1():
    query = WorkshopAction.query()
    query = query.filter(WorkshopAction.active == True)  # noqa: E712
    return query.filter(WorkshopAction.parent_id == None)  # noqa: E711


@colander.deferred
def deferred_info1(node, kw):
    options = [(str(a.id), a.label) for a in get_info1()]
    options.insert(0, ("", "- Sélectionner un intitulé -"))
    return deform.widget.SelectWidget(values=options)


def get_filter_info1():
    query = WorkshopAction.query()
    return query.filter(WorkshopAction.parent_id == None)  # noqa: E711


@colander.deferred
def deferred_filter_info1(node, kw):
    options = [(str(a.id), a.label) for a in get_filter_info1()]
    options.insert(0, ("", "Toutes"))
    return deform.widget.SelectWidget(values=options)


@colander.deferred
def deferred_info2(node, kw):
    options = [("", "- Sélectionner un sous-titre -")]
    for info1 in get_info1():
        if info1.children:
            group_options = [(str(a.id), a.label) for a in info1.children]
            group = deform.widget.OptGroup(info1.label, *group_options)
            options.append(group)
    return deform.widget.SelectWidget(values=options)


@colander.deferred
def deferred_info3(node, kw):
    options = [("", "- Sélectionner un sous-titre -")]
    for info1 in get_info1():
        for info2 in info1.children:
            group_label = info2.label
            group_options = [(str(a.id), a.label) for a in info2.children]
            group = deform.widget.OptGroup(group_label, *group_options)
            options.append(group)
    return deform.widget.SelectWidget(values=options)


def range_validator(form, values):
    """
    Ensure start_time is before end_time
    """
    if values["start_time"] >= values["end_time"]:
        message = "L’heure de début doit précéder celle de fin"
        exc = colander.Invalid(form, message)
        exc["start_time"] = "Doit précéder la fin"
        raise exc


class ParticipantsSequence(colander.SequenceSchema):
    """
    Schema for the list of participants
    """

    participant_id = participant_choice_node()


class TimeslotSchema(colander.MappingSchema):
    id = forms.id_node()
    name = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(max=255),
        title="Intitulé",
        description="Intitulé utilisé dans la feuille d’émargement \
correspondante (ex: Matinée 1)",
    )
    start_time = forms.now_node(title="Début de la tranche horaire")
    end_time = forms.now_node(title="Fin de la tranche horaire")


class TimeslotsSequence(colander.SequenceSchema):
    timeslot = TimeslotSchema(
        title="Tranche horaire",
        validator=range_validator,
    )


def get_deferred_tags_choices():
    """
    Build a deferred for tags selection widget
    """

    @colander.deferred
    def deferred_tags_choices(node, kw):
        """
        return a deferred tags selection widget
        """

        # Note on placeholders
        # Cleaner fix would be to replace `default_option` 2-uple arg
        # with a `placeholder` str arg, as in JS code.
        # Use of placeholder arg is mandatory with Select2
        # otherwise the clear button crashes.
        # https://github.com/select2/select2/issues/5725
        values = WorkshopTagOption.query("id", "label").all()
        return deform.widget.Select2Widget(
            values=values,
            placeholder="- Sélectionner une ou plusieurs étiquettes -",
            default_option=("", "- Sélectionner une ou plusieurs étiquettes -"),
            title="zéro à plusieurs étiquettes pour l’atelier",
            multiple=True,
        )

    return deferred_tags_choices


def workshop_tags_node():
    """
    Return a schema node for tags selection
    """
    return colander.SchemaNode(
        colander.Set(),
        name="tags",
        widget=get_deferred_tags_choices(),
        preparer=forms.uniq_entries_preparer,
        title="Étiquettes de l’atelier",
        description=deferred_workshop_tag_description,
        missing=colander.drop,
    )


def remove_workshop_manager_fields(node, kw):
    """
    Remove fields specific to workshop managers
    """
    if not kw["request"].has_permission(PERMISSIONS["global.manage_workshop"]):
        del node["company_manager_id"]


@colander.deferred
def deferred_workshop_tag_description(node, kw):
    if kw["request"].has_permission(PERMISSIONS["global.config_workshop"]):
        description = (
            "Ajouter les étiquettes dans la partie Configuration "
            "\u2192 Module accompagnement \u2192 Configuration du "
            "module Ateliers \u2192 Étiquettes d’atelier"
        )
    else:
        description = ""
    return description


class WorkshopSchema(colander.Schema):
    """
    Schema for workshop creation/edition
    """

    come_from = forms.come_from_node()
    name = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(max=255),
        title="Titre de l’atelier",
    )

    company_manager_id = company_manager_node_factory(
        title="Enseigne gestionnaire de l’atelier",
        missing=colander.drop,
    )

    trainers = accompagnateur_choice_node_factory(
        multiple=True,
        title="Animateur(s)/Animatrice(s)",
        preparer=forms.uniq_entries_preparer,
        validator=colander.Length(min=1, min_err="Veuillez sélectionner un animateur"),
    )

    tags = workshop_tags_node()

    signup_mode = colander.SchemaNode(
        colander.String(),
        title="Mode d’inscription",
        widget=deform.widget.SelectWidget(
            values=EVENT_SIGNUP_MODE,
            default="closed",
        ),
        validator=colander.OneOf([key for key, _ in EVENT_SIGNUP_MODE]),
    )

    description = colander.SchemaNode(
        colander.String(),
        title="Description",
        widget=deform.widget.TextAreaWidget(),
        missing="",
    )

    place = colander.SchemaNode(
        colander.String(),
        title="Lieu",
        widget=deform.widget.TextAreaWidget(),
        missing="",
    )

    info1_id = colander.SchemaNode(
        colander.Integer(),
        widget=deferred_info1,
        title="Intitulé de l’action financée 1",
        description="Utilisée comme titre dans la sortie PDF",
        missing=colander.null,
        default=colander.null,
    )
    info2_id = colander.SchemaNode(
        colander.Integer(),
        widget=deferred_info2,
        title="Intitulé de l’action financée 2",
        description="Utilisée comme sous-titre dans la sortie PDF",
        missing=colander.null,
        default=colander.null,
    )
    info3_id = colander.SchemaNode(
        colander.Integer(),
        widget=deferred_info3,
        title="Intitulé de l’action financée 3",
        description="Utilisée comme second sous-titre dans la sortie PDF",
        missing=colander.null,
        default=colander.null,
    )

    max_participants = colander.SchemaNode(
        colander.Integer(),
        title="Nombre maximum de participants",
        description="0 pour nombre de participants illimités",
        missing=0,
        default=0,
        validator=colander.Range(0, 9999),
    )

    participants = ParticipantsSequence(
        title="Participants",
        widget=deform_widget.SequenceWidget(
            min_len=0,
            add_subitem_text_template="Ajouter un participant",
        ),
    )
    timeslots = TimeslotsSequence(
        title="Tranches horaires",
        description="Les différentes tranches horaires de l’atelier \
donnant lieu à un émargement",
        widget=deform_widget.SequenceWidget(min_len=1),
    )

    def validator(self, node, value):
        """
        Check maximum participants
        - check number of participants < max_participants
        - use max_participants = 0 for disabling this verification
        """
        max_participants = value.get("max_participants")
        participants = value.get("participants")

        if max_participants > 0 and len(participants) > max_participants:
            self.raise_invalid(
                "Le nombre de participants ({}) excède le maximum ({}).".format(
                    len(participants), max_participants
                )
            )


def get_workshop_schema():
    return WorkshopSchema(after_bind=remove_workshop_manager_fields)


def get_list_schema(
    company=False,
    user=False,
    include_open=False,
    is_current_user=False,
    default_company_value=colander.null,
    training: bool = True,
):
    """
    Return a schema for filtering workshop list

    :param bool company: The view is related to a company
    :param bool user: The view is related to a user
    :param bool include_open: Include open workshops
    :param bool is_current_user: The view is related to the current user
    :param training: Used to list training workshops
    """
    schema = lists.BaseListsSchema().clone()

    schema["search"].title = "Intitulé de l’atelier"

    year = forms.year_filter_node(
        name="year",
        query_func=get_workshop_years,
        title="Année",
        default=forms.deferred_default_year,
    )
    schema.add_custom(year)

    date_range = forms.fields.DateRangeSchema()
    schema.add_custom(date_range)

    if not company or include_open:
        company_manager = company_node(
            name="company_manager",
            default=default_company_value,
            title="Enseigne gestionnaire de l’atelier",
            widget_options={
                "query": Company.query_for_select_with_trainer,
                "more_options": [
                    ("-1", "Interne CAE (sans enseigne ou enseigne interne)")
                ],
                "default_option": ("", "Toutes"),
            },
            missing=colander.drop,
        )
        schema.add_custom(company_manager)

    # if training:
    #     schema.add_custom(trainer_filter_node_factory(name="trainer_id"))
    # else:
    schema.add_custom(accompagnateur_filter_node_factory(name="trainer_id"))

    if not company and not user:
        schema.add_custom(participant_filter_node_factory(name="participant_id"))

    info_id_1 = colander.SchemaNode(
        colander.Integer(),
        name="info_1_id",
        title="Action financée",
        missing=colander.drop,
        widget=deferred_filter_info1,
    )
    schema.add_custom(info_id_1)

    if user and include_open:
        if is_current_user:
            label = "Uniquement les ateliers où je suis inscrit"
            default = False
        else:
            label = "Uniquement les ateliers où l’utilisateur est inscrit"
            default = True
        only_subscribed_node = colander.SchemaNode(
            colander.Boolean(),
            name="onlysubscribed",
            title="",
            label=label,
            missing=colander.drop,
            default=default,
        )
        schema.add_custom(only_subscribed_node)

    tags = workshop_tags_node()
    schema.add_custom(tags)

    if not company and not user:
        notfilled_node = colander.SchemaNode(
            colander.Boolean(),
            name="notfilled",
            arialabel="Uniquement les ateliers avec émargements non remplis",
            label="Émargements non remplis",
            missing=colander.drop,
            toggle=False,
        )
        schema.add_latest(notfilled_node)

    return schema


class AttendanceEntry(colander.MappingSchema):
    """
    Relationship edition
    Allows to edit the attendance status
    """

    account_id = forms.id_node()
    timeslot_id = forms.id_node()
    status = forms.status_filter_node(ATTENDANCE_STATUS, default="registered")


class TimeslotAttendanceEntries(colander.SequenceSchema):
    """ """

    attendance = AttendanceEntry()


class Attendances(colander.MappingSchema):
    """
    Attendance registration schema
    """

    attendances = TimeslotAttendanceEntries()
