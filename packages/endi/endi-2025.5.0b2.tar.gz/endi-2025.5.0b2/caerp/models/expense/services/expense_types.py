from sqlalchemy import (
    func,
)

from caerp_base.models.base import (
    DBSESSION,
)


class ExpenseTypeService:
    """Handle complex queries en ExpenseTypes"""

    @staticmethod
    def get_by_label(cls, label: str, case_sensitive: bool = False):
        query = cls.query().filter(cls.active == True)  # noqa: E712
        exact_match = query.filter(cls.label == label).one_or_none()

        if exact_match or case_sensitive:
            return exact_match
        else:
            insensitive_match = query.filter(
                func.lower(cls.label) == func.lower(label)
            ).one_or_none()
            return insensitive_match

    @classmethod
    def allowed_driver(cls, user, year):
        """
        Applies the optional per-user restriction on ExpenseKmType

        :param user User: the user who declared this vehicle
        :param year: the year the vehicle is declared for
        :return: the allowed ExpenseTypeKm
        :rtype: list of ExpenseTypeKm
        """
        from caerp.models.expense.types import ExpenseKmType

        query = DBSESSION().query(ExpenseKmType)
        query = query.filter_by(active=True)
        query = query.filter_by(year=year)

        if user.vehicle and "-" in user.vehicle:
            label, code = user.vehicle.rsplit("-", 1)
            query = query.filter_by(label=label).filter_by(code=code)

        return query

    @classmethod
    def find_internal(cls, etype_class):
        return etype_class.query().filter_by(internal=True).all()
