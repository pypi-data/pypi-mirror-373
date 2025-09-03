"""
    Tools for rendering and handling pdf files

    write_pdf(request, filename, html)
    buffer_pdf(html)

    In case of using headers and/or footers, more manipulation is necessary

    Use overlays and the HTMLWithHeadersAndFooters tool

    see task pdf rendering tools
"""
import logging
import base64
import re
import pkg_resources
import io
from weasyprint import HTML, CSS

from os.path import join

from pyramid.renderers import render
from pyramid.threadlocal import get_current_request

from caerp.export.utils import write_file_to_request


logger = logging.getLogger(__name__)


def render_html(request, template, datas):
    """
    Compile the current template with the given datas
    """
    return render(template, datas, request)


def write_html_as_pdf_response(request, filename, html):
    """
    Convert the given html string to pdf and attach it as a file response
    object to the request

    :param obj request: The Pyramid Request
    :param str filename: The pdf filename
    :param str html: An html string
    """
    result = html_to_pdf_buffer(html)
    write_file_to_request(request, filename, result)
    return request


def html_to_pdf_buffer(html):
    """
    Convert the given html string to a pdf buffer

    :param str html: The html string
    :rtype: instance of io.BytesIO
    """
    result = io.BytesIO()
    renderer = HTML(
        string=html,
        url_fetcher=fetch_resource,
        encoding="utf-8",
        base_url="/",
    )
    renderer.write_pdf(result, stylesheets=weasyprint_pdf_css())
    result.seek(0)
    return result


# Static resource management
def weasyprint_pdf_css():
    """
    Return the weasyprint CSS resource object for pdf.css
    """
    pdf_css = CSS(
        filename=pkg_resources.resource_filename("caerp", "static/css/pdf.css")
    )
    return [pdf_css]


DATAURI_TMPL = "data:{0};base64,{1}"
FILEPATH_REGX = re.compile("^/files/(?P<fileid>[0-9]+).png")
PUBLIC_FILES_REGX = re.compile("^/public/(?P<filekey>.+)")


def get_db_file_resource(fileobj):
    """
    Return a resource string usable by the pdf renderer for dynamically db
    loaded resources

    :param obj fileobj: a file object with a mimetype attr and a get_value
    method

    :returns: a resource string (default : with a void png)
    """
    if fileobj is not None:
        try:
            data = fileobj.getvalue()
        except IOError:  # In case the file isn't on disk anymore
            logger.exception("File does not exist")
            data = b""
        mimetype = fileobj.mimetype
    else:
        data = b""
        mimetype = "image/png"
    return dict(string=data, mimetype=mimetype)


def fetch_resource(uri, rel=None):
    """
    Callback used by pisa to locally retrieve ressources
    giving the uri
    if the uri starts with /files : we're looking for a db file
    else we're looking for a static resource
    """
    print("Fetching resource from %s" % uri)
    if uri.startswith("file://"):
        uri = uri[7:]
    f_regex_group = FILEPATH_REGX.match(uri)
    pf_regex_group = PUBLIC_FILES_REGX.match(uri)

    if f_regex_group is not None:
        # C'est un modèle File que l'on doit renvoyer
        filename = f_regex_group.group("fileid")
        # On récupère l'objet fichier
        from caerp.models.files import File

        fileobj = File.get(filename)
        resource = get_db_file_resource(fileobj)

    elif pf_regex_group is not None:
        key = pf_regex_group.group("filekey")
        from caerp.models.config import ConfigFiles

        fileobj = ConfigFiles.get(key)
        resource = get_db_file_resource(fileobj)

    else:
        # C'est un fichier statique
        request = get_current_request()
        introspector = request.registry.introspector
        if uri.startswith("/"):
            uri = uri[1:]
        mainuri, sep, relative_filepath = uri.partition("/")
        mainuri = mainuri + "/"
        resource_path = ""
        mimetype = ""
        for staticpath in introspector.get_category("static views"):
            if mainuri == staticpath["introspectable"]["name"]:
                basepath = staticpath["introspectable"]["spec"]
                resource_path = join(basepath, relative_filepath)
                if ":" in resource_path:
                    package, filename = resource_path.split(":")
                    resource_path = pkg_resources.resource_filename(
                        package,
                        filename,
                    )
                    from caerp.export.utils import detect_file_mimetype

                    mimetype = detect_file_mimetype(filename)
                    resource = dict(
                        string=open(resource_path, "rb").read(), mimetype=mimetype
                    )

    return resource


# Advanced Weasyprint usage
def get_element(boxes, element):
    """
    Given a set of boxes representing the elements of a PDF page in a
    DOM-like way, find the box which is named `element`.

    Look at the notes of the class for more details on Weasyprint insides.
    """
    result = None
    for box in boxes:
        if box.element_tag == element:
            result = box
            break
        else:
            result = get_element(box.all_children(), element)
    return result


class Overlay:
    """
    Stores datas used to manipulate an overlay (footer, header ...)

    An overlay can be template based or panel based (panels allows to provide
    more computation on python side, with better testing ability)

    :param str template_path: The path to the template to render
    :param str panel_name: The name of the pyramid_layout panel to use
    :param dict context_dict: The context dict to pass to the template/panel
    :param str type_: type of overlay footer/header/main the type is used for
    margin computation
    """

    def __init__(
        self, template_path=None, panel_name=None, context_dict=None, type_="footer"
    ):
        if template_path and panel_name:
            raise Exception("Please choose between template_path and panel_name")
        self.template_path = template_path
        self.panel_name = panel_name
        self.context_dict = context_dict
        self.type_ = type_

    def render(self, request, extra_context_dict):
        context = {**self.context_dict, **extra_context_dict}
        if self.panel_name:
            result = request.layout_manager.render_panel(self.panel_name, **context)
        else:
            result = render_html(request, self.template_path, context)
        return result


class OverlayRenderer:
    OVERLAY_LAYOUT = "@page {size: A4 portrait; margin: 0;}"

    def __init__(self, request, overlay, weasyprint_args):
        self.overlay = overlay
        self.request = request
        self.weasyprint_args = weasyprint_args

    def _get_page(self, extra_context_dict, render_args):
        html_string = self.overlay.render(self.request, extra_context_dict)
        html = HTML(string=html_string, **self.weasyprint_args)

        stylesheets = render_args.setdefault("stylesheets", [])
        stylesheets.append(CSS(string=self.OVERLAY_LAYOUT))

        doc = html.render(**render_args)
        return doc.pages[0]

    def get_body(self, extra_context_dict, render_args):
        """
        Compile the body 'Box' of the given overlay

        :rtype: Box instance
        """
        page = self._get_page(extra_context_dict, render_args)

        body = get_element(page._page_box.all_children(), "body")
        body = body.copy_with_children(body.all_children())
        return body

    def get_height(self, render_args):
        """
        Compute the overlay's height
        """
        page = self._get_page({"pdf_current_page": 0, "pdf_page_count": 0}, render_args)
        html = get_element(page._page_box.all_children(), self.overlay.type_)

        if self.overlay.type_ == "footer":
            height = page.height - html.position_y
        else:
            height = html.height
        return int(height)


class HTMLWithHeadersAndFooters(HTML):
    """
    Generate a PDF out of a rendered template, with the possibility to
    integrate nicely a header and a footer if provided.

    Notes:
    ------
    - When Weasyprint renders an html into a PDF, it goes though several
      intermediate steps.  Here, in this class, we deal mostly with a box
      representation: 1 `Document` have 1 `Page` or more, each `Page` 1 `Box`
      or more. Each box can contain other box. Hence the recursive method
      `get_element` for example.
      For more, see:
      https://weasyprint.readthedocs.io/en/stable/hacking.html#dive-into-the-source
      https://weasyprint.readthedocs.io/en/stable/hacking.html#formatting-structure
    - Warning: the logic of this class relies heavily on the internal
      Weasyprint API. This snippet was written at the time of the release 47,
      it might break in the future.
    - This generator draws its inspiration and, also a bit of its
      implementation, from this discussion in the library github issues:
      https://github.com/Kozea/WeasyPrint/issues/92
    """

    def __init__(
        self,
        request,
        main_html,
        header_overlay=None,
        footer_overlay=None,
        extra_vertical_margin=0,
        **kwargs,
    ):
        """
        :param str main_html: The html source string
        :param obj header_overlay: An Overlay instance for header
        :param obj footer overlay: An Overlay instance for footer
        :param int extra_vertical_margin: An extra margin to apply between
        the main content and header and the footer.  The goal is to avoid
        having the content of `main_html` touching the header or the
        footer.
        """
        self.request = request
        self.main_html = main_html
        if header_overlay:
            self.header_overlay = OverlayRenderer(request, header_overlay, kwargs)
        else:
            self.header_overlay = None

        if footer_overlay:
            self.footer_overlay = OverlayRenderer(request, footer_overlay, kwargs)
        else:
            self.footer_overlay = None

        self.extra_vertical_margin = extra_vertical_margin
        self.weasyprint_args = kwargs
        HTML.__init__(self, string=main_html, **kwargs)

    def _get_context_dict(self, page_nb, page_count):
        """
        Build a context dict added to the overlays templating context in order
        to be able to insert dynamic page related datas

        :rtype: dict
        """
        custom_context_dict = {
            "pdf_current_page": page_nb + 1,
            "pdf_page_count": page_count,
        }
        return custom_context_dict

    def _apply_overlay_on_main(self, main_doc, render_args):
        """
        Insert the header and the footer in the main document.

        Parameters
        ----------
        main_doc: Document
            The top level representation for a PDF page in Weasyprint.
        header_body: BlockBox
            A representation for an html element in Weasyprint.
        footer_body: BlockBox
            A representation for an html element in Weasyprint.
        """
        page_count = len(main_doc.pages)

        for page_nb, page in enumerate(main_doc.pages):
            page_body = get_element(page._page_box.all_children(), "body")
            custom_context_dict = self._get_context_dict(page_nb, page_count)

            if self.header_overlay:
                header_body = self.header_overlay.get_body(
                    custom_context_dict,
                    render_args,
                )
                page_body.children += header_body.all_children()

            if self.footer_overlay:
                footer_body = self.footer_overlay.get_body(
                    custom_context_dict,
                    render_args,
                )
                page_body.children += footer_body.all_children()

    def _get_margins(self, header_size, footer_size):
        """
        Build a css string indicating margins
        """
        result = "margin-left: 1cm;margin-right:1cm;"
        if header_size:
            header_size += self.extra_vertical_margin
            result += "margin-top: {header_size}px;".format(header_size=header_size)
        else:
            result += "margin-top: 1cm;"
        if footer_size:
            footer_size += self.extra_vertical_margin
            result += "margin-bottom: {footer_size}px;".format(footer_size=footer_size)
        else:
            result += "margin-bottom: 1cm;"
        return result

    def render(
        self,
        stylesheets=None,
        enable_hinting=False,
        presentational_hints=False,
        font_config=None,
        **kw,
    ):
        """
        Render all content with the header and footer

        :returns: A weasyprint Document instance
        """

        if not isinstance(stylesheets, list):
            stylesheets = []

        render_args = {
            "stylesheets": stylesheets,
            "enable_hinting": enable_hinting,
            "presentational_hints": presentational_hints,
            "font_config": font_config,
        }
        footer_height = header_height = 0
        if self.header_overlay:
            header_height = self.header_overlay.get_height(render_args)

        if self.footer_overlay:
            footer_height = self.footer_overlay.get_height(render_args)

        # Add custom stylesheet with appropriate margins
        margins = self._get_margins(header_height, footer_height)
        if margins:
            content_print_layout = "@page {%s}" % (margins,)
            custom_page_css = [CSS(string=content_print_layout)]
        else:
            custom_page_css = []

        main_doc = HTML.render(
            self,
            stylesheets=stylesheets + custom_page_css,
            enable_hinting=enable_hinting,
            presentational_hints=presentational_hints,
            font_config=font_config,
            **kw,
        )

        if self.header_overlay or self.footer_overlay:
            self._apply_overlay_on_main(main_doc, render_args)

        return main_doc
