import frappe
from frappe.model.document import Document
import json
import math
import random
import string
from itertools import groupby

def generate_barcode_so(doc,name):
    if doc.order_type_2 == "Online Shop":
        if doc.total_qty > 0:
            length = 4
            num_strings = math.ceil(int(doc.total_qty) / 10)
            generated_strings = set()

            data = []
            for j in doc.items:
                data.append({'qty': j.qty,'item_category': j.item_category})

            sorted_data = sorted(data, key=lambda x: x["item_category"])

            result = {
                        key: sum(item["qty"] for item in group)
                        for key, group in groupby(sorted_data, key=lambda x: x["item_category"])
                    }
            mb = 0
            for x in result:
                value = result[x]
                qty_per_master_box = frappe.get_value("Shipping Packaging",{'name': x},'quantity_per_master_box')
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