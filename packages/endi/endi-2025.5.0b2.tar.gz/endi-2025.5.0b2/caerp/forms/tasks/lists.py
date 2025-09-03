import logging
import colander
from caerp_base.models.base import DBSESSION
from sqlalchemy import or_
from caerp.forms.custom_types import AmountType
from caerp.models.task import Invoice, CancelInvoice, Task

logger = logging.getLogger(__name__)


def existing_invoice_official_number_validator(number, year=None):
    query = Task.query()
    query = query.with_polymorphic([Invoice, CancelInvoice])
    query = query.filter_by(official_number=number)
    if year:
        query = query.filter(
            or_(Invoice.financial_year == year, CancelInvoice.financial_year == year)
        )
    return DBSESSION.query(query.exists()).scalar()


class PeriodSchema(colander.MappingSchema):
    """
    A form used to select a period
    """

    is_range = True
    start = colander.SchemaNode(
        colander.Date(),
        title="Émis(e) entre le",
        description="",
        missing=colander.drop,
    )
    end = colander.SchemaNode(
        colander.Date(),
        title="et le",
        description="",
        missing=colander.drop,
    )


class AmountRangeSchema(colander.MappingSchema):
    """
    Used to filter on a range of amount
    """

    is_range = True

    start = colander.SchemaNode(
        AmountType(5),
        title="TTC entre",
        missing=colander.drop,
        description="",
    )
    end = colander.SchemaNode(
        AmountType(5),
        title="et",
        missing=colander.drop,
        description="",
    )


class NumberRangeSchema(colander.MappingSchema):
    is_range = True

    start = colander.SchemaNode(
        colander.String(),
        title="Depuis la facture numéro",
        description="Numéro de facture à partir duquel exporter",
        missing=colander.drop,
    )

    end = colander.SchemaNode(
        colander.String(),
        title="Jusqu'à la facture numéro",
        description=(
            "Numéro de facture jusqu'auquel exporter (dernier document si vide)"
        ),
        missing=colander.drop,
    )

    def validator(self, form, value):
        """
        Validate the number range
        """
        logger.debug(value)
        start_num = value.get("start")
        end_num = value.get("end")

        if start_num:
            if not existing_invoice_official_number_validator(start_num):
                exc = colander.Invalid(
                    form,
                    "Aucune facture {} n'a pu être retrouvée".format(start_num),
                )
                exc["start"] = "Aucune facture n'existe avec ce n° de facture"
                raise exc

            if end_num:
                if not existing_invoice_official_number_validator(end_num):
                    exc = colander.Invalid(
                        form,
                        "Aucune facture {} n'a pu être retrouvée".format(end_num),
                    )
                    exc["end"] = "Aucune facture n'existe avec ce n° de facture"
                    raise exc
