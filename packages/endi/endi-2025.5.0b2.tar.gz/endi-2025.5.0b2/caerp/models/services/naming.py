from caerp.models.node import Node
from caerp.models.project.naming import LabelOverride


_DEFAULT_LABELS = {
    "signed_agreement": "Bon pour accord",
}
_DEFAULT_LABELS.update(Node.NODE_LABELS)


class NamingService:
    """
    Handles naming overrides per business type

    Names sources are (specific to general) :
    - from Task.frozen_settings attribute (on Task models)
    - from db (LabelOverride)
    - default hardcoded labels
    """

    # Those we will be exposed to admin in settings admin
    SUPPORTED_LABEL_KEYS = [
        "estimation",
        "invoice",
        "cancelinvoice",
        "internalinvoice",
        "internalcancelinvoice",
        "internalestimation",
        "signed_agreement",
    ]
    DEFAULT_LABELS = {k: _DEFAULT_LABELS[k] for k in SUPPORTED_LABEL_KEYS}

    @classmethod
    def get_default_label(cls, label_key):
        try:
            return cls.DEFAULT_LABELS[label_key]
        except KeyError:
            raise ValueError(f"The label_key {label_key} is not supported")

    @classmethod
    def get_label_for_business_type_id(
        cls,
        label_key: str,
        business_type_id: int,
    ) -> str:
        """
        :returns: label from LabelOverride if any, default label else.
        """
        label_override = (
            LabelOverride.query()
            .filter_by(
                business_type_id=business_type_id,
                label_key=label_key,
            )
            .first()
        )
        if label_override is None:
            return cls.get_default_label(label_key)
        else:
            return label_override.label_value

    @classmethod
    def get_labels_for_business_type_id(cls, business_type_id: int) -> dict:
        """
        Return labels set for a given business_id, either
        overriden or default.
        """
        labels_dict = cls.DEFAULT_LABELS.copy()

        query = LabelOverride.query().filter_by(
            business_type_id=business_type_id,
        )
        for label_override in query:
            labels_dict[label_override.label_key] = label_override.label_value

        return dict(label_overrides=labels_dict)

    @classmethod
    def get_label_for_context(
        cls,
        label_key: str,
        context: Node,
    ) -> str:
        """
        Gets the label according to a given context,

        Use the more specific source available.
        """

        from caerp.models.project import Project
        from caerp.models.task import Task  # avoid circular dep.
        from caerp.models.project.business import Business

        frozen_settings = {}
        business_type_id = None

        if isinstance(context, Task):
            business_type_id = context.business_type_id
        elif isinstance(context, Business):
            business_type_id = context.business_type_id
        elif isinstance(context, Project):
            extra_business_types = context.business_types
            if len(extra_business_types) == 0:
                business_type_id = context.project_type.get_default_business_type().id
        try:
            return frozen_settings["label_overrides"][label_key]
        except KeyError:
            return cls.get_label_for_business_type_id(
                label_key,
                business_type_id,
            )
