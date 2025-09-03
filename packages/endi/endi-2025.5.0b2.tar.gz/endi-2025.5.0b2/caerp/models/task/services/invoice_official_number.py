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


class InvoiceNumberService(AbstractNumberService):
    lock_name = "invoice_number"

    @classmethod
    def get_sequences_map(cls):
        from caerp.models.task.task import Task

        seq_kwargs = dict(
            types=["invoice", "cancelinvoice"],
            model_class=Task,
        )
        return {
            "SEQGLOBAL": GlobalSequence(
                db_key=SequenceNumber.SEQUENCE_INVOICE_GLOBAL,
                init_value_config_key="global_invoice_sequence_init_value",
                **seq_kwargs,
            ),
            "SEQYEAR": YearSequence(
                db_key=SequenceNumber.SEQUENCE_INVOICE_YEAR,
                init_value_config_key="year_invoice_sequence_init_value",
                init_date_config_key="year_invoice_sequence_init_date",
                **seq_kwargs,
            ),
            "SEQMONTH": MonthSequence(
                db_key=SequenceNumber.SEQUENCE_INVOICE_MONTH,
                init_value_config_key="month_invoice_sequence_init_value",
                init_date_config_key="month_invoice_sequence_init_date",
                **seq_kwargs,
            ),
            "SEQMONTHANA": MonthCompanySequence(
                db_key=SequenceNumber.SEQUENCE_INVOICE_MONTH_COMPANY,
                company_init_date_fieldname="month_company_invoice_sequence_init_date",
                company_init_value_fieldname=(
                    "month_company_invoice_sequence_init_value"
                ),
                **seq_kwargs,
            ),
        }

    @classmethod
    def is_already_used(cls, request, node_id, official_number) -> bool:
        """
        Vérifie si le numéro est déjà utilisé pour une autre facture
        """
        # NB : On accède à l'engine pour effectuer notre requête en dehors de la
        # transaction : cf https://framagit.org/caerp/caerp/-/issues/2811
        engine = request.dbsession.connection().engine

        from caerp.models.task import Task

        sql = select(func.count(Task.id)).where(
            Task.official_number == official_number,
            Task.type_.in_(("invoice", "cancelinvoice")),
            Task.legacy_number == False,
            Task.id != node_id,
        )

        query = engine.execute(sql)
        return query.scalar() > 0


class InternalInvoiceNumberService(AbstractNumberService):
    lock_name = "internalinvoice_number"

    @classmethod
    def get_sequences_map(cls):
        from caerp.models.task.task import Task

        seq_kwargs = dict(
            types=["internalinvoice", "internalcancelinvoice"],
            model_class=Task,
        )
        return {
            "SEQGLOBAL": GlobalSequence(
                db_key=SequenceNumber.SEQUENCE_INTERNALINVOICE_GLOBAL,
                init_value_config_key="global_internalinvoice_sequence_init_value",
                **seq_kwargs,
            ),
            "SEQYEAR": YearSequence(
                db_key=SequenceNumber.SEQUENCE_INTERNALINVOICE_YEAR,
                init_value_config_key="year_internalinvoice_sequence_init_value",
                init_date_config_key="year_internalinvoice_sequence_init_date",
                **seq_kwargs,
            ),
            "SEQMONTH": MonthSequence(
                db_key=SequenceNumber.SEQUENCE_INTERNALINVOICE_MONTH,
                init_value_config_key="month_internalinvoice_sequence_init_value",
                init_date_config_key="month_internalinvoice_sequence_init_date",
                **seq_kwargs,
            ),
            "SEQMONTHANA": MonthCompanySequence(
                db_key=SequenceNumber.SEQUENCE_INTERNALINVOICE_MONTH_COMPANY,
                **seq_kwargs,
            ),
        }

    @classmethod
    def is_already_used(cls, request, node_id, official_number) -> bool:
        """
        Vérifie si le numéro est déjà utilisé pour une autre facture interne
        """
        # NB : On accède à l'engine pour effectuer notre requête en dehors de la
        # transaction : cf https://framagit.org/caerp/caerp/-/issues/2811
        engine = request.dbsession.connection().engine

        from caerp.models.task import Task

        sql = select(func.count(Task.id)).where(
            Task.official_number == official_number,
            Task.type_.in_(("internalinvoice", "internalcancelinvoice")),
            Task.legacy_number == False,
            Task.id != node_id,
        )

        query = engine.execute(sql)
        return query.scalar() > 0
