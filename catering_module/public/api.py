import frappe 
import requests
import random
import string

@frappe.whitelist()
def list_work_order(tgl_pengiriman, slot_pengiriman):
    output = []
    sales_order = frappe.db.get_list("Sales Order", pluck="name", filters=[["delivery_date","=",tgl_pengiriman],["slot_pengiriman","=",slot_pengiriman],["docstatus","=",1]])
    if sales_order:
        work_orders = frappe.db.get_list("Work Order", pluck="name", filters=[["sales_order", "in", sales_order]])
        for i in work_orders:
            required_items_data = []
            wo = frappe.get_doc("Work Order",i)
            for j in wo.required_items:
                required_items_data.append({
                    "item_code": j.item_code,
                    "required_qty": j.required_qty,
                })
            output.append({
                "name": wo.name,
                "production_item": wo.production_item,
                "items": required_items_data,
                "delivery_date": tgl_pengiriman,
                "slot_pengiriman": slot_pengiriman,
                "item_group": frappe.get_value("Item", {"item_code": wo.production_item},"item_group")
            })

    frappe.response['data'] = output

@frappe.whitelist()
def get_nearest_distribution_point(my_location):
    try:
        base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"

        distribution_points = frappe.get_list("Distribution Point",fields=["name","latlong","address"])
        
        origins = my_location
        destinations = '|'.join(point['latlong'] for point in distribution_points)

        params = {
            "origins": origins,
            "destinations": destinations,
            "key": frappe.db.get_single_value("Google API Setup","api_key")
        }

        response = requests.get(base_url, params=params)
        data = response.json()

        if data.get("status") == "OK":
            elements = data["rows"][0]["elements"]
            min_distance = float('inf')
            nearest_point_index = -1

            for i, element in enumerate(elements):
                if element.get("status") == "OK":
                    distance = element["distance"]["value"]
                    if distance < min_distance:
                        min_distance = distance
                        nearest_point_index = i
            nearest_point = []
            if nearest_point_index != -1:
                nearest_point.append(distribution_points[nearest_point_index])
                frappe.response["code"] = 200
                frappe.response["message"] = "Success"
                frappe.response["data"] = nearest_point
        else:
            frappe.response["code"] = 400
            frappe.response["message"] = "Request Failed"
            frappe.response["data"] = data
            
    except Exception as e:
        frappe.response["code"] = 400
        frappe.response["message"] = "Request Failed"
        frappe.response["data"] = e

@frappe.whitelist()
def generate_unique_strings(num_strings, length):
    generated_strings = set()
    while len(generated_strings) < num_strings:
        alphanumeric_characters = string.ascii_letters + string.digits
        new_string = ''.join(random.choice(alphanumeric_characters) for _ in range(length)).upper()
        if new_string not in generated_strings:
            generated_strings.add(new_string)
            yield new_string

    return generated_strings