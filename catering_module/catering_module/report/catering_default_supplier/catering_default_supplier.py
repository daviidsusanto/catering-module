# Copyright (c) 2023, Satu Meja and contributors
# For license information, please see license.txt

import frappe
from collections import defaultdict
from frappe import _

def execute(filters=None):
	if not filters:
		filters = {}

	columns, data = get_columns(), get_data(filters)
	return columns, data

def get_columns():
	return [
		{
			"label": _("Nama Item"),
			"fieldname": "nama_item",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Weekdays Pagi"),
			"fieldname": "weekdays_pagi",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Weekdays Siang"),
			"fieldname": "weekdays_siang",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Weekdays Sore"),
			"fieldname": "weekdays_sore",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Sabtu Pagi"),
			"fieldname": "sabtu_pagi",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Sabtu Siang"),
			"fieldname": "sabtu_siang",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Sabtu Sore"),
			"fieldname": "sabtu_sore",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Minggu Pagi"),
			"fieldname": "minggu_pagi",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Minggu Siang"),
			"fieldname": "minggu_siang",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Minggu Sore"),
			"fieldname": "minggu_sore",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Tanggal Merah Pagi"),
			"fieldname": "tanggal_merah_pagi",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Tanggal Merah Siang"),
			"fieldname": "tanggal_merah_siang",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Tanggal Merah Sore"),
			"fieldname": "tanggal_merah_sore",
			"fieldtype": "Data",
			"width": 200
		}
	]


def get_data(filters=None):
	# filter_fleet_type_code = filters.get("fleet_type_code")
	# filter_fleet_status = filters.get("fleet_status")

	conditions = ""

	# if filter_fleet_type_code:
	# 	conditions += "AND fleet_type_code = %s "%(frappe.db.escape(filters.get("fleet_type_code")))

	# if filter_fleet_status:
	# 	if filter_fleet_status == "Open":
	# 		conditions += "AND shipment_date is null"
	# 	elif filter_fleet_status == "On Job":
	# 		conditions += "AND shipment_date is not null"
	# 	else:
	# 		conditions += ""

	data = frappe.db.sql("""
		SELECT 
			item.item_name as nama_item,sup.day, sup.slot_pengiriman, sup.default_supplier_name
		FROM `tabItem` item
		LEFT JOIN `tabDefault Supplier List` sup
		ON item.name = sup.parent
	""".format(cond=conditions),as_dict=1)

	grouped_data = defaultdict(dict)

	for entry in data:
		if entry['day'] and entry['slot_pengiriman']:
			key = f"{entry['day'].lower()}_{entry['slot_pengiriman'].lower()}"
			grouped_data[entry['nama_item']][key] = entry['default_supplier_name']

	output = []
	for nama_item, suppliers in grouped_data.items():
		item_entry = {'nama_item': nama_item}
		for slot in ['weekdays_pagi', 'weekdays_siang', 'weekdays_sore', 'sabtu_pagi','sabtu_siang','sabtu_sore','minggu_pagi','minggu_siang','minggu_sore','tanggal_merah_pagi','tanggal_merah_siang','tanggal_merah_sore']:
			item_entry[slot] = suppliers.get(slot, "-")
		output.append(item_entry)

	return output