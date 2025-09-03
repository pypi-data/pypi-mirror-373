import logging
import typing

import colander
import colanderalchemy
import deform.schema

from caerp.forms import custom_types
from caerp.utils.compat import Iterable

logger = logging.getLogger(__name__)


class ConversionError(Exception):
    pass


class NoSuchConverter(ConversionError):
    def __init__(self, schema_node: colander.SchemaNode):
        self.schema_node = schema_node

    def __str__(self):
        return f"No converter for {self.schema_node} of type {self.schema_node.typ}"

    def __repr__(self) -> str:
        return self.__str__()


def convert_length_validator_factory(max_key: str, min_key: str) -> typing.Callable:
    """
    :type max_key: str
    :type min_key: str
    """

    def validator_converter(
        schema_node: colander.SchemaNode, validator: typing.Callable
    ) -> dict:
        """
        :type schema_node: colander.SchemaNode
        :type validator: colander.interfaces.Validator
        :rtype: dict
        """
        converted = None
        if isinstance(validator, colander.Length):
            converted = {}
            if validator.max is not None:
                converted[max_key] = validator.max
            if validator.min is not None:
                converted[min_key] = validator.min
        return converted

    return validator_converter


def convert_oneof_validator_factory(null_values: Iterable = (None,)) -> typing.Callable:
    """
    :type null_values: iter
    """

    def validator_converter(
        schema_node: colander.SchemaNode, validator: typing.Callable
    ) -> dict:
        """
        :type schema_node: colander.SchemaNode
        :type validator: colander.interfaces.Validator
        :rtype: dict
        """
        converted = None
        if isinstance(validator, colander.OneOf):
            converted = {}
            converted["enum"] = list(validator.choices)
            # if not schema_node.required:
            #     converted["enum"].extend(list(null_values))
        return converted

    return validator_converter


def convert_range_validator(
    schema_node: colander.SchemaNode, validator: typing.Callable
) -> dict:
    """
    :type schema_node: colander.SchemaNode
    :type validator: colander.interfaces.Validator
    :rtype: dict
    """
    converted = None
    if isinstance(validator, colander.Range):
        converted = {}
        if validator.max is not None:
            converted["maximum"] = validator.max
        if validator.min is not None:
            converted["minimum"] = validator.min
    return converted


def convert_regex_validator(schema_node: colander.SchemaNode, validator):
    """
    :type schema_node: colander.SchemaNode
    :type validator: colander.interfaces.Validator
    :rtype: dict
    """
    converted = None
    if isinstance(validator, colander.Regex):
        converted = {}
        if hasattr(colander, "url") and validator is colander.url:
            converted["format"] = "uri"
            # Modification relative à notre librairie frontend jsonschema-yup
            converted["url"] = True
        elif isinstance(validator, colander.Email):
            converted["format"] = "email"
            # Modification relative à notre librairie frontend jsonschema-yup
            converted["email"] = True
        else:
            converted["pattern"] = validator.match_object.pattern
            if validator.msg:
                converted["errMessage"] = validator.msg
    return converted


def get_amount_regex_validator():
    return {"pattern": r"^[0-9 ]*[.,]?\d*$"}


class ValidatorConversionDispatcher(object):
    def __init__(self, *converters):
        self.converters = converters

    def __call__(self, schema_node, validator=None):
        """
        :type schema_node: colander.SchemaNode
        :type validator: colander.interfaces.Validator
        :rtype: dict
        """
        if validator is None:
            validator = schema_node.validator
        converted = {}
        if validator is not None:
            for converter in (self.convert_all_validator,) + self.converters:
                ret = converter(schema_node, validator)
                if ret is not None:
                    converted = ret
                    break
        return converted

    def convert_all_validator(self, schema_node, validator):
        """
        :type schema_node: colander.SchemaNode
        :type validator: colander.interfaces.Validator
        :rtype: dict
        """
        converted = None
        if isinstance(validator, colander.All):
            converted = {}
            for v in validator.validators:
                ret = self(schema_node, v)
                converted.update(ret)
        return converted


class TypeConverter(object):

    type = ""

    def __init__(self, dispatcher: "TypeConversionDispatcher"):
        self.dispatcher = dispatcher

    def convert_validator(self, schema_node: colander.SchemaNode) -> dict:
        return {}

    def get_type_conversior(self, schema_node: colander.SchemaNode) -> str:
        return self.type

    def convert_type(self, schema_node: colander.SchemaNode, converted: dict) -> dict:
        converted["type"] = self.type

        if not schema_node.required:
            converted["nullable"] = True
        else:
            converted["required"] = True

        if hasattr(schema_node, "options"):
            converted["options"] = schema_node.options

        if getattr(schema_node, "readonly", False):
            converted["readOnly"] = True

        if schema_node.title:
            converted["title"] = schema_node.title

        if schema_node.description:
            converted["description"] = schema_node.description

        if schema_node.default not in (colander.null, None, colander.required):
            converted["default"] = schema_node.serialize(schema_node.default)

        return converted

    def __call__(
        self, schema_node: colander.SchemaNode, converted: dict = None
    ) -> dict:
        if converted is None:
            converted = {}
        converted = self.convert_type(schema_node, converted)
        converted.update(self.convert_validator(schema_node))
        return converted


class BaseStringTypeConverter(TypeConverter):

    type = "string"
    format = None

    def convert_type(self, schema_node, converted):
        """
        :type schema_node: colander.SchemaNode
        :type converted: dict
        :rtype: dict
        """
        converted = super(BaseStringTypeConverter, self).convert_type(
            schema_node, converted
        )

        if self.format is not None:
            converted["format"] = self.format
        return converted


class BooleanTypeConverter(TypeConverter):
    type = "boolean"


class DateTypeConverter(BaseStringTypeConverter):
    format = "date"


class DateTimeTypeConverter(BaseStringTypeConverter):
    format = "date-time"


class NumberTypeConverter(TypeConverter):
    type = "number"
    convert_validator = ValidatorConversionDispatcher(
        convert_range_validator,
        convert_oneof_validator_factory(),
    )


class IntegerTypeConverter(NumberTypeConverter):
    type = "integer"


class StringTypeConverter(BaseStringTypeConverter):
    convert_validator = ValidatorConversionDispatcher(
        convert_length_validator_factory("maxLength", "minLength"),
        convert_regex_validator,
        convert_oneof_validator_factory(("", None)),
    )


class AmountTypeConverter(BaseStringTypeConverter):
    def convert_type(self, schema_node, converted):
        result = super().convert_type(schema_node, converted)
        result.update(get_amount_regex_validator())
        return result


class TimeTypeConverter(BaseStringTypeConverter):
    format = "time"


class ObjectTypeConverter(TypeConverter):

    type = "object"

    def convert_type(self, schema_node, converted):
        """
        :type schema_node: colander.SchemaNode
        :type converted: dict
        :rtype: dict
        """
        converted = super(ObjectTypeConverter, self).convert_type(
            schema_node, converted
        )
        properties = {}
        required = []
        for sub_node in schema_node.children:
            properties[sub_node.name] = self.dispatcher(sub_node)
            if sub_node.required:
                required.append(sub_node.name)
        converted["properties"] = properties
        # On stocke les champs requis au sein de l'objet pour faciliter
        # La récupération du statut requis niveau front
        if len(required) > 0:
            converted["required_fields"] = required
        return converted


class ArrayTypeConverter(TypeConverter):

    type = "array"
    convert_validator = ValidatorConversionDispatcher(
        convert_length_validator_factory("maxItems", "minItems"),
    )

    def convert_type(self, schema_node, converted):
        """
        :type schema_node: colander.SchemaNode
        :type converted: dict
        :rtype: dict
        """
        converted = super(ArrayTypeConverter, self).convert_type(schema_node, converted)
        converted["items"] = self.dispatcher(schema_node.children[0])
        return converted


class TypeConversionDispatcher(object):

    converters = {
        colander.Boolean: BooleanTypeConverter,
        colander.Date: DateTypeConverter,
        colander.DateTime: DateTimeTypeConverter,
        colander.Float: NumberTypeConverter,
        custom_types.QuantityType: NumberTypeConverter,
        colander.Integer: IntegerTypeConverter,
        custom_types.AmountType: AmountTypeConverter,
        colander.Mapping: ObjectTypeConverter,
        colander.Sequence: ArrayTypeConverter,
        colander.String: StringTypeConverter,
        colander.Time: TimeTypeConverter,
        # For Files uploaded through
        deform.schema.FileData: IntegerTypeConverter,
    }

    def __init__(self, converters=None):
        """
        :type converters: dict
        """
        if converters is not None:
            self.converters.update(converters)

    def __call__(self, schema_node):
        """
        :type schema_node: colander.SchemaNode
        :rtype: dict
        """
        schema_type = schema_node.typ
        schema_type = type(schema_type)
        converter_class = self.converters.get(schema_type)
        if converter_class is None:
            raise NoSuchConverter(schema_node)
        converter = converter_class(self)
        converted = converter(schema_node)
        return converted


def finalize_conversion(converted):
    """
    :type converted: dict
    :rtype: dict
    """
    converted["$schema"] = "http://json-schema.org/draft-07/schema#"
    return converted


def convert_to_jsonschema(
    schema_node: typing.Union[colander.Schema, colanderalchemy.SQLAlchemySchemaNode],
    converters: typing.Optional[dict] = None,
) -> dict:
    """Convert a colander schema to jsonschema format

    :param schema_node: The Colander Schema
    :type schema_node: colander.Schema
    :param converters: prepopulated jsonschema dict, defaults to None
    :type converters: dict, optional
    :return: A jsonschema representation of the form
    :rtype: dict
    """
    dispatcher = TypeConversionDispatcher(converters)
    converted = dispatcher(schema_node)
    converted = finalize_conversion(converted)
    return converted
