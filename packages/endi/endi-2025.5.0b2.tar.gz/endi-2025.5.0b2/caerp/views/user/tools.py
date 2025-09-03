FORM_CONFIG_KEY = "user_form"
URL_KEY = "callback_urls"
DEFAULTS_KEY = "defaults"


class UserFormConfigState:
    def __init__(self, session):
        self.session = session

    def _get_config(self):
        return self.session.get(FORM_CONFIG_KEY, {})

    def set_config(self, config):
        self.session[FORM_CONFIG_KEY] = config
        self.session.changed()

    def get_next_step(self):
        config = self._get_config()
        steps = config.get(URL_KEY)
        result = None
        if steps:
            result = steps.pop()
            self.set_steps(steps)
        return result

    def set_steps(self, steps):
        config = self._get_config()
        config[URL_KEY] = steps
        self.set_config(config)

    def get_defaults(self):
        config = self._get_config()
        defaults = config.get(DEFAULTS_KEY, {})
        return defaults

    def get_default(self, key, default_value):
        defaults = self.get_defaults()
        return defaults.get(key, default_value)

    def pop_default(self, key, default_value):
        defaults = self.get_defaults()
        res = defaults.pop(key, default_value)
        self.set_defaults(defaults)
        return res

    def add_defaults(self, defaults):
        old_defaults = self.get_defaults()
        old_defaults.update(defaults)
        config = self._get_config()
        config[DEFAULTS_KEY] = old_defaults
        self.set_config(config)

    def set_defaults(self, defaults):
        config = self._get_config()
        config[DEFAULTS_KEY] = defaults
        self.set_config(config)
