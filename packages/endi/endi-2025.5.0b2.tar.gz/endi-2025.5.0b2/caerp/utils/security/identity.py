"""
Retrieve the user object
"""
import logging
from typing import Optional

from pyramid.security import forget
from sqlalchemy.orm import (
    load_only,
    contains_eager,
    selectinload,
)

from caerp.models.user.user import User
from caerp.models.user.login import Login
from caerp.models.user.group import Group


logger = logging.getLogger(__name__)


def get_identity(request, userid: str) -> Optional[User]:
    """
    Returns the current User object
    """
    logger.info("# Retrieving avatar #")
    logger.info(f"  + Login : {userid}")
    query = request.dbsession.query(User)
    query = query.join(Login)
    query = query.options(load_only("firstname", "lastname", "user_prefs"))
    query = query.options(
        contains_eager(User.login)
        .load_only("login")
        .selectinload(Login._groups)
        .load_only("name")
        .selectinload(Group.access_rights)
        .load_only("name"),
        selectinload(User.companies).load_only("id", "active", "name"),
    )
    query = query.filter(Login.login == userid)
    result = query.first()
    if result is None:
        logger.warn(" - No user found !!")
        forget(request)
        return None
    logger.debug("User found")
    logger.debug("-> End of the avatar collection")
    return result
