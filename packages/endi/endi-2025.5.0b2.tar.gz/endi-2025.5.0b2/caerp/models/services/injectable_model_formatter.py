import string


class InjectableModelFormatter(string.Formatter):
    """
    str.format()-like but with custom vars to allow injecting properties from a model

    the Model class must define a __injectable_fields__ property containing a list of properties

    e.g:

    class A:
        __injectable_fields__ = ["a", "b"]

        a = "fu"

        def __init__(self, b):
            self.b = b

        @property
        def c(self):
            return "zoo"


    obj = A("cab")
    formatter = InjectableModelFormatter()
    formatter.format("{a} - {b}", obj)
    'fu - cab'
    formatter.format("{z}", obj)
    KeyError
    formatter.format("{c} {z}", obj, z=1)
    'zoo 1'
    """

    def get_value(self, key, args, kwargs):
        try:
            injectable_instance = args[0]
            args = args[1:]
        except KeyError:
            raise ValueError("Pass an object as first argument of format()")

        try:
            allowed_fields = injectable_instance.__injectable_fields__
        except AttributeError:
            raise ValueError(
                "first argument of format()  must be "
                "an object defining an __injectable_fields__ attr"
            )

        if key in allowed_fields:
            return getattr(injectable_instance, key)
        else:  # also allow extra-params to be used for formatting
            return super().get_value(key, args, kwargs)
