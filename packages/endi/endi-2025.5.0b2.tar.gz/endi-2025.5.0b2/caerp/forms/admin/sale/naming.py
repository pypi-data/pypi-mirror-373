from caerp.utils.compat import Iterable
from typing import Tuple

import colander

from caerp.models.project.types import BusinessType
from caerp.models.project.naming import LabelOverride
from caerp.models.services.naming import NamingService


def combine_label_keys_business_types() -> Iterable[Tuple[BusinessType, str]]:
    business_types = BusinessType.query_for_select()

    for business_type in business_types:
        for label_key in NamingService.SUPPORTED_LABEL_KEYS:
            yield business_type, label_key


def mk_field_name(business_type: BusinessType, label_key: str) -> str:
    return f"business_type-{business_type.id}+{label_key}"


def get_label_override_set_schema() -> colander.SchemaNode:
    """
    Build a single flat schema for holding all name overrides

    This is not a standard ColanderAlchemy-style mapping, but it allows with
    some view-side code to update the LabelOverride instances.
    """
    schema = colander.SchemaNode(colander.Mapping())

    for business_type, label_key in combine_label_keys_business_types():
        sub_schema = colander.SchemaNode(
            colander.String(),
            name=mk_field_name(business_type, label_key),
            title=f"Renomme « {NamingService.get_default_label(label_key)} » en :",
            section=business_type.label,
            missing=colander.drop,
        )
        schema.add(sub_schema)
    return schema
