import frappe
from frappe.model.document import Document
import json
import math

def validate_stock_qty_rounded(doc,name):
    for i in doc.items:
        rounding_up = frappe.get_value("Item",i.item_code,"kelipatan_rounding_up")
        x = i.qty / rounding_up
        x = math.ceil(x)
        hasil = x * rounding_up
        i.stock_qty = hasil