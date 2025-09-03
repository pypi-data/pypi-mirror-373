"""
    Widget library
"""

import typing
import urllib.parse
import logging

from mako.template import Template
from caerp.utils.sys_environment import resource_filename
from caerp.utils.pdf import render_html

log = logging.getLogger(__name__)


def mako_renderer(tmpl, **kw):
    """
    A mako renderer to be used inside deform special widgets
    """
    template = Template(resource_filename(tmpl))
    return template.render(**kw)


def cmp_urls(url1, url2):
    """
    Compare two urls

    :param str url1:
    :param str url2:
    :result: True or False
    :rtype: bool
    """
    return url1 == url2


class Widget:
    """
    Base widget
    """

    name = None
    template = None
    request = None

    def set_template(self, template):
        """
        Change the template of the menu
        """
        self.template = template

    def render(self, request):
        """
        return an html output of the widget
        """
        request = self.request or request
        return render_html(request, self.template, {"elem": self})


class PermWidget:
    """
    widget with permission
    """

    perm = None

    def set_special_perm_func(self, func):
        """
        Allows to insert a specific permission function
        """
        self.special_perm_func = func

    def permitted(self, context, request):
        """
        Return True if the user has the right to access the destination
        """
        right = True
        if self.perm:
            right = request.has_permission(self.perm, context)
        if right and hasattr(self, "special_perm_func"):
            right = self.special_perm_func(context, request)
        return right


class StaticWidget(PermWidget):
    """
    Static Html widget with permission management
    @html : an html string (maybe you can use Webhelpers to build it)
    @perm: the permission needed to display this element
    """

    def __init__(self, html, perm=None):
        self.html = html
        self.perm = perm

    def render(self, request):
        """
        Return the html output
        """
        if self.permitted(request.context, request):
            return self.html
        else:
            return ""


class ViewLink(Widget, PermWidget):
    template = "base/button.mako"

    def __init__(
        self,
        label,
        perm=None,
        path=None,
        css="",
        js=None,
        title=None,
        icon="",
        request=None,
        confirm=None,
        url=None,
        **kw,
    ):
        self.label = label
        self.perm = perm
        self.path = path
        if confirm:
            self.js = "return confirm('{0}')".format(
                confirm.replace("'", "\\'").replace("\n", "")
            )
        else:
            self.js = js
        if title:
            self.title = title
        else:
            self.title = self.label
        self.url_kw = kw
        self._url = url
        self.css = css
        self.icon = icon
        self.request = request

    def url(self, request):
        """
        Returns the button's url
        """
        request = self.request or request

        if "referer" in self.url_kw and request.referer is not None:
            return request.referer
        elif self._url is not None:
            return self._url
        elif self.path:
            return request.route_path(self.path, **self.url_kw)
        else:
            return "#{0}".format(self.perm)

    def onclick(self):
        """
        return the onclick attribute
        """
        return self.js

    def selected(self, request):
        """
        Return True if the button is active
        """
        request = self.request or request
        cur_path = request.current_route_path(_query={})
        if "action" in request.GET:
            cur_path += "?action=%s" % request.GET["action"]

        cur_path = urllib.parse.unquote(cur_path)
        btn_path = self.url(request)
        return cmp_urls(btn_path, cur_path)


class Submit(Widget):
    """
    Submit Link used to be included in a form
    It's componed by :
    @label : the label of the button
    @perm : permission needed to display this button
    @value: value of the button
    @name : name of the button (the couple name=value is submitted)
    @title: title used onmouseover
    @css: css class string
    @_type: type of the button
    """

    template = "base/submit.mako"
    css = "btn btn-primary"
    js = None
    type_ = "submit"
    icon = None
    disabled = False

    def __init__(
        self, label, value, title=None, request=None, confirm=None, name="submit"
    ):
        self.label = label
        self.value = value
        self.name = name or "submit"
        self.title = title or self.label
        if confirm:
            self.js = "return confirm('{0}')".format(confirm.replace("'", "\\'"))
        if request:
            self.request = request


class ToggleLink(Widget, PermWidget):
    template = "base/togglelink.mako"

    def __init__(
        self, label, perm=None, target=None, title=None, css="", icon="", expanded=True
    ):
        self.label = label
        self.perm = perm
        self.target = target
        self.title = title or label
        self.css = css
        self.icon = icon
        self.expanded = expanded


class ButtonLink(Widget):
    template = "base/button.mako"

    def __init__(self, label, path, js=None, title=None, icon="", css="", **kw):
        self.label = label
        self.path = path
        self.js = js
        self.title = title or self.label
        self.icon = icon
        self.css = css
        self.url_kw = kw

    def url(self, request):
        """
        Returns the button's url
        """
        return request.route_path(self.path, **self.url_kw)

    def onclick(self):
        """
        return the onclick attribute
        """
        return self.js

    def selected(self, request):
        """
        Return True if the button is active
        """
        request = self.request or request
        cur_path = request.current_route_path()
        if "action" in request.GET:
            cur_path += "?action=%s" % request.GET["action"]

        cur_path = urllib.parse.unquote(cur_path)
        btn_path = self.url(request)
        return cmp_urls(btn_path, cur_path)


class ButtonJsLink(ButtonLink):
    template = "base/button.mako"

    def url(self, request):
        return "#{0}".format(self.path)

    def selected(self, request):
        """
        return True if it's selected
        """
        return False


class PopUp:
    """
    A popup
    """

    def __init__(self, name, title, html):
        self.name = name
        self.title = title
        self.html = html

    def open_btn(self, label=None, factory=ButtonJsLink, **kw):
        label = label or self.title
        return factory(label, js=self._get_js_link(), path="popup-%s" % self.name, **kw)

    def _get_js_link(self):
        return "$('#{0}').dialog('open');".format(self.name)


class Menu(Widget):
    template = None

    def __init__(self, template=None, css=None, icon=None):
        self.items = []
        if template:
            self.set_template(template)
        if css:
            self.css = css
        if icon:
            self.icon = icon

    def add(self, item):
        """
        Add an item to the menu
        """
        self.items.append(item)

    def insert(self, item, index=0):
        """
        Insert an item in the menu
        """
        self.items.insert(index, item)

    def void(self):
        """
        Return True if the menu is void
        """
        return not bool(len(self.items))


class ActionMenu(Menu):
    """
    Represent the ActionMenu
    """

    template = "base/actionmenu.mako"


class ButtonDropDownMenu(Menu):
    """
    A standalone dropdown menu from a button
    """

    template = "base/buttondropdownmenu.mako"


class Navigation:
    def __init__(self):
        self.breadcrumb: typing.List["Link"] = []
        self.back_link = None
        self.links = []

    def get_back_link(self):
        if self.back_link is not None:
            return self.back_link
        # On assure qu'on ait une liste et pas un génarateur
        self.breadcrumb = list(self.breadcrumb)
        if len(self.breadcrumb) > 1:
            # L'avant dernier
            return self.breadcrumb[-2].url

        return None


class Link:
    """
    A <a> link, leading to GET request

    Mandatory :

        url
        label

    title: title de l'ancre
    js: Code js à lancer onclick
    icon: nom de l'icône
    css: class Css
    disabled: Le bouton est-il actif ?
    confirm: Libellé à afficher avant de valider le onclick
    popup: Le lien doit-il être ouvert dans une nouvelle fenêtre
    """

    panel_name = "link"

    def __init__(
        self,
        url,
        label,
        title: typing.Optional[str] = None,
        js: typing.Optional[str] = None,
        icon: typing.Optional[str] = "",
        css: typing.Optional[str] = "",
        disabled: bool = False,
        confirm: typing.Optional[str] = None,
        popup: bool = False,
        **kwargs,
    ):
        self.label = label
        if popup:
            self.url = "javascript:void(0);"
            js = "window.openPopup('{url}')".format(url=url)
        else:
            self.url = url

        self.title = title or self.label
        if confirm:
            self.js = "const result=confirm('{0}');".format(
                confirm.replace("'", "\\'").replace("\n", "\\n")
            )
            if popup:
                self.js += "if (result){ %s }" % (js,)
            self.js += "return result;"
        else:
            self.js = js
        self.icon = icon
        self.css = css
        self.disabled = disabled
        self.__dict__.update(kwargs)


class POSTButton(Link):
    """A <form><button>, leading to POST request

    Includes handling of CSRF.
    """

    panel_name = "post_button"

    def __init__(self, *args, **kwargs):
        """
        Takes same args as Link, plus :

        :param extra_fields list: key/value (as tuples) that will be passed
          in form (using ``<input type=hidden>``)
        """
        self.extra_fields = kwargs.pop("extra_fields", [])
        super(POSTButton, self).__init__(*args, **kwargs)


class Column:
    """
    Wraps a column definition
    """

    def __init__(self, label, sort_key=None, css_class=None, short_label=None):
        self.sortable = sort_key is not None
        self.sort_key = sort_key
        self.label = label
        self.css_class = css_class
        self.short_label = short_label
