from importlib.abc import Traversable
import os

from caerp.views import caerp_add_route
from caerp.views.user.routes import USER_ITEM_URL
from caerp.views.business.routes import BUSINESS_ITEM_ROUTE


TRAINER_LIST_URL = "/trainers"
TRAINER_URL = "/trainerdatas"

USER_TRAINER_URL = os.path.join(USER_ITEM_URL, "trainerdatas")
USER_TRAINER_ADD_URL = os.path.join(USER_TRAINER_URL, "add")
USER_TRAINER_EDIT_URL = os.path.join(USER_TRAINER_URL, "edit")
USER_TRAINER_DELETE_URL = os.path.join(USER_TRAINER_URL, "delete")
USER_TRAINER_FILE_URL = os.path.join(USER_TRAINER_URL, "filelist")
USER_TRAINER_FILE_EDIT_URL = os.path.join(USER_TRAINER_FILE_URL, "{id2}")
TRAINING_DASHBOARD_URL = "/companies/{id}/trainings"

BUSINESS_BPF_DATA_LIST_URL = os.path.join(BUSINESS_ITEM_ROUTE, "bpf")
BUSINESS_BPF_DATA_FORM_URL = os.path.join(BUSINESS_ITEM_ROUTE, "bpf/{year}")
BUSINESS_BPF_DATA_DELETE_URL = os.path.join(BUSINESS_ITEM_ROUTE, "bpf/{year}/delete")


def includeme(config):
    config.add_route(TRAINER_LIST_URL, TRAINER_LIST_URL)
    config.add_route(TRAINER_URL, TRAINER_URL)

    for route in (
        USER_TRAINER_URL,
        USER_TRAINER_ADD_URL,
        USER_TRAINER_EDIT_URL,
        USER_TRAINER_DELETE_URL,
        USER_TRAINER_FILE_URL,
    ):
        config.add_route(route, route, traverse="/users/{id}")

    config.add_route(
        TRAINING_DASHBOARD_URL, TRAINING_DASHBOARD_URL, traverse="/companies/{id}"
    )

    for url in (
        BUSINESS_BPF_DATA_FORM_URL,
        BUSINESS_BPF_DATA_LIST_URL,
        BUSINESS_BPF_DATA_DELETE_URL,
    ):
        config.add_route(url, url, traverse="/businesses/{id}")

    caerp_add_route(config, USER_TRAINER_FILE_EDIT_URL, traverse="/files/{id2}")
