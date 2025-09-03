from sqlalchemy import or_


class BusinessLinkedServiceMixin:
    """
    Methods to be added on a BusinessLinkedModelMixin related service

    The inheriting service must be targeting a model that inherits
    BusinessLinkedModelMixin.
    """

    @staticmethod
    def linkable(cls, business):
        """Return the objects available for linking with a given business

        :param parent_model class:
        :param parent_model_company_id_field: the model class attribute holding
          company link

        :rtype query of BaseExpenseLine:
        """
        customer = business.get_customer()
        query = (
            cls.query()
            .join(cls.parent_model)
            .filter(
                cls.parent_model.company_id == business.get_company_id(),
                cls.business_id == None,  # noqa
                or_(
                    cls.project_id == business.project_id,
                    cls.project_id == None,
                ),
                or_(
                    cls.customer_id == customer.id,
                    cls.customer_id == None,
                ),
            )
        )
        return query

    @staticmethod
    def query_linked_to(cls, target: "BusinessMetricsMixin"):
        from caerp.models.project.business import Business
        from caerp.models.project import Project

        query = cls.query().join(cls.parent_model)
        fk_filter_column = getattr(cls, target.fk_filter_field)

        query = query.filter(fk_filter_column == target.id)
        return query
