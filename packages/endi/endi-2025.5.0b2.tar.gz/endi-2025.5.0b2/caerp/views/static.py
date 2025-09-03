"""
    Custom views for dynamic static datas
"""
import os


from caerp.consts.permissions import PERMISSIONS
from pyramid.response import Response
from pyramid.security import NO_PERMISSION_REQUIRED
from caerp.utils.sys_environment import resource_filename


def make_root_static_view(filename, ctype):
    """
    Return a static view rendering given file with headers set to the ctyp
    Content-Type
    """
    fpath = resource_filename(os.path.join("static", filename))
    file_datas = open(fpath, "rb").read()

    def static_view(context, request):
        file_response = Response(content_type=ctype, body=file_datas)
        return file_response

    return static_view


def includeme(config):
    config.add_route("favicon.ico", "/favicon.ico")
    config.add_route("robots.txt", "/robots.txt")
    config.add_view(
        make_root_static_view("robots.txt", "text/plain"),
        route_name="robots.txt",
        permission=NO_PERMISSION_REQUIRED,
    )
    config.add_view(
        make_root_static_view("favicons/favicon.ico", "image/x-icon"),
        route_name="favicon.ico",
        permission=NO_PERMISSION_REQUIRED,
    )
