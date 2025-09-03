"""
Main file for our pyramid application
"""

import locale

# flake8: noqa: E402
import logging

from packaging.version import Version

from caerp.utils.sys_environment import (
    package_name,  # Imported here for easy import in the app
)
from caerp.utils.sys_environment import collect_envvars_as_settings, package_version

locale.setlocale(locale.LC_ALL, "fr_FR.UTF-8")
locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")

from caerp_base.models.initialize import configure_warnings, initialize_sql
from pyramid.config import Configurator
from pyramid_beaker import set_cache_regions_from_settings
from sqlalchemy import engine_from_config

from caerp.resources import lib_caerp as fanstatic_caerp_library
from caerp.utils.filedepot import configure_filedepot
from caerp.utils.renderer import customize_renderers
from caerp.utils.rest.apiv1 import add_rest_service
from caerp.utils.session import get_session_factory

logger = logging.getLogger(__name__)
_called_from_test = False


CAERP_MANDATORY_MODULES = (
    "caerp.views.auth",
    "caerp.views.business",
    "caerp.views.company",
    "caerp.views.third_party.customer",
    "caerp.views.estimations",
    "caerp.views.expenses",
    "caerp.views.files",
    "caerp.views.indicators",
    "caerp.views.invoices",
    "caerp.views.job",
    "caerp.views.manage",
    "caerp.views.payment",
    "caerp.views.sale_product",
    "caerp.views.project",
    "caerp.views.index",
    "caerp.views.export.routes",
    "caerp.views.export.invoice",
    "caerp.views.export.expense",
    "caerp.views.export.payment",
    "caerp.views.export.expense_payment",
    "caerp.views.static",
    "caerp.views.user",
    "caerp.views.rest_consts",
    "caerp.views.release_notes",
    "caerp.views.notification",
    "caerp.views.sepa",
    "caerp.views.smtp",
)

CAERP_OTHER_MODULES = (
    "caerp.views.accompagnement",
    "caerp.views.accounting",
    "caerp.views.commercial",
    "caerp.views.competence",
    "caerp.views.csv_import",
    "caerp.views.holiday",
    "caerp.views.price_study",
    "caerp.views.progress_invoicing",
    "caerp.views.export.bpf",
    "caerp.views.export.supplier_invoice",
    "caerp.views.export.supplier_payment",
    "caerp.views.internal_invoicing",
    "caerp.views.management",
    "caerp.views.statistics",
    "caerp.views.dataqueries",
    "caerp.views.supply.orders",
    "caerp.views.supply.invoices",
    "caerp.views.third_party.supplier",
    "caerp.views.training",
    "caerp.views.treasury_files",
    "caerp.views.userdatas",
    "caerp.views.validation",
    "caerp.views.workshops",
    "caerp.views.custom_documentation",
)

CAERP_LAYOUTS_MODULES = (
    "caerp.default_layouts",
    "caerp.views.user.layout",
)

CAERP_PANELS_MODULES = (
    "caerp.panels.activity",
    "caerp.panels.business",
    "caerp.panels.company_index",
    "caerp.panels.expense",
    "caerp.panels.files",
    "caerp.panels.form",
    "caerp.panels.indicators",
    "caerp.panels.manage",
    "caerp.panels.menu",
    "caerp.panels.navigation",
    "caerp.panels.project",
    "caerp.panels.sidebar",
    "caerp.panels.supply",
    "caerp.panels.third_party",
    "caerp.panels.tabs",
    "caerp.panels.task",
    "caerp.panels.widgets",
    "caerp.panels.workshop",
)

CAERP_EVENT_MODULES = (
    "caerp.events.model_events",
    "caerp.events.status_changed",
    "caerp.events.files",
    "caerp.events.indicators",
    "caerp.events.business",
)
CAERP_REQUEST_SUBSCRIBERS = (
    "caerp.subscribers.new_request",
    "caerp.subscribers.before_render",
)

CAERP_SERVICE_FACTORIES = (
    (
        "services.treasury_invoice_producer",
        "caerp.compute.sage.InvoiceExportProducer",
        "caerp.interfaces.ITreasuryProducer",
        "caerp.models.task.Invoice",
    ),
    (
        "services.treasury_invoice_producer",
        "caerp.compute.sage.InvoiceExportProducer",
        "caerp.interfaces.ITreasuryProducer",
        "caerp.models.task.CancelInvoice",
    ),
    (
        "services.treasury_internalinvoice_producer",
        "caerp.compute.sage.InternalInvoiceExportProducer",
        "caerp.interfaces.ITreasuryProducer",
        "caerp.models.task.InternalInvoice",
    ),
    (
        "services.treasury_internalinvoice_producer",
        "caerp.compute.sage.InternalInvoiceExportProducer",
        "caerp.interfaces.ITreasuryProducer",
        "caerp.models.task.InternalCancelInvoice",
    ),
    (
        "services.treasury_invoice_writer",
        "caerp.export.sage.SageInvoiceCsvWriter",
        "caerp.interfaces.ITreasuryInvoiceWriter",
        None,
    ),
    (
        "services.treasury_payment_producer",
        "caerp.compute.sage.PaymentExportProducer",
        "caerp.interfaces.ITreasuryProducer",
        "caerp.models.task.Payment",
    ),
    (
        "services.treasury_internalpayment_producer",
        "caerp.compute.sage.InternalPaymentExportProducer",
        "caerp.interfaces.ITreasuryProducer",
        "caerp.models.task.InternalPayment",
    ),
    (
        "services.treasury_payment_writer",
        "caerp.export.sage.SagePaymentCsvWriter",
        "caerp.interfaces.ITreasuryPaymentWriter",
        None,
    ),
    (
        "services.treasury_expense_producer",
        "caerp.compute.sage.ExpenseExportProducer",
        "caerp.interfaces.ITreasuryProducer",
        "caerp.models.expense.sheet.ExpenseSheet",
    ),
    (
        "services.treasury_expense_writer",
        "caerp.export.sage.SageExpenseCsvWriter",
        "caerp.interfaces.ITreasuryExpenseWriter",
        None,
    ),
    (
        "services.treasury_expense_payment_producer",
        "caerp.compute.sage.ExpensePaymentExportProducer",
        "caerp.interfaces.ITreasuryProducer",
        "caerp.models.expense.payment.ExpensePayment",
    ),
    (
        "services.treasury_expense_payment_writer",
        "caerp.export.sage.SageExpensePaymentCsvWriter",
        "caerp.interfaces.ITreasuryExpensePaymentWriter",
        None,
    ),
    (
        "services.treasury_supplier_invoice_producer",
        "caerp.compute.sage.SupplierInvoiceExportProducer",
        "caerp.interfaces.ITreasuryProducer",
        "caerp.models.supply.supplier_invoice.SupplierInvoice",
    ),
    (
        "services.treasury_internalsupplier_invoice_producer",
        "caerp.compute.sage.InternalSupplierInvoiceExportProducer",
        "caerp.interfaces.ITreasuryProducer",
        "caerp.models.supply.internalsupplier_invoice.InternalSupplierInvoice",
    ),
    (
        "services.treasury_supplier_invoice_writer",
        "caerp.export.sage.SageSupplierInvoiceCsvWriter",
        "caerp.interfaces.ITreasurySupplierInvoiceWriter",
        None,
    ),
    (
        "services.treasury_supplier_payment_producer",
        "caerp.compute.sage.SupplierPaymentExportProducer",
        "caerp.interfaces.ITreasuryProducer",
        "caerp.models.supply.SupplierInvoiceSupplierPayment",
    ),
    (
        "services.treasury_supplier_payment_user_producer",
        "caerp.compute.sage.SupplierUserPaymentExportProducer",
        "caerp.interfaces.ITreasuryProducer",
        "caerp.models.supply.SupplierInvoiceUserPayment",
    ),
    (
        "services.treasury_internalsupplier_payment_producer",
        "caerp.compute.sage.InternalSupplierPaymentExportProducer",
        "caerp.interfaces.ITreasuryProducer",
        "caerp.models.supply.InternalSupplierInvoiceSupplierPayment",
    ),
    (
        "services.treasury_supplier_payment_writer",
        "caerp.export.sage.SageSupplierPaymentCsvWriter",
        "caerp.interfaces.ITreasurySupplierPaymentWriter",
        None,
    ),
    (
        "services.task_pdf_rendering_service",
        "caerp.views.task.pdf_rendering_service.TaskPdfFromHtmlService",
        "caerp.interfaces.ITaskPdfRenderingService",
        "caerp.models.task.Task",
    ),
    (
        "services.task_pdf_storage_service",
        "caerp.views.task.pdf_storage_service.PdfFileDepotStorageService",
        "caerp.interfaces.ITaskPdfStorageService",
        "caerp.models.task.Task",
    ),
    (
        "services.payment_record_service",
        "caerp_payment.public.PaymentService",
        "caerp.interfaces.IPaymentRecordService",
        (
            "caerp.models.task.Invoice",
            "caerp.models.task.Payment",
        ),
    ),
    (
        "services.internalpayment_record_service",
        "caerp.models.task.services.InternalPaymentRecordService",
        "caerp.interfaces.IPaymentRecordService",
        (
            "caerp.models.task.InternalInvoice",
            "caerp.models.task.InternalPayment",
        ),
    ),
    (
        "services.waiting_documents_service",
        "caerp.models.status.ValidationStatusHolderService",
        "caerp.interfaces.IValidationStatusHolderService",
        None,
    ),
    (
        "services.payment_groupper_service",
        "caerp.compute.sage.payment.PaymentExportGroupper",
        "caerp.interfaces.ITreasuryGroupper",
        "caerp.models.task.payment.BaseTaskPayment",
    ),
    (
        "services.payment_groupper_service",
        "caerp.compute.sage.invoice.InvoiceExportGroupper",
        "caerp.interfaces.ITreasuryGroupper",
        "caerp.models.task.invoice.Invoice",
    ),
    (
        "services.sign_pdf_service",
        None,
        "caerp.interfaces.ISignPDFService",
        None,
    ),
)
# (key, callable, interface, context, params)
# key : The setting key
# callable : The callable returning the object (global to the wsgi context)
# interface : The interface it implements
# context : The context it should be used for
# params : tuple of params passed to the callable as *params
CAERP_SERVICES = (
    # Statut de validation des Task
    (
        "services.validation_state_manager.invoice",
        "caerp.controllers.state_managers.validation.get_default_validation_state_manager",
        "caerp.interfaces.IValidationStateManager",
        "caerp.models.task.invoice.Invoice",
        ("invoice",),
    ),
    (
        "services.validation_state_manager.cancelinvoice",
        "caerp.controllers.state_managers.validation.get_default_validation_state_manager",
        "caerp.interfaces.IValidationStateManager",
        "caerp.models.task.invoice.CancelInvoice",
        ("cancelinvoice",),
    ),
    (
        "services.validation_state_manager.estimation",
        "caerp.controllers.state_managers.validation.get_default_validation_state_manager",
        "caerp.interfaces.IValidationStateManager",
        "caerp.models.task.estimation.Estimation",
        ("estimation",),
    ),
    (
        "services.validation_state_manager.internalinvoice",
        "caerp.controllers.state_managers.validation.get_default_validation_state_manager",
        "caerp.interfaces.IValidationStateManager",
        "caerp.models.task.internalinvoice.InternalInvoice",
        ("internalinvoice",),
    ),
    (
        "services.validation_state_manager.internalcancelinvoice",
        "caerp.controllers.state_managers.validation.get_default_validation_state_manager",
        "caerp.interfaces.IValidationStateManager",
        "caerp.models.task.internalinvoice.InternalCancelInvoice",
        ("internalcancelinvoice",),
    ),
    (
        "services.validation_state_manager.internalestimation",
        "caerp.controllers.state_managers.validation.get_default_validation_state_manager",
        "caerp.interfaces.IValidationStateManager",
        "caerp.models.task.internalestimation.InternalEstimation",
        ("internalestimation",),
    ),
    # Status de validation des NDDs
    (
        "services.validation_state_manager.expense",
        "caerp.controllers.state_managers.validation.get_default_validation_state_manager",
        "caerp.interfaces.IValidationStateManager",
        "caerp.models.expense.sheet.ExpenseSheet",
        ("expense",),
    ),
    # Statut de validation des factures/avoirs fournisseurs
    (
        "services.validation_state_manager.supplier_order",
        "caerp.controllers.state_managers.validation.get_default_validation_state_manager",
        "caerp.interfaces.IValidationStateManager",
        "caerp.models.supply.supplier_order.SupplierOrder",
        ("supplier_order",),
    ),
    (
        "services.validation_state_manager.supplier_invoice",
        "caerp.controllers.state_managers.validation.get_default_validation_state_manager",
        "caerp.interfaces.IValidationStateManager",
        "caerp.models.supply.supplier_invoice.SupplierInvoice",
        ("supplier_invoice",),
    ),
    (
        "services.validation_state_manager.internalsupplier_order",
        "caerp.controllers.state_managers.validation.get_default_validation_state_manager",
        "caerp.interfaces.IValidationStateManager",
        "caerp.models.supply.internalsupplier_order.InternalSupplierOrder",
        ("internalsupplier_order",),
    ),
    (
        "services.validation_state_manager.internalsupplier_invoice",
        "caerp.controllers.state_managers.validation.get_default_validation_state_manager",
        "caerp.interfaces.IValidationStateManager",
        "caerp.models.supply.internalsupplier_invoice.InternalSupplierInvoice",
        ("internalsupplier_invoice",),
    ),
    # Statut des jusitificatifs de NDD
    (
        "services.justified_state_manager.expense",
        "caerp.controllers.state_managers.justified.get_default_justified_state_manager",
        "caerp.interfaces.IJustifiedStateManager",
        [
            "caerp.models.expense.sheet.ExpenseSheet",
            "caerp.models.expense.sheet.ExpenseLine",
        ],
        ("expense",),
    ),
    # Statut de signature des Devis
    (
        "services.signed_state_manager.estimation",
        "caerp.controllers.state_managers.signed.get_default_signed_status_manager",
        "caerp.interfaces.ISignedStateManager",
        "caerp.models.task.Estimation",
        ("estimation",),
    ),
    # Statut de paiement des factures/factures frns / NDDs
    (
        "services.payment_state_manager.invoice",
        "caerp.controllers.state_managers.payment.get_default_payment_state_manager",
        "caerp.interfaces.IPaymentStateManager",
        "caerp.models.task.invoice.Invoice",
        ("invoice",),
    ),
    (
        "services.payment_state_manager.expense",
        "caerp.controllers.state_managers.payment.get_default_payment_state_manager",
        "caerp.interfaces.IPaymentStateManager",
        "caerp.models.expense.sheet.ExpenseSheet",
        ("expense",),
    ),
    (
        "services.payment_state_manager.supplier_invoice",
        "caerp.controllers.state_managers.payment.get_default_payment_state_manager",
        "caerp.interfaces.IPaymentStateManager",
        "caerp.models.supply.SupplierInvoice",
        ("supplier_invoice",),
    ),
)


def get_groups(login, request):
    """
    return the current user's groups
    """
    import logging

    logger = logging.getLogger(__name__)
    user = request.identity
    if user is None:
        logger.debug("User is None")
        principals = None

    elif getattr(request, "principals", []):
        principals = request.principals

    else:
        logger.debug(" + Building principals")
        principals = [f"user:{user.id}"]
        for group in user.login.groups:
            principals.append("group:{0}".format(group))

        for company in user.companies:
            if company.active:
                principals.append("company:{}".format(company.id))

        request.principals = principals
        logger.debug(" -> Principals Built : caching")

    return principals


def prepare_config(**settings):
    """
    Prepare the configuration object to setup the main application elements
    """
    session_factory = get_session_factory(settings)
    set_cache_regions_from_settings(settings)

    # Evite les imports circulaires avec caerp_celery
    from caerp.utils.security import SessionSecurityPolicy

    config = Configurator(
        settings=settings,
        # authentication_policy=auth_policy,
        # authorization_policy=acl_policy,
        session_factory=session_factory,
        security_policy=SessionSecurityPolicy(),
    )
    return config


def hack_caerp_static_path(settings):
    if "caerp.fanstatic_path" in settings:
        path_name = settings.get("caerp.fanstatic_path")
        print(("Hacking fanstatic's source path with %s" % path_name))
        fanstatic_caerp_library.path = path_name


def setup_bdd(settings):
    """
    Configure the database:

        - Intialize tables
        - populate database with default values

    :param obj settings: The ConfigParser object
    :returns: The dbsession
    :rtype: obj
    """
    from caerp.models import adjust_for_engine

    engine = engine_from_config(settings, "sqlalchemy.")
    adjust_for_engine(engine)
    dbsession = initialize_sql(engine)
    return dbsession


def config_views(config):
    """
    Configure caerp views
    """
    logger.debug("Loading views")

    # On register le module views.admin car il contient des outils spécifiques
    # pour les vues administrateurs (Ajout autonomatisé d'une arborescence,
    # ajout de la directive config.add_admin_view
    # Il s'occupe également d'intégrer toutes les vues, layouts... spécifiques
    # à l'administration
    config.include("caerp.views.admin")

    config.include("caerp.views.export.log_list")

    for module in CAERP_MANDATORY_MODULES:
        config.add_module(module)

    # Ici on permet la configuration des modules complémentaires depuis le .ini
    settings = config.registry.settings
    if "caerp.modules" not in settings:
        modules = CAERP_OTHER_MODULES
    else:
        modules = settings.get("caerp.modules", "").split()

    # Commit the configuration to allow overrides of core module views/routes
    # by optional modules views/routes
    config.commit()
    for module in modules:
        config.add_module(module)


def setup_request_methods(config, dbsession):
    from caerp.models.config import get_config

    # Adding some usefull properties to the request object
    config.add_request_method(
        lambda _: dbsession(), "dbsession", property=True, reify=True
    )
    config.add_request_method(
        lambda _: get_config(), "config", property=True, reify=True
    )


def config_layouts(config):
    logger.debug("  + Adding layouts")
    for module in CAERP_LAYOUTS_MODULES:
        config.include(module)


def config_subscribers(config):
    logger.debug("  + Adding subscribers")
    for module in CAERP_REQUEST_SUBSCRIBERS:
        config.include(module)


def config_panels(config):
    logger.debug("  + Adding panels")
    for module in CAERP_PANELS_MODULES:
        config.include(module)


def config_events(config):
    logger.debug("  + Adding event hooks")
    for module in CAERP_EVENT_MODULES:
        config.include(module)


def config_services(config):
    """
    Setup the services (pyramid_services) used in enDI
    """
    logger.debug("  + Adding pyramid_services")
    settings = config.registry.settings
    for service_name, default, interface, contexts, params in CAERP_SERVICES:
        module_path = settings.get("caerp." + service_name, default)
        module = config.maybe_dotted(module_path)

        if not isinstance(contexts, (tuple, list)):
            contexts = [contexts]

        for ctx in contexts:
            config.register_service(module(*params), interface, context=ctx)

    for service_name, default, interface, contexts in CAERP_SERVICE_FACTORIES:
        module = settings.get("caerp." + service_name, default)

        if not isinstance(contexts, (tuple, list)):
            contexts = [contexts]

        for ctx in contexts:
            config.register_service_factory(module, interface, context=ctx)


def add_static_views(config, settings):
    """
    Add the static views used in enDI
    """
    statics = settings.get("caerp.statics", "static")
    config.add_static_view(
        statics,
        "caerp:static",
        cache_max_age=3600,
    )

    # Static path for generated files (exports / pdfs ...)
    tmp_static = settings.get("caerp.static_tmp", "caerp:tmp")
    config.add_static_view("cooked", tmp_static)

    # Allow to specify a custom fanstatic root path
    hack_caerp_static_path(settings)


def add_http_error_views(config, settings):
    template_args = {"title": "Page non trouvée (erreur 404)"}
    config.add_notfound_view(
        view=lambda _: template_args,
        renderer="http_404.mako",
    )


def enable_sqla_listeners():
    from caerp.models.listeners import SQLAListeners

    logger.debug("  + Enabling sqla listeners")
    SQLAListeners.start_listening()


def include_custom_modules(config):
    """
    Include custom modules using the caerp.includes mechanism
    """
    settings = config.registry.settings
    for module in settings.get("caerp.includes", "").split():
        if module.strip():
            config.add_plugin(module)


def configure_traversal(config, dbsession) -> Configurator:
    """
    Configure the traversal related informations
    - Set acls on models
    - Setup the root factory
    - Set the default permission
    """
    logger.debug("  + Setting up traversal")
    from caerp.utils.security import RootFactory, TraversalDbAccess, set_models_acl

    set_models_acl()
    TraversalDbAccess.dbsession = dbsession

    # Application main configuration
    config.set_root_factory(RootFactory)
    config.set_default_permission("global.authenticated")
    return config


def add_base_directives_and_predicates(config):
    """
    Add custom predicates and directives used in enDI's codebase
    """
    logger.debug("  + Adding predicates and directives")
    from caerp.utils.predicates import SettingHasValuePredicate
    from caerp.utils.security import ApiKeyAuthenticationPredicate

    # On ajoute le registre 'modules' et ses directives
    config.include("caerp.utils.modules")

    # On ajoute le registre 'dataqueries' et ses directives
    config.include("caerp.utils.dataqueries")
    # On charge également le module des requêtes
    config.include("caerp.dataqueries")

    # Allows to restrict view acces only if a setting is set
    config.add_view_predicate("if_setting_has_value", SettingHasValuePredicate)
    # Allows to authentify a view through hmac api key auth
    config.add_view_predicate("api_key_authentication", ApiKeyAuthenticationPredicate)

    # Shortcut to add rest service (collection + Add / edit delete views)
    config.add_directive("add_rest_service", add_rest_service)

    return config


def prepare_view_config(config, dbsession, from_tests, **settings):
    """
    Prepare view configuration

    Configure all tools used to include views
    """
    logger.debug("Preparing elements before loading views")
    configure_traversal(config, dbsession)
    add_base_directives_and_predicates(config)
    setup_request_methods(config, dbsession)

    # Customize renderers (json, form rendering with i18n ...)
    config.include(customize_renderers)

    # Events and pyramid_services
    config.include(config_subscribers)
    config.include(config_events)
    config.include(config_services)
    config.include("caerp.utils.menu")
    config.include("caerp.utils.notification")
    if from_tests:
        # add_tree_view_directive attache des classes les unes aux autres et
        # provoquent des problèmes ingérables dans les tests
        # TODO: Il devrait utiliser le registry pour attacher parents et
        # enfants
        def add_tree_view_directive(config, *args, **kwargs):
            if "parent" in kwargs:
                kwargs.pop("parent")
            if "route_name" not in kwargs:
                # Use the route_name set on the view by default
                kwargs["route_name"] = args[0].route_name
            config.add_view(*args, **kwargs)

    else:
        from caerp.views import add_tree_view_directive
    config.add_directive("add_tree_view", add_tree_view_directive)

    # Widgets base layout related includes
    add_static_views(config, settings)
    add_http_error_views(config, settings)
    config.include(config_layouts)
    config.include(config_panels)
    return config


def base_configure(config, dbsession, from_tests=False, **settings):
    """
    All plugin and others configuration stuff
    """
    prepare_view_config(config, dbsession, from_tests, **settings)
    config.include(config_views)

    config.commit()
    config.begin()

    config.include(include_custom_modules)

    enable_sqla_listeners()

    return config


def version(strip_suffix=False) -> str:
    """
    Return enDI's version number (as defined in setup.py)

    :param: strip any suffix after patch release (ex: 1.2.3b3 → 1.2.3)
    """
    if strip_suffix:
        return Version(package_version).base_version
    else:
        return package_version


def main(global_config, **settings):
    """
    Main entry function

    :returns: a Pyramid WSGI application.
    """
    configure_warnings()
    # Récupère les variables d'environnement
    settings = collect_envvars_as_settings(settings)
    config = prepare_config(**settings)

    logger.debug("Setting up the bdd")
    dbsession = setup_bdd(settings)
    config = base_configure(config, dbsession, **settings)
    config.include("caerp.utils.sqlalchemy_fix")

    logger.debug("Configuring file depot")
    configure_filedepot(settings)

    config.configure_celery(global_config["__file__"])

    return config.make_wsgi_app()
