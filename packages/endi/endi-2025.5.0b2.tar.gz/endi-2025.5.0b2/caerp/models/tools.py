from sqlalchemy import inspect, or_, not_


def get_excluded_colanderalchemy(title):
    """
    Return colanderalchemy for excluded field but with title set (for other
    sqla inspection based modules like py3o inspection or ods generation)
    """
    return {"exclude": True, "title": title}


def set_attribute(instance, key, value, initiator=None):
    """Set the value of an attribute, firing history events.

    This function is copied from the attributes module but adds the
    "initiator" argument.

    Mike Bayer's code provided on the sqlalchemy mailling list

    """
    state = inspect(instance)
    dict_ = state.dict
    state.manager[key].impl.set(state, dict_, value, initiator)


def get_labor_units_sqla_filter(model_cls, attribute="unity"):
    """
    Build a filter to collect only labor units
    """
    return getattr(model_cls, attribute).regexp_match("^.*heure.*$|^.*main.*oeuvre.*$")


def get_not_labor_units_sqla_filter(model_cls, attribute="unity"):
    return or_(
        not_(
            getattr(model_cls, attribute).regexp_match("^.*heure.*$|^.*main.*oeuvre.*$")
        ),
        getattr(model_cls, attribute) == None,
    )
