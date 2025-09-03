import functools

import colander

from caerp import forms
from caerp.forms.tasks.invoice import get_add_edit_invoice_schema
from caerp.utils.renderer import get_json_dict_repr


def _customize_sap_taskline_fields(schema):
    customize = functools.partial(forms.customize_field, schema)
    customize("date", missing=colander.required)
    return schema


def _customize_sap_tasklinegroup_fields(schema):
    if "lines" in schema:
        child_schema = schema["lines"].children[0]
        _customize_sap_taskline_fields(child_schema)
    return schema


def _customize_sap_invoice_schema(schema):
    if "line_groups" in schema:
        child_schema = schema["line_groups"].children[0]
        _customize_sap_tasklinegroup_fields(child_schema)
    return schema


def validate_sap_invoice(invoice_object, request):
    schema = get_add_edit_invoice_schema()
    schema = _customize_sap_invoice_schema(schema)
    schema = schema.bind(request=request)
    appstruct = get_json_dict_repr(invoice_object, request)
    appstruct["line_groups"] = get_json_dict_repr(
        invoice_object.line_groups, request=request
    )
    appstruct["discounts"] = get_json_dict_repr(invoice_object.discounts, request)
    cstruct = schema.deserialize(appstruct)
    return cstruct
