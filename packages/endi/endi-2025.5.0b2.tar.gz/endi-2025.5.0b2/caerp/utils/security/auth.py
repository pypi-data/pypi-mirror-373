import logging
from sqlalchemy import select
from pyramid.security import remember

from caerp.models.user.login import Login, UserConnections

logger = logging.getLogger(__name__)


def log_user_connection(request, userid: str) -> UserConnections:
    cnx = UserConnections(user_id=userid)
    cnx = request.dbsession.merge(cnx)
    return cnx


def _get_longtimeout(request):
    """
    Return the configured session timeout for people keeping connected
    """
    settings = request.registry.settings
    default = 3600
    longtimeout = settings.get("session.longtimeout", default)
    try:
        longtimeout = int(longtimeout)
    except:
        longtimeout = default
    return longtimeout


def connect_user(request, login: str, remember_me: bool = False):
    """
    Effectively connect the user

    :param obj request: The pyramid Request object
    :pram dict form_datas: Validated form_datas
    """
    login_object = request.dbsession.execute(
        select(Login).where(Login.login == login)
    ).scalar_one()
    logger.info(
        " + '{0}' id : {1} has been authenticated".format(login, login_object.id)
    )
    # Log the user connection for history tracking
    log_user_connection(request, login_object.user_id)
    # Storing the form_datas in the request object
    remember(request, login)

    if remember_me:
        logger.info("  * The user wants to be remembered")
        longtimeout = _get_longtimeout(request)
        request.response.set_cookie(
            "remember_me", "ok", max_age=longtimeout, samesite="strict"
        )
