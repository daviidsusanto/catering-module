import frappe
from frappe.model.document import Document
import json
import math
import random
import string
from itertools import groupby
from frappe.model.mapper import get_mapped_doc

def generate_barcode_so(doc,name):
    if doc.order_type_2 == "Online Shop":
        if doc.total_qty > 0:
            length = 4
            num_strings = math.ceil(int(doc.total_qty) / 10)
            generated_strings = set()

            data = []
            for j in doc.items:
                data.append({'qty': j.qty,'item_category': j.item_category})

            sorted_data = sorted(data, key=lambda x: x["item_category"] if x["item_category"] else "")

            result = {
                        key: sum(item["qty"] for item in group)
                        for key, group in groupby(sorted_data, key=lambda x: x["item_category"])
                    }
            mb = 0
            for x in result:
                value = result[x]
                qty_per_master_box = frappe.get_value("Shipping Packaging",{'name': x},'kapasitas_shipping_point')
                if qty_per_master_box:
                    mb += math.ceil(value / qty_per_master_box)

            for i in range(0,mb):
                alphanumeric_characters = string.ascii_letters + string.digits
                new_string = ''.join(random.choice(alphanumeric_characters) for _ in range(length)).upper()
                if new_string not in generated_strings:
                    generated_strings.add(new_string)
                    
            if generated_strings:
                doc.barcode = []
                for i in generated_strings:
                    doc.append("barcode",{
                        "barcode": doc.name + "-" + i
                    })

def override_rate_is_free_item(doc,name):
    for i in doc.items:
        if i.is_free_item:
            i.discount_percentage = 100
            i.rate = 0
            i.amount = 0
    
    doc.delivery_date_custom = doc.delivery_date

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