import colander
import deform

ITEMS_PER_PAGE_OPTIONS = (
    (
        "10",
        "10 par page",
    ),
    (
        "20",
        "20 par page",
    ),
    (
        "30",
        "30 par page",
    ),
    (
        "40",
        "40 par page",
    ),
    (
        "50",
        "50 par page",
    ),
    (
        "1000000",
        "Tous",
    ),
)


@colander.deferred
def deferred_default_sort(node, kw):
    return kw["default_sort"]


@colander.deferred
def deferred_sort_validator(node, kw):
    return colander.OneOf(list(kw["sort_columns"].keys()))


@colander.deferred
def deferred_default_direction(node, kw):
    return kw["default_direction"]


@colander.deferred
def deferred_items_per_page(node, kw):
    """
    get the default items_per_page value from the request cookies
    """
    req = kw["request"]
    item_per_page = req.cookies.get("items_per_page", 10)
    try:
        item_per_page = int(item_per_page)
    except ValueError:
        item_per_page = 10
    return item_per_page


@colander.deferred
def deferred_items_per_page_validator(node, kw):
    """
    Return a fake validator that only set a cookie in the session
    """
    req = kw["request"]

    def set_cookie(node, value):
        if value <= 100 and value >= 10:
            req.response.set_cookie("items_per_page", str(value), samesite="Lax")
            req.cookies["items_per_page"] = str(value)

    return set_cookie


class BaseListsSchema(colander.Schema):
    """
    Base List schema used to validate the common list view options
    raw search
    pagination arguments
    sort parameters
    """

    search = colander.SchemaNode(
        colander.String(),
        missing="",
        widget=deform.widget.TextInputWidget(css_class="input-medium search-query"),
        default="",
    )
    items_per_page = colander.SchemaNode(
        colander.Integer(),
        widget=deform.widget.SelectWidget(
            values=ITEMS_PER_PAGE_OPTIONS,
            css_class="input-small",
        ),
        validator=deferred_items_per_page_validator,
        missing=deferred_items_per_page,
        default=deferred_items_per_page,
        title="Afficher",
    )
    page = colander.SchemaNode(
        colander.Integer(),
        widget=deform.widget.HiddenWidget(),
        missing=0,
        default=0,
        title="",
    )
    sort = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.HiddenWidget(),
        missing=deferred_default_sort,
        default=deferred_default_sort,
        validator=deferred_sort_validator,
        title="",
    )
    direction = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.HiddenWidget(),
        missing=deferred_default_direction,
        validator=colander.OneOf(["asc", "desc"]),
        default=deferred_default_direction,
        title="",
    )

    def add_custom(self, node):
        """Add behavior modified to let items_per_page at the end"""
        try:
            self.add_before("items_per_page", node)
        except KeyError:
            self.add(node)

    def add_latest(self, node):
        """Add items behind items_per_page"""
        self.add(node)


class FilterSchema(colander.MappingSchema):
    search = colander.SchemaNode(
        colander.String(),
        title="Recherche",
        missing="",
    )
