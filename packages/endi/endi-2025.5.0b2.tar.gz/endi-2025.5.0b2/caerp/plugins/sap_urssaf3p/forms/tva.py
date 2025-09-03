import functools

import deform
import deform_extensions

from caerp.forms import customize_field
from caerp.forms.admin.sale.tva import (
    get_tva_edit_schema,
    PRODUCT_GRID,
)


def get_product_grid():
    """
    Tries to customize the PRODUCT_GRID core layout a future-proof way.
    """
    out_list = []
    code_nature_row = (("urssaf_code_nature", 12),)
    for row in PRODUCT_GRID:
        if row[0][0] == "active":
            out_list.append(code_nature_row)
        out_list.append(row)

    if not code_nature_row in out_list:
        # Fallback in case grid changed in codebase
        out_list.append(code_nature_row)

    return out_list


def sap_urssaf3p_get_tva_edit_schema():
    schema = get_tva_edit_schema()
    product_schema = schema["products"].children[0]
    product_schema.widget = deform_extensions.GridMappingWidget(
        named_grid=get_product_grid()
    )
    customize_product = functools.partial(customize_field, product_schema)

    customize_product(
        "urssaf_code_nature",
        title="« Code Nature » URSSAF",
        description="cf nomenclature URSSAF, indispensable pour utiliser l'avance immédiate SAP avec ce produit",
        widget=deform.widget.TextInputWidget(),
    )
    return schema
