import logging


from caerp.models.project.business import Business
from caerp.models.project.services.business_status import BusinessStatusService
from .document_events import StatusChangedEvent


logger = logging.getLogger(__name__)


class BpfDataModified:
    def __init__(self, request, business_id):
        self.request = request
        self.business_id = business_id


def on_bpf_data_changed(event):
    if isinstance(event, BpfDataModified):
        business = Business.get(event.business_id)
        if business:
            BusinessStatusService.update_bpf_indicator(business)
    elif isinstance(event, StatusChangedEvent):
        if event.status == "valid":
            if event.node_type in ("invoice", "cancelinvoice"):
                business = event.node.business
                if business.business_type.bpf_related:
                    BusinessStatusService.update_bpf_indicator(business)


def includeme(config):
    config.add_subscriber(on_bpf_data_changed, BpfDataModified)
    config.add_subscriber(on_bpf_data_changed, StatusChangedEvent)
