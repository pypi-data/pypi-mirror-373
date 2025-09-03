from caerp_base.models.base import DBSESSION


class UserService:
    @classmethod
    def authenticate(cls, user_cls, login, password):
        result = DBSESSION().query(user_cls).filter(user_cls.login == login).first()
        if result is not None and result.auth(password):
            return result.id
        return None


class UserPrefsService:
    """Handles account.user_datas field

    That field is a melting-pot for user preferences and things we want to
    remmember at user scope.

    Limitation : properties are stored as text JSON, thus, it has no structure
    from MySQL standpoint and this is not possible to filter on it at SQL
    level.
    """

    # Not all known properties are listed above here, as some keys are dynamic
    # (eg: /project/:id/)
    DEFAULT_VALUES = {
        "expense": {"bookmarks": {}},
        "last_managed_company": None,
    }

    @classmethod
    def get(cls, request, key):
        if not request.identity:
            return None

        if request.identity.user_prefs is None:
            request.identity.user_prefs = {}

        try:
            return request.identity.user_prefs[key]
        except KeyError:
            return cls.DEFAULT_VALUES.get(key)

    @classmethod
    def set(cls, request, key, value):
        if not request.identity:
            return None
        if request.identity.user_prefs is None:
            request.identity.user_prefs = {}
        request.identity.user_prefs[key] = value
        cls._save(request, key)

    @classmethod
    def _save(cls, request, key):
        # NOte : Here we ensure passing through the __setitem__ method of our
        # MutableDict (see models.types for more informations)
        user = request.identity
        user.user_prefs[key] = user.user_prefs[key]
        request.dbsession.merge(user)
        request.dbsession.flush()
