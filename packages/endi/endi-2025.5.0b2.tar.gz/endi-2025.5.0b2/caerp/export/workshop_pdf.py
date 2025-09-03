"""
Utilities used to export an workshop in pdf format
"""
import io
from caerp.utils.pdf import (
    fetch_resource,
    HTMLWithHeadersAndFooters,
    Overlay,
    weasyprint_pdf_css,
)


def _pdf_renderer(workshop, timeslots, request):
    """
    Build a Weasyprint html to pdf renderer specific to activities. Here we
    need a custom footer
    """
    footer = Overlay(
        panel_name="workshop_pdf_footer",
        context_dict={"context": workshop},
    )
    content = request.layout_manager.render_panel(
        "workshop_pdf_content", context=workshop, timeslots=timeslots
    )
    html_object = HTMLWithHeadersAndFooters(
        request,
        content,
        footer_overlay=footer,
        url_fetcher=fetch_resource,
        base_url="test",
    )
    return html_object


def workshop_pdf(workshop, timeslots, request):
    """
    Generates the pdf output for a given workshop

    :rtype: io.BytesIO instance
    """
    result = io.BytesIO()
    html_object = _pdf_renderer(workshop, timeslots, request)
    html_object.write_pdf(result, stylesheets=weasyprint_pdf_css())
    result.seek(0)
    return result
