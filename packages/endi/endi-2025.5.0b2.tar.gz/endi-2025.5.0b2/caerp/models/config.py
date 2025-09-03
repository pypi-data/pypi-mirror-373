"""
    Config model stores :
    enDI's welcome message
    Documents footers, headers ...
"""

import logging
import datetime
import io
import json
from typing import Any, Type
from sqlalchemy import (
    Column,
    Text,
    Integer,
    String,
    event,
)

from depot.fields.sqlalchemy import (
    UploadedFileField,
    _SQLAMutationTracker,
)

from caerp_base.models.mixins import (
    PersistentACLMixin,
)

from caerp_base.models.base import DBBASE, DBSESSION
from caerp_base.models.base import default_table_args
from caerp.utils.filedepot import _to_fieldstorage
from caerp.compute.math_utils import (
    convert_to_int,
    convert_to_float,
)
from caerp.utils.datetimes import parse_date

logger = logging.getLogger(__name__)


class ConfigRequired:
    def __repr__(self):
        return "<config.required>"

    def __bool__(self):
        return False


_required = ConfigRequired()


def convert_to_bool(v, default=_required) -> bool:
    """
    Convert config values to boolean
    """
    if v is None:
        if default != _required:
            return default
        else:
            raise ValueError()
    elif v == "0":
        return False
    else:
        return bool(v)


class ConfigFiles(PersistentACLMixin, DBBASE):
    """
    A file model
    """

    __tablename__ = "config_files"
    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True)
    name = Column(String(100))
    data = Column(UploadedFileField)
    mimetype = Column(String(100))
    size = Column(Integer)

    def getvalue(self):
        """
        Method making our file object compatible with the common file rendering
        utility
        """
        return self.data.file.read()

    @property
    def label(self):
        """
        Simple shortcut for getting a label for this file
        """
        return self.name

    @classmethod
    def get(cls, key):
        """
        Override the default get method to get by key and not by id
        """
        return cls.query().filter(cls.key == key).first()

    @classmethod
    def set(cls, key, appstruct):
        """
        Set a file for the given key, if the key isn't field yet, add a new
        instance
        """
        instance = cls.get(key)
        if instance is None:
            instance = cls(key=key)

        if "filename" in appstruct:
            instance.name = appstruct["filename"]

        if "_acl" in appstruct:
            instance._acl = appstruct["_acl"]

        data = appstruct.pop("fp", None)
        for attr_name, attr_value in list(appstruct.items()):
            setattr(instance, attr_name, attr_value)
        if data is not None:
            instance.data = data

        if instance.id is not None:
            DBSESSION().merge(instance)
        else:
            DBSESSION().add(instance)

    @classmethod
    def delete(cls, key):
        """
        Override the default delete method to delete by key and not by id
        """
        return cls.query().filter(cls.key == key).delete()

    @classmethod
    def rename(cls, key, newkey):
        """
        rename a key
        """
        instance = cls.get(key)
        if instance is None:
            raise KeyError(f"configuration key {key} does not exists")

        cls.delete(newkey)  # remove a possible previous key

        instance.key = newkey
        DBSESSION().merge(instance)

    @classmethod
    def __declare_last__(cls):
        # Unconfigure the event set in _SQLAMutationTracker, we have _save_data
        mapper = cls._sa_class_manager.mapper
        args = (mapper.attrs["data"], "set", _SQLAMutationTracker._field_set)
        if event.contains(*args):
            event.remove(*args)

        # Declaring the event on the class attribute instead of mapper property
        # enables proper registration on its subclasses
        event.listen(cls.data, "set", cls._set_data, retval=True)

    @classmethod
    def _set_data(cls, target, value, oldvalue, initiator):
        if hasattr(value, "seek"):
            value.seek(0)
            value = value.read()

        if isinstance(value, bytes):
            value = _to_fieldstorage(
                fp=io.BytesIO(value), filename=target.name, size=len(value)
            )

        newvalue = _SQLAMutationTracker._field_set(target, value, oldvalue, initiator)

        return newvalue


def _type_value(value, type_=str, default=_required):
    """
    Optionally type the returned value.

    Meant to be used for config keys, with well-known types, not in the wild
    (no error handling for that).

    :param str value: The value to convert
    :param class type_: The expected output type_
    :param default: The default value to return default to _required when no
    value is passed
    """
    result = value

    try:
        # Ici on transforme la valeur par défaut non renseignée _required en
        # None Les fonctions de conversion ci-dessous identifie la valeur None
        # comme une valeur non spécifiée, on refait le chemin inverse dans
        # l'except
        if default == _required:
            kwargs = {}
        else:
            kwargs = {"default": default}

        if type_ is datetime.date:
            result = parse_date(result, **kwargs)
        elif type_ is int:
            result = convert_to_int(result, **kwargs)
        elif type_ is float:
            result = convert_to_float(result, **kwargs)
        elif type_ is bool:
            result = convert_to_bool(result, **kwargs)
        elif type_ is dict:
            result = json.loads(result)
    except ValueError as e:
        # Intercept the default value management
        if default != _required:
            result = default
        else:
            raise e

    return result


class Config(DBBASE):
    """
    Table containing the main configuration
      `name` varchar(255) NOT NULL,
      `value` text,
      PRIMARY KEY  (`name`)
    """

    __tablename__ = "config"
    __table_args__ = default_table_args
    name = Column("name", String(255), primary_key=True)
    value = Column("value", Text())

    def __init__(self, **kwargs):
        for key, value in list(kwargs.items()):
            if value is not None:
                setattr(self, key, value)

    @classmethod
    def get(cls, keyname, default=None):
        query = super(Config, cls).query()
        query = query.filter(Config.name == keyname)
        result = query.first()
        if default and result is None:
            result = default
        return result

    @classmethod
    def get_value(cls, keyname: str, default: Any = _required, type_: Type = str):
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
        config = cls.get(keyname)
        result = None

        if config is not None:
            result = _type_value(config.value, type_=type_, default=default)

        if result is None and default != _required:
            result = default

        return result

    @classmethod
    def set(cls, key, value):
        instance = cls.get(key)
        if instance is None:
            instance = cls(name=key)

        instance.value = value
        DBSESSION().merge(instance)
        DBSESSION().flush()


class TypableDict(dict):
    def get_value(self, keyname, default=_required, type_=str):
        v = self.get(keyname)
        if v is None and default == _required:
            return v
        else:
            return _type_value(v, type_, default=default)


def get_config():
    """
    Return a dict-like with the config objects
    """
    return TypableDict((entry.name, entry.value) for entry in Config.query().all())


def get_admin_mail():
    """
    Collect the administration mail in the current configuration

    :returns: A configured CAE administration mail
    :rtype: str
    """
    result = Config.get("cae_admin_mail")
    if result is not None:
        result = result.value
    return result
