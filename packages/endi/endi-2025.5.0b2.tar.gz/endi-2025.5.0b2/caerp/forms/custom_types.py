"""
    Custom colander types
"""
import colander

from caerp.compute.math_utils import amount, integer_to_amount


def specialfloat(self, value):
    """
    preformat the value before passing it to the float function
    """
    if isinstance(value, (str, bytes)):
        value = value.replace("€", "").replace(",", ".").replace(" ", "")
    return float(value)


class QuantityType(colander.Number):
    """
    Preformat entry supposed to be numeric entries

    .. code-block:: python

        node = colander.SchemaNode(QuantityType())
        assert node.deserialize("123") == 123
        assert node.deserialize("123,45") == 123.45
        assert node.deserialize("123.456") == 123.456
        assert node.deserialize("12 345,25 €") == 12345.25
    """

    num = specialfloat


class AmountType(colander.Number):
    """
    Amounts are submitted as float strings (with spaces, commas and euro sign)
    but are stored as integers in the database.

    This colander node typ handles the conversion between float and integer

    :param int precision: The number of decimal places stored in the database (default: 2)

    .. code-block:: python

        node = colander.SchemaNode(AmountType(precision=3))
        assert node.serialize(node, 123456) == "123.456"
        assert node.deserialize(node, "123.456") == 123456
        assert node.serialize(node, 123456789) == "123456.789"
        assert node.deserialize(node, "123456.789") == 123456789
        assert node.deserialize(node, "12 3456,789 €") == 123456789
    """

    num = specialfloat

    def __init__(self, precision=2):
        colander.Number.__init__(self)
        self.precision = precision

    def serialize(self, node, appstruct):
        if appstruct is colander.null:
            return colander.null

        try:
            return str(integer_to_amount(self.num(appstruct), self.precision))
        except Exception:
            raise colander.Invalid(
                node,
                '"{val}" n\'est pas un montant valide'.format(val=appstruct),
            )

    def deserialize(self, node, cstruct):
        if cstruct != 0 and not cstruct:
            return colander.null

        try:
            return amount(self.num(cstruct), self.precision)
        except Exception:
            raise colander.Invalid(
                node, '"{val}" n\'est pas un montant valide'.format(val=cstruct)
            )


class Integer(colander.Number):
    """
    Fix https://github.com/Pylons/colander/pull/35
    """

    num = int

    def serialize(self, node, appstruct):
        if appstruct in (colander.null, None):
            return colander.null
        try:
            return str(self.num(appstruct))
        except Exception:
            raise colander.Invalid(
                node, "'${val}' n'est pas un nombre".format(val=appstruct)
            )


class CsvTuple(colander.SchemaType):
    def serialize(self, node, appstruct):
        if appstruct in (colander.null, None):
            return colander.null
        return tuple((a for a in appstruct.split(",") if a))

    def deserialize(self, node, cstruct):
        if cstruct is colander.null:
            return colander.null

        if not colander.is_nonstr_iter(cstruct):
            raise colander.Invalid(
                node,
                colander._("${cstruct} is not iterable", mapping={"cstruct": cstruct}),
            )

        return ",".join(cstruct)


class CustomSet(colander.Set):
    """
    Colander Node typ allowing to pass a set of values in a form :

    - of a comma separated string
    - of a list
    - of a single string element

    .. code-block:: python

        node = colander.SchemaNode(CustomSet())
        node.deserialize(["1", "2", "3"]) == {"1", "2", "3"}
        node.deserialize("1,2,3") == {"1", "2", "3"}
        node.deserialize("1") == {"1"}
    """

    def deserialize(self, node, cstruct):
        if cstruct == "":
            cstruct = colander.null
        elif isinstance(cstruct, str):
            cstruct = cstruct.split(",")

        return super().deserialize(node, cstruct)


class GlobalAllValidator:
    """
    Run multiple validators and stop on the first error.

    The problem this validator solves :

    colander.All() will run all validators in sequence, collect all errors and
    store them in a tree of Invalid objects. It makes nearly impossible to
    serialize the error tree to a JSON object.

    GlobalAllValidator will run all validators in sequence, stop on the first error
    and return that error that can be serialized easily.
    """

    def __init__(self, *validators):
        self.validators = validators

    def __call__(self, node, value):
        for validator in self.validators:
            validator(node, value)
