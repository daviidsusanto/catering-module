import frappe
from frappe.model.document import Document
import json
import math
import random
import string

def get_barcode_from_so(doc,name):
    list_so = []
    doc.barcode = []
    for i in doc.locations:
        list_so.append(i.sales_order)

    list_so = list(set(list_so))

    for x in list_so:
        so = frappe.get_doc("Sales Order",x)
        if so.barcode:
            for i in so.barcode:
                doc.append("barcode",{
                    "barcode": i.barcode
                })