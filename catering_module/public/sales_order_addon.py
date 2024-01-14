import frappe
from frappe.model.document import Document
import json
import math
import random
import string
from itertools import groupby
from frappe.model.mapper import get_mapped_doc
from assets.catering_module.api import get_packaging_type, get_vehicle_type

def generate_barcode_so(doc,name):
    if doc.order_type_2 == "Online Shop":
        if doc.total_qty > 0:
            total_shipping_point = 0
            category = []
            length_of_string = 4

            for j in doc.items:
                size = 0
                shipping_point = frappe.get_value("Item",{"item_name": j.item_code}, "shipping_point") or 0
                size += int(shipping_point) * j.qty
                total_shipping_point += int(size) or 0
                category.append(frappe.get_value("Item",{"item_name": j.item_code}, "shipping_item_category"))

            tumpeng_tampah = 0
            if "Tumpeng" in category or "Tampah" in category:
                shipping_item_category = "Tumpeng"
                tumpeng_tampah = 1
            else:
                shipping_item_category = [val for val in category if val not in ["tumpeng", "tampah"]][0]

            # Logic Get Vehicle Type
            __get_vehicle_type = get_vehicle_type(int(total_shipping_point), shipping_item_category)

            # Logic Get Packaging Type
            __get_packaging_type = get_packaging_type(__get_vehicle_type.get("vehicle_type"), int(total_shipping_point), tumpeng_tampah)

            doc.barcode = []
            doc.custom_shipping_packaging = []
            if __get_packaging_type:
                if int(__get_packaging_type.get("packaging_plastik_kecil")) > 0:
                    packaging_id = "Plastik Kecil"
                    doc.append('custom_shipping_packaging',{
                        'type_packaging': packaging_id,
                        'qty': __get_packaging_type.get("packaging_plastik_kecil")
                    })
                    for pk in range(__get_packaging_type.get("packaging_plastik_kecil")):
                        random_str = generate_random_string(length_of_string)
                        doc.append('barcode', {
                            'barcode': doc.name + "-" + random_str
                        })
                        print("kenaaaa")
                
                if int(__get_packaging_type.get("packaging_masterbox_kecil")) > 0:
                    packaging_id = "Masterbox Kecil"
                    doc.append('custom_shipping_packaging',{
                        'type_packaging': packaging_id,
                        'qty': __get_packaging_type.get("packaging_masterbox_kecil")
                    })
                    for mk in range(__get_packaging_type.get("packaging_masterbox_kecil")):
                        random_str = generate_random_string(length_of_string)
                        doc.append('barcode', {
                            'barcode': doc.name + "-" + random_str
                        })

                if int(__get_packaging_type.get("packaging_masterbox_besar")) > 0:
                    packaging_id = "Masterbox Besar"
                    doc.append('custom_shipping_packaging',{
                        'type_packaging': packaging_id,
                        'qty': __get_packaging_type.get("packaging_masterbox_besar")
                    })
                    for mb in range(__get_packaging_type.get("packaging_masterbox_besar")):
                        random_str = generate_random_string(length_of_string)
                        doc.append('barcode', {
                            'barcode': doc.name + "-" + random_str
                        })

                if int(__get_packaging_type.get("packaging_tumpeng")) > 0:
                    packaging_id = "Tumpeng"
                    doc.append('custom_shipping_packaging',{
                        'type_packaging': packaging_id,
                        'qty': __get_packaging_type.get("packaging_tumpeng")
                    })
                    for tp in range(__get_packaging_type.get("packaging_tumpeng")):
                        random_str = generate_random_string(length_of_string)
                        doc.append('barcode', {
                            'barcode': doc.name + "-" + random_str
                        })

                if int(__get_packaging_type.get("packaging_tampah")) > 0:
                    packaging_id = "Tampah"
                    doc.append('custom_shipping_packaging',{
                        'type_packaging': packaging_id,
                        'qty': __get_packaging_type.get("packaging_tampah")
                    })
                    for th in range(__get_packaging_type.get("packaging_tampah")):
                        random_str = generate_random_string(length_of_string)
                        doc.append('barcode', {
                            'barcode': doc.name + "-" + random_str
                        })

def override_rate_is_free_item(doc,name):
    for i in doc.items:
        if i.is_free_item:
            i.discount_percentage = 100
            i.rate = 0
            i.amount = 0
    doc.delivery_date_custom = doc.delivery_date

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    unique_chars = random.sample(characters, length)
    random_string = ''.join(unique_chars)
    return random_string.upper()

def create_sales_invoice(doc,name):
    if doc.order_type_2 == "Online Shop" and doc.docstatus == 1:
        si = frappe.new_doc("Sales Invoice")
        si.customer = doc.customer
        si.posting_date = doc.transaction_date
        si.posting_time = doc.jam_pengiriman
        si.payment_due_date = frappe.utils.nowdate()
        si.approval_code = doc.approval_code
        for i in doc.items:
            if not i.is_free_item:
                si.append("items",{
                    "item_code": i.item_code,
                    "item_name": i.item_name,
                    "description": i.description,
                    "qty": i.qty,
                    "uom": i.uom,
                    "is_free_item": i.is_free_item,
                    "rate": i.rate,
                    "warehouse": i.warehouse,
                    "sales_order": doc.name
                })
            else:
                si.append("items",{
                    "item_code": i.item_code,
                    "item_name": i.item_name,
                    "description": i.description,
                    "qty": i.qty,
                    "uom": i.uom,
                    "discount_percentage": 100,
                    "is_free_item": i.is_free_item,
                    "rate": 0,
                    "amount": 0,
                    "warehouse": i.warehouse,
                    "sales_order": doc.name
                })
        for i in doc.taxes:
            si.append("taxes",{
                "charge_type": i.charge_type,
                "account_head": i.account_head,
                "description": i.description,
                "cost_center": i.cost_center,
                "rate": i.rate,
                "tax_amount": i.tax_amount,
                "total": i.total,
            })
        si.save()
