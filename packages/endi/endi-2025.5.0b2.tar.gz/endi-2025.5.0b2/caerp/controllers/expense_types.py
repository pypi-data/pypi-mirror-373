import itertools
from sqlalchemy import select, or_, and_
from caerp.models.expense.types import ExpenseType, ExpenseKmType
from caerp.models.user.user import User


class ExpenseTypeQueryService:
    @classmethod
    def _type_ids_from_lines(cls, *args):
        """
        Collects the ids of the ExpenseTypes linked to the elements of provided
        lists

        param *args: one or several iterables of elements having a
            `type_id` attr
        return: list of ExpenseTypes id (deduplicated)
        """
        return list({obj.type_id for obj in itertools.chain(*args)})

    @classmethod
    def purchase_options(cls, internal=False, *lines):
        """
        Return a query to retrieve the purchase options including those used in the
        all the lines lists
        """
        query = (
            select(ExpenseType)
            .where(ExpenseType.type == "expense")
            .where(
                or_(
                    and_(
                        ExpenseType.active == True,  # noqa
                        or_(
                            ExpenseType.category == ExpenseType.PURCHASE_CATEGORY,
                            ExpenseType.category == None,
                        ),
                    ),
                    ExpenseType.id.in_(cls._type_ids_from_lines(*lines)),
                )
            )
        )
        if internal:
            query = query.where(ExpenseType.internal == True)
        else:
            query = query.where(
                or_(
                    ExpenseType.internal != True,
                    ExpenseType.internal == None,
                )
            )
        return query.order_by(ExpenseType.order)

    @classmethod
    def expense_options(cls, *lines):
        """
        Return a query collecting types related to the declaration of
        Expenses or types present in the given lines
        """
        query = (
            select(ExpenseType)
            .where(
                ExpenseType.type.in_(["expense", "expensetel"]),
            )
            .where(
                or_(
                    and_(
                        ExpenseType.active == True,  # noqa
                        or_(
                            ExpenseType.category == ExpenseType.EXPENSE_CATEGORY,
                            ExpenseType.category == None,
                        ),
                    ),
                    ExpenseType.id.in_(cls._type_ids_from_lines(*lines)),
                )
            )
        )
        return query.order_by(ExpenseType.order)

    @classmethod
    def _is_user_vehicle_query(cls, user, year):
        """
        Applies the optional per-user restriction on ExpenseKmType

        :param user User: the user who declared this vehicle
        :param year: the year the vehicle is declared for
        :return: the allowed ExpenseTypeKm
        :rtype: list of ExpenseTypeKm
        """

        query = select(ExpenseKmType.id).where(
            ExpenseKmType.active == True,
            ExpenseKmType.year == year,
        )

        if user.vehicle and "-" in user.vehicle:
            label, code = user.vehicle.rsplit("-", 1)
            query = query.where(
                ExpenseKmType.label == label, ExpenseKmType.code == code
            )

        return query

    @classmethod
    def expensekm_options(cls, user: User, year: int, *lines):
        """
        Collect ExpenseKmType options for the given year,
        matching the given user's vehicle or used in the given ExpenseKmLine
        """
        filtered_active_types_subquery = cls._is_user_vehicle_query(user, year)
        used_types_subquery = cls._type_ids_from_lines(*lines)
        query = select(ExpenseKmType).where(
            or_(
                ExpenseKmType.id.in_(filtered_active_types_subquery),
                ExpenseKmType.id.in_(used_types_subquery),
            )
        )
        return query
