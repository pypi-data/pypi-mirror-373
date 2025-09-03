from sqlalchemy import select
from caerp.models.user.group import Group


def get_default_group_for_account_type(request, account_type: str):
    """
    Return the default group(s) for the specified account type
    """
    query = select(Group)
    if account_type == "hybride":
        query = query.where(Group.account_type.in_(("entrepreneur", "equipe_appui")))
    else:
        query = query.where(Group.account_type == account_type)
    query = query.filter(Group.default_for_account_type == True)
    return request.dbsession.execute(query).scalars().all()
