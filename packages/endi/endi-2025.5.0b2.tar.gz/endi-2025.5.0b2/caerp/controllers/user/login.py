from caerp.consts.users import ACCOUNT_TYPES, ACCOUNT_TYPES_LABELS
from caerp.models.user.login import Login
from caerp.services.user.group import get_default_group_for_account_type


def change_login_account_type(request, login: Login, new_account_type: str):
    """
    Change the account type of a login object
    Ensures that the login only has groups associated to the account type
    if the new account type is one of entrepreneur or equipe_appui.

    Also ensures that the associated User has a UserDatas object associated
    if the new account type is entrepreneur.
    """
    if new_account_type not in ACCOUNT_TYPES_LABELS.keys():
        raise ValueError("Invalid account type")

    if new_account_type in (
        ACCOUNT_TYPES["entrepreneur"],
        ACCOUNT_TYPES["equipe_appui"],
    ):

        login._groups = [
            group
            for group in login._groups
            if group.account_type in (new_account_type, "all")
        ]

    default_groups = get_default_group_for_account_type(request, new_account_type)
    for group in default_groups:
        if group not in login._groups:
            login._groups.append(group)

    login.account_type = new_account_type
    request.dbsession.merge(login)
    request.dbsession.flush()

    user = login.user
    if (
        new_account_type in (ACCOUNT_TYPES["entrepreneur"], ACCOUNT_TYPES["hybride"])
        and not login.user.userdatas
    ):
        from caerp.controllers.user.userdata import add_userdata_to_user

        add_userdata_to_user(request, user)

    return login
