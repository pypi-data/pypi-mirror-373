from sqlalchemy.sql.expression import select
from sqlalchemy import func
from caerp.models.sequence_number import (
    GlobalSequence,
    MonthCompanySequence,
    MonthSequence,
    SequenceNumber,
    YearSequence,
)

from caerp.models.services.official_number import AbstractNumberService


class SupplierInvoiceNumberService(AbstractNumberService):
    lock_name = "supplier_invoice_number"

    @classmethod
    def get_sequences_map(cls):
        from caerp.models.supply.supplier_invoice import SupplierInvoice

        seq_kwargs = dict(
            types=["supplier_invoice"],
            model_class=SupplierInvoice,
        )
        return {
            "SEQGLOBAL": GlobalSequence(
                db_key=SequenceNumber.SEQUENCE_SUPPLIERINVOICE_GLOBAL,
                init_value_config_key="global_supplierinvoice_sequence_init_value",
                **seq_kwargs,
            ),
            "SEQYEAR": YearSequence(
                db_key=SequenceNumber.SEQUENCE_SUPPLIERINVOICE_YEAR,
                init_value_config_key="year_supplierinvoice_sequence_init_value",
                init_date_config_key="year_supplierinvoice_sequence_init_date",
                **seq_kwargs,
            ),
            "SEQMONTH": MonthSequence(
                db_key=SequenceNumber.SEQUENCE_SUPPLIERINVOICE_MONTH,
                init_value_config_key="month_supplierinvoice_sequence_init_value",
                init_date_config_key="month_supplierinvoice_sequence_init_date",
                **seq_kwargs,
            ),
            "SEQMONTHANA": MonthCompanySequence(
                db_key=SequenceNumber.SEQUENCE_SUPPLIERINVOICE_MONTH_COMPANY,
                **seq_kwargs,
            ),
        }

    @classmethod
    def is_already_used(cls, request, node_id, official_number) -> bool:
        # NB : On accède à l'engine pour effectuer notre requête en dehors de la
        # transaction : cf https://framagit.org/caerp/caerp/-/issues/2811
        engine = request.dbsession.connection().engine

        # Imported here to avoid circular dependencies
        from caerp.models.supply.supplier_invoice import SupplierInvoice

        sql = select(func.count(SupplierInvoice.id))
        sql = sql.where(
            SupplierInvoice.official_number == official_number,
            SupplierInvoice.id != node_id,
            SupplierInvoice.type_ == "supplier_invoice",
        )
        query = engine.execute(sql)
        return query.scalar() > 0


class InternalSupplierInvoiceNumberService(AbstractNumberService):
    lock_name = "internal_supplier_invoice_number"

    @classmethod
    def get_sequences_map(cls):
        from caerp.models.supply.internalsupplier_invoice import (
            InternalSupplierInvoice,
        )

        seq_kwargs = dict(
            types=["internalsupplier_invoice"],
            model_class=InternalSupplierInvoice,
        )
        return {
            "SEQGLOBAL": GlobalSequence(
                db_key=SequenceNumber.SEQUENCE_INTERNALSUPPLIERINVOICE_GLOBAL,
                init_value_config_key=(
                    "global_internalsupplierinvoice_sequence_init_value"
                ),
                **seq_kwargs,
            ),
            "SEQYEAR": YearSequence(
                db_key=SequenceNumber.SEQUENCE_INTERNALSUPPLIERINVOICE_YEAR,
                init_value_config_key=(
                    "year_internalsupplierinvoice_sequence_init_value"
                ),
                init_date_config_key="year_internalsupplierinvoice_sequence_init_date",
                **seq_kwargs,
            ),
            "SEQMONTH": MonthSequence(
                db_key=SequenceNumber.SEQUENCE_INTERNALSUPPLIERINVOICE_MONTH,
                init_value_config_key=(
                    "month_internalsupplierinvoice_sequence_init_value"
                ),
                init_date_config_key="month_internalsupplierinvoice_sequence_init_date",
                **seq_kwargs,
            ),
            "SEQMONTHANA": MonthCompanySequence(
                db_key=SequenceNumber.SEQUENCE_INTERNALSUPPLIERINVOICE_MONTH_COMPANY,  # noqa: E501
                **seq_kwargs,
            ),
        }

    @classmethod
    def is_already_used(cls, request, node_id, official_number) -> bool:
        # NB : On accède à l'engine pour effectuer notre requête en dehors de la
        # transaction : cf https://framagit.org/caerp/caerp/-/issues/2811
        engine = request.dbsession.connection().engine

        # Imported here to avoid circular dependencies
        from caerp.models.supply import InternalSupplierInvoice

        sql = select(func.count(InternalSupplierInvoice.id))
        sql = sql.where(
            InternalSupplierInvoice.official_number == official_number,
            InternalSupplierInvoice.id != node_id,
        )
        query = engine.execute(sql)
        return query.scalar() > 0
