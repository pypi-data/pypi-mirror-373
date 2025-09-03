"""
Utilitaires pour faciliter la récupération des informations de configuration
"""
from sqlalchemy import select
from caerp.models.config import Config, _required, _type_value


from typing import Any, Optional, Type


def get_config_value(
    request, keyname: str, default: Any = _required, type_: Type = str
) -> Any:
    """
    Return a typed configuration value

    Case 1  : type_ is managed by the _type_value function (one of
    float/int/date)

        - We try to convert the value
        - If a default is provided, we fallback on the default, else an
        exception is raised

    Case 2 : The data is not set, we return default or None

    Case 3 : The data is set but no managed type_ is provided, we return
    the data

    :param str keyname: The config key (name attribute)
    :param default: The default value to return, if default is not set, we
    return None in the Cases 2 and 3

    :param class type_: The type_ of the value we want in return
    """
    config = request.dbsession.execute(
        select(Config.value).where(Config.name == keyname)
    ).scalar()
    result = None

    if config is not None:
        result = _type_value(config, type_=type_, default=default)

    if result is None and default != _required:
        result = default

    return result


def get_cae_name(request) -> Optional[str]:
    """
    Return the name of the Company or None
    """
    return get_config_value(request, "cae_business_name")


def get_cae_address(request, full=False) -> Optional[str]:
    """
    Return the postal address of the CAE or None
    """
    address = get_config_value(request, "cae_address")
    if full:
        zipcode = get_config_value(request, "cae_zipcode")
        city = get_config_value(request, "cae_city")
        return f"{address}\n{zipcode} {city}"
    return address
