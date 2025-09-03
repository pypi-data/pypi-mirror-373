from typing import Callable


class SQLAListeners:
    """
    Stores a global registry of functions configuring sqlalchemy listeners

    Functions come by pair : one to configure (containing
    sqlalchemy.event.listen calls) and one to deconfigure (containing
    sqlalchemy.event.remove calls).

    Goal is to be able to disable at once all event listeners in situations
    where we want to avoid side effect (eg: bulk data handling).
    """

    start_funcs = []
    stop_funcs = []

    @classmethod
    def register(cls, start_func: Callable, stop_func: Callable = None):
        cls.start_funcs.append(start_func)
        if stop_func:
            cls.stop_funcs.append(stop_func)

    @classmethod
    def _call_all(funcs):
        for f in funcs:
            f()

    @classmethod
    def start_listening(cls):
        for func in cls.start_funcs:
            func()

    @classmethod
    def stop_listening(cls):
        for func in cls.stop_funcs:
            func()
