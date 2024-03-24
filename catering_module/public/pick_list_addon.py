import frappe
from frappe.model.document import Document
import json
import math
import random
import string
from datetime import *
from .biteship_api import *


def order_now(doc, name):
    logger = frappe.logger("order_now", allow_site=True, file_count=100)
    res = {}
    if doc.delivery_status == "Delivered":
        for item in doc.sales_order_pick_list:
            so = frappe.get_doc("Sales Order", item.sales_order)
            if so.custom_courier_status == "Delay" and not so.order_id:
                url = "/v1/orders"
                items = []
                for item in so.items:
                    items.append({
                        "id": item.item_code,
                        "name": item.item_name,
                        "image": frappe.get_value("Item", item.item_code, "image"),
                        "description": frappe.get_value("Item", item.item_code, "description"),
                        "value": item.amount,
                        "quantity": item.qty,
                        "height": frappe.get_value("Shipping Packaging", item.item_category, "dimension_height"),
                        "length": frappe.get_value("Shipping Packaging", item.item_category, "dimension_depth"),
                        "weight": frappe.get_value("Shipping Packaging", item.item_category, "dimension_weight"),
                        "width": frappe.get_value("Shipping Packaging", item.item_category, "dimension_width")
                    })

                data = {
                    "shipper_contact_name": frappe.get_value("Distribution Point", so.distribution_point, "staff_name"),
                    "shipper_contact_phone": frappe.get_value("Distribution Point", so.distribution_point, "staff_phone"), 
                    "shipper_contact_email": frappe.db.get_single_value("Catering Module Settings", "shipper_contact_email"), 
                    "shipper_organization": frappe.db.get_single_value("Catering Module Settings", "shipper_organization"), 
                    "origin_contact_name": frappe.get_value("Distribution Point", so.distribution_point, "staff_name"), 
                    "origin_contact_phone": frappe.get_value("Distribution Point", so.distribution_point, "staff_phone"), 
                    "origin_address": frappe.get_value("Distribution Point", so.distribution_point, "address"), 
                    "origin_note": "",
                    "origin_coordinate": {
                        "latitude": float(frappe.get_value("Distribution Point", so.distribution_point, "gps_lat_distribution_point")),
                        "longitude": float(frappe.get_value("Distribution Point", so.distribution_point, "gps_long_distribution_point"))
                    },
                    "destination_contact_name": so.nama_pic_penerima, 
                    "destination_contact_phone": so.no_telepon_pic_penerima,
                    "destination_contact_email": frappe.get_value("Customer", so.customer, "email"),
                    "destination_address": frappe.get_value("Address", so.shipping_address_name, "address_line1"), 
                    "destination_note": so.address_notes,
                    "destination_coordinate":{
                        "latitude": float(frappe.get_value("Address", so.shipping_address_name, "gps_lat_customer")), 
                        "longitude": float(frappe.get_value("Address", so.shipping_address_name, "gps_long_customer"))
                    },
                    "courier_company": so.courier_company,
                    "courier_type": so.courier_type,
                    "delivery_type": "scheduled",
                    "delivery_date": datetime.now(),
                    "delivery_time": datetime.now(),
                    "order_note": so.order_notes,
                    "items": items
                }
                logger.info("so_name: {}-{}".format(so.name, data))
                res = base_api(url, 'POST', json.dumps(data, default=defaultconverter))
                print(res)
                logger.info("res: {}".format(res))
                if res.get('success'):
                    so.db_set('order_id', res.get('id'), update_modified=False, notify=True, commit=True)
                    so.db_set('courier_tracking_id', res.get('courier').get('tracking_id'), update_modified=False, notify=True, commit=True)
                    so.db_set('courier_waybill_id', res.get('courier').get('waybill_id'), update_modified=False, notify=True, commit=True)
                    so.db_set('courier_company', res.get('courier').get('company'), update_modified=False, notify=True, commit=True)
                    so.db_set('courier_driver_name', res.get('courier').get('name'), update_modified=False, notify=True, commit=True)
                    so.db_set('courier_driver_phone', res.get('courier').get('phone'), update_modified=False, notify=True, commit=True)
                    so.db_set('courier_link', res.get('courier').get('link'), update_modified=False, notify=True, commit=True)
                    so.db_set('biteship_status', res.get('status'), update_modified=False, notify=True, commit=True)
                    so.db_set('shippment_fee', res.get('price'), update_modified=False, notify=True, commit=True)
                else:
                    logger.info('Error: {}-{}'.format(res.get('error'), res.get('code')))


# def get_barcode_from_so(doc,name):
#     list_so = []
#     doc.barcode = []
#     for i in doc.locations:
#         list_so.append(i.sales_order)

#     list_so = list(set(list_so))

#     for x in list_so:
#         so = frappe.get_doc("Sales Order",x)
#         if so.barcode:
#             for i in so.barcode:
#                 doc.append("barcode",{
#                     "barcode": i.barcode
#                 })

# from frappe.model.mapper import get_mapped_doc
# from frappe.utils import add_days, cint, cstr, flt, get_link_to_form, getdate, nowdate, strip_html

# @frappe.whitelist()
# def create_pick_list(source_name, target_doc=None):
# 	from erpnext.stock.doctype.packed_item.packed_item import is_product_bundle

# 	def update_item_quantity(source, target, source_parent) -> None:
# 		picked_qty = flt(source.picked_qty) / (flt(source.conversion_factor) or 1)
# 		qty_to_be_picked = flt(source.qty) - max(picked_qty, flt(source.delivered_qty))

# 		target.qty = qty_to_be_picked
# 		target.stock_qty = qty_to_be_picked * flt(source.conversion_factor)

# 	def update_packed_item_qty(source, target, source_parent) -> None:
# 		qty = flt(source.qty)
# 		for item in source_parent.items:
# 			if source.parent_detail_docname == item.name:
# 				picked_qty = flt(item.picked_qty) / (flt(item.conversion_factor) or 1)
# 				pending_percent = (item.qty - max(picked_qty, item.delivered_qty)) / item.qty
# 				target.qty = target.stock_qty = qty * pending_percent
# 				return

# 	def should_pick_order_item(item) -> bool:
# 		return (
# 			abs(item.delivered_qty) < abs(item.qty)
# 			and item.delivered_by_supplier != 1
# 			and not is_product_bundle(item.item_code)
# 		)

# 	doc = get_mapped_doc(
# 		"Sales Order",
# 		source_name,
# 		{
# 			"Sales Order": {"doctype": "Pick List", "validation": {"docstatus": ["=", 1]}},
# 			"Sales Order Item": {
# 				"doctype": "Pick List Item",
# 				"field_map": {"parent": "sales_order", "name": "sales_order_item"},
# 				"postprocess": update_item_quantity,
# 				"condition": should_pick_order_item,
# 			},
# 			"Packed Item": {
# 				"doctype": "Pick List Item",
# 				"field_map": {
# 					"parent": "sales_order",
# 					"name": "sales_order_item",
# 					"parent_detail_docname": "product_bundle_item",
# 				},
# 				"field_no_map": ["picked_qty"],
# 				"postprocess": update_packed_item_qty,
# 			},
# 		},
# 		target_doc,
# 	)

# 	doc.purpose = "Delivery"

# 	return doc