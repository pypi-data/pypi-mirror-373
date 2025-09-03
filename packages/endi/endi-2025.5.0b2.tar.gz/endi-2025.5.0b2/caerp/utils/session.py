"""
    Custom beaker session handling allowing to use a remember me cookie
    that allows long time connections
"""

import logging


logger = logging.getLogger(__name__)


def _delete_redis_session_from_cookie_value(request, cookie_value):
    """
    Delete a redis user session associated to the cookie value.
    Allows to delete a session from a backend to backend call (like oidc backend logout)
    """
    from pyramid_session_redis import (
        SignedSerializer,
        _NullSerializer,
    )
    from pyramid_session_redis.connection import get_default_connection

    cookie_signer = SignedSerializer(
        request.registry.settings["redis.sessions.secret"],
        "pyramid_session_redis.",
        "sha512",
        serializer=_NullSerializer(),
    )
    session_id = cookie_signer.loads(cookie_value)

    redis_conn = get_default_connection(request)
    redis_conn.delete(session_id)


def _get_beaker_setting(settings, key):
    """Handle both beaker settings key syntaxes"""
    if key in settings:
        return settings[key]
    elif f"beaker.{key}" in settings:
        return settings[f"beaker.{key}"]
    else:
        return None


def _get_file_session_id_from_cookie_value(request, cookie_value):
    """
    Retrieve the session id from a cookie value (session id is encrypted)
    """
    from beaker.session import SignedCookie

    cookie_handler = SignedCookie(
        _get_beaker_setting(request.registry.settings, "session.secret"), cookie_value
    )
    return cookie_handler.value_decode(cookie_value)[0]


def _get_beaker_session_storage_manager(request, file_session_id):
    """
    Build beaker's storage manager to be able to manipulate session
    data directly from caerp's code
    """
    from beaker.cache import clsmap

    storage_type = _get_beaker_setting(request.registry.settings, "session.type")
    data_dir = _get_beaker_setting(request.registry.settings, "session.data_dir")
    lock_dir = _get_beaker_setting(request.registry.settings, "session.lock_dir")

    factory = clsmap[storage_type]
    return factory(
        file_session_id, data_dir=data_dir, lock_dir=lock_dir, digest_filenames=False
    )


def _delete_beaker_session_from_cookie_value(request, cookie_value):
    """
    Delete a beaker session associated to the given cookie value.
    Allows to delete a session from a backend to backend call (like oidc backend logout)
    """
    file_session_id = _get_file_session_id_from_cookie_value(request, cookie_value)
    session_storage_manager = _get_beaker_session_storage_manager(
        request, file_session_id
    )
    session_storage_manager.do_remove()


def _get_redis_session_factory(settings):
    """
    Initialize the redis session factory to be used in caerp
    """
    try:
        from pyramid_session_redis import session_factory_from_settings
    except ImportError as error:
        logger.warning("Please install the pyramid_session_redis package")
        raise error

    factory = session_factory_from_settings(settings)
    return factory


def _get_beaker_session_factory(settings):
    """
    Wrap the beaker session factory to add longtimeout support
    """
    from beaker.session import SessionObject
    from pyramid_beaker import session_factory_from_settings

    factory = session_factory_from_settings(settings)

    class CaerpSessionObject(factory):
        """
        Our pyramid session object
        """

        _longtimeout = int(factory._options.pop("longtimeout"))

        def __init__(self, request):
            options = self._options.copy()
            if "remember_me" in list(request.cookies.keys()):
                options["timeout"] = self._longtimeout

            SessionObject.__init__(self, request.environ, **options)

            def session_callback(request, response):
                exception = getattr(request, "exception", None)
                if exception is None or self._cookie_on_exception and self.accessed():
                    self.persist()
                    headers = self.__dict__["_headers"]
                    if headers["set_cookie"] and headers["cookie_out"]:
                        response.headerlist.append(
                            ("Set-Cookie", headers["cookie_out"])
                        )

            request.add_response_callback(session_callback)

    return CaerpSessionObject


def _get_redis_session_id(request):
    return request.cookies.get("session")


def _get_beaker_session_id(request):
    return request.cookies.get("beaker.session.id")


def get_session_factory(settings):
    """
    Entry point to get the session factory.
    Handles both beaker and redis session factories
    """
    if settings.get("redis.sessions.url", False):
        logger.debug("Using redis session factory")
        return _get_redis_session_factory(settings)
    else:
        logger.debug("Using beaker session factory")
        return _get_beaker_session_factory(settings)


def get_session_id(request):
    """
    Entrypoint to get the session id.
    Handles both beaker and redis session factories
    """
    if request.registry.settings.get("redis.sessions.url", False):
        return _get_redis_session_id(request)
    else:
        return _get_beaker_session_id(request)


def delete_session_from_cookie_value(request, cookie_value):
    """
    Entrypoint to delete a session from a cookie value.
    Handles both beaker and redis session factories.
    """
    if request.registry.settings.get("redis.sessions.url", False):
        return _delete_redis_session_from_cookie_value(request, cookie_value)
    else:
        return _delete_beaker_session_from_cookie_value(request, cookie_value)
