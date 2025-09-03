from caerp_base.models.base import DBSESSION


class TaskMentionService:
    @classmethod
    def populate(cls, task):
        from caerp.models.project import BusinessType

        with DBSESSION.no_autoflush:
            task.mandatory_mentions = BusinessType.get_mandatory_mentions(
                task.business_type_id,
                task.type_,
            )
