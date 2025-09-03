"""
Main deferreds functions used in enDI

The widgets provided here are model agnostic
"""
import datetime
import datetime
import logging
from typing import Any, Dict, List, Optional, Tuple

import colander
import deform
import deform_extensions
import schwifty
from sqlalchemy import func, select
import schwifty
from sqlalchemy import func, select
from sqlalchemy.sql.elements import ColumnElement

from caerp.utils import strings
from caerp.utils.html import clean_html, strip_html
from caerp.utils.html import clean_html, strip_html

EXCLUDED = {"exclude": True}
MAIL_ERROR_MESSAGE = "Veuillez entrer une adresse mail valide"
logger = logging.getLogger(__name__)


def DeferredAll(*validators):
    """
    Like colander.All validator but supporting deferred validators

    *validators

        one or several colander validators, which can be deferred or not.

    :returns: a deferred validator
    """

    @colander.deferred
    def deferred_all_validator(node, kw):
        def _all_validators(node, value):
            for validator in validators:
                # Resolve deferred if required
                if isinstance(validator, colander.deferred):
                    validator = validator(node, kw)
                validator(node, value)

        return _all_validators

    return deferred_all_validator


@colander.deferred
def deferred_today(node, kw):
    """
    return a deferred value for "today"
    """
    return datetime.date.today()


@colander.deferred
def deferred_now(node, kw):
    """
    Return a deferred datetime value for now
    """
    return datetime.datetime.now()


@colander.deferred
def deferred_current_user_id(node, kw):
    """
    Return a deferred for the current user
    """
    return kw["request"].identity.id


def get_date_input(**kw):
    """
    Return a date input displaying a french user friendly format
    """
    date_input = deform.widget.DateInputWidget(**kw)
    return date_input


def get_datetime_input(**kw):
    """
    Return a datetime input displaying a french user friendly format
    """
    datetime_input = deform_extensions.CustomDateTimeInputWidget(**kw)
    return datetime_input


def today_node(**kw):
    """
    Return a schema node for date selection, defaulted to today
    """
    if "default" not in kw:
        kw["default"] = deferred_today
    widget_options = kw.pop("widget_options", {})
    return colander.SchemaNode(
        colander.Date(), widget=get_date_input(**widget_options), **kw
    )


def now_node(**kw):
    """
    Return a schema node for time selection, defaulted to "now"
    """
    if "default" not in kw:
        kw["default"] = deferred_now
    return colander.SchemaNode(
        colander.DateTime(default_tzinfo=None), widget=get_datetime_input(), **kw
    )


def come_from_node(**kw):
    """
    Return a form node for storing the come_from page url
    """
    if "missing" not in kw:
        kw["missing"] = ""
    return colander.SchemaNode(
        colander.String(), widget=deform.widget.HiddenWidget(), **kw
    )


@colander.deferred
def deferred_default_popup(node, kw):
    """
    Check if the popup key is present in get or post params and return its id
    """
    return kw["request"].params.get("popup", "")


def popup_node(**kw):
    """
    Return a form node for storing the come_from page url
    """
    return colander.SchemaNode(
        colander.String(),
        widget=deform.widget.HiddenWidget(),
        missing=colander.drop,
        default=deferred_default_popup,
    )


def _textarea_node_validator(value):
    """
    Check that the given value is not void (it could contain void html tags)
    """
    return bool(strip_html(value))


textarea_node_validator = colander.Function(
    _textarea_node_validator, msg="Ce paramètre est requis"
)


def strip_string_preparer(value):
    """
    Strip leading and trailing whitespace from the given value
    """
    if isinstance(value, str):
        return value.strip()
    return value


def lower_string_preparer(value):
    """
    Convert the given value to lowercase
    """
    if isinstance(value, str):
        return value.lower()
    return value


def richtext_widget(options=None, widget_options=None, admin=False):
    """
    Return a text area widget
    """
    options = options or {}
    widget_options = widget_options or {}
    plugins = [
        "lists",
        "searchreplace visualblocks fullscreen",
        # "contextmenu paste"
    ]
    menubar = False
    if admin:
        plugins.append("insertdatetime searchreplace code table")
        plugins.append("advlist link autolink")
        menubar = True

    options.update(
        {
            "content_css": "/fanstatic/fanstatic/css/richtext.css",
            "theme_advanced_toolbar_location": "top",
            "theme_advanced_toolbar_align": "left",
            "width": "100%",
            "language": "fr_FR",
            "menubar": menubar,
            "plugins": plugins,
            "theme": "silver",
            # NB : La skin est overridée dans la balise script du template
            # deform/richtext.pt
            "skin": "oxide",
            "theme_advanced_resizing": True,
            "convert_fonts_to_spans": True,
            "paste_as_text": False,
            "contextmenu": False,
            "toolbar": (
                "undo redo | styleselect | bold italic | alignleft aligncenter "
                "alignright alignjustify | bullist numlist outdent indent |"
                "forecolor backcolor | fontsizeselect |removeformat"
            ),
            "fontsize_formats": "6pt 8pt 10pt 12pt 14pt 16pt 18pt 24pt 36pt 48pt",
            "browser_spellcheck": True,
        }
    )

    return deform.widget.RichTextWidget(options=list(options.items()), **widget_options)


def clean_html_preparer(text: str) -> str:
    """Preparer that clean all the html for us"""
    if text and text != colander.null:
        return clean_html(text)
    else:
        return text


def textarea_node(**kw):
    """
    Return a node for storing Text objects

    richtext (True / False)

        should we provide a rich text widget if True, richtext_options dict
        values will be passed to the CKEditor library

    admin (True / False)

        Should we provide a widget with all options

    widget_options

        Options passed to the widget's class

    """
    widget_options = kw.pop("widget_options", {})

    if kw.pop("richwidget", None):
        # If the admin option is set,
        admin_field = kw.pop("admin", False)
        options = kw.pop("richtext_options", {})
        wid = richtext_widget(options, widget_options, admin=admin_field)
    else:
        widget_options.setdefault("rows", 4)
        wid = deform.widget.TextAreaWidget(**widget_options)

    kw.setdefault("preparer", clean_html_preparer)
    return colander.SchemaNode(colander.String(), widget=wid, **kw)


@colander.deferred
def deferred_default_year(node, kw):
    return datetime.date.today().year


def get_year_select_deferred(query_func, default_val=None):
    """
    return a deferred widget for year selection
    :param query_func: the query function returning a list of years (taks kw as
    parameters)
    """

    @colander.deferred
    def deferred_widget(node, kw):
        years = query_func(kw)
        years.reverse()
        values = list(zip(years, years))
        if default_val is not None and default_val not in years:
            values.insert(0, default_val)

        return deform.widget.SelectWidget(
            values=values,
            css_class="input-small",
        )

    return deferred_widget


def year_select_node(query_func, **kw):
    """
    Return a year select node with defaults and missing values

    :param query_func: a function to call that return the years we want to
        display
    """
    title = kw.pop("title", "")
    missing = kw.pop("missing", deferred_default_year)
    widget_options = kw.pop("widget_options", {})
    default = kw.pop("default", deferred_default_year)
    default_val = widget_options.get("default_val")
    return colander.SchemaNode(
        colander.Integer(),
        widget=get_year_select_deferred(query_func, default_val),
        default=default,
        missing=missing,
        title=title,
        **kw,
    )


def year_filter_node(query_func, **kw):
    widget_options = kw.pop("widget_options", {}).copy()
    # Do not filter by default
    widget_options.setdefault("default_val", ("-1", "Toutes"))
    default = kw.pop("default", colander.null)
    return year_select_node(
        query_func,
        missing=kw.pop("missing", colander.drop),
        default=default,
        widget_options=widget_options,
        **kw,
    )


@colander.deferred
def default_month(node, kw):
    return datetime.date.today().month


def get_month_options():
    return [
        (index, strings.month_name(index, capitalize=True)) for index in range(1, 13)
    ]


def range_validator(appstruct):
    """
    Validate that start and end keys are in the good order (dates, amounts ...)

    :param dict appstruct: The validated datas containing a start and a
    end key
    """
    start = appstruct.get("start")
    if start is not None:
        end = appstruct.get("end")
        if end is not None:
            if end < start:
                return False
    return True


def get_month_select_widget(widget_options):
    """
    Return a select widget for month selection
    """
    options = get_month_options()
    default_val = widget_options.get("default_val")
    if default_val is not None:
        options.insert(0, default_val)
    return deform.widget.SelectWidget(values=options, css_class="input-small")


def month_select_node(**kw):
    """
    Return a select widget for month selection
    """
    title = kw.pop("title", "")
    default = kw.pop("default", default_month)
    missing = kw.pop("missing", default_month)
    widget_options = kw.pop("widget_options", {})
    return colander.SchemaNode(
        colander.Integer(),
        widget=get_month_select_widget(widget_options),
        default=default,
        missing=missing,
        title=title,
        **kw,
    )


def mail_validator():
    """
    Return an email entry validator with a custom error message
    """
    return colander.Email(MAIL_ERROR_MESSAGE)


def mail_node(**kw):
    """
    Return a generic customized mail input field
    """
    title = kw.pop("title", None) or "Adresse e-mail"
    return colander.SchemaNode(
        colander.String(), title=title, validator=mail_validator(), **kw
    )


def id_node():
    """
    Return a node for id recording (usefull in edition forms for retrieving
    original objects)
    """
    return colander.SchemaNode(
        colander.Integer(),
        widget=deform.widget.HiddenWidget(),
        missing=colander.drop,
    )


def public_file_appstruct(request, config_key, file_object):
    """
    Build a form appstruct suitable for a colander File Node from a ConfigFile
    instance

    :param obj request: The Pyramid request
    :param str config_key: The config key under which the file is stored :param
    obj file_object: A :class:`caerp.models.files.ConfigFile` instance
    :rtype: dict
    """
    if file_object is None:
        raise Exception(
            "file_appstruct should not be called with a None " "file object"
        )
    else:
        from caerp.views.files.routes import PUBLIC_ITEM

        return {
            "uid": file_object.id,
            "filename": file_object.name,
            "preview_url": request.route_path(PUBLIC_ITEM, name=config_key),
        }


def file_appstruct(request, file_id):
    """
    Build a form appstruct suitable for a colander File Node from a File
    instance

    :param obj request: The Pyramid request
    :param int file_id: The id of a :class:`caerp.models.files.File`
    instance
    :rtype: dict
    """
    if file_id is None:
        raise Exception(
            "file_appstruct should not be called with a None " "file object"
        )
    else:
        from caerp.views.files.routes import FILE_PNG_ITEM

        return {
            "uid": file_id,
            "filename": "%s.png" % file_id,
            "preview_url": request.route_path(FILE_PNG_ITEM, id=file_id),
        }


def flatten_appstruct(appstruct):
    """
    return a flattened appstruct, suppose all keys in the dict and subdict
    are unique
    """
    res = {}
    for key, value in list(appstruct.items()):
        if not isinstance(value, dict):
            res[key] = value
        else:
            res.update(value)
    return res


def flatten_appstruct_to_key_value(appstruct, path=[], res={}):
    """
    return a flattened path/value dictionnary
    the key contains keys/indexes/attribute names with dot '.' separator
    """
    if type(appstruct) is list:
        for idx, value in enumerate(appstruct):
            res = flatten_appstruct_to_key_value(value, path + [str(idx)], res)
    elif type(appstruct) is dict:
        for key, value in appstruct.items():
            res = flatten_appstruct_to_key_value(value, path + [key], res)
    else:
        res[".".join(path)] = appstruct
    return res


def merge_session_with_post(model, app_struct, remove_empty_values=True):
    """
    Merge Deform validated datas with SQLAlchemy's objects
    Allow to spare some lines of assigning datas to the object
    before writing to database

    model

        The sqlalchemy model

    app_struct

        The datas retrieved for example from a form

    remove_empty_values

        should we remove the colander.null / None values or set them
        on model.
    """
    for key, value in list(app_struct.items()):
        if value == colander.null:
            value = None
        if not (remove_empty_values and value is None):
            setattr(model, key, value)
    return model


def get_excluded(title=None):
    """
    Return a colanderalchemy info dict for excluded columns (includes a title
    for other sqla inspection tools like sqla_inspect library)
    """
    res = {"exclude": True}
    if title is not None:
        res["title"] = title
    return res


def get_hidden_field_conf(title=None):
    """
    Return the model's info conf to get a colanderalchemy hidden widget
    """
    res = {"widget": deform.widget.HiddenWidget(), "missing": None}
    if title is not None:
        res["title"] = title
    return res


def _add_filter_to_model_query(node, bind_params, model, query, filter_def):
    """
    Add a filter to the given query, treat several filter formats

    2-uple (key, value)

        will be converted in .filter(getattr(model, key) == value)

        >>> filter_ = (attr, value)

    sqlalchemy filter

        will be passed directly to the filter method
            list of filters [filter1, filter2, ...]
            Sqlalchemy expressions like

            >>> filter_ = Node.type == 'test'
            >>> filter_ = Node.type.in_(['invoice', 'cancelinvoice'])

    callbale

        Will be called with node and bind_params as argument and should return
        a Sqlalchemy filter
    """
    if isinstance(filter_def, (tuple, list, set)) and len(filter_def) == 2:
        key, value = filter_def
        query = query.filter(getattr(model, key) == value)
    elif isinstance(filter_def, ColumnElement):
        query = query.filter(filter_def)
    elif callable(filter_def):
        query_filter = filter_def(node, kw=bind_params)
        if isinstance(query_filter, ColumnElement):
            query = query.filter(query_filter)
        elif isinstance(query_filter, dict):
            query = query.filter_by(**query_filter)
        else:
            raise Exception(
                "The callable {} should return a valid Sqlalchemy "
                "filter or dict params for filter_by".format(filter_def)
            )
    else:
        raise Exception("Unsupported filter {}".format(filter_def))
    return query


def get_deferred_model_select_validator(
    model, id_key="id", filters=[], query_builder=None
):
    """
    Return a deferred validator based on the given model

        model

            Option model having at least two attributes id and label

        id_key

            The model attr used to store the related object in db (mostly id)

        filters

            see _add_filter_to_model_query

    """

    @colander.deferred
    def deferred_validator(node, kw):
        """
        The deferred function that will be fired on schema binding
        """
        query = _build_model_query(node, model, kw, filters, query_builder)

        return colander.OneOf([getattr(m, id_key) for m in query])

    return deferred_validator


get_deferred_select_validator = get_deferred_model_select_validator


def _build_model_query(node, model, bind_params, filters, query_builder=None):
    """
    Build a query based on the given node, model, filters, and optional query_builder

    :param node: The current node being validated
    :param model: The SQLAlchemy model
    :param bind_params: The bind_params for the current node
    :param filters: List of 2-tuples (key, value)
    :param query_builder: An optional callable that can modify the query
    :returns: A SQLAlchemy query
    """
    if query_builder is not None:
        query = query_builder(bind_params)
    else:
        query = model.query()
        for filter_def in filters:
            query = _add_filter_to_model_query(
                node, bind_params, model, query, filter_def
            )
    return query


def _get_model_select_option_values(
    query,
    keys,
    add_default=True,
    empty_filter_msg="",
):
    """
    Build option list that can be used by SelectWidget and CheckboxListWidget

    :param obj model: The model to query
    :param tuple keys: A 2-uple (idkey, labelkey) to query on the model (it's
    possible to pass callables getting the model as only argument)
    :param list filters: List of 2-uples (key, value)
    :param bool add_default: Should we add a default void value
    :returns: a list of 2-uples
    """
    key1, key2 = keys

    values = []
    if add_default or empty_filter_msg:
        values.append(("", empty_filter_msg))

    for instance in query:
        if callable(key1):
            key = key1(instance)
        else:
            key = getattr(instance, key1)

        if callable(key2):
            label = key2(instance)
        else:
            label = getattr(instance, key2)
        # Avoid duplicates
        if (key, label) not in values:
            values.append((key, label))
    return values


def get_deferred_model_select(
    model,
    multi=False,
    mandatory=False,
    keys=("id", "label"),
    filters=[],
    empty_filter_msg="",
    widget_class=deform.widget.SelectWidget,
    query_builder=None,
):
    """
    Return a deferred select widget based on the given model

        model

            Option model having at least two attributes id and label

        multi

            Should it support multiple item selection

        mandatory

            Is it a mandatory entry, if not, we insert a void value
            default: False

        keys

            a 2-uple describing the (value, label) of the select's options

        filters

            see _add_filter_to_model_query

        widget_class

            A deform widget to use. Should be compatible with the default
            deform.widget.SelectWidget

        query_builder

            A callable query_builder takes bind_params as argument and
            should return a SQLAlchemy query
    """

    @colander.deferred
    def deferred_widget(node, bind_params):
        """
        The deferred function that will be fired on schema binding
        """
        query = _build_model_query(node, model, bind_params, filters, query_builder)

        values = _get_model_select_option_values(
            query,
            keys,
            add_default=not mandatory,
            empty_filter_msg=empty_filter_msg,
        )
        return widget_class(values=values, multi=multi)

    return deferred_widget


get_deferred_select = get_deferred_model_select


def get_deferred_model_select_checkbox(
    model,
    keys=("id", "label"),
    filters=[],
    widget_options={},
    query_builder=None,
):
    """
    Return a deferred select widget based on the given model

        model

            Option model having at least two attributes id and label

        keys

            a 2-uple describing the (value, label) of the select's options

        filters

            list of 2-uples allowing to filter the model query
            (attr/value)

        widget_options

            deform widget options

        query_builder

            A callable query_builder takes bind_params as argument and
            should return a SQLAlchemy query
    """

    @colander.deferred
    def deferred_widget(node, bind_params):
        """
        The deferred function that will be fired on schema binding
        """
        query = _build_model_query(node, model, bind_params, filters, query_builder)

        values = _get_model_select_option_values(
            query,
            keys,
            add_default=False,
        )
        return deform.widget.CheckboxChoiceWidget(values=values, **widget_options)

    return deferred_widget


def get_model_default_value(
    request, model, default_key="default", id_key="id", filters=None
):
    """
    Return the model's default value
    """
    query = select(getattr(model, id_key)).filter(getattr(model, default_key))
    if filters is not None:
        query = _add_filter_to_model_query(None, {}, model, query, filters)
    default = request.dbsession.execute(query).scalar()
    if default is not None:
        return default
    else:
        return colander.null


def get_deferred_default(model, default_key="default", id_key="id"):
    """
    Return a deferred for default model selection

        model

            Option model having at least an id and a default attribute

        default_key

            A boolean attr defining which element is the default one

        id_key

            The default value attr
    """

    @colander.deferred
    def deferred_default(node, kw):
        """
        The deferred function that will be fired on schema binding
        """
        request = kw["request"]
        return get_model_default_value(request, model, default_key, id_key)

    return deferred_default


def get_select(values, multi=False, mandatory=True):
    """
    Return a select widget with the provided options

         values

            options as expected by the deform select widget (a sequence of
            2-uples: (id, label))
    """
    if not isinstance(values, list):
        values = list(values)
    if not mandatory:
        values.insert(0, ("", ""))
    return deform.widget.SelectWidget(values=values, multi=False)


def get_select_validator(options):
    """
    return a validator for the given options

        options

            options as expected by the deform select widget (a sequence of
            2-uples : (id, label))

    """
    return colander.OneOf([o[0] for o in options])


def get_radio(values, mandatory=True, **kw):
    """
    Return a radio widget with the provided options

         values

            options as expected by the deform select widget (a sequence of
            2-uples: (id, label))
    """
    if not isinstance(values, list):
        values = list(values)
    if not mandatory:
        values.insert(0, ("", ""))
    return deform.widget.RadioChoiceWidget(values=values, **kw)


positive_validator = colander.Range(
    min=0,
    min_err="Doit être positif",
)
negative_validator = colander.Range(
    max=0,
    min_err="Doit être négatif",
)


class CustomModelSchemaNode(colander.SchemaNode):
    """
    Using colanderalchemy, it generates a schema regarding a given model, for
    relationships, it provides a schema for adding related datas.  We want to
    be able to configure relationships to existing datas (for example to
    configurable options)

    This SchemaNode subclass provides the methods expected in colanderalchemy
    for serialization/deserialization, it allows us to insert custom schemanode
    in colanderalchemy SQLAlchemySchemaNode

    Can be used in two ways :

    If it's a OnetoOne Relationship :

        >>> node = CustomModelSchemaNode(
                colander.Integer(),
                name="default_business_type",
                model=BusinessType,
                remote_id="id"
            )

    If it's used in OneToMany or ManyToMany Relationships :

        >>> node = CustomModelSchemaNode(
                colander.Integer(),
                name="id",
                model=BusinessType,
            )
    """

    def _get_remote_attribute_name(self):
        return getattr(self, "remote_name", self.name)

    def dictify(self, instance):
        """
        Return the datas needed to fill the form
        """
        attr_name = self._get_remote_attribute_name()
        return getattr(instance, attr_name)

    def objectify(self, value):
        """
        Return the related object that have been configured
        """
        from caerp_base.models.base import DBSESSION

        attr_name = self._get_remote_attribute_name()
        res = (
            DBSESSION()
            .query(self.model)
            .filter(getattr(self.model, attr_name) == value)
            .first()
        )
        if res is None:
            res = colander.null
        logger.debug("Objectify: %s", res)
        return res


def get_sequence_child_item_id_node(model, **kw):
    """
    Build a child item SchemaNode compatible with colanderalchemy's
    serialization technic it provides a node with dictify and objectify methods

    It can be used when editing M2M or O2M relationships

    :param obj model: The model we relay
    """
    if "name" not in kw:
        kw["name"] = "id"

    return CustomModelSchemaNode(colander.Integer(), model=model, **kw)


def get_sequence_child_item(
    model,
    required=False,
    child_attrs=("id", "label"),
    filters=[],
    query_builder=None,
):
    """
    Return the schema node to be used for sequence of related elements
    configuration

    Usefull in a many to many or one to many relationships.
    Needed to be able to configure a sequence of relations to existing objects

    e.g:

        ICPE_codes = relationship(
            "ICPECode",
            secondary=ICPE_CODE_ASSOCIATION_TABLE,
            info={
                'colanderalchemy':{
                    'title': _("Code(s) ICPE"),
                    'children': forms.get_sequence_child_item(model)
                }
            },
            backref="company_info",
        )

    :param obj model: The model used for child items
    :param bool required: At least one element is required ?
    :param tuple child_attrs: The child attributes used to build the options in
    the form ('id_attr', 'label_attr') in most cases id_attr is used as foreign
    key and label_attr is the model's attribute used for display
    :param filters: see _add_filter_to_model_query for details
    """
    missing = colander.drop
    if required:
        missing = colander.required

    return [
        get_sequence_child_item_id_node(
            widget=get_deferred_model_select(
                model,
                keys=child_attrs,
                filters=filters,
                query_builder=query_builder,
            ),
            missing=missing,
            model=model,
            validator=get_deferred_model_select_validator(
                model, filters=filters, query_builder=query_builder
            ),
        )
    ]


class CustomModelSequenceSchemaNode(colander.SchemaNode):
    def __init__(self, *args, **kw):
        colander.SchemaNode.__init__(self, *args, **kw)

    def dictify(self, values):
        return [val.id for val in values]

    def objectify(self, ids):
        from caerp_base.models.base import DBSESSION

        return DBSESSION().query(self.model).filter(self.model.id.in_(ids)).all()


def get_model_checkbox_list_node(model, model_attrs=("id", "label"), filters=[], **kw):
    """
    Build a colander node representing a list of items presented in a checkbox
    list
    """
    query_builder = kw.pop("query_builder", None)
    widget_options = kw.pop("widget_options", {})
    return CustomModelSequenceSchemaNode(
        colander.Set(),
        model=model,
        widget=get_deferred_model_select_checkbox(
            model,
            keys=model_attrs,
            filters=filters,
            widget_options=widget_options,
            query_builder=query_builder,
        ),
        **kw,
    )


def customize_field(schema, field_name, widget=None, validator=None, **kw):
    """
    Customize a form schema field

    :param obj schema: the colander form schema
    :param str field_name: The name of the field to customize
    :param obj widget: a custom widget
    :param obj validator: A custom validator
    :param dict kw: Keyword args set as attributes on the schema field

    """
    if field_name in schema:
        schema_node = schema[field_name]
        if widget is not None:
            schema_node.widget = widget

        if validator is not None:
            schema_node.validator = validator

        for attr, value in list(kw.items()):
            setattr(schema_node, attr, value)
    return schema


def reorder_schema(schema, child_order):
    """
    reorder a schema folowing the child_order

    :param obj schema: The colander schema :class:`colander.Schema`
    :param tuple child_order: The children order
    :returns: The schema
    :rtype: :class:`colander.Schema`
    """
    schema.children = [schema[node_name] for node_name in child_order]
    return schema


def deferred_id_validator(deferred_query):
    """
    Validate that the id belongs to one of the rows from a query

    :param deferred_query: a function returning a query, and receiving standard
      colander.deferred arguments
    """

    @colander.deferred
    def _deferred_id_validator(node, kw):
        return colander.OneOf([i.id for i in deferred_query(node, kw)])

    return _deferred_id_validator


def get_choice_node_widget_options(resource_name, resource_name_plural=None, **kw):
    """
    Build widget Options to build a Select2Widget
    """
    if kw.get("multiple", False):
        if resource_name_plural is None:
            resource_name = f"{resource_name}s"
        else:
            resource_name = resource_name_plural
    widget_options = {
        "title": kw.get("title", resource_name),
        "placeholder": kw.get("placeholder", f"- Sélectionner {resource_name}"),
        "default_option": ("", ""),
        "multiple": kw.get("multiple", False),
    }
    widget_options.update(kw)
    return widget_options


def mk_choice_node_factory(
    base_node_factory, resource_name, resource_name_plural=None, **parent_kw
):
    """
    Specialize a node factory using Select2Widget
    to an item chooser among a list of items.

    Typical use:  field in add/edit form (think ForeignKey)

    :param function base_node_factory: a base node factory
    :param resource_name str: the name of the resource to be selected
      (used in widget strings and as default title)
    :param resource_name_plural str: the pluralized form of the resource name
    """
    if resource_name_plural is None:
        resource_name_plural = resource_name + "s"

    def choice_node(**kw):
        # if a keyword is defined in both parent call and choice_node call,
        # priorize choice_node call (more specific).
        for k, v in list(parent_kw.items()):
            kw.setdefault(k, v)

        if kw.get("multiple", False):
            _resource_name = resource_name_plural
        else:
            _resource_name = resource_name

        widget_options = {
            "title": kw.get("title", _resource_name),
            "placeholder": "- Sélectionner {} -".format(_resource_name),
            "default_option": ("", ""),  # required by placeholder
            "multiple": kw.get("multiple", False),
        }
        widget_options.update(kw.pop("widget_options", {}))
        return base_node_factory(widget_options=widget_options, **kw)

    return choice_node


def mk_filter_node_factory(base_node_factory, empty_filter_msg, **parent_kw):
    """
    Specialize a a node factory using Select2Widget
    to a list filtering node factory.

    :param function base_node_factory: a base node factory
    :param empty_filter_msg str: the name of the list item for "no filter"
      (used in widget strings)
    """

    def filter_node(**kw):
        for k, v in list(parent_kw.items()):
            kw.setdefault(k, v)
        widget_options = {"default_option": ("", empty_filter_msg)}
        widget_options.update(kw.pop("widget_options", {}))

        return base_node_factory(
            missing=colander.drop, widget_options=widget_options, **kw
        )

    return filter_node


def status_filter_node(
    status_options,
    name="status",
    title="Statut",
    default="all",
):
    """
    "Filter by status" SchemaNode for listings
    """
    return colander.SchemaNode(
        colander.String(),
        name=name,
        title=title,
        widget=deform.widget.SelectWidget(values=status_options),
        validator=colander.OneOf([s[0] for s in status_options]),
        missing=default,
        default=default,
    )


def uniq_entries_preparer(cstruct):
    """
    Add this one as a preparer to a colander.SchemaNode of type Sequence in
    order to remove duplicates and None values
    """
    if cstruct:
        return [i for i in set(cstruct) if i]
    else:
        return cstruct


def max_len_validator(length):
    """
    Build a colander length validator for max length
    """
    return colander.Length(max=length, max_err="Ne doit pas dépasser ${max} caractères")


def truncate_preparer(max_len):
    """
    Build a truncate function to be used as a schemaNode preparer
    The function truncate a string to limit its length to the max number of
    characters

    :param str max_len: The max number of characters
    :returns: A preparer function
    """

    def _preparer(value):
        if isinstance(value, (str, bytes)):
            value = value[:max_len]
        return value

    return _preparer


def colander_invalid_on_multiple_nodes(
    node: colander.SchemaNode, childnames: List[str], message: str
):
    """
    Build colander.Invalid on a node and some of its children at once

    To be used in a colander schema node validator
    """
    exc = colander.Invalid(node, "")
    for child in childnames:
        exc.add(colander.Invalid(node[child], message))
    return exc


def force_iterable_preparer(value):
    """Force the value to be an iterable in case the frontend sends a single value in place of a list"""
    logger.debug("force_iterable_preparer: %s", value)
    if isinstance(value, (int, str, bytes, float)):
        logger.debug("force_iterable_preparer:forcing list")
        return [value]
    return value


def get_deferred_global_default_value(
    config_key: Optional[str] = None,
    company_attr: Optional[str] = None,
    default_notfound=None,
):
    """
    Build a deferred that collect a default value at company and/or Config level
    """
    from caerp.models.company import Company
    from caerp.models.config import Config
    from caerp.services.company import find_company_id_from_model

    @colander.deferred
    def deferred(node, kw):
        """Return the global default value for a colander node"""

        result = None
        if company_attr is not None:
            context = kw["request"].context
            company_id = find_company_id_from_model(kw["request"], context)
            query = select(getattr(Company, company_attr)).filter(
                Company.id == company_id
            )
            result = kw["request"].dbsession.execute(query).scalar()

        if result is None and config_key is not None:
            if node.typ == colander.Boolean:
                cast = bool
            elif node.typ == colander.Integer:
                cast = int
            else:
                cast = str
            result = Config.get_value(config_key, type_=cast)

        if result is None:
            result = default_notfound
        return result

    return deferred


def add_antenne_option_field(request, schema, index=0):
    """
    Add antenne_option field to a schema.

    :param request: The request context
    :param schema: The colander schema to add the field to
    :param int index: The index where the field should be inserted
    """
    from caerp.models.user.userdatas import AntenneOption

    if request.dbsession.execute(select(func.count(AntenneOption.id))).scalar_one() > 0:
        schema.insert(
            index,
            colander.SchemaNode(
                colander.Integer(),
                name="antenne_id",
                title="Antenne",
                widget=get_deferred_select(AntenneOption, mandatory=False),
                missing=None,
            ),
        )


def iban_validator(node, values):
    """
    validator for iban strings. Raise a colander.Invalid exception
    when the value is not a valid IBAN.
    """
    try:
        schwifty.IBAN(values, validate_bban=True)
    except schwifty.exceptions.SchwiftyException:
        raise colander.Invalid(node, "Veuillez saisir un IBAN valide")


def bic_validator(node, values):
    "Veuillez saisir un BIC valide"
    try:
        schwifty.BIC(values)
    except schwifty.exceptions.SchwiftyException:
        raise colander.Invalid(node, "Veuillez saisir un BIC valide")


def deform_options_to_js_options(
    options: List[Tuple[Any, str]]
) -> List[Dict[str, Any]]:
    """
    Convert a list of tuples to a list of dictionaries

    Usage : take a list of tuples made for deform.widget.SelectWidget and convert it
    to a list of dictionaries for vuejs Select widget
    """
    return [{"id": item[0], "label": item[1]} for item in options]
