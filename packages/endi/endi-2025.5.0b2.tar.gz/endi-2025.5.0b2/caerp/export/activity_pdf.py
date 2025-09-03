"""
Utilities used to export an activity in pdf format
"""
import io
from caerp.utils.pdf import (
    fetch_resource,
    HTMLWithHeadersAndFooters,
    Overlay,
    weasyprint_pdf_css,
)


def _pdf_renderer(activity, request):
    """
    Build a Weasyprint html to pdf renderer specific to activities. Here we
    need a custom footer
    """
    footer = Overlay(
        panel_name="activity_pdf_footer",
        context_dict={"context": activity},
    )
    content = request.layout_manager.render_panel(
        "activity_pdf_content", context=activity
    )
    html_object = HTMLWithHeadersAndFooters(
        request,
        content,
        footer_overlay=footer,
        url_fetcher=fetch_resource,
        base_url="test",
    )
    return html_object


def activity_pdf(activity, request):
    """
    Generates the pdf output for a given activity

    :rtype: io.BytesIO instance
    """
    result = io.BytesIO()
    html_object = _pdf_renderer(activity, request)
    html_object.write_pdf(result, stylesheets=weasyprint_pdf_css())
    result.seek(0)
    return result
