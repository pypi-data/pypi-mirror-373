import logging

from caerp_base.models.base import DBSESSION

from caerp.utils.datetimes import get_current_year

logger = logging.getLogger(__name__)


class BusinessStatusService:
    """
    Service class providing Business status management tools
    """

    @classmethod
    def populate_indicators(cls, business):
        """
        Generate base indicators for a given business

        :param obj business: The Business instance
        :returns: The Business instance
        :rtype: obj
        """
        cls.get_or_create_invoice_indicator(business)
        if business.business_type.bpf_related:
            cls.update_bpf_indicator(business)
        return business

    @classmethod
    def get_or_create_bpf_indicator(cls, business):
        if not business.business_type.bpf_related:
            return None
        from caerp.models.indicators import CustomBusinessIndicator

        indicator = (
            CustomBusinessIndicator.query()
            .filter_by(
                name="bpf_filled",
                business=business,
            )
            .first()
        )
        if indicator is None:
            indicator = CustomBusinessIndicator(
                name="bpf_filled",
                label="Données BPF",
            )
            DBSESSION().add(indicator)
            business.indicators.append(indicator)
            DBSESSION().merge(business)
        return indicator

    @classmethod
    def update_bpf_indicator(cls, business, current_year=None):
        if not business.business_type.bpf_related:
            return None
        if current_year is None:
            current_year = get_current_year()

        invoicing_years = set(business.invoicing_years())
        bpf_years = set(i.financial_year for i in business.bpf_datas)

        missing_years = invoicing_years - bpf_years
        indicator = cls.get_or_create_bpf_indicator(business)
        has_invoices = len(invoicing_years) > 0
        has_bpf_data = len(bpf_years) > 0
        miss_some_years = len(missing_years) > 0

        if not has_invoices and not has_bpf_data:
            # At the moment, bpf cannot be filled without invoice
            # let's not block the user
            indicator.status = indicator.WARNING_STATUS
            indicator.label = "Données BPF non remplies"
        elif has_invoices and miss_some_years:
            indicator.label = "Données BPF non remplies pour {}".format(
                ", ".join(str(i) for i in missing_years),
            )
            previous_year = current_year - 1
            if previous_year in missing_years:
                # year is closed, time to fill bpf data before April
                indicator.status = indicator.DANGER_STATUS
            else:
                indicator.status = indicator.WARNING_STATUS
        else:
            indicator.label = "Données BPF"
            indicator.status = indicator.SUCCESS_STATUS
            logger.debug("Indicator set to success")
        return indicator

    @classmethod
    def get_or_create_invoice_indicator(cls, business):
        from caerp.models.indicators import CustomBusinessIndicator

        indicator = (
            CustomBusinessIndicator.query()
            .filter_by(business_id=business.id)
            .filter_by(name="invoiced")
            .first()
        )

        if indicator is None:
            indicator = CustomBusinessIndicator(
                name="invoiced",
                label="Facturation",
            )
            DBSESSION().add(indicator)
            DBSESSION().flush()
            business.indicators.append(indicator)
            DBSESSION().merge(business)
        return indicator

    @classmethod
    def update_classic_invoicing_indicator(cls, business):
        """
        Update the invoicing status indicator of the given business

        :param obj business: The Business instance
        :returns: The Business instance
        :rtype: obj
        """
        invoicing_status = True
        if business.amount_to_invoice() >= 0:
            for deadline in business.payment_deadlines:
                if not deadline.invoiced:
                    invoicing_status = False
                    break

        indicator = None
        if invoicing_status is True:
            indicator = cls.get_or_create_invoice_indicator(business)
            indicator.status = indicator.SUCCESS_STATUS
            DBSESSION().merge(indicator)
        else:
            indicator = cls.get_or_create_invoice_indicator(business)
            indicator.status = indicator.DANGER_STATUS
            DBSESSION().merge(indicator)

        return indicator

    @classmethod
    def update_invoicing_status(cls, business, invoice=None, cancelinvoice=None):
        """
        Update the invoicing status of this business

        If classic mode is used : check deadlines associated to this invoice
        If progress mode is used: check progress invoicing statuses

        :param obj business: The Business instance
        :param obj invoice: The validated Invoice instance
        :returns: The Business instance
        :rtype: obj
        """
        logger.debug(
            "Update invoicing status {} {} {}".format(business, invoice, cancelinvoice)
        )
        if invoice:
            deadline = business.find_deadline_from_invoice(invoice)
            if deadline is not None and invoice.status == "valid":
                logger.debug(" + deadline {} is now invoiced".format(deadline.id))
                deadline.invoiced = True
                DBSESSION().merge(deadline)
        elif cancelinvoice:
            deadline = business.find_deadline_from_invoice(cancelinvoice.invoice)
            if deadline is not None:
                logger.debug(
                    " + deadline {} is not invocied anymore".format(deadline.id)
                )
                if cancelinvoice.status == "valid":
                    deadline.invoiced = False
                    deadline.invoice_id = None
                    logger.debug(
                        " + deadline {} is detached from invoice".format(deadline.id)
                    )
                DBSESSION().merge(deadline)

        if business.invoicing_mode == business.PROGRESS_MODE:
            invoicing_status = business.progress_invoicing_is_complete()
            indicator = cls.get_or_create_invoice_indicator(business)
            if invoicing_status is True:
                indicator.status = indicator.SUCCESS_STATUS
            else:
                indicator.status = indicator.DANGER_STATUS
            DBSESSION().merge(indicator)
        elif business.invoicing_mode == business.CLASSIC_MODE:
            cls.update_classic_invoicing_indicator(business)

    @classmethod
    def _compute_status(cls, business):
        """
        Get the actual status of a business collecting datas from its
        indicators

        :param obj business: The Business instance
        :returns: The new status
        :rtype: str
        """
        from caerp.models.indicators import CustomBusinessIndicator, Indicator

        # file requirements inclus également les fichiers requis dans les devis/factures
        freq_status = business.get_file_requirements_status()

        query = (
            DBSESSION()
            .query(CustomBusinessIndicator.status)
            .filter(CustomBusinessIndicator.business_id == business.id)
            .distinct()
        )
        result = [a[0] for a in query.all()]

        result.append(freq_status)

        return Indicator.find_lowest_status(result)

    @classmethod
    def update_status(cls, business):
        """
        Update the business status if needed

        :param obj business: The Business instance
        :returns: The Business instance
        :rtype: obj
        """
        status = cls._compute_status(business)
        if status != business.status:
            business.status = status
            DBSESSION().merge(business)
        return business

    @classmethod
    def on_task_status_change(cls, request, business, task, status):
        from caerp.models.task import CancelInvoice, Estimation, Invoice

        logger.debug("Business on task status change")
        logger.debug(business)
        logger.debug(task)
        logger.debug(status)

        if status == "valid":
            if isinstance(task, Invoice):
                cls.update_invoicing_status(business, invoice=task)

            elif isinstance(task, Estimation):
                cls.update_invoicing_status(business)

            elif isinstance(task, CancelInvoice):
                cls.update_invoicing_status(business, cancelinvoice=task)

            cls.update_status(business)

        if status == "signed_status":
            business.on_estimation_signed_status_change(request)
