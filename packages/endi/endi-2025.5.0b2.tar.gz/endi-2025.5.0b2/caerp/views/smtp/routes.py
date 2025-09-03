import os

from caerp.views import caerp_add_route
from caerp.views.company.routes import ITEM_ROUTE as COMPANY_ITEM_ROUTE

COMPANY_SMTP_SETTINGS_ROUTE = os.path.join(COMPANY_ITEM_ROUTE, "smtp_settings")
API_BASE_ROUTE = "/api/v1/smtp_settings"
API_ITEM_ROUTE = os.path.join(API_BASE_ROUTE, "{id}")
TEST_MAIL_ROUTE = "/api/v1/smtp_settings/test_mail"

API_COMPANY_SMTP_ROUTE = "/api/v1/companies/{id}/smtp_settings"
API_COMPANY_TESTMAIL_ROUTE = os.path.join(API_COMPANY_SMTP_ROUTE, "test_mail")

SEND_MAIL_ROUTE = "/nodes/{id}/send_by_email"


def includeme(config):
    config.add_route(API_BASE_ROUTE, API_BASE_ROUTE)

    caerp_add_route(config, API_ITEM_ROUTE, traverse="/smtp_settings/{id}")
    caerp_add_route(config, TEST_MAIL_ROUTE)

    caerp_add_route(config, COMPANY_SMTP_SETTINGS_ROUTE, traverse="/companies/{id}")
    caerp_add_route(config, API_COMPANY_SMTP_ROUTE, traverse="/companies/{id}")
    caerp_add_route(config, API_COMPANY_TESTMAIL_ROUTE, traverse="/companies/{id}")

    caerp_add_route(config, SEND_MAIL_ROUTE, traverse="/nodes/{id}")
