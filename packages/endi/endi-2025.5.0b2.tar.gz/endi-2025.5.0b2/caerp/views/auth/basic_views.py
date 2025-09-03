"""
Genuine authentication views
"""
import json
import logging
from caerp.consts.permissions import PERMISSIONS
from typing import Optional

import colander
import httpagentparser
from deform import Button, Form, ValidationFailure
from pyramid.httpexceptions import HTTPFound
from pyramid.security import NO_PERMISSION_REQUIRED, forget

from caerp.forms import public_file_appstruct
from caerp.forms.user.login import get_auth_schema, get_json_auth_schema
from caerp.models.config import Config, ConfigFiles
from caerp.resources import login_resources
from caerp.utils.rest.apiv1 import Apiv1Error, Apiv1Resp, RestError
from caerp.utils.security.auth import connect_user
from caerp.utils.sys_environment import resource_filename
from caerp.views import BaseView

logger = logging.getLogger(__name__)


LOGIN_TITLE = "Bienvenue dans enDI"
LOGIN_ERROR_MSG = "Erreur d'authentification"
LOGIN_SUCCESS_MSG = "Authentification réussie"


def api_login_post_view(request):
    """
    A Json login view
    expect a login and a password element (in json format)
    returns a json dict :
        success : {'status':'success'}
        error : {'status':'error', 'errors':{'field':'error message'}}
    """
    schema = get_json_auth_schema()
    appstruct = request.json_body
    try:
        appstruct = schema.deserialize(appstruct)
    except colander.Invalid as err:
        logger.exception("  - Erreur")
        raise RestError(err.asdict(), 400)
    else:
        connect_user(request, appstruct["login"], appstruct.get("remember_me", False))
    return Apiv1Resp(request)


def _get_login_form(request, use_ajax=False):
    """
    Return the login form object

    :param obj request: The pyramid request object
    :param bool use_ajax: Is this form called through xhr (should it be an ajax
        form) ?
    """
    action: Optional[str] = None
    if use_ajax:
        action = request.route_path("login")
        ajax_options = """{
            'dataType': 'json',
            'success': ajaxAuthCallback
            }"""

    else:
        ajax_options = "{}"

    form = Form(
        get_auth_schema(),
        action=action,
        use_ajax=use_ajax,
        formid="authentication",
        ajax_options=ajax_options,
        buttons=(
            Button(
                name="submit",
                title="Connexion",
                type="submit",
            ),
        ),
    )
    return form


def api_login_get_view(request):
    """
    View used to check if the user is authenticated

    :returns:
        A json dict :
            user should login :
                {'status': 'error', 'datas': {'login_form': <html string>}}
            user is logged in:
                {'status': 'success', 'datas': {}}
    """
    login = request.authenticated_userid

    if login is not None:
        result = Apiv1Resp(request)
    else:
        login_form = _get_login_form(request, use_ajax=True)
        form = login_form.render()
        result = Apiv1Error(request, datas={"login_form": form})
    return result


def get_browser_infos(request):
    """
    Return current browser user_agent, name and version
    """
    user_agent = request.environ.get("HTTP_USER_AGENT")
    parsed_user_agent = httpagentparser.detect(user_agent, fill_none=True)
    if not parsed_user_agent:
        browser_name = user_agent.split("/")[0]
        browser_version = user_agent.split("/")[1]
    else:
        browser_name = parsed_user_agent["browser"]["name"]
        browser_version = parsed_user_agent["browser"]["version"]
    if browser_version:
        browser_major_version = browser_version.split(".")[0]
    else:
        logger.info("Navigateur sans version : probablement un BOT")
        browser_major_version = ""
    return dict(
        user_agent=user_agent,
        name=browser_name,
        version=browser_version,
        major_version=browser_major_version,
    )


def is_browser_supported(request):
    """
    Return whether or not current browser is supported
    """

    # Récupération des données de support depuis le fichier JSON
    browser_support_filepath = resource_filename("static/browser_support.json")
    with open(browser_support_filepath) as browser_support_file:
        browser_support_data = json.load(browser_support_file)

    # Récupération des infos sur le navigateur de l'utilisateur
    browser_infos = get_browser_infos(request)
    browser_name = browser_infos["name"]
    browser_major_version = browser_infos["major_version"]

    # Vérification du support
    is_browser_supported = False
    if browser_name in browser_support_data and browser_major_version:
        if int(browser_major_version) >= int(browser_support_data[browser_name]):
            is_browser_supported = True
    return is_browser_supported


class LoginView(BaseView):
    """
    the login view
    """

    def get_next_page(self) -> str:
        """
        Return the next page to be visited after login, get it form the request
        or returns index
        """
        nextpage = self.request.params.get("nextpage", "/")
        # avoid redirection looping or set default
        if nextpage in [None, self.request.route_url("login")]:
            nextpage = self.request.route_url("index")

        return nextpage

    def form_response(self, html_form, failed=False):
        """
        Return the response
        """
        if self.request.is_xhr:
            result = Apiv1Error(self.request, datas={"login_form": html_form})
        else:
            result = {
                "title": LOGIN_TITLE,
                "html_form": html_form,
            }
            if failed:
                result["message"] = LOGIN_ERROR_MSG
        return result

    def success_response(self):
        """
        Return the result to send on successfull authentication
        """
        if self.request.is_xhr:
            result = Apiv1Resp(self.request)
        else:
            result = HTTPFound(
                location=self.get_next_page(),
                headers=self.request.response.headers,
            )
        return result

    def __call__(self):
        if self.request.identity is not None:
            return self.success_response()

        login_resources.need()
        form = _get_login_form(self.request, use_ajax=self.request.is_xhr)

        if "submit" in self.request.params:
            controls = list(self.request.params.items())
            logger.info(
                "Authenticating : '{0}' (xhr : {1})".format(
                    self.request.params.get("login"), self.request.is_xhr
                )
            )
            try:
                form_datas = form.validate(controls)
            except ValidationFailure as err:
                logger.exception(" - Authentication error")
                err_form = err.render()
                result = self.form_response(err_form, failed=True)
            else:
                connect_user(
                    self.request,
                    form_datas["login"],
                    remember_me=form_datas.get("remember_me", False),
                )
                result = self.success_response()
        else:
            # Check browser support
            if not is_browser_supported(self.request):
                logger.warn("Current browser is not supported")
                if "force_support" in self.request.POST:
                    logger.warn("--> User-forced browser support !")
                else:
                    return HTTPFound(location=self.request.route_url("nosupport"))
            if not self.request.is_xhr:
                form.set_appstruct({"nextpage": self.get_next_page()})
            result = self.form_response(form.render())
        return result


def logout_view(request):
    """
    The logout view
    """
    loc = request.route_url("index")
    forget(request)
    request.response.delete_cookie("remember_me")
    response = HTTPFound(location=loc, headers=request.response.headers)
    return response


def login_photos(request):
    """
    Data for login background photos
    """

    login_backgrounds = []
    for idx in range(10):
        photo_key = f"login_backgrounds.{idx}.photo"
        background_photo = ConfigFiles.get(photo_key)
        if background_photo is None:
            break
        background = {
            "photo": public_file_appstruct(request, photo_key, background_photo)
        }
        for key in ["title", "subtitle", "author"]:
            background[key] = Config.get_value(f"login_backgrounds.{idx}.{key}", "")
        login_backgrounds.append(background)

    return login_backgrounds


class BrowserNosupportView(BaseView):
    def __call__(self):
        if is_browser_supported(self.request):
            return HTTPFound("/")
        else:
            browser_infos = get_browser_infos(self.request)
            return dict(
                title="Navigateur non supporté",
                user_agent=browser_infos["user_agent"],
                browser_name=browser_infos["name"],
                browser_version=browser_infos["version"],
            )


def includeme(config):
    """
    Add auth related routes/views
    """
    config.add_view(logout_view, route_name="logout", permission=NO_PERMISSION_REQUIRED)
    config.add_view(
        LoginView,
        route_name="login",
        permission=NO_PERMISSION_REQUIRED,
        renderer="login.mako",
        layout="login",
    )
    config.add_view(
        LoginView,
        route_name="login",
        xhr=True,
        permission=NO_PERMISSION_REQUIRED,
        renderer="json",
        layout="default",
    )

    # API v1
    config.add_view(
        api_login_get_view,
        route_name="apiloginv1",
        permission=NO_PERMISSION_REQUIRED,
        renderer="json",
        request_method="GET",
    )
    config.add_view(
        api_login_post_view,
        route_name="apiloginv1",
        permission=NO_PERMISSION_REQUIRED,
        renderer="json",
        request_method="POST",
    )

    config.add_route("login_photos", "/login_photos")
    config.add_view(
        login_photos,
        route_name="login_photos",
        permission=NO_PERMISSION_REQUIRED,
        renderer="json",
        request_method="GET",
    )

    config.add_view(
        BrowserNosupportView,
        route_name="nosupport",
        permission=NO_PERMISSION_REQUIRED,
        renderer="browser_nosupport.mako",
    )
