"""
    Handle static libraries insid'enDI with the help of fanstatic
"""
from fanstatic import Group, Library, Resource
from fanstatic.core import set_resource_file_existence_checking
from js.bootstrap import bootstrap_js
from js.jquery import jquery
from js.jquery_form import jquery_form
from js.jquery_timepicker_addon import timepicker_js
from js.jqueryui import ui_datepicker_fr, ui_dialog, ui_sortable

set_resource_file_existence_checking(False)

lib_caerp = Library("fanstatic", "static")


def get_resource(
    filepath,
    minified=None,
    depends=None,
    bottom=False,
):
    """
    Return a resource object included in enDI
    """
    library = lib_caerp
    return Resource(
        library,
        filepath,
        minified=minified,
        depends=depends,
        bottom=bottom,
    )


_select2_css = get_resource(
    "css/select2.css",
    minified="css/select2.min.css",
)
_select2 = get_resource(
    "js/vendors/select2.full.js", minified="js/vendors/select2.full.min.js"
)
select2_fr = get_resource("js/vendors/select2_fr.js", depends=[_select2, _select2_css])

tinymce_library = Library("tinymce59", "static/js/vendors/tinymce")
tinymce = Resource(
    tinymce_library, "tinymce.js", minified="tinymce.min.js", depends=None, bottom=False
)
# Css resources
brand_css = get_resource("css/brand.css", depends=[])
main_css = get_resource("css/main.css", depends=[])
opa_css = get_resource("css/opa.css", depends=[main_css])
opa_vendor_js = get_resource(
    "js/build/vendor.js",
    minified="js/build/vendor.min.js",
    bottom=True,
)
base_setup_js = get_resource(
    "js/build/base_setup.js",
    minified="js/build/base_setup.min.js",
    depends=(opa_vendor_js,),
    bottom=True,
)

# Js static resources
_date = get_resource("js/date.js")
_math = get_resource("js/math.js")
_dom = get_resource("js/dom.js", depends=[jquery])
_utils = get_resource("js/utils.js")
_default_layout = get_resource("js/default_layout.js", depends=[jquery])
_svgxuse = get_resource("js/vendors/svgxuse.js", minified="js/vendors/svgxuse.min.js")


def get_opa_group():
    """
    Return the resources used on one page applications pages
    """
    return Group(
        [
            brand_css,
            main_css,
            opa_css,
            opa_vendor_js,
            base_setup_js,
            _utils,
            _svgxuse,
            _select2_css,
        ]
    )


vendor_vue_js = get_resource(
    "js/build/vendor-vue.js",
    minified="js/build/vendor-vue.min.js",
    bottom=True,
)


def get_opa_group_vue():
    return Group(
        [
            _utils,
            brand_css,
            main_css,
            opa_css,
            vendor_vue_js,
            base_setup_js,
            _svgxuse,
            _select2_css,
        ]
    )


def get_annex_group_vue():
    """
    Retuns the group for secondary views (not main content) using vuejs
    """
    # We exclude base_setup_js to avoid double initialization of some UX elements
    # like company selector
    return Group([brand_css, main_css, vendor_vue_js, _svgxuse, _select2_css])


def get_main_group():
    """
    Return the main resource Group that will be used on all pages
    """
    # UnPackaged external libraries
    underscore = get_resource(
        "js/vendors/underscore.js", minified="js/vendors/underscore-min.js"
    )

    main_js = get_resource(
        "js/main.js",
        depends=[
            ui_dialog,
            ui_sortable,
            underscore,
            timepicker_js,
            bootstrap_js,
            _math,
        ],
    )

    js_tools = Group(
        [
            main_js,
            _dom,
            _math,
            _date,
            select2_fr,
            _utils,
            _default_layout,
            _svgxuse,
        ]
    )

    return Group(
        [
            brand_css,
            main_css,
            js_tools,
            jquery_form,
            ui_datepicker_fr,
        ]
    )


main_group = get_main_group()
opa_group = get_opa_group()


def get_module_group():
    """
    Return main libraries used in custom modules (backbone marionette and
    handlebar stuff)

    NB : depends on the main_group
    """
    handlebar = get_resource(
        "js/vendors/handlebars.runtime-v4.7.6.js",
        minified="js/vendors/handlebars.runtime.min-v4.7.6.js",
    )
    backbone = get_resource(
        "js/vendors/backbone.js",
        minified="js/vendors/backbone-min.js",
        depends=[main_group],
    )
    backbone_marionnette = get_resource(
        "js/vendors/backbone.marionette.js",
        minified="js/vendors/backbone.marionette.min.js",
        depends=[backbone],
    )
    # Bootstrap form validation stuff
    backbone_validation = get_resource(
        "js/vendors/backbone-validation.js",
        minified="js/vendors/backbone-validation-min.js",
        depends=[backbone],
    )
    backbone_validation_bootstrap = get_resource(
        "js/backbone-validation-bootstrap.js", depends=[backbone_validation]
    )
    # Popup object
    backbone_popup = get_resource(
        "js/backbone-popup.js", depends=[backbone_marionnette]
    )
    # Some specific tuning
    backbone_tuning = get_resource(
        "js/backbone-tuning.js", depends=[backbone_marionnette, handlebar]
    )
    # The main templates
    main_templates = get_resource("js/template.js", depends=[handlebar])
    # Messages
    message_js = get_resource("js/message.js", depends=[handlebar])
    return Group(
        [
            backbone_marionnette,
            backbone_validation_bootstrap,
            backbone_tuning,
            backbone_popup,
            main_templates,
            message_js,
        ]
    )


module_libs = get_module_group()


def get_module_resource(module, tmpl=False, extra_depends=()):
    """
    Return a resource group (or a single resource) for the given module

    static/js/<module>.js and static/js/templates/<module>.js

    :param str module: the name of a js file
    :param bool tmpl: is there an associated tmpl
    :param extra_depends: extra dependencies
    """
    depends = [module_libs]
    depends.extend(extra_depends)
    if tmpl:
        tmpl_resource = get_resource(
            "js/templates/%s.js" % module, depends=[module_libs]
        )
        depends.append(tmpl_resource)

    return get_resource("js/%s.js" % module, depends=depends)


address = get_module_resource("address")
tva = get_module_resource("tva")

task_list_js = get_module_resource("task_list")
task_duplicate_js = get_module_resource("task_duplicate")
estimation_signed_status_js = get_module_resource("estimation_signed_status")
event_list_js = get_module_resource("event_list")

job_js = get_module_resource("job", tmpl=True)

competence_js = get_module_resource("competence", tmpl=True, extra_depends=[select2_fr])
holiday_js = get_module_resource("holiday", tmpl=True)
commercial_js = get_module_resource("commercial")

bpf_js = get_module_resource("bpf")
dispatch_supplier_invoice_js = get_module_resource("dispatch_supplier_invoice")

pdf_css = get_resource("css/pdf.css")
# Permet d'overrider ou compléter les css de la sortie pdf pour l'affichage
# html
task_preview_css = get_resource("css/task_preview.css")

activity_edit_js = get_resource("js/activity_edit.js")


# File upload page js requirements
fileupload_js = get_resource(
    "js/fileupload.js",
    depends=[main_group],
)

# Chart tools
d3_js = get_resource("js/vendors/d3.v3.js", minified="js/vendors/d3.v3.min.js")
radar_chart_js = get_resource("js/vendors/radar-chart.js", depends=[d3_js])
radar_chart_css = get_resource(
    "css/radar-chart.css", minified="css/radar-chart.min.css"
)
competence_radar_js = get_module_resource(
    "competence_radar",
    extra_depends=(
        radar_chart_js,
        radar_chart_css,
    ),
)

# This is not realy admin, but rather moderation
admin_expense_js = get_module_resource("admin_expense")

admin_expense_types_js = get_module_resource("admin_expense_type")

# Task form resources
task_css = get_resource("css/task.css", depends=(opa_css,))
task_js = get_resource(
    "js/build/task.js",
    minified="js/build/task.min.js",
    depends=[opa_vendor_js],
    bottom=True,
)
task_resources = Group([task_js, task_css])
node_view_only_js = get_resource(
    "js/build/node_view_only.js",
    minified="js/build/node_view_only.min.js",
    depends=[opa_vendor_js],
    bottom=True,
)

# Expense form resources
expense_css = get_resource("css/expense.css", depends=(opa_css,))
expense_js = get_resource(
    "js/build/expense.js",
    minified="js/build/expense.min.js",
    depends=[opa_vendor_js],
    bottom=True,
)
expense_resources = Group([expense_js, expense_css])

# Sale product form resources
sale_product_css = get_resource("css/sale_product.css", depends=(opa_css,))
sale_product_js = get_resource(
    "js/build/sale_product.js",
    minified="js/build/sale_product.min.js",
    depends=[opa_vendor_js],
    bottom=True,
)
sale_product_resources = Group([sale_product_js, sale_product_css])
# Supplier Order
supplier_order_js = get_resource(
    "js/build/supplier_order.js",
    minified="js/build/supplier_order.min.js",
    depends=[opa_vendor_js],
    bottom=True,
)
supplier_invoice_js = get_resource(
    "js/build/supplier_invoice.js",
    minified="js/build/supplier_invoice.min.js",
    depends=[opa_vendor_js],
    bottom=True,
)

supplier_order_resources = Group([supplier_order_js, expense_css])
supplier_invoice_resources = Group([supplier_invoice_js, expense_css])

# Statistic page resources
statistic_js = get_resource(
    "js/build/statistics.js",
    minified="js/build/statistics.min.js",
    depends=[opa_vendor_js],
    bottom=True,
)
statistic_resources = Group([statistic_js])

# User page related resources
login_css = get_resource("css/login.css", depends=(main_css,))
login_resources = Group([login_css, main_group])

dashboard_css = get_resource("css/dashboard.css", depends=(main_css,))
dashboard_resources = Group([dashboard_css, main_group])

user_css = get_resource("css/user.css", depends=(main_css,))
user_resources = Group([user_css, main_group])

admin_css = get_resource("css/admin.css", depends=(main_css,))
admin_resources = Group([admin_css, main_group, tinymce])

opa_vue_group = get_opa_group_vue()
annex_vue_group = get_annex_group_vue()

company_js = get_resource(
    "js/build/company.js",
    minified="js/build/company.min.js",
    depends=[opa_vue_group],
    bottom=True,
)

company_map_js = get_resource(
    "js/build/company_map.js",
    minified="js/build/company_map.min.js",
    depends=[opa_vue_group],
    bottom=True,
)

customer_js = get_resource(
    "js/build/customer.js",
    minified="js/build/customer.min.js",
    depends=[opa_vue_group],
    bottom=True,
)
task_add_js = get_resource(
    "js/build/task_add.js",
    minified="js/build/task_add.min.js",
    depends=[opa_vue_group],
    bottom=True,
)

task_payment_js = get_resource(
    "js/build/task_payment.js",
    minified="js/build/task_payment.min.js",
    depends=[opa_vue_group],
    bottom=True,
)
notification_js = get_resource(
    "js/build/notification.js",
    minified="js/build/notification.min.js",
    depends=[annex_vue_group],
    bottom=True,
)
smtp_settings_js = get_resource(
    "js/build/smtp_settings.js",
    minified="js/build/smtp_settings.min.js",
    depends=[annex_vue_group],
    bottom=True,
)
sale_files_js = get_resource(
    "js/build/sale_files.js",
    minified="js/build/sale_files.min.js",
    depends=[opa_vue_group],
    bottom=True,
)
pdf_preview_js = get_resource(
    "js/build/pdf_preview.js",
    minified="js/build/pdf_preview.min.js",
    depends=[opa_vue_group],
    bottom=True,
)
vue_multiselect_css = get_resource("css/vue-multiselect.min.css")
sepa_credit_transfer_js = get_resource(
    "js/build/sepa_credit_transfer.js",
    minified="js/build/sepa_credit_transfer.min.js",
    depends=[opa_vue_group, vue_multiselect_css],
    bottom=True,
)
