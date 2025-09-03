from typing import Optional

from sqlalchemy import func


class WorkUnitService:
    @staticmethod
    def get_by_label(
        cls: "WorkUnit", label: str, case_sensitive: bool
    ) -> Optional["WorkUnit"]:
        """Get a Unity by its label

        Match may be case-insensitive. If a case-sensitive match exist,
        it will always be preferred.
        """
        exact_match = cls.query().filter(cls.label == label).first()

        if case_sensitive or exact_match:
            return exact_match

        else:
            insensitive_match = (
                cls.query().filter(func.lower(cls.label) == func.lower(label)).first()
            )
            return insensitive_match
