import frappe
from frappe.model.document import Document
import json
import math

def validate_qty(doc,name):
    if doc.required_items:
        for i in doc.required_items:
            i.required_qty = math.ceil(i.required_qty)