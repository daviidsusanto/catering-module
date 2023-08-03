import frappe
from frappe.model.document import Document
import json
import math

def validate_qty(doc,name):
	if doc.required_items:
		for i in doc.required_items:
			item = frappe.get_doc("Item",i.item_code)
			qty_recipe = i.required_qty / (1 + (item.q_factor/100))
			x = qty_recipe / item.kelipatan_rounding_up
			x = math.ceil(x)
			hasil = x * item.kelipatan_rounding_up
			i.required_qty = hasil


@frappe.whitelist()
def make_stock_entry(work_order_id, purpose, qty=None):
	work_order = frappe.get_doc("Work Order", work_order_id)
	if not frappe.db.get_value("Warehouse", work_order.wip_warehouse, "is_group"):
		wip_warehouse = work_order.wip_warehouse
	else:
		wip_warehouse = None

	stock_entry = frappe.new_doc("Stock Entry")
	stock_entry.purpose = purpose
	stock_entry.work_order = work_order_id
	stock_entry.company = work_order.company
	stock_entry.from_bom = 1
	stock_entry.bom_no = work_order.bom_no
	stock_entry.use_multi_level_bom = work_order.use_multi_level_bom
	# accept 0 qty as well
	stock_entry.fg_completed_qty = (
		qty if qty is not None else (flt(work_order.qty) - flt(work_order.produced_qty))
	)

	if work_order.bom_no:
		stock_entry.inspection_required = frappe.db.get_value(
			"BOM", work_order.bom_no, "inspection_required"
		)

	if purpose == "Material Transfer for Manufacture":
		stock_entry.to_warehouse = wip_warehouse
		stock_entry.project = work_order.project
	else:
		stock_entry.from_warehouse = wip_warehouse
		stock_entry.to_warehouse = work_order.fg_warehouse
		stock_entry.project = work_order.project

	stock_entry.set_stock_entry_type()
	stock_entry.get_items()
	if stock_entry.get("items"):
		for i in stock_entry.items:
			if i.s_warehouse:
				item = frappe.get_doc("Item",i.item_code)
				qty_recipe = i.qty / (1 + (item.q_factor/100))
				x = qty_recipe / item.kelipatan_rounding_up
				x = math.ceil(x)
				hasil = x * item.kelipatan_rounding_up
				i.qty = hasil

	stock_entry.set_serial_no_batch_for_finished_good()
	return stock_entry.as_dict()