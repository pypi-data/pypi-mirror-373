import datetime
import typing
from sqlalchemy import select
from caerp.models.user import (
    User,
    UserConnections,
)


def get_last_connection(request, user_id: int) -> typing.Optional[datetime.datetime]:
    query = (
        select(UserConnections.month_last_connection)
        .where(UserConnections.user_id == user_id)
        .order_by(UserConnections.month_last_connection.desc())
        .limit(1)
    )
    result = request.dbsession.execute(query).scalar()
    return result


def has_access_right(request, user: User, access_right_name: str) -> bool:
    """
    Tells whether a given user has the given access right granted

    This is intended to be called for informative use (eg: table of permissions listing
     all users), *not* for access control of logged-in user.

     For access control, use SessionSecurityPolicy stuff.

    :param access_right_name: access right name, as defined in
      caerp.consts.access_rights.ACCESS_RIGHTS
    """
    if user.login is None:
        return False
    else:
        for group in user.login._groups:
            for access_right in group.access_rights:
                if access_right.name == access_right_name:
                    return True

    return False
