import frappe
from frappe.model.document import Document
import json
import math
import random
import string

def generate_barcode_so(doc,name):
    if doc.total_qty > 0:
        length = 4
        num_strings = math.ceil(int(doc.total_qty) / 10)
        generated_strings = set()
        for i in range(0,num_strings):
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
