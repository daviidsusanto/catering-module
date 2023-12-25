from . import __version__ as app_version

app_name = "catering_module"
app_title = "Catering Module"
app_publisher = "Satu Meja"
app_description = "Catering Module Satu Meja"
app_email = "satumeja@mail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/catering_module/css/catering_module.css"
# app_include_js = "/assets/catering_module/js/catering_module.js"
# app_include_js = "public/js/qz_printing_addon.js"

# include js, css files in header of web template
# web_include_css = "/assets/catering_module/css/catering_module.css"
# web_include_js = "/assets/catering_module/js/catering_module.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "catering_module/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_js = {
    "BOM" : "public/js/bom_addon.js",
    "BOM Item" : "public/js/bom_addon.js",
    "Sales Order" : "public/js/sales_order_addon.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "catering_module.utils.jinja_methods",
#	"filters": "catering_module.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "catering_module.install.before_install"
# after_install = "catering_module.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "catering_module.uninstall.before_uninstall"
# after_uninstall = "catering_module.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "catering_module.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }
doc_events = {
	"Work Order": {
		"validate": "catering_module.public.work_order_addon.validate_qty",
		"after_insert": "catering_module.public.work_order_addon.validate_qty",
	},
	"Sales Order": {
		"validate": ["catering_module.public.sales_order_addon.generate_barcode_so",
				"catering_module.public.sales_order_addon.override_rate_is_free_item"],
		"after_insert": "catering_module.public.sales_order_addon.create_sales_invoice",
	},
	"Stock Entry": {
		"on_submit": [
				"catering_module.public.stock_entry_addon.validate_qty",
				"catering_module.public.stock_entry_addon.auto_create_se_for_kelebihan_qty"
		] 
	},
	"Sales Invoice": {
		"validate": "catering_module.public.sales_invoice_addon.change_coa_free_item",
	},
	"Purchase Order": {
		"on_submit": "catering_module.public.purchase_order_addon.send_whatsapp_notif_to_supplier",
	},
	"Pick List": {
		# "validate": "catering_module.public.pick_list_addon.get_barcode_from_so",
		"validate": "catering_module.public.pick_list_addon.order_now"
	}
}


# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"catering_module.tasks.all"
#	],
#	"daily": [
#		"catering_module.tasks.daily"
#	],
#	"hourly": [
#		"catering_module.tasks.hourly"
#	],
#	"weekly": [
#		"catering_module.tasks.weekly"
#	],
#	"monthly": [
#		"catering_module.tasks.monthly"
#	],
# }

scheduler_events = {
    "cron": {
        "00 01 * * *": [
            "catering_module.public.biteship_api.enqueue_schedule_orders"
        ],
        "00 02 * * *": [
            "catering_module.public.biteship_api.enqueue_schedule_orders"
        ],
        "00 03 * * *": [
            "catering_module.public.biteship_api.enqueue_schedule_orders"
        ],
		"*/5 * * * *": [
            "catering_module.public.biteship_api.enqueue_schedule_orders"
        ]
    }
}

# Testing
# -------

# before_tests = "catering_module.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "catering_module.event.get_events"
# }

override_whitelisted_methods = {
	"erpnext.manufacturing.doctype.work_order.work_order.make_stock_entry": "catering_module.public.work_order_addon.make_stock_entry"
}


#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "catering_module.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["catering_module.utils.before_request"]
# after_request = ["catering_module.utils.after_request"]

# Job Events
# ----------
# before_job = ["catering_module.utils.before_job"]
# after_job = ["catering_module.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"catering_module.auth.validate"
# ]
