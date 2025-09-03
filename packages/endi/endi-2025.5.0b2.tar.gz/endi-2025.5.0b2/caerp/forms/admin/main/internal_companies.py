import colander

from caerp.forms.company import company_choice_node


class InternalCompaniesSchema(colander.MappingSchema):
    companies = company_choice_node(
        multiple=True,
        title="Enseignes internes à la CAE",
    )
