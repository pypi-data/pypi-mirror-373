"""
    Base views with commonly used utilities
"""

import functools
import inspect
import itertools
import logging
from typing import Dict, List, Optional, Union

import colander
import colanderalchemy
import deform
import deform_extensions
from caerp_base.models.base import DBSESSION
from caerp_celery.models import Job
from caerp_celery.tasks.utils import check_alive
from deform import Button, Form
from deform_extensions import GridFormWidget
from paginate_sqlalchemy import SqlalchemyOrmPage
from pyramid.httpexceptions import HTTPFound
from pyramid.interfaces import ISession
from pyramid.request import Request
from pyramid.response import Response
from pyramid_deform import CSRFSchema
from sqla_inspect.csv import SqlaCsvExporter
from sqla_inspect.excel import SqlaXlsExporter
from sqla_inspect.ods import SqlaOdsExporter
from sqlalchemy import asc, desc

from caerp.compute.math_utils import convert_to_int
from caerp.consts.permissions import PERMISSIONS
from caerp.export.utils import write_file_to_request
from caerp.forms.lists import BaseListsSchema
from caerp.resources import tinymce
from caerp.services.serializers.base import BaseSerializer
from caerp.utils.renderer import set_close_popup_response
from caerp.utils.rest.apiv1 import RestError
from caerp.utils.rest.parameters import (
    FieldOptions,
    LoadOptions,
    PaginationOptions,
    RestCollectionMetadata,
    RestCollectionResponse,
    SortOptions,
)
from caerp.utils.widgets import Link

logger = logging.getLogger(__name__)


submit_btn = Button(
    name="submit", type="submit", title="Valider", css_class="btn btn-primary"
)
cancel_btn = Button(name="cancel", type="submit", title="Annuler", css_class="btn")

API_ROUTE = "/api/v1"


class BaseView:
    def __init__(self, context, request=None):
        self.logger = logging.getLogger("caerp.views.__init__")
        self.logger.info(f"Using view {self}")
        if request is None:
            # Needed for manually called views
            self.request: Request = context
            self.context = self.request.context
        else:
            self.request: Request = request
            self.context = context
        self.session: ISession = self.request.session
        self.dbsession: DBSESSION = self.request.dbsession


class BaseListClass(BaseView):
    """
    Base class for list related views (list view and exports)

        * It launches a query to retrieve records
        * Validates GET params regarding the given schema
        * filter the query with the provided filter_* methods

    @param schema: Schema used to validate the GET params provided in the
                    url, the schema should inherit from
                    caerp.views.forms.lists.BaseListsSchema to preserve
                    most of the processed automation
    @param sort_columns: dict of {'sort_column_key':'sort_column'...}.
        Allows to generate the validator for the sort availabilities and
        to automatically add a order_by clause to the query. sort_column
        may be equal to Table.attribute if join clauses are present in the
        main query.
    @default_sort: the default sort_column_key to be used
    @default_direction: the default sort direction (one of ['asc', 'desc'])

    Subclass should provide
      - a view callable (either __call__() or a named method).
      - a _collect_appstruct() method
    """

    default_sort = "name"
    sort_columns = {"name": "name"}
    default_direction = "asc"

    def _get_bind_params(self):
        """
        return the params passed to the form schema's bind method
        if subclass override this method, it should call the super
        one's too
        """
        return dict(
            request=self.request,
            default_sort=self.default_sort,
            default_direction=self.default_direction,
            sort_columns=self.sort_columns,
        )

    def query(self):
        """
        The main query, should be overrided by a subclass
        """
        raise NotImplementedError("You should implement the query method")

    def _get_filters(self):
        """
        collect the filter_... methods attached to the current object
        """
        for key in dir(self):
            if key.startswith("filter_"):
                func = getattr(self, key)
                if inspect.ismethod(func):
                    yield func

    def _filter(self, query, appstruct):
        """
        filter the query with the configured filters
        """
        for method in self._get_filters():
            query = method(query, appstruct)
        return query

    def _get_sort_key(self, appstruct):
        """
        Retrieve the sort key to use

        :param dict appstruct: Form submitted datas
        :rtype: str
        """
        if "sort" in self.request.GET:
            result = self.request.GET["sort"]
        elif "sort" in appstruct:
            result = appstruct["sort"]
        else:
            result = self.default_sort
        return result

    def _get_sort_direction(self, appstruct):
        """
        Retrieve the sort direction to use

        :param dict appstruct: Form submitted datas
        :rtype: str
        """
        if "direction" in self.request.GET:
            result = self.request.GET["direction"]
        elif "direction" in appstruct:
            result = appstruct["direction"]
        else:
            result = self.default_direction
        return result

    def _sort(self, query, appstruct):
        """
        Sort the results regarding the default values and
        the sort_columns dict, maybe overriden to provide a custom sort
        method
        """
        sort_column_key = self._get_sort_key(appstruct)
        if self.sort_columns and sort_column_key:
            self.logger.info("  + Sorting the query : %s" % sort_column_key)

            custom_sort_method = getattr(self, "sort_by_%s" % sort_column_key, None)
            if custom_sort_method is not None:
                query = custom_sort_method(query, appstruct)
            else:
                sort_column = self.sort_columns.get(sort_column_key)

                if sort_column:
                    sort_direction = self._get_sort_direction(appstruct)
                    self.logger.info("  + Direction : %s" % sort_direction)

                    if sort_direction == "asc":
                        func = asc
                        query = query.order_by(func(sort_column))
                    elif sort_direction == "desc":
                        func = desc
                        query = query.order_by(func(sort_column))
        return query


class BaseListClassWithForm(BaseListClass):
    """
    A list view, handling a search/filter form.

    A subclass shoud provide at least a schema and a query method
    """

    grid = None
    filter_button_label = "Lancer la recherche avec ces critères"
    filter_button_icon = "search"
    filter_button_css = "btn btn-primary icon only"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error = None

    def get_schema(
        self,
    ) -> Union[None, colander.Schema, colanderalchemy.SQLAlchemySchemaNode]:
        if self.schema is not None:
            schema = self.schema
            if (
                inspect.isclass(schema)
                or inspect.isfunction(schema)
                or inspect.ismethod(schema)
            ):
                schema = schema()
            return schema
        else:
            return None

    def set_form_widget(self, form):
        """
        Attach a custom widget to the given form

        :param obj form: The deform.Form instance
        :returns: The deform.Form instance
        :rtype: obj
        """
        if self.grid is not None:
            form.formid = "grid_search_form"
            form.widget = deform_extensions.GridFormWidget(named_grid=self.grid)
        else:
            form.widget.template = "searchform.pt"
        return form

    def get_filter_button(self):
        """
        Return the definition of the filter button
        """
        self.logger.info("Building the filter button : %s" % self.filter_button_label)
        return deform.Button(
            title=self.filter_button_label,
            name="submit",
            type="submit",
            css_class=self.filter_button_css,
            icon=self.filter_button_icon,
        )

    def get_form(self, schema):
        """
        Return the search form that should be used for this view

        :param obj schema: The form's colander.Schema
        :returns: The form object
        :rtype: obj
        """
        # counter is used to avoid field name conflicts
        form = Form(schema, counter=itertools.count(15000), method="GET")
        form = self.set_form_widget(form)
        form.buttons = (self.get_filter_button(),)
        return form

    def _get_submitted(self):
        return self.request.GET

    def _collect_appstruct(self):
        """
        collect the filter options from the current url

        Use the schema to validate the GET params of the current url and
        returns the formated datas
        """
        self.schema = self.get_schema()
        appstruct = {}
        if self.schema is not None:
            self.schema = self.schema.bind(**self._get_bind_params())
            try:
                form = self.get_form(self.schema)
                submitted = self._get_submitted()
                if "__formid__" in submitted:
                    submitted = list(submitted.items())
                    logger.info("  - Form submitted values : %s" % submitted)
                    appstruct = form.validate(submitted)
                else:
                    appstruct = form.cstruct
            except deform.ValidationFailure as e:
                # If values are not valid, we want the default ones to be
                # provided see the schema definition
                self.logger.exception("  - Current search values are not valid ")
                self.logger.error(e)
                if hasattr(e, "error"):
                    self.logger.error(e.error)
                appstruct = self.schema.deserialize({})
                self.error = e
                # https://framagit.org/caerp/caerp/-/issues/2789
                # raise e

        return self.schema, appstruct

    def __call__(self):
        self.logger.info("# Calling the list view #")
        self.logger.info(" + Collecting the appstruct from submitted datas")
        schema, appstruct = self._collect_appstruct()
        self.appstruct = appstruct
        self.logger.info(appstruct)
        self.logger.info(" + Launching query")
        query = self.query()
        if query is not None:
            self.logger.info(" + Filtering query")
            query = self._filter(query, appstruct)
            self.logger.info(" + Sorting query")
            query = self._sort(query, appstruct)

        self.logger.info(" + Building the return values")
        return self._build_return_value(schema, appstruct, query)

    def _build_return_value(self, schema, appstruct, query):
        """
        To be implemented : datas returned by the view
        """
        return {}


def get_page_url(request, page):
    """
    Page url generator to be used with webob.paginate's tool

    Note : default Webob pagination tool doesn't respect query_params order and
    breaks mapping order, so we can't preserve search params in list views
    """
    args = request.GET.copy()
    args["page"] = str(page)
    return request.current_route_path(_query=args)


class PopupMixin:
    """
    Provide methods for handling popup related actions
    """

    request = None
    popup_force_reload = False

    def add_popup_response(self):
        """
        Add custom response string to the request :
            Pop message
            or
            Refresh parent page

        regarding the options
        if
        a message was set in the queue, it's shown with a refresh link
        else
        we fully reload the page

        """
        self.logger.info("Building a popup_close response")
        params = {
            "force_reload": self.popup_force_reload,
        }
        msg = self.request.session.pop_flash(queue="")
        if msg:
            params["message"] = msg[0]

        set_close_popup_response(self.request, **params)


class BaseListView(BaseListClassWithForm):
    """
    A base list view used to provide an easy way to build list views
    Uses the BaseListClass and add the templating datas :

        * Provide a pagination object
        * Provide a search form based on the given schema
        * Launches complementary methods to populate request vars like popup
        or actionmenu

    @param add_template_vars: list of attributes (or properties)
                                that will be automatically added
    """

    add_template_vars = ()
    grid = None
    use_paginate = True
    title = None
    title_detail = None

    def _get_item_url(self, item, action=None, **kw):
        """
        Build an url to an item's action

        Usefull from inside the stream_actions method

        :param obj item: An instance with an id
        :param str action: The name of the action
        (duplicate/disable/edit...)
        :param dict kw: Other optionnal route params passed to route_path call

        :returns: An url
        :rtype: str
        """
        if not hasattr(self, "item_route_name"):
            raise NotImplementedError("Un attribut item_route_name doit être défini")

        query = dict(self.request.GET)
        if action is not None:
            query["action"] = action

        return self.request.route_path(
            self.item_route_name, id=item.id, _query=query, **kw
        )

    def _get_current_page(self, appstruct):
        """
        Return the current requested page
        """
        if "page" in self.request.GET:
            res = self.request.GET["page"]
        elif "page" in appstruct:
            res = appstruct["page"]
        else:
            res = 1
        return convert_to_int(res, 1)

    def _paginate(self, query, appstruct):
        """
        wraps the current SQLA query with pagination
        """
        if self.use_paginate:
            # Url builder for page links
            page_url = functools.partial(get_page_url, self.request)

            current_page = self._get_current_page(appstruct)
            items_per_page = convert_to_int(appstruct.get("items_per_page", 30), 30)

            self.logger.info(
                " + Page : %s, items per page : %s" % (current_page, items_per_page)
            )

            page = SqlalchemyOrmPage(
                query,
                current_page,
                url_maker=page_url,
                items_per_page=items_per_page,
            )
            self.logger.info(page)
            return page
        else:
            return query

    def more_template_vars(self, response_dict):
        """
        Add template vars to the response dict
        List the attributes configured in the add_template_vars attribute
        and add them
        """
        result = {}
        for name in self.add_template_vars:
            result[name] = getattr(self, name)
        return result

    def populate_actionmenu(self, appstruct):
        """
        Used to populate an actionmenu (if there's one in the page)
        actionmenu is a request attribute used to automate the integration
        of actionmenus in pages
        """
        pass

    def _build_return_value(self, schema, appstruct, query):
        """
        Return the datas expected by the template
        """
        if query is None:
            records = None
        else:
            if self.use_paginate:
                records = self._paginate(query, appstruct)
            else:
                records = query

        result = dict(records=records, use_paginate=self.use_paginate)

        if schema is not None:
            if self.error is not None:
                result["form_object"] = self.error
                result["form"] = self.error.render()
            else:
                form = self.get_form(schema)
                if appstruct and "__formid__" in self.request.GET:
                    form.set_appstruct(appstruct)
                result["form_object"] = form
                result["form"] = form.render()

        result["title"] = self.title
        result["title_detail"] = self.title_detail
        result.update(self.more_template_vars(result))
        self.populate_actionmenu(appstruct)
        return result


class BaseCsvView(BaseListClassWithForm):
    """
    Base Csv view

    A list view that returns a streamed file

    A subclass should implement :

        * a query method
        * filename property

    To be able to handle the rows that are streamed:

        * a _stream_rows method

    If this view should support the GET params filtering method (export
    associated to a list view), a subclass should provide:

        * a schema attr
        * filter_ methods
    """

    model = None
    writer = SqlaCsvExporter

    @property
    def filename(self):
        """
        To be implemented by the subclass
        """
        pass

    def _stream_rows(self, query):
        """
        Return a generator with the rows we expect in our output,
        default is to return the sql ones
        """
        for item in query.all():
            yield item

    def _init_writer(self):
        self.logger.info("# Initializing a writer %s" % self.writer)
        self.logger.info(" + For the model : %s" % self.model)
        writer = self.writer(model=self.model)
        if hasattr(self, "sheet_title") and hasattr(writer, "set_title"):
            writer.set_title(self.sheet_title)
        return writer

    def _build_return_value(self, schema, appstruct, query):
        """
        Return the streamed file object
        """
        writer = self._init_writer()
        self.logger.info(" + Streaming rows")
        for item in self._stream_rows(query):
            writer.add_row(item)
        self.logger.info(" + Writing the file to the request")
        write_file_to_request(self.request, self.filename, writer.render())
        return self.request.response


class BaseXlsView(BaseCsvView):
    writer = SqlaXlsExporter


class BaseOdsView(BaseCsvView):
    writer = SqlaOdsExporter


class BaseFormView(BaseView, PopupMixin):
    """
    Allows to easily build form views

    **Attributes that you may override**

    .. attribute:: add_template_vars

        List of attribute names (or properties) that will be added to the
        result dict object and that you will be able to use in your
        templates (('title',) by default)

    .. attribute:: buttons

        list or tupple of deform.Button objects (or strings), only a submit
        button is added by default

    .. attribute:: schema

        colander form schema to be used to render our form you may also
        want to override get_schema method instead

    .. attribute:: form_class

        form class to use (deform.Form by default)

    **Methods that your should implement**

    .. method:: <button_name>_success(appstruct)

        Is called when the form has been submitted and validated with
        the button called button_name.

        *appstruct* : the colander validated datas (a dict)

    **Methods that you may implement**

    .. method:: before(form)

        Allows to execute some code before the validation process
        e.g: add datas to the form that will be rendered
        Will typically be overrided in an edit form.

        *form* : the form object that's used in our view

    .. method:: get_schema(): return the unbound schema to be used ; may be
       preferred to schema attribute if you want something dynamic.

    .. method:: <button_name>_failure(e)

        Is called when the form has been submitted the button called
        button_name and the datas have not been validated.

        *e* : deform.exception.ValidationFailure that has
            been raised by colander

    .. code-block:: python

        class MyFormView(BaseFormView):
            title = "My form view"
            schema = MyColanderSchema

            def before(self, form):
                form.set_appstruct(self.request.context.appstruct())

            def submit_success(self, appstruct):
                # Handle the filtered appstruct
    """

    form_class = deform.Form
    form_options = ()
    schema = None
    buttons = (submit_btn,)
    use_csrf_token = False  # FIXME: make it default to True

    title = None
    title_detail = None
    add_template_vars = ()

    def __init__(self, context, request=None):
        super().__init__(context, request)
        if self.request.has_permission(PERMISSIONS["global.access_ea"]):
            tinymce.need()

    def before(self, form):
        if hasattr(self, "named_form_grid"):
            form.widget = GridFormWidget(named_grid=self.named_form_grid)
        elif hasattr(self, "form_grid"):
            form.widget = GridFormWidget(grid=self.form_grid)

    def get_schema(
        self,
    ) -> Union[colander.Schema, colanderalchemy.SQLAlchemySchemaNode]:
        if self.schema is not None:
            schema = self.schema
            if (
                inspect.isclass(schema)
                or inspect.isfunction(schema)
                or inspect.ismethod(schema)
            ):
                schema = schema()
            return schema
        else:
            raise NotImplementedError(
                "You should implement one of get_schema() method or schema attr"
            )

    def get_bind_data(self) -> dict:
        return dict(request=self.request)

    def appstruct(self):
        """
        Returns an ``appstruct`` for form default values when rendered.

        By default, this method does nothing. Override this method in
        your dervived class and return a suitable entity that can be
        used as an ``appstruct`` and passed to the
        :meth:`deform.Field.render` of an instance of
        :attr:`form_class`.
        """
        return None

    def failure(self, e):
        """
                Default action upon form validation failure.

                Returns the result of :meth:`render` of the given ``e`` object
                (an instance of :class:`deform.exception.ValidationFailure`) as the
        --        ``form`` key in a ``dict`` structure.
        """
        return {"form": e.render()}

    def show(self, form):
        """
        Render the given form, with or without an ``appstruct`` context.

        The given ``form`` argument will be rendered with an ``appstruct``
        if :meth:`appstruct` provides one.  Otherwise, it is rendered without.
        Returns the rendered form as the ``form`` key in a ``dict`` structure.
        """
        appstruct = self.appstruct()
        if appstruct is None:
            rendered = form.render()
        else:
            rendered = form.render(appstruct)
        return {
            "form": rendered,
        }

    def __call__(self):
        self.schema = self.get_schema()

        if self.use_csrf_token and "csrf_token" not in self.schema:
            self.schema.children.append(CSRFSchema()["csrf_token"])

        try:
            use_ajax = getattr(self, "use_ajax", False)
            ajax_options = getattr(self, "ajax_options", "{}")
            self.schema = self.schema.bind(**self.get_bind_data())
            form = self.form_class(
                self.schema,
                buttons=self.buttons,
                use_ajax=use_ajax,
                ajax_options=ajax_options,
                **dict(self.form_options),
            )

            self.before(form)
            reqts = form.get_widget_resources()
            result = None

            for button in form.buttons:
                if button.name in self.request.POST:
                    success_method = getattr(self, "%s_success" % button.name)
                    controls = self.request.POST.items()

                    if button.name == "cancel":
                        result = success_method(dict(controls))
                        break

                    try:
                        validated = form.validate(controls)
                        result = success_method(validated)
                    except deform.exception.ValidationFailure as e:
                        fail = getattr(self, "%s_failure" % button.name, None)
                        if fail is None:
                            fail = self.failure
                        result = fail(e)
                    break

            if result is None:
                result = self.show(form)

            if isinstance(result, dict):
                result["js_links"] = reqts["js"]
                result["css_links"] = reqts["css"]

        except colander.Invalid as exc:
            self.logger.exception(
                "Exception while rendering form '%s': %s - struct received: %s",
                self.title,
                exc,
                self.appstruct(),
            )
            raise
        if isinstance(result, dict):
            result.update(self._more_template_vars())

        if self.request.is_popup:
            if isinstance(result, HTTPFound):
                logger.info("Returning popup response")
                self.add_popup_response()
                return self.request.response
        return result

    def _more_template_vars(self):
        """
        Add template vars to the response dict
        """
        result = {}
        # Force title in template vars
        result["title"] = self.title
        result["title_detail"] = self.title_detail

        for name in self.add_template_vars:
            result[name] = getattr(self, name)
        return result

    def form_label(self) -> str:
        """
        Usefull optionnal tool used in multiform views (when we can add an
        element in different ways

        :returns: The name of the submitted form
        :rtype: str
        """
        return self.request.POST.get("__formid__", "")

    def _get_form(self):
        """
        A simple hack to be able to retrieve the form once again
        """
        use_ajax = getattr(self, "use_ajax", False)
        ajax_options = getattr(self, "ajax_options", "{}")
        self.schema = self.get_schema().bind(**self.get_bind_data())
        form = self.form_class(
            self.schema,
            buttons=self.buttons,
            use_ajax=use_ajax,
            ajax_options=ajax_options,
            **dict(self.form_options),
        )
        self.before(form)
        return form

    def submit_failure(self, e):
        """
        Called by default when we failed to submit the values
        We add a token here for forms that are collapsed by default to keep
        them open if there is an error
        """
        self.logger.exception(e)
        # On loggergue l'erreur colander d'origine
        self.logger.exception(e.error)
        print(e)
        print((e.error))
        return dict(form=e.render(), formerror=True)


class BaseAddView(BaseFormView):
    """
    Admin view that should be subclassed adding a colanderalchemy schema

    class AdminModel(BaseAddView):
        schema = SQLAlchemySchemaNode(MyModel)
        model = MyModel
    """

    add_template_vars = ("title", "help_msg")
    msg = "Vos modifications ont bien été enregistrées"
    factory = None
    redirect_route = None

    @property
    def help_msg(self):
        factory = getattr(self, "factory", None)
        if factory is not None:
            calchemy_dict = getattr(factory, "__colanderalchemy_config__", {})
        else:
            calchemy_dict = {}
        return calchemy_dict.get("help_msg", "")

    def create_instance(self):
        """
        Initiate a new instance
        """
        if self.factory is None:
            raise NotImplementedError("Missing mandatory 'factory' attribute")
        return self.factory()

    def merge_appstruct(self, appstruct, model):
        """
        Merge the appstruct with the newly create model

        :param dict appstruct: Validated form datas
        :param obj model: A new instance of the object we create
        :returns: The model this view is supposed to add
        """
        model = self.get_schema().objectify(appstruct, model)
        return model

    def submit_success(self, appstruct):
        new_model = self.create_instance()
        new_model = self.merge_appstruct(appstruct, new_model)
        self.dbsession.add(new_model)

        if hasattr(self, "on_add"):
            self.on_add(new_model, appstruct)

        self.dbsession.flush()
        if self.msg:
            self.request.session.flash(self.msg)

        if hasattr(self, "redirect"):
            return self.redirect(appstruct, new_model)
        elif self.redirect_route is not None:
            return HTTPFound(self.request.route_path(self.redirect_route))


class BaseEditView(BaseFormView):
    """
    ColanderAlchemy schema based view

    class AdminModel(BaseEditView):
        schema = SQLAlchemySchemaNode(MyModel)


    Methods and attributes you can set

    Form Schema related hooks

        attribute schema

            Form Schema to use in this form view
            Can be
              a callable
              a class
              an instance of a schema

        get_schema



    """

    add_template_vars = ("title", "help_msg")
    msg = "Vos modifications ont bien été enregistrées"
    redirect_route = None

    @property
    def help_msg(self):
        factory = getattr(self, "factory", None)
        if factory is not None:
            calchemy_dict = getattr(factory, "__colanderalchemy_config__", {})
        else:
            calchemy_dict = {}
        return calchemy_dict.get("help_msg", "")

    def get_default_appstruct(self):
        """
        Collect datas that will initially populate the form
        """
        model = self.get_context_model()
        return self.schema.dictify(model)

    def before(self, form):
        BaseFormView.before(self, form)
        form.set_appstruct(self.get_default_appstruct())

    def merge_appstruct(self, appstruct, model):
        """
        Merge the appstruct with current model

        :param dict appstruct: Validated form datas
        :param obj model: A new instance of the object we create
        :returns: The model this view is supposed to add
        """
        model = self.get_schema().objectify(appstruct, model)
        return model

    def get_context_model(self):
        """
        Return the model we're editing, by default it's the current context but
        in case of OneToOne relationship, it can be that the context is a
        related model, Overriding this method we can provide the model to edit

        :returns: The model that will be edited by this view
        """
        return self.context

    def on_edit(self, appstruct, model):
        """Hook launched before the session is flushed"""
        pass

    def flash_message(self, appstruct, model):
        if self.msg:
            self.request.session.flash(self.msg)

    def submit_success(self, appstruct):
        model = self.get_context_model()
        model = self.merge_appstruct(appstruct, model)
        self.dbsession.merge(model)

        self.on_edit(appstruct, model)

        self.dbsession.flush()
        self.flash_message(appstruct, model)

        if hasattr(self, "redirect"):
            return self.redirect(appstruct)
        elif self.redirect_route is not None:
            return HTTPFound(self.request.route_path(self.redirect_route))
        else:
            raise NotImplementedError("A redirection strategy should be provided")

    def cancel_success(self, appstruct):
        if hasattr(self, "redirect"):
            return self.redirect(appstruct)
        elif self.redirect_route is not None:
            return HTTPFound(self.request.route_path(self.redirect_route))
        else:
            raise NotImplementedError("A redirection strategy should be provided")


class DisableView(BaseView):
    """
    Main view for enabling/disabling elements

    Support following attributes/methods

    Attributes

        enable_msg

                Message flashed when enabled

        disable_msg

                Message flashed when disabled

        redirect_route

                The name of a route to redirect to

    Methods

        redirect

            Return a dynamicallay created HTTPFound instance

        on_disable

            Launched on item disable

        on_enable

            Launched on item enable

        disable

            By default disable the current context but can be overridden


    class MyDisableView(DisableView):
        enable_msg = "Has been enabled"
        disabled_msg = "Has been disabled"
        redirect_route = "The route name"
    """

    enable_msg = None
    disable_msg = None
    redirect_route = None
    active_key = "active"

    def get_item(self):
        return self.context

    def __call__(self):
        item = self.get_item()
        if getattr(item, self.active_key):
            setattr(item, self.active_key, False)
            self.dbsession.merge(item)

            if hasattr(self, "on_disable"):
                self.on_disable()

            if self.disable_msg is not None:
                self.request.session.flash(self.disable_msg)
        else:
            setattr(item, self.active_key, True)
            self.dbsession.merge(item)
            if hasattr(self, "on_enable"):
                self.on_enable()
            if self.enable_msg is not None:
                self.request.session.flash(self.enable_msg)

        if hasattr(self, "redirect"):
            return self.redirect()
        elif self.redirect_route is not None:
            return HTTPFound(self.request.route_path(self.redirect_route))


class DeleteView(BaseView, PopupMixin):
    """
    Deletion view deletes the current context

    Class Attributes

        delete_msg

            The message poped to the end user after the element is deleted

        redirect_route

            The name of the route we redirect after deletion


    Following methods can be overriden if needed

    delete

        Perform the orm delete action

    on_before_delete

        Run before the deletion

    on_delete

        Run after the object has been deleted

    redirect_route

        Data that will be returned by the view
        (default is HTTPFound but can also be json data)


    .. code-block:: python

        class MyDeleteView(DeleteView):
            delete_msg = "L'élément a bien été supprimé"
            redirect_route = "templates"

    redirect

        Method that can be overriden to return a HTTPFound instance

    """

    delete_msg = "L'élément a bien été supprimé"
    redirect_route = None

    def _log_deletion(self):
        logger.info(
            "# {} deletes {} {}".format(
                self.request.identity,
                str(self.context.__class__.__name__),
                self.context.id,
            )
        )

    def on_before_delete(self):
        pass

    def on_delete(self):
        pass

    def redirect(self):
        return HTTPFound(self.request.route_path(self.redirect_route))

    def delete(self):
        self.dbsession.delete(self.context)

    def __call__(self):
        self._log_deletion()
        self.on_before_delete()
        try:
            self.delete()
        except Exception:
            logger.exception("Unknown error")
            self.request.session.flash(
                "Une erreur inconnue s'est produite",
                queue="error",
            )

        else:
            if self.delete_msg is not None:
                self.request.session.flash(self.delete_msg)

            self.on_delete()

        result = self.redirect()
        if self.request.is_popup:
            if isinstance(result, HTTPFound):
                self.add_popup_response()
                return self.request.response
        return result


class DuplicateView(BaseView):
    """
    Base Duplication view

    calls the duplicate method on the view's context
    flash a link to the duplicated item
    redirect to the redirect route

    :attr str route_name: The route_name used to generate the link to the
    duplication view (implement _link to override default generation)

    :attr str collection_route_name: optionnal collection route name to which
    redirect (default set to route_name + 's'), implement a _redirect method to
    override the redirection mechanism

    :attr str message: The duplication message, take a single formatting value
    (the link to the new item)
    """

    message = None
    route_name = None
    collection_route_name = None

    def _link(self, item):
        if self.route_name is None:
            raise NotImplementedError("Set a route_name attribute for link generation")
        return self.request.route_path(self.route_name, id=item.id)

    def _message(self, item):
        if self.message is None:
            raise NotImplementedError(
                "Set a message attribute for flashed message generation"
            )
        return self.message.format(self._link(item))

    def redirect(self, item):
        """
        Default redirect implementation

        :param obj item: The newly created element (flushed)
        :returns: The url to redirect to
        :rtype: str
        """
        return HTTPFound(self.request.route_path(self.route_name, id=item.id))

    def __call__(self):
        item = self.context.duplicate()
        self.dbsession.add(item)
        # We need an id
        self.dbsession.flush()
        if hasattr(self, "on_duplicate"):
            self.on_duplicate(item)

        self.request.session.flash(self._message(item))
        return self.redirect(item)


class BaseRestView(BaseView):
    """
    A base rest view

    provides the base structure for a rest view for sqlalchemy model access

    it handles :

        get
        delete
        put
        post requests

    thanks to the colanderalchemy tools, we dynamically build the resulting
    model

    Main Add/edit process:

        1- get_schema
        2- Hook : pre_format
        3- create/update model
        4- Hook : post_format
        5- session.merge/session.add
        6- Hook : after_flush

    Following datas should be provided :

        * Attributes

            schema

                A colanderalchemy schema, it can be provided through a property
                or a simple attribute. For on the fly schema handling, you can
                also override the get_schema method that returns self.schema by
                default

    The following could be provided

        Methods

            get_schema

                See above comment

            pre_format

                Preformat submitted values before passing them to the form
                schema

            post_format

                Launched after the model has been created/updated and before
                add/merge

            after_flush

                Launched after the entry was added / merged in the session and
                flushed


    For get method :

    a "fields" parameter can be passed to get a subset of the context's json data


    GET /api/v1/estimations/125?fields=attachments&fields=description

    NB :
    - Only attributes and properties can be retrieved that way
    - Unless what is done in the __json__ method, the data are returned without any
      formatting

    """

    schema = None

    def get_schema(
        self, submitted: dict
    ) -> Union[colanderalchemy.SQLAlchemySchemaNode, colander.Schema]:
        """Build the colander schema to be used

        :param submitted: Data submitted to the api endpoint

        :return: A form schema used to validate the submitted data
        """
        if self.schema is None:
            raise NotImplementedError("No schema was provided")
        else:
            return self.schema

    def _filter_edition_schema(self, schema, submitted):
        """
        filter the schema in case of edition removing all keys not present in
        the submitted datas (allow to edit only one field)

        :param dict submitted: the raw submitted datas
        :param obj schema: the schema we're going to use
        """
        # le schéma peut être un attribut de classe, dans ce cas, lorsque l'on
        # supprime des noeuds du schéma ci-dessous, ils sont supprimés pour
        # toute la durée de vie du processus wsgi Cela provoque des
        # comportement étrange. Pour éviter cela, on renvoie un clone du schéma
        # qui ne durera que le temps de la requête
        if hasattr(schema, "clone"):
            schema = schema.clone()
        else:
            # On loggue pour identifier d'éventuelles situation que l'on aurait
            # pas anticipée.
            logger.info(
                "TODO CHECK Class {} : This schema {} has no 'clone' method".format(
                    self, schema
                )
            )
        # In edition, we only keep edited fields
        submitted_keys = list(submitted.keys())
        toremove = [node for node in schema if node.name not in submitted_keys]
        for node in toremove:
            del schema[node.name]

        return schema

    def format_item_result(self, model) -> Union[dict, object]:
        """Build the data to be returned by the api endpoint

        :param item: The current sqlalchemy Model

        :return: An object with a __json__ method or a dict that can be json serialized
        """
        if "fields" in self.request.GET:
            fields = self.request.GET.getall("fields")
            result = {}
            for field in fields:
                if hasattr(model, field):
                    result[field] = getattr(model, field)
                else:
                    logger.warn(
                        "Le contexte {} n'a pas d'attribut ou de property {}".format(
                            model, field
                        )
                    )
            return result

        return model

    def get(self):
        """
        End point for HTTP GET calls
        """
        return self.format_item_result(self.context)

    def pre_format(self, datas, edit=False):
        """
        Allows to apply pre-formatting to the submitted datas

        HTTP POST and PUT calls

        :param dict datas: The submitted datas
        :param bool edit: Is it an edition view ?
        """
        return datas

    def post_format(self, entry, edit, attributes):
        """
        Allows to apply post formatting to the model before flushing it

        HTTP POST and PUT calls

        :param entry: The instance added/edited
        :param bool edit: Is it an edition view ?
        :param dict attributes: The validated submitted data
        """
        return entry

    def after_flush(self, entry, edit, attributes):
        """
        Allows to modify datas after the main entry was flushed

        HTTP POST and PUT calls

        :param entry: The instance added/edited
        :param bool edit: Is it an edition view ?
        :param dict attributes: The validated submitted data
        :return: the altered model
        """
        return entry

    def get_editted_element(self, attributes):
        """
        Returns the element we edit

        HTTP PUT calls

        :param dict attributes: The validated submitted data
        """
        return self.context

    def _edit_element(self, schema, attributes):
        editted = self.get_editted_element(attributes)
        entry = schema.objectify(attributes, editted)
        entry = self.post_format(entry, True, attributes)
        entry = self.dbsession.merge(entry)
        self.dbsession.flush()
        return entry

    def _add_element(self, schema, attributes):
        entry = schema.objectify(attributes)
        entry = self.post_format(entry, False, attributes)
        self.dbsession.add(entry)
        # We need an id => flush
        self.dbsession.flush()
        return entry

    def _submit_datas(self, submitted, edit=False):
        self.logger.info(" + Submitting %s" % submitted)
        submitted = self.pre_format(submitted, edit)
        self.logger.info(" + After pre format %s" % submitted)
        schema = self.get_schema(submitted)

        if edit:
            schema = self._filter_edition_schema(schema, submitted)

        schema = schema.bind(request=self.request)

        try:
            attributes = schema.deserialize(submitted)
        except colander.Invalid as err:
            self.logger.exception("  - Erreur")
            self.logger.exception(submitted)
            raise RestError(err.asdict(), 400)

        self.logger.info(" + After deserialize : %s" % attributes)
        if edit:
            entry = self._edit_element(schema, attributes)
        else:
            entry = self._add_element(schema, attributes)
        entry = self.after_flush(entry, edit, attributes)
        self.logger.info("Finished")
        return self.format_item_result(entry)

    def get_posted_data(self):
        """
        Returns the data passed for a PUT/POST request
        Handle the case where we send multipart/form-data formatted data
        (case we send a file through ajax calls)
        """
        # NB : le Content-type contient également un boundary
        # multipart/form-data; boundary=---------------------------1231564564645...
        if self.request.headers.get(
            "Content-Type"
        ) and "multipart/form-data" in self.request.headers.get("Content-Type", []):
            result = dict(self.request.POST)
        else:
            result = self.request.json_body
        return result

    def post(self):
        """
        HTTP POST api endpoint
        """
        self.logger.info("POST request")
        submitted = self.get_posted_data()
        return self._submit_datas(submitted, edit=False)

    def put(self):
        """
        HTTP PUT api endpoint
        """
        self.logger.info("PUT request")
        submitted = self.get_posted_data()
        return self._submit_datas(submitted, edit=True)

    def pre_delete(self):
        pass

    def on_delete(self):
        pass

    def delete(self):
        """
        HTTP DELETE api endpoint
        """
        self.pre_delete()
        self.dbsession.delete(self.context)
        self.on_delete()
        return {}


class BaseRestViewV2(BaseRestView):
    sort_columns = {}
    default_sort = None
    default_sort_direction = staticmethod(asc)

    def get_filter_schema(self, load_options: LoadOptions):
        raise NotImplementedError("Subclasses must implement this method")

    def validate_filters(self, load_options: LoadOptions) -> dict:
        filter_schema = self.get_filter_schema(load_options)

        logger.info("Validating filters...")
        logger.info(f"Filters before validation : {load_options.filters}")
        try:
            return filter_schema.deserialize(load_options.filters)
        except colander.Invalid as e:
            logger.error(f"An error occured when validating filters : {str(e)}")
            raise RestError(str(e))

    def validate_fields(self, load_options: LoadOptions) -> Optional[FieldOptions]:
        # TODO : validation et champs par défaut
        return load_options.fields

    def _get_filters(self):
        """
        collect the filter_... methods attached to the current object
        """
        for key in dir(self):
            if key.startswith("filter_"):
                func = getattr(self, key)
                if inspect.ismethod(func):
                    yield func

    def _filter(self, query, filters: Optional[dict]):
        """
        filter the query with the configured filters
        """
        for method in self._get_filters():
            query = method(query, filters)
        return query

    def build_collection_query(
        self, filters: Optional[dict], fields: Optional[FieldOptions]
    ):
        """
        Build a sqlalchemy Select object returning the collection and the item count
        can handle joins ... regarding the asked fields and the filters in use

        e.g :

            return select(Customer, func.count(Customer.id).over().label('total'))
        """
        raise NotImplementedError("Subclasses must implement this method")

    def build_collection_metadata(
        self, filters: Optional[dict], fields: Optional[FieldOptions]
    ):
        """
        Build a sqlalchemy Select object returning the collection and the item count
        can handle joins ... regarding the asked fields and the filters in use

        e.g :

            return select(Customer, func.count(Customer.id).over().label('total'))
        """
        raise NotImplementedError("Subclasses must implement this method")

    def sort_query(self, query, sort: Optional[SortOptions]):
        if sort and sort.sort:
            if sort.sort_direction == "asc":
                sort_func = asc
            elif sort.sort_direction == "desc":
                sort_func = desc
            else:
                sort_func = self.default_sort_direction
            # query = query.order_by(func(getattr(BaseSepaWaitingPayment, sort.sort)))
            self.logger.info(f"  + Sorting the query : f{sort}")

            custom_sort_method = getattr(self, f"sort_by_{sort.sort}", None)

            if custom_sort_method is not None:
                query = custom_sort_method(query, sort, sort_func)
            else:
                sort_column = self.sort_columns.get(sort.sort)
                if sort_column is None and self.default_sort is not None:
                    sort_column = self.sort_columns[self.default_sort]

                if sort_column is not None:
                    logger.info(f"  + Sorting the query by default : {sort_column}")
                    logger.info(sort_func)
                    query = query.order_by(sort_func(sort_column))
        return query

    def paginate_query(self, query, pagination: Optional[PaginationOptions]):
        if pagination and pagination.per_page > 0:
            page = pagination.page
            # Ici on translate le numéro de page qui au sens sql commence à 0
            if page > 0:
                page = page - 1
            per_page = pagination.per_page
            query = query.offset(page * per_page).limit(per_page)
        return query

    def _get_serializer(self, fields) -> BaseSerializer:
        raise NotImplementedError("Subclasses must implement this method")

    def _format_result_items(self, query, fields) -> List[dict]:
        result = []
        serializer = self._get_serializer(fields)
        self.logger.info(f"  + fields : {fields}")
        for db_item in self.request.dbsession.execute(query).scalars():
            self.logger.info(f"  + Serializing item : {db_item}")
            item_dict = serializer.run(self.request, db_item)
            result.append(item_dict)
        return result

    def _format_item_result(self, model, fields) -> dict:
        serializer = self._get_serializer(fields)
        return serializer.run(self.request, model)

    def get(self):
        fields = LoadOptions.from_request(self.request)
        fields = self.validate_fields(fields)
        return self._format_item_result(self.context, fields)

    def get_query_count(self, query) -> int:
        first_item = self.request.dbsession.execute(query).first()
        if first_item is not None:
            query_count = first_item[1]
        else:
            query_count = 0
        return query_count

    def build_collection_response(
        self, query, fields, pagination: Optional[PaginationOptions]
    ) -> RestCollectionResponse:
        items = self._format_result_items(query, fields)
        query_count = self.get_query_count(query)
        metadata = RestCollectionMetadata(
            total_count=query_count, pagination=pagination
        )
        return RestCollectionResponse(
            items=items,
            metadata=metadata,
        )

    def collection_get(self) -> RestCollectionResponse:
        try:
            load_options = LoadOptions.from_request(self.request)
        except colander.Invalid as e:
            raise RestError(e.asdict())
        # Sort et pagination sont traités directement
        # dans le LoadOptions.from_request()
        sort = load_options.sort
        pagination = load_options.pagination

        filters = self.validate_filters(load_options)
        fields = self.validate_fields(load_options)

        logger.info("Filters : {}".format(filters))
        logger.info("Fields : {}".format(fields))
        logger.info("Sort : {}".format(sort))
        logger.info("Pagination : {}".format(pagination))

        query = self.build_collection_query(filters, fields)
        query = self.sort_query(query, sort)
        query = self.paginate_query(query, pagination)
        results = self.build_collection_response(query, fields, pagination)
        return results


class TreeMixinMetaClass(type):
    """
    Metaclasse qui attache un attribut children spécifique à chaque classe
    fille créée


    LE problème d'origine :

        class A:
            children = []

        class B(A):
            pass

        B.children.append('o')
        A.children
        ['o']

    Avec cette métaclasse

    A.children = []
    """

    def __new__(cls, clsname, bases, attrs):
        newclass = super(TreeMixinMetaClass, cls).__new__(cls, clsname, bases, attrs)
        newclass.children = []
        return newclass


class TreeMixin(metaclass=TreeMixinMetaClass):
    """
    Mixin adding tree structure to views

    class MyView(BaseView, TreeMixin):
        route_name = "/myviewroute"


    Inherit from the TreeMixin and attach views to parent views

    route_name

        current route_name

    children

        class attribute in list format registering all view children

    parent

        weakref to the parent view
    """

    route_name = None
    parent_view = None
    description = ""
    title = ""

    @classmethod
    def get_url(cls, request):
        if getattr(cls, "tree_url", None) is not None:
            return cls(request).tree_url

        elif getattr(cls, "route_name", None) is not None:
            if isinstance(cls.route_name, property):
                return cls(request).route_name
            else:
                return request.route_path(cls.route_name)
        else:
            return ""

    @classmethod
    def get_me_as_back_url(cls, request):
        """
        Collect the back url pointing to the current view, ask the parent if
        needed
        """
        if getattr(cls, "tree_is_visible", None) is not None:
            visible = cls(request).tree_is_visible
        else:
            visible = True
        if visible:
            return cls.get_url(request)
        elif cls.parent_view:
            return cls.parent_view.get_me_as_back_url(request)
        else:
            return "#"

    @classmethod
    def get_title(cls, request):
        if isinstance(cls.title, property):
            return cls(request).title
        else:
            return cls.title

    @classmethod
    def get_breadcrumb(cls, request, is_leaf=False):
        """
        Collect breadcrumb entries

        :param obj request: The Pyramid request
        :param bool is_leaf: Do we ask the leaf node
        :returns: A generator of 2-uples (title, url)
        """
        if cls.parent_view is not None:
            for link in cls.parent_view.get_breadcrumb(request):
                yield link

        if getattr(cls, "tree_is_visible", None) is not None:
            visible = cls(request).tree_is_visible
        else:
            visible = True

        if not is_leaf:
            if visible:
                yield Link(cls.get_url(request), cls.get_title(request))
        else:
            yield Link("", cls.get_title(request))

    @classmethod
    def get_back_url(cls, request):
        logger.info("Asking for the parent url : {0}".format(cls))
        if cls.parent_view is not None:
            return cls.parent_view.get_me_as_back_url(request)
        else:
            return None

    @classmethod
    def get_navigation(cls, request):
        result = []
        for child in cls.children:
            if getattr(child, "route_name", None) is not None:
                result.append(
                    Link(
                        label=child.title,
                        url=child.route_name,
                        title=child.description,
                        permission=getattr(child, "permission", None),
                    )
                )
            else:
                url = child.get_url(request)
                if url:
                    result.append(
                        Link(
                            label=child.title,
                            title=child.description,
                            url=url,
                            permission=getattr(child, "permission", None),
                        )
                    )
        return result

    @property
    def navigation(self):
        return self.get_navigation(self.request)

    @property
    def breadcrumb(self):
        return self.get_breadcrumb(self.request, is_leaf=True)

    @property
    def back_link(self) -> Optional[str]:
        return self.get_back_url(self.request)

    @classmethod
    def add_child(cls, view_class):
        cls.children.append(view_class)
        view_class.parent_view = cls

    def populate_navigation(self):
        try:
            self.request.navigation.breadcrumb = self.breadcrumb
            self.request.navigation.back_link = self.back_link
        except Exception as err:
            logger.exception("Error in populate_navigation")
            logger.error("I'm %s " % self)
            logger.error("Parent : %s" % self.parent_view)
            raise err


def make_panel_wrapper_view(panel_name, js_resources=()):
    """
    Return a view wrapping the given panel

    :param str panel_name: The name of the panel
    """

    def myview(request):
        """
        Return a panel name for our panel wrapper
        """
        if js_resources:
            for js_resource in js_resources:
                js_resource.need()
        return {"panel_name": panel_name}

    return myview


def add_panel_view(config, panel_name, **kwargs):
    """
    Add a panel view to the current configuration
    """
    config.add_view(
        make_panel_wrapper_view(panel_name),
        renderer="panel_wrapper.mako",
        xhr=True,
        **kwargs,
    )


def add_panel_page_view(config, panel_name, **kwargs):
    js_resources = kwargs.pop("js_resources", ())
    config.add_view(
        make_panel_wrapper_view(panel_name, js_resources),
        renderer="panel_page_wrapper.mako",
        **kwargs,
    )


def add_tree_view_directive(config, *args, **kwargs):
    """
    Custom add view directive specific to views using the TreeMixin class
    It allows to pass a parent parameter matching the parent view

    This way views can display a breadcrumb for navigation
    """
    if "parent" in kwargs:
        parent = kwargs.pop("parent")
        if not hasattr(parent, "add_child"):
            raise NotImplementedError(
                "The parent (%s) view should inherit the Treemixin class" % parent
            )
        parent.add_child(args[0])

    if "route_name" not in kwargs:
        # Use the route_name set on the view by default
        kwargs["route_name"] = args[0].route_name

    config.add_view(*args, **kwargs)


def redirect_to_index_view(request, context):
    """
    Vue redirigeant l'utilisateur vers l'index d'enDI (utilisée lorsque l'on
    remappe les urls)
    """
    return HTTPFound("/")


class AsyncJobMixin:
    """
    Helpers for the views launching and watching celery tasks

    Handles popup views as well as regular views
    """

    def show_error(self, msg: str, show_refresh_button=False) -> Response:
        """
        Shows fatal error to user, and leaving/close page/popup

        A refresh button may be shown (popup only).
        """
        if self.request.is_popup:
            set_close_popup_response(
                self.request,
                error=msg,
                refresh=show_refresh_button,
            )
            return self.request.response
        else:
            self.request.session.flash(msg, "error")
            return HTTPFound(self.request.referrer)

    def is_celery_alive(self) -> Optional[Response]:
        service_ok, msg = check_alive()
        if not service_ok:
            return self.show_error(msg, show_refresh_button=True)

    def initialize_job_result(self, job_class, **kwargs) -> Job:
        """
        Record the empty job result to database

        :param job_class:
        :param kwargs: any kwargs, are passed to Job constuctor
        """
        job = job_class()
        job.set_owner(self.request.identity.login.login)
        self.request.dbsession.add(job)
        self.request.dbsession.flush()
        logger.info(f"    + The job {job.id} was initialized")
        logger.info("    + Delaying the task to celery")
        return job

    def redirect_to_job_watch(self, job, job_result):
        logger.info(
            "The Celery Task {0} has been delayed, its result "
            "sould be retrieved from the FileGenerationJob {1}".format(
                job.id, job_result.id
            )
        )
        if self.request.is_popup:
            query = dict(popup=1)
        else:
            query = {}
        return HTTPFound(self.request.route_path("job", id=job_result.id, _query=query))


class JsAppViewMixin:
    """For views having a JS app Using REST API requiring

    Helps building AppOption JS object for JS app use a consistent way accross
    enDi.

    Conventions:
    - context resource URL is given by context_url() implementation
    - form_config_url is context url + form_config=1 (this route has to exist)

    Usage:
    - implement context_url()
    - call get_js_app_options() to build context with context_url/form_config_url keys
    - don't forget to initialize AppOption object in your mako template.
    """

    def context_url(self, _query: Dict[str, str] = {}):
        raise NotImplementedError

    def form_config_url(self):
        return self.context_url(_query={"form_config": "1"})

    def get_come_from(self, appstruct: Optional[dict] = {}) -> Optional[str]:
        come_from = self.request.params.get("come_from", None)
        if come_from is None:
            come_from = self.request.referer
            if come_from is None:
                come_from = appstruct.get("come_from", None)
        return come_from

    def get_js_app_options(self) -> dict:
        options = {
            "context_url": self.context_url(),
            "form_config_url": self.form_config_url(),
            "come_from": self.get_come_from(),
        }
        options.update(self.more_js_app_options())
        return options

    def more_js_app_options(self):
        """
        Add options passed to the AppOption object
        """
        return {}


class RestListMixinClass(BaseListClass):
    """
    Base mixin for rest list views with pagination

        * It launches a query to retrieve records
        * Validates GET params regarding the given schema
        * filter the query with the provided filter_* methods
        * orders the query
        * sorts the query

    @param list_schema: Schema used to validate the GET params provided in the
                    url, the schema should inherit from
                    caerp.views.forms.lists.BaseListsSchema to preserve
                    most of the processed automation
                    list_schema can be either a callable or an instance
    @param sort_columns: dict of {'sort_column_key':'sort_column'...}.
        Allows to generate the validator for the sort availabilities and
        to automatically add a order_by clause to the query. sort_column
        may be equal to Table.attribute if join clauses are present in the
        main query.
    @default_sort: the default sort_column_key to be used
    @default_direction: the default sort direction (one of ['asc', 'desc'])

    you must implement method :

        query()

            Returns an iterable of items

    you must implement property :

        list_schema (see above)

    you can implement methods

        filter_*(self, query, appstruct)

            Allows to provide several filters
            Should act on the query and returns it

        _sort_by_<sort_key>(self, query, appstruct)

            Handles sorting stuff if the given sort_key is used
            Should act on the query and returns it

        format_collection(self, query)

            Builds the data returned to the end user when calling the collection GET
            api endpoint
    """

    list_schema = BaseListsSchema
    default_sort = None
    sort_columns = {}

    def _get_submitted(self):
        return self.request.GET

    def get_list_schema(self):
        schema = self.list_schema
        if callable(schema):
            schema = schema()
        return schema

    def _collect_appstruct(self):
        """
        collect the filter options from the current url

        Use the schema to validate the GET params of the current url and
        returns the formated datas
        """
        schema = None
        appstruct = {}
        schema = self.get_list_schema().bind(**self._get_bind_params())
        if schema is not None:
            try:
                submitted = self._get_submitted()
                self.logger.info(submitted)
                if submitted:
                    # TODO: Correctif provisoire pour les différences de noms de param
                    if "sort_by" in submitted and "sort" not in submitted:
                        submitted["sort"] = submitted["sort_by"]
                    if "order" in submitted and "direction" not in submitted:
                        submitted["direction"] = submitted["order"]
                    self.logger.info("Submitted filter datas : {}".format(submitted))
                    appstruct = schema.deserialize(submitted)
                else:
                    appstruct = schema.deserialize({})
            except colander.Invalid:
                # If values are not valid, we want the default ones to be
                # provided see the schema definition
                self.logger.exception("  - Current search values are not valid")
                appstruct = schema.deserialize({})
                raise RestError(
                    errors=["Rest API : Les valeurs du filtre sont invalides"],
                    code=422,
                )
        return schema, appstruct

    def _paginator_state(self, appstruct, total_entries):
        """
        Build a state dict compatible with backbone.paginator
        See :
            https://github.com/backbone-paginator/backbone.paginator#fetching-data-and-managing-states
        """
        return {
            "page": appstruct["page"],
            "per_page": appstruct["items_per_page"],
            "sort_by": appstruct["sort"],
            "order": appstruct["direction"],
            "total_entries": total_entries,
        }

    def _paginate(self, query, appstruct):
        """
        Add limit and offset to the query regarding the pagination query
        parameters

        :param obj query: The query to paginate
        :param dict appstruct: The filter datas that were provided
        :returns: The paginated query
        """
        if "page" in self.request.GET:
            items_per_page = appstruct.get("items_per_page", 25)
            page = appstruct["page"]
            query = query.offset(page * items_per_page)
            query = query.limit(items_per_page)
        return query

    def format_collection(self, query):
        """
        Format the collection returned to the end user

        result of HTTP GET call on the collection endpoint
        """
        return query.all()

    def collection_get(self):
        """
        Collection HTTP GET method endpoint
        """
        self.logger.info("# Calling the list view #")
        self.logger.info(" + Collecting the appstruct from submitted datas")
        schema, appstruct = self._collect_appstruct()
        self.logger.info(appstruct)
        self.logger.info(" + Launching query")
        query = self.query()
        if query is not None:
            self.logger.info(" + Filtering query")
            query = self._filter(query, appstruct)
            self.logger.info(" + Sorting query")
            query = self._sort(query, appstruct)
            # We count before paginating
            count = query.count()
            query = self._paginate(query, appstruct)
            self.logger.info(f"{count} items {query.count()}")
        else:
            count = 0

        if "page" in self.request.GET:
            return self._paginator_state(appstruct, count), query.all()
        else:
            return self.format_collection(query)


def caerp_add_route(config, route_name, **kwargs):
    """Utility to add route, transforming the route name into a regex pattern."""
    pattern = r"{}".format(route_name.replace("id}", r"id:\d+}"))
    config.add_route(route_name, pattern, **kwargs)
