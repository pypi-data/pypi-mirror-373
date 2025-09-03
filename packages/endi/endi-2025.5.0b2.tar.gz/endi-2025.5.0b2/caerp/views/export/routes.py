BPF_EXPORT_ODS_URL = "/export/training/bpf.ods"
EXPORT_LOG_LIST_ROUTE = "/export/export_log"


def includeme(config):
    for route in [
        BPF_EXPORT_ODS_URL,
        EXPORT_LOG_LIST_ROUTE,
    ]:
        config.add_route(route, route)
