"""
    Activity related form schemas

    New activity creation
    Activity search schema
"""
import colander
import deform
import deform_extensions

from caerp.consts.access_rights import ACCESS_RIGHTS
from caerp.models.activity import (
    ActivityType,
    ActivityMode,
    ActivityAction,
    STATUS_SEARCH,
    ATTENDANCE_STATUS,
    ATTENDANCE_STATUS_SEARCH,
    get_activity_years,
)
from caerp.forms.user import (
    conseiller_choice_node,
    conseiller_filter_node_factory,
)
from caerp.forms.workshop import (
    participant_choice_node,
    participant_filter_node_factory,
)
from caerp.forms.company import company_choice_node
from caerp import forms
from caerp.forms import lists


def get_activity_types():
    return ActivityType.query().filter(ActivityType.active == True)  # noqa: E712


def get_activity_modes():
    return [mode.label for mode in ActivityMode.query()]


def get_actions():
    query = ActivityAction.query()
    query = query.filter(ActivityAction.active == True)  # noqa: E712
    return query.filter(ActivityAction.parent_id == None)  # noqa: E711


def get_subaction_options():
    options = [
        ("", "Sélectionner une sous-action"),
    ]
    for action in get_actions():
        gr_options = [(str(a.id), a.label) for a in action.children]
        group = deform.widget.OptGroup(action.label, *gr_options)
        options.append(group)
    return options


def get_deferred_select_type(default=False):
    @colander.deferred
    def deferred_select_type(node, kw):
        values = [(str(a.id), a.label) for a in get_activity_types()]
        if default:
            values.insert(0, ("", "Tous les rendez-vous"))
        return deform.widget.SelectWidget(values=values)

    return deferred_select_type


@colander.deferred
def deferred_select_mode(node, kw):
    modes = get_activity_modes()
    options = list(zip(modes, modes))
    return deform.widget.SelectWidget(values=options)


@colander.deferred
def deferred_select_action(node, kw):
    options = [
        ("", "Sélectionner une action"),
    ]
    options.extend([(str(a.id), a.label) for a in get_actions()])
    return deform.widget.SelectWidget(values=options)


@colander.deferred
def deferred_select_subaction(node, kw):
    options = get_subaction_options()
    return deform.widget.SelectWidget(values=options)


@colander.deferred
def deferred_type_validator(node, kw):
    values = [a.id for a in get_activity_types()]
    values.append(-1)
    return colander.OneOf(values)


@colander.deferred
def deferred_mode_validator(node, kw):
    values = [a.label for a in get_activity_modes()]
    values.append(-1)
    return colander.OneOf(values)


class CreateActivitySchema(colander.MappingSchema):
    """
    Activity creation schema
    """

    come_from = forms.come_from_node()

    conseillers = conseiller_choice_node(
        title="Accompagnateurs menant le rendez-vous",
        multiple=True,
        validator=colander.Length(min=1),
        preparer=forms.uniq_entries_preparer,
    )
    datetime = forms.now_node(title="Date de rendez-vous")
    type_id = colander.SchemaNode(
        colander.Integer(),
        widget=get_deferred_select_type(),
        title="Nature du rendez-vous",
    )
    action_id = colander.SchemaNode(
        colander.Integer(),
        widget=deferred_select_action,
        title="Intitulé de l'action (financée)",
        missing=colander.null,
        default=colander.null,
    )
    subaction_id = colander.SchemaNode(
        colander.Integer(),
        widget=deferred_select_subaction,
        title="Intitulé sous-action",
        missing=colander.null,
        default=colander.null,
    )
    mode = colander.SchemaNode(
        colander.String(),
        widget=deferred_select_mode,
        title="Mode d'entretien",
    )
    participants = participant_choice_node(
        multiple=True,
        description="Participants attendus au rendez-vous",
        validator=colander.Length(min=1),
        preparer=forms.uniq_entries_preparer,
    )
    companies = company_choice_node(
        multiple=True,
        title="Enseignes concernées (donner le droit de consultation)",
        description="Les membres de ces enseignes qui ne participent \
pas au rendez-vous peuvent quand même le consulter.",
        missing=colander.drop,
    )


class NewActivitySchema(CreateActivitySchema):
    """
    New activity Schema, used to initialize an activity, provides an option
    to start it directly
    """

    now = colander.SchemaNode(
        colander.Boolean(),
        label="Démarrer le rendez-vous immédiatement",
        default=False,
    )


class Attendance(colander.MappingSchema):
    account_id = forms.id_node()
    event_id = forms.id_node()
    username = colander.SchemaNode(
        colander.String(),
        title="",
        widget=deform_extensions.DisabledInput(),
        missing="",
    )
    status = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.RadioChoiceWidget(
            values=ATTENDANCE_STATUS,
            inline=True,
        ),
        validator=colander.OneOf([x[0] for x in ATTENDANCE_STATUS]),
        title="",
        missing="excused",
    )


class Attendances(colander.SequenceSchema):
    attendance = Attendance(title="")


class RecordActivitySchema(colander.Schema):
    """
    Schema for activity recording
    """

    attendances = Attendances(
        title="Présence",
        widget=deform.widget.SequenceWidget(
            template="fixed_len_sequence.pt", item_template="fixed_len_sequence_item.pt"
        ),
    )

    objectifs = forms.textarea_node(
        title="Objectifs du rendez-vous",
        richwidget=True,
        missing="",
    )

    point = forms.textarea_node(
        title="Points abordés",
        richwidget=True,
        missing="",
    )

    action = forms.textarea_node(
        title="Plan d'action et préconisations",
        richwidget=True,
        missing="",
    )

    documents = forms.textarea_node(
        title="Documents produits",
        richwidget=True,
        missing="",
    )

    notes = forms.textarea_node(
        title="Notes",
        richwidget=True,
        missing="",
    )

    duration = colander.SchemaNode(
        colander.Integer(),
        title="Durée",
        description="La durée du rendez-vous, en minute (ex : 90)",
        widget=deform.widget.TextInputWidget(
            input_append="minutes",
        ),
    )


def get_list_schema(is_admin=False):
    schema = lists.BaseListsSchema().clone()

    schema.insert(
        0,
        forms.today_node(
            name="date_range_end",
            default=colander.null,
            missing=colander.drop,
            title="Et le",
            widget_options={"css_class": "input-medium search-query"},
        ),
    )

    schema.insert(
        0,
        forms.today_node(
            name="date_range_start",
            default=colander.null,
            missing=colander.drop,
            title="Entre le",
            widget_options={"css_class": "input-medium search-query"},
        ),
    )

    schema.insert(
        0,
        colander.SchemaNode(
            colander.Integer(),
            name="type_id",
            title="Nature du rendez-vous",
            widget=get_deferred_select_type(True),
            validator=deferred_type_validator,
            missing=colander.drop,
        ),
    )

    schema.insert(0, forms.status_filter_node(STATUS_SEARCH, default=colander.drop))
    schema.insert(
        0,
        forms.status_filter_node(
            ATTENDANCE_STATUS_SEARCH,
            name="user_status",
            title="Présence",
            default=colander.drop,
        ),
    )

    if is_admin:
        schema.insert(
            0,
            participant_filter_node_factory(name="participant_id", title="Participant"),
        )
        schema.insert(
            0,
            conseiller_filter_node_factory(
                name="conseiller_id",
                title="Accompagnateur",
            ),
        )

    year = forms.year_filter_node(
        name="year",
        title="Année",
        query_func=get_activity_years,
        default=forms.deferred_default_year,
    )
    schema.insert(0, year)

    del schema["search"]
    return schema
