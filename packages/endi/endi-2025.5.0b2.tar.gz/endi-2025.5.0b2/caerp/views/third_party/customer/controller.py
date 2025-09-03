from caerp.utils.compat import Iterable
import logging
import typing

import colander
import colanderalchemy
from sqlalchemy import func, desc

from caerp.models.third_party.customer import Customer
from caerp.models.config import Config
from caerp.models.project.project import ProjectCustomer
from caerp.forms.third_party.customer import (
    get_company_customer_schema,
    get_individual_customer_schema,
    get_internal_customer_schema,
)
from caerp.utils.controller import BaseAddEditController, RelatedAttrManager

logger = logging.getLogger(__name__)


class CustomerRelatedAttrManager(RelatedAttrManager):
    def _add_related_project_ids(self, customer, customer_dict):
        result = self.dbsession.query(ProjectCustomer.c.project_id).filter(
            ProjectCustomer.c.customer_id == customer.id
        )
        customer_dict["project_ids"] = [p[0] for p in result]
        return customer_dict


class CustomerAddEditController(BaseAddEditController):
    related_manager_factory = CustomerRelatedAttrManager

    def get_company_schema(self) -> colanderalchemy.SQLAlchemySchemaNode:
        return get_company_customer_schema()

    def get_individual_schema(self) -> colanderalchemy.SQLAlchemySchemaNode:
        return get_individual_customer_schema()

    def _internal_active(self) -> bool:
        return Config.get_value("internal_invoicing_active", default=True, type_=bool)

    def get_internal_schema(self) -> colanderalchemy.SQLAlchemySchemaNode:
        return get_internal_customer_schema(edit=self.edit)

    def get_customer_type(self, submitted: dict) -> str:
        if self.edit:
            customer_type = self.context.type
        else:
            customer_type = submitted.get("type", "company")
            # On s'assure qu'on ne peut pas ajouter des clients internes
            # si l'option est désactivée
            if customer_type == "internal" and not self._internal_active():
                customer_type = "company"
        return customer_type

    def get_schema(self, submitted: dict) -> colander.Schema:
        """
        Build and cache the current schema
        """
        if "schema" not in self._cache:
            customer_type = self.get_customer_type(submitted)
            logger.debug(f"It's a {customer_type} call")
            method = f"get_{customer_type}_schema"
            self._cache["schema"] = getattr(self, method)()
        return self._cache["schema"]

    def get_schemas(self) -> typing.Dict[str, colander.Schema]:
        """
        Renvoie les schémas disponibles

        :return: Liste des schémas colander
        :rtype: typing.Dict[str, colander.Schema]
        """
        result = {
            "individual": self.get_individual_schema().bind(request=self.request),
            "company": self.get_company_schema().bind(request=self.request),
        }
        if self._internal_active():
            result["internal"] = self.get_internal_schema().bind(request=self.request)
        return result

    def after_add_edit(
        self, customer: Customer, edit: bool, attributes: dict
    ) -> Customer:
        """
        Post formatting Hook

        :param customer: Current customer (added/edited)
        :type customer: Customer

        :param edit: Is it an edit form ?
        :type edit: bool

        :param attributes: Validated attributes sent to this view
        :type attributes: dict

        :return: The modified customer
        :rtype: Customer
        """
        if not edit:
            customer.company = self.context
            customer.type = self.get_customer_type(attributes)
        return customer

    def get_available_types(self) -> Iterable[typing.Dict]:
        """
        Renvoie les types de client que l'on peut créer
        """
        types = [
            {"value": "individual", "label": "Personne physique"},
            {"value": "company", "label": "Personne morale"},
        ]
        if self._internal_active():
            types.append({"value": "internal", "label": "Enseigne de la CAE"})
        return types

    def get_default_type(self) -> str:
        """Find the default customer type to provide by default

        :return: The name of the type
        :rtype: str
        """
        result = "company"
        if not isinstance(self.context, Customer):
            # On cherche le type de client que cette enseigne utilise
            query_result = (
                self.request.dbsession.query(
                    Customer.type, func.count(Customer.id).label("count")
                )
                .filter(
                    Customer.type.in_(["individual", "company"]),
                    Customer.company_id == self.context.id,
                )
                .group_by("type")
                .order_by(desc("count"))
                .first()
            )

            if query_result is not None:
                result = query_result[0]
        return result
