import logging
from caerp.models.user.user import User
from caerp.models.user.userdatas import UserDatas, get_default_cae_situation

logger = logging.getLogger(__name__)


def add_userdata_to_user(request, user: User) -> UserDatas:
    if user.userdatas is None:
        logger.debug(f"Adding userdatas for the user {user}")
        user_datas = UserDatas()
        user_datas.user = user
        user_datas.coordonnees_civilite = user.civilite
        user_datas.coordonnees_lastname = user.lastname
        user_datas.coordonnees_firstname = user.firstname
        user_datas.coordonnees_email1 = user.email
        user_datas.situation_situation_id = get_default_cae_situation()
        request.dbsession.add(user_datas)
        request.dbsession.flush()
        return user_datas
    return user.userdatas
