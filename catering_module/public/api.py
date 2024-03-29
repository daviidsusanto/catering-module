import frappe 
import requests
import random
import string
import json
from math import floor, ceil
from itertools import groupby

from catering_module.public.biteship_api import base_api

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
def get_nearest_distribution_point(latitude,longitude):
    if frappe.db.get_single_value("API Setup", "active"):
        try:
            base_url = "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix"

            distribution_points = frappe.get_list("Distribution Point",fields=["name","gps_lat_distribution_point","gps_long_distribution_point","address"])
            
            data = {}
            origins = []

            for origin in distribution_points:
                latitude_origin = origin["gps_lat_distribution_point"]
                longitude_origin = origin["gps_long_distribution_point"]
                origin_data = {
                        "waypoint": {
                            "location": {
                                "latLng": {
                                    "latitude": float(latitude_origin),
                                    "longitude": float(longitude_origin)
                                }
                            }
                        }
                    }
                origins.append(origin_data)

            data.update({"origins": origins})

            destination = {
                    "destinations": [
                        {
                            "waypoint": {
                                "location": {
                                    "latLng": {
                                        "latitude": float(latitude),
                                        "longitude": float(longitude)
                                    }
                                }
                            }
                        }
                    ]
                }
            
            data.update(destination)
            # data.update({
            #     "travelMode": travel_mode,
            #     "routingPreference": "TRAFFIC_AWARE"
            # })
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": frappe.db.get_single_value("API Setup","api_key_distance_matrix"),
                "X-Goog-FieldMask": "originIndex,destinationIndex,duration,distanceMeters,status,condition"
            }

            response = requests.post(base_url, headers=headers, data=json.dumps(data))
            res = response.json()
            if res:
                # Find the item with the lowest distanceMeters value
                min_distance_item = min(res, key=lambda x: x["distanceMeters"])

                # Retrieve the corresponding origin index
                origin_index = min_distance_item["originIndex"]
                origin_latlong = data["origins"][origin_index]["waypoint"]["location"]["latLng"]
                distribution_nearest = frappe.get_value("Distribution Point",{'gps_lat_distribution_point': str(origin_latlong['latitude']),"gps_long_distribution_point": str(origin_latlong['longitude'])},["name","gps_lat_distribution_point","gps_long_distribution_point","address"],as_dict=1)
                
                frappe.response["code"] = 200
                frappe.response["message"] = "Success"
                frappe.response["data"] = distribution_nearest
            else:
                frappe.response["code"] = 400
                frappe.response["message"] = "Request Failed"
                frappe.response["data"] = None
                
        except Exception as e:
            frappe.response["code"] = 400
            frappe.response["message"] = "Request Failed"
            frappe.response["data"] = e
    else:
        frappe.response["code"] = 400
        frappe.response["message"] = "Distance Matrix Service not Active, Please Set On API Setup"
        frappe.response["data"] = None

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

@frappe.whitelist()
def submit_hasil_jadi_real(no_wo, qty_sistem, qty_real, bahan_baku, barang_jadi, bom_no):
    check_status_wo = frappe.get_doc("Work Order", no_wo)
    status_wo = check_status_wo.status

    if status_wo != "Completed" :
        stock_entry = frappe.new_doc("Stock Entry")
        stock_entry.posting_date = frappe.utils.today()
        stock_entry.posting_time = frappe.utils.now()
        stock_entry.stock_entry_type = "Manufacture"
        stock_entry.work_order = no_wo
        stock_entry.from_bom = 1
        stock_entry.use_multi_level_bom = 0
        stock_entry.bom_no = bom_no
        stock_entry.fg_completed_qty = qty_sistem

        data_bahan_baku = bahan_baku
        for item_data in data_bahan_baku:
            stock_entry.append("items", {
                "item_code": item_data["item_code"],
                "qty": float(item_data["qty"]),
                "uom": item_data["uom"],
                "s_warehouse": "Stores - AK",
                "is_finished_item": 0
            })
            stock_entry.append("items", {
                "item_code": barang_jadi,
                "qty": float(qty_sistem),
                "qty_hasil_real": qty_real,
                "uom": "Gram",
                "t_warehouse": "Finished Goods - AK",
                "is_finished_item": 1
            })
            
        stock_entry.save()
        stock_entry.submit()
        
        frappe.response['data'] = stock_entry

    else: 
        frappe.response['data'] = "WO sudah selesai"

@frappe.whitelist()
def get_work_orders(tgl_pengiriman, slot_pengiriman):
    output = []
    production_plan = frappe.db.get_list("Custom Production Plan", pluck="name", filters=[["delivery_date", "=", tgl_pengiriman]])
    work_orders = frappe.db.get_list("Work Order", pluck="name", filters=[["production_plan", "in", production_plan]])
    for wo in work_orders:
        recipe_data = []
        work_order = frappe.get_doc("Work Order", wo)

        item_doc = frappe.get_doc("Item", work_order.production_item)
        
        if item_doc.item_group == "RMT" or item_doc.item_group == "WIP":
            for recipe in work_order.required_items :
                recipe_data.append({
                   "item_code": recipe.item_code,
                    "required_qty": recipe.required_qty,
                }) 
                
            output.append({
                "name": wo,
                "production_item": work_order.production_item,
                "qty_to_manufacture": work_order.qty,
                "bom_no": work_order.bom_no,
                "items": recipe_data
                
            })        

    frappe.response['data'] = output

@frappe.whitelist()
def create_sales_order(data):
    # try:
    output = {}
    if data.get('customer_phone_no'):
        if not frappe.db.exists("Customer", {"phone_number": data.get('customer_phone_no')}):
            cust = create_new_cust(data)
            so = make_so(data, cust.name)
        else:
            cust = frappe.get_doc("Customer", {"phone_number": data.get('customer_phone_no')})
            check_address(data, cust)
            so = make_so(data, cust.name)
        output.update({
            "sales_order_id": so.name,
            "creation": so.creation,
            "customer": so.customer,
            "customer_name": so.customer_name,
            "order_type": so.order_type,
            "transaction_date": so.transaction_date,
            "delivery_date": so.delivery_date,
            "slot_pengiriman": so.slot_pengiriman,
            "jam_pengiriman": so.jam_pengiriman,
            "online_shop_invoice_no": so.online_shop_invoice_no,
            "distribution_point": so.distribution_point,
            "nama_pic_penerima": so.nama_pic_penerima,
            "no_telepon_pic_penerima": so.no_telepon_pic_penerima,
            "shipping_address_name": so.shipping_address_name,
            "address_notes": so.address_notes,
            "order_notes": so.order_notes,
            "estimasi_jam_pengiriman": so.estimasi_jam_pengiriman,
            "customer_group": so.customer_group,
            "territory": so.territory,
            "status": so.status,
            "delivery_status": so.delivery_status,
            "total": so.total,
            "total_taxes_and_charges":so.total_taxes_and_charges,
            "grand_total": so.grand_total,
            "custom_design": so.custom_design,
            "taxes": so.taxes,
            "items": so.items
        })
    # del frappe.local.response['exc_type']
    frappe.response["code"] = 200
    frappe.response["message"] = "Success"
    frappe.response['data'] = output
    # except Exception as e:
    #     frappe.response["code"] = 400
    #     frappe.response["message"] = "Request Failed"
    #     frappe.response["data"] = e

def create_new_cust(data):
    cust = frappe.new_doc("Customer")
    cust.phone_number = data.get('customer_phone_no')
    cust.customer_name = data.get('customer_name')
    cust.customer_type = data.get('customer_type')
    cust.customer_group = data.get('customer_group')
    cust.email = data.get('email')
    if not frappe.db.exists("Territory", data.get('territory')):
        territory = frappe.new_doc("Territory")
        territory.territory_name = data.get('territory')
        territory.save()
    cust.territory = data.get('territory')
    cust.save()
    check_address(data, cust)
    return cust

def check_address(data, cust):
    address_exist = frappe.get_all(
        "Address", fields=["*"], filters={"phone": data.get('customer_phone_no'), "address_line1": data.get('address')})
    if not address_exist:
        new_address = frappe.new_doc("Address")
        new_address.address_title = data.get('customer_phone_no')
        new_address.address_type = "Shipping"
        new_address.address_line1 = data.get('address')
        new_address.city = data.get('city')
        new_address.gps_lat_customer = data.get('gps_lat_customer')
        new_address.gps_long_customer = data.get('gps_long_customer')
        new_address.phone = data.get('customer_phone_no')
        new_address.save()
        cust.db_set("customer_primary_address", new_address.name, update_modified=False)
    else:
        cust.db_set("customer_primary_address", address_exist[0].name, update_modified=False)

def make_so(data, cust_id):
    so = frappe.new_doc("Sales Order")
    so.customer = cust_id
    so.order_type = "Sales"
    so.order_type_2 = "Online Shop"
    so.transaction_date = frappe.utils.today()
    so.address_notes = data.get('address_notes')
    so.nama_pic_penerima = data.get('nama_pic_penerima')
    so.no_telepon_pic_penerima = data.get('no_telepon_pic_penerima')
    so.distribution_point = data.get('distribution_point')
    so.online_shop_invoice_no = data.get('online_shop_invoice_no')
    so.slot_pengiriman = data.get('slot_pengiriman')
    so.delivery_date = data.get('delivery_date')
    so.jam_pengiriman = data.get('jam_pengiriman')
    so.approval_code = data.get('approval_code')
    so.order_notes = data.get('order_notes')
    so.estimasi_jam_pengiriman = data.get('estimasi_jam_pengiriman')
    so.shipping_address_name = frappe.get_value("Customer", cust_id, "customer_primary_address")
    so.courier_type = data.get('courier_type')
    so.courier_company = data.get('courier_company')
    if data.get('custom_design'):
        for i in data.get('custom_design'):
            so.append('custom_design', {
                'design_type': i.get('design_type'),
                'design_file_original': i.get('design_file_original'),
                'design_file_with_order_data': i.get('design_file_with_order_data')
            })
    if data.get('order_details'):
        for j in data.get('order_details'):
            item = frappe.get_doc("Item", {"item_name": j.get('item_code')})
            if j.get('is_free_item'):
                so.append('items', {
                    'item_code': item.item_code,
                    'qty': j.get('qty'),
                    'is_free_item': True,
                    'rate': 0,
                    'amount': 0,
                    'item_category': item.shipping_item_category,
                    'size': item.shipping_point
                })
            else:
                so.append('items', {
                    'item_code': item.item_code,
                    'qty': j.get('qty'),
                    'is_free_item': False,
                    'rate': j.get('rate'),
                    'amount': int(j.get('rate')) * int(j.get('qty')),
                    'item_category': item.shipping_item_category,
                    'size': item.shipping_point
                })
    if data.get('promotions'):
         for k in data.get('promotions'):
            promotions = frappe.get_all("Promotion Program", fields=["*"], filters={"name": k['description']})
            if promotions:
                amount = k['amount']
                so.append('taxes', {
                    'charge_type': promotions[0].type,
                    'account_head': promotions[0].account_head,
                    'cost_center': promotions[0].cost_center,
                    'description': promotions[0].description,
                    'tax_amount': amount
                })

    so.save()
    so.submit()
    return so

@frappe.whitelist()
def item_category_list():
    try:
        item_category = frappe.get_all("Shipping Item Category", fields=["*"])
        output = []
        if item_category:
            for i in item_category:
                output.append(i.shipping_item_category)
        frappe.response["code"] = 200
        frappe.response["message"] = "Success"
        frappe.response['data'] = output
    except Exception as e:
        frappe.response["code"] = 400
        frappe.response["message"] = "Request Failed"
        frappe.response["data"] = e

@frappe.whitelist()
def submit_wo_kitchen(no_wo, qty_sistem, qty_real, bahan_baku, barang_jadi, bom_no):
    check_status_wo = frappe.get_doc("Work Order", no_wo)
    status_wo = check_status_wo.status

    if status_wo != "Completed" :
        stock_entry = frappe.new_doc("Stock Entry")
        stock_entry.posting_date = frappe.utils.today()
        stock_entry.posting_time = frappe.utils.now()
        stock_entry.stock_entry_type = "Manufacture"
        stock_entry.work_order = no_wo
        stock_entry.from_bom = 1
        stock_entry.use_multi_level_bom = 0
        stock_entry.bom_no = bom_no
        stock_entry.fg_completed_qty = qty_sistem
        stock_entry.from_warehouse = "Finished Goods - SM"

        data_bahan_baku = bahan_baku
        for item_data in data_bahan_baku:
            stock_entry.append("items", {
                "item_code": item_data["item_code"],
                "qty": float(item_data["qty"]),
                "uom": item_data["uom"],
                "s_warehouse": "Stores - SM",
                "is_finished_item": 0
            })
            
        stock_entry.append("items", {
            "item_code": barang_jadi,
            "qty": float(qty_sistem),
            "qty_hasil_real": float(qty_real),
            "uom": "Gram",
            "t_warehouse": "Finished Goods - SM",
            "is_finished_item": 1
        })
            
        stock_entry.save()
        stock_entry.submit()
        
        frappe.response['data'] = stock_entry
        
    else: 
        frappe.response['message'] = "WO sudah selesai"

@frappe.whitelist()
def qr_so_packing(nomor_so):
    output = []
    check_so = frappe.db.exists("Sales Order", nomor_so)
    if check_so :
        sales_order = frappe.get_doc("Sales Order", nomor_so)
        orders_data = []
        for orders in sales_order.items :
            orders_data.append({
                "item_code": orders.item_code,
                "qty": orders.qty,
            }) 
                
        output.append({
            "name": nomor_so,
            "customer": sales_order.customer_name,
            "delivery_date": sales_order.delivery_date,
            "slot_pengiriman": sales_order.slot_pengiriman,
            "jam_pengiriman": sales_order.jam_pengiriman,
            "total_qty": sales_order.total_qty,
            "data_order" : orders_data
        })
        
        frappe.response['data'] = output
    else :
        frappe.response['message'] = "data tidak ada"

@frappe.whitelist()
def qr_wo_kitchen(nomor_wo):
    output = []
    check_wo = frappe.db.exists("Work Order", nomor_wo)
    if check_wo :
        work_order = frappe.get_doc("Work Order", nomor_wo)
        recipe_data = []
        for recipe in work_order.required_items :
            recipe_data.append({
                "item_code": recipe.item_code,
                "required_qty": recipe.required_qty,
            }) 
                
        output.append({
            "name": nomor_wo,
            "production_item": work_order.production_item,
            "qty_to_manufacture": work_order.qty,
            "bom_no": work_order.bom_no,
            "items": recipe_data
        })
        
        frappe.response['data'] = output
    else :
        frappe.response['message'] = "data tidak ada"


def dist_point_check(latitude,longitude):
    base_url = "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix"

    distribution_points = frappe.get_list("Distribution Point",fields=["name","gps_lat_distribution_point","gps_long_distribution_point","address"])
            
    data = {}
    origins = []

    for origin in distribution_points:
        latitude_origin = origin["gps_lat_distribution_point"]
        longitude_origin = origin["gps_long_distribution_point"]
        origin_data = {
                "waypoint": {
                    "location": {
                        "latLng": {
                            "latitude": float(latitude_origin),
                            "longitude": float(longitude_origin)
                        }
                    }
                }
            }
        origins.append(origin_data)

    data.update({"origins": origins})

    destination = {
            "destinations": [
                {
                    "waypoint": {
                        "location": {
                            "latLng": {
                                "latitude": float(latitude),
                                "longitude": float(longitude)
                            }
                        }
                    }
                }
            ]
        }
    
    data.update(destination)
    # data.update({
    #     "travelMode": travel_mode,
    #     "routingPreference": "TRAFFIC_AWARE"
    # })
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": frappe.db.get_single_value("API Setup","api_key_distance_matrix"),
        "X-Goog-FieldMask": "originIndex,destinationIndex,duration,distanceMeters,status,condition"
    }

    distribution_nearest = {}
    response = requests.post(base_url, headers=headers, data=json.dumps(data))
    res = response.json()
    if res:
        # Find the item with the lowest distanceMeters value
        min_distance_item = min(res, key=lambda x: x["distanceMeters"])

        # Retrieve the corresponding origin index
        origin_index = min_distance_item["originIndex"]
        origin_latlong = data["origins"][origin_index]["waypoint"]["location"]["latLng"]
        distribution_nearest = frappe.get_value("Distribution Point",{'gps_lat_distribution_point': str(origin_latlong['latitude']),"gps_long_distribution_point": str(origin_latlong['longitude'])},["name","gps_lat_distribution_point","gps_long_distribution_point","address"],as_dict=1)
    
    return distribution_nearest

@frappe.whitelist()
def check_rates(data):
    try:
        res = {}
        data_order = {}
        url = "/v1/rates/couriers"
        item_orders = []
        category = []
        total_shipping_point = 0

        for i in data.get("order_details"):
            size = 0
            shipping_point = frappe.get_value("Item",{"item_name": i.get("item_code")}, "shipping_point") or 0
            size += int(shipping_point) * i.get("qty")
            total_shipping_point += int(size) or 0
            category.append(frappe.get_value("Item",{"item_name": i.get("item_code")}, "shipping_item_category"))

        tumpeng = 0
        tampah = 0
        if "Tumpeng" in category:
            shipping_item_category = "Tumpeng"
            tumpeng = 1
        elif "Tampah" in category:
            shipping_item_category = "Tampah"
            tampah = 1
        else:
            shipping_item_category = [val for val in category if val not in ["tumpeng", "tampah"]][0]

         # Logic Get Vehicle Type
        __get_vehicle_type = get_vehicle_type(int(total_shipping_point), shipping_item_category)

        # Logic Get Packaging Type
        __get_packaging_type = get_packaging_type(__get_vehicle_type.get("vehicle_type"), int(total_shipping_point), tumpeng, tampah)

        if __get_packaging_type:
            if int(__get_packaging_type.get("packaging_plastik_kecil")) > 0:
                packaging_id = "Plastik Kecil"
                item_orders.append({
                    "name" : packaging_id,
                    "description" : packaging_id,
                    "value" : 1,
                    "quantity" : int(__get_packaging_type.get("packaging_plastik_kecil")),
                    "height": frappe.get_value("Shipping Packaging", packaging_id, "dimension_height"),
                    "length": frappe.get_value("Shipping Packaging", packaging_id, "dimension_depth"),
                    "weight": frappe.get_value("Shipping Packaging", packaging_id, "dimension_weight"),
                    "width": frappe.get_value("Shipping Packaging", packaging_id, "dimension_width")
                })

            if int(__get_packaging_type.get("packaging_masterbox_kecil")) > 0:
                packaging_id = "Masterbox Kecil"
                item_orders.append({
                    "name" : packaging_id,
                    "description" : packaging_id,
                    "value" : 1,
                    "quantity" : int(__get_packaging_type.get("packaging_masterbox_kecil")),
                    "height": frappe.get_value("Shipping Packaging", packaging_id, "dimension_height"),
                    "length": frappe.get_value("Shipping Packaging", packaging_id, "dimension_depth"),
                    "weight": frappe.get_value("Shipping Packaging", packaging_id, "dimension_weight"),
                    "width": frappe.get_value("Shipping Packaging", packaging_id, "dimension_width")
                })

            if int(__get_packaging_type.get("packaging_masterbox_besar")) > 0:
                packaging_id = "Masterbox Besar"
                item_orders.append({
                    "name" : packaging_id,
                    "description" : packaging_id,
                    "value" : 1,
                    "quantity" : int(__get_packaging_type.get("packaging_masterbox_besar")),
                    "height": frappe.get_value("Shipping Packaging", packaging_id, "dimension_height"),
                    "length": frappe.get_value("Shipping Packaging", packaging_id, "dimension_depth"),
                    "weight": frappe.get_value("Shipping Packaging", packaging_id, "dimension_weight"),
                    "width": frappe.get_value("Shipping Packaging", packaging_id, "dimension_width")
                })

            # if int(__get_packaging_type.get("packaging_tumpeng")) > 0:
            #     packaging_id = "Tumpeng"
            #     item_orders.append({
            #         "name" : packaging_id,
            #         "description" : packaging_id,
            #         "value" : 0,
            #         "quantity" : int(__get_packaging_type.get("packaging_tumpeng")),
            #         "height": frappe.get_value("Shipping Packaging", packaging_id, "dimension_height"),
            #         "length": frappe.get_value("Shipping Packaging", packaging_id, "dimension_depth"),
            #         "weight": frappe.get_value("Shipping Packaging", packaging_id, "dimension_weight"),
            #         "width": frappe.get_value("Shipping Packaging", packaging_id, "dimension_width")
            #     })

        dist_point = dist_point_check(data.get("gps_lat_customer"),data.get("gps_long_customer"))

        data_order.update({
            "origin_latitude": float(dist_point.gps_lat_distribution_point),
            "origin_longitude": float(dist_point.gps_long_distribution_point),
            "destination_latitude": float(data.get("gps_lat_customer")),
            "destination_longitude": float(data.get("gps_long_customer")),
            "couriers": __get_vehicle_type.get("courier_company"),
        })

        data_order.update({
            "items": item_orders
        })

        # data_order.update({
        #     "origin_latitude": -6.2253114,
        #     "origin_longitude": 106.7993735,
        #     "destination_latitude": -6.28927,
        #     "destination_longitude": 106.77492000000007,
        #     "couriers":"grab",
        # })
        # data_order.update({
        #     "items":[{
        #     "id" : "5db7ee67382e185bd6a14608",
        #     "name" : "Black L",
        #     "image" : "",
        #     "description" : "White Shirt",
        #     "value" : 165000,
        #     "quantity" : 1,
        #     "height" : 10,
        #     "length" : 10,
        #     "weight" : 200,
        #     "width" :10
        # }]
        #     })
        
        res = base_api(url, 'POST', json.dumps(data_order))
        output = {}
        if res:
            if res["code"] == 20001009:
                for i in res["pricing"]:
                    if __get_vehicle_type.get("courier_type") == i["type"]:
                        output.update({
                            "price": i["price"],
                            "type": i["type"],
                            "service_name" : i["courier_service_name"],
                            "company": i["company"],
                            "distribution_point": dist_point.name,
                            "distribution_point_address": dist_point.address,
                            "distribution_point_latitude": dist_point.gps_lat_distribution_point,
                            "distribution_point_longitude": dist_point.gps_long_distribution_point
                        })
            else:
                output.update(res)

        frappe.response["code"] = 200
        frappe.response["http_status_code"] = 200
        frappe.response["message"] = "success"
        frappe.response["data"] = output
        
    except Exception as e:
        frappe.response["code"] = 400
        frappe.response["http_status_code"] = 400
        frappe.response["message"] = "Request Failed"
        frappe.response["data"] = e

@frappe.whitelist()
def check_items(item_code):
    items = frappe.get_list("Item",filters={"name":item_code},fields=["name","shipping_point"])
    if items:
        frappe.response["code"] = 200
        frappe.response["http_status_code"] = 200
        frappe.response["message"] = "Success"
        frappe.response["data"] = items[0]
    else:
        frappe.response["code"] = 404
        frappe.response["http_status_code"] = 404
        frappe.response["message"] = "Data Not Found"
        frappe.response["data"] = None

@frappe.whitelist()
def get_vehicle_type(total_shipping_point, shipping_category):
    result = {
        "vehicle_type": "",
        "courier_type": "",
        "courier_company": ""
    }

    shipping_point_max_motor = frappe.get_value("Delivery Vehicle Type", "Motor", "shipping_point_maximum") or 0
    shipping_point_max_mobil = frappe.get_value("Delivery Vehicle Type", "Mobil", "shipping_point_maximum") or 0
    shipping_point_max_mobil_tumpeng = frappe.get_value("Delivery Vehicle Type", "Mobil", "shipping_point_maximum_tumpeng") or 0
    shipping_point_max_mobil_tampah = frappe.get_value("Delivery Vehicle Type", "Mobil", "shipping_point_maximum_tampah") or 0
    shipping_point_max_van = frappe.get_value("Delivery Vehicle Type", "Van", "shipping_point_maximum") or 0
    shipping_point_max_van_tumpeng = frappe.get_value("Delivery Vehicle Type", "Van", "shipping_point_maximum_tumpeng") or 0
    shipping_point_max_van_tampah = frappe.get_value("Delivery Vehicle Type", "Van", "shipping_point_maximum_tampah") or 0

    if (total_shipping_point <= shipping_point_max_motor) and (shipping_category not in ["Tumpeng", "Tampah"]):
        result["vehicle_type"] = "motor"
        result["courier_type"] = "instant"
        result["courier_company"] = "gojek"

    if (shipping_category == "Tumpeng"):
        if (total_shipping_point <= shipping_point_max_mobil_tumpeng):
            result["vehicle_type"] = "mobil"
            result["courier_type"] = "instant_car"
            result["courier_company"] = "grab"
        elif (total_shipping_point > shipping_point_max_mobil_tumpeng) and (total_shipping_point <= shipping_point_max_van_tumpeng):
            result["vehicle_type"] = "van"
            result["courier_type"] = "van"
            result["courier_company"] = "deliveree"
        elif (total_shipping_point > shipping_point_max_van):
            result["vehicle_type"] = "van"
            result["courier_type"] = "van"
            result["courier_company"] = "deliveree"
    elif (shipping_category == "Tampah"):
        if (total_shipping_point <= shipping_point_max_mobil_tampah):
            result["vehicle_type"] = "mobil"
            result["courier_type"] = "instant_car"
            result["courier_company"] = "grab"
        elif (total_shipping_point > shipping_point_max_mobil_tampah) and (total_shipping_point <= shipping_point_max_van_tampah):
            result["vehicle_type"] = "van"
            result["courier_type"] = "van"
            result["courier_company"] = "deliveree"
        elif (total_shipping_point > shipping_point_max_van):
            result["vehicle_type"] = "van"
            result["courier_type"] = "van"
            result["courier_company"] = "deliveree"
    else:
        if (total_shipping_point > shipping_point_max_motor) and (total_shipping_point <= shipping_point_max_mobil):
            result["vehicle_type"] = "mobil"
            result["courier_type"] = "instant_car"
            result["courier_company"] = "grab"
        elif (total_shipping_point > shipping_point_max_mobil) and (total_shipping_point <= shipping_point_max_van):
            result["vehicle_type"] = "van"
            result["courier_type"] = "van"
            result["courier_company"] = "deliveree"
        elif (total_shipping_point > shipping_point_max_van):
            result["vehicle_type"] = "van"
            result["courier_type"] = "van"
            result["courier_company"] = "deliveree"

    return result

@frappe.whitelist()
def get_packaging_type(vehicle_type, total_shipping_point, tumpeng=None, tampah=None):
    result = {
        "packaging_plastik_kecil": 0,
        "packaging_masterbox_kecil": 0,
        "packaging_masterbox_besar": 0,
        "packaging_tumpeng": 0,
        "packaging_tampah": 0
    }

    max_packaging_plastik_kecil = frappe.get_value("Shipping Packaging", "Plastik Kecil", "kapasitas_shipping_point")
    max_packaging_masterbox_kecil = frappe.get_value("Shipping Packaging", "Masterbox Kecil", "kapasitas_shipping_point")
    max_packaging_masterbox_besar = frappe.get_value("Shipping Packaging", "Masterbox Besar", "kapasitas_shipping_point")
    max_packaging_tumpeng = 60
    max_packaging_tampah = 60

    if vehicle_type.lower() == "motor":
        max_shipping_point = frappe.get_value("Delivery Vehicle Type", "Motor", "shipping_point_maximum")
        if total_shipping_point >= 1 and total_shipping_point <= 6:
            result["packaging_plastik_kecil"] += 1
        elif total_shipping_point >= 7 and total_shipping_point <= 80:
            if max_packaging_masterbox_besar:
                temp_c = total_shipping_point/max_packaging_masterbox_besar
                result["packaging_masterbox_besar"] += floor(temp_c)
                if result["packaging_masterbox_besar"] != 0 or temp_c != 0:
                    temp_b = total_shipping_point % max_packaging_masterbox_besar
                    if temp_b >= 7:
                        if max_packaging_masterbox_kecil:
                            temp_a = temp_b/max_packaging_masterbox_kecil
                            result["packaging_masterbox_kecil"] += floor(temp_a)
                            if result["packaging_masterbox_kecil"] != 0 or temp_a != 0:
                                temp_o = temp_b % max_packaging_masterbox_kecil
                                if temp_o >= 7:
                                    result["packaging_masterbox_kecil"] += 1
                                elif temp_o != 0 and temp_o < 7:
                                    result["packaging_plastik_kecil"] = 1
                    elif temp_b != 0 and temp_b < 7:
                        result["packaging_plastik_kecil"] = 1
                else:
                    temp_b = total_shipping_point/max_packaging_masterbox_kecil
                    if temp_b != 0:
                        temp_a = temp_b % max_packaging_masterbox_kecil
                        if temp_a >= 7:
                            result["packaging_masterbox_kecil"] += 1
                        elif temp_a != 0 and temp_a < 7:
                            result["packaging_plastik_kecil"] = 1

    if vehicle_type.lower() == "mobil":
        min_shipping_point = frappe.get_value("Delivery Vehicle Type", "Motor", "shipping_point_maximum") + 1
        max_shipping_point = frappe.get_value("Delivery Vehicle Type", "Mobil", "shipping_point_maximum")

        if tumpeng:
            result["packaging_tumpeng"] += 1
        if tampah:
            result["packaging_tampah"] += 1

        if total_shipping_point >= 81 and total_shipping_point <= 240:
            temp_b = total_shipping_point/max_packaging_masterbox_kecil
            result["packaging_masterbox_kecil"] += floor(temp_b)
            if result["packaging_masterbox_kecil"] != 0 or temp_b != 0:
                temp_a = total_shipping_point % max_packaging_masterbox_kecil
                if temp_a >= 7:
                    result["packaging_masterbox_kecil"] += 1
                elif temp_a != 0 and temp_a < 7:
                    result["packaging_plastik_kecil"] = 1
            else:
                temp_a = total_shipping_point/max_packaging_plastik_kecil
                result["packaging_plastik_kecil"] = floor(temp_a)
                if result["packaging_plastik_kecil"] != 0 or temp_a != 0:
                    temp_o = total_shipping_point % max_packaging_plastik_kecil
                    if temp_o != 0:
                        result["packaging_plastik_kecil"] += 1

    if vehicle_type.lower() == "Van":
        min_shipping_point = frappe.get_value("Delivery Vehicle Type", "Mobil", "shipping_point_maximum") + 1
        max_shipping_point = frappe.get_value("Delivery Vehicle Type", "Van", "shipping_point_maximum")

        if tumpeng:
            result["packaging_tumpeng"] += 1
        if tampah:
            result["packaging_tampah"] += 1

        if total_shipping_point >= 241 and total_shipping_point <= 1512:
            temp_b = total_shipping_point / max_packaging_masterbox_kecil
            result["packaging_masterbox_kecil"] = floor(temp_b)
            if result["packaging_masterbox_kecil"] != 0 or temp_b != 0:
                temp_a = total_shipping_point % max_packaging_masterbox_kecil
                if temp_a >= 7:
                    result["packaging_masterbox_kecil"] += 1
                elif temp_a != 0 and temp_a < 7:
                    result["packaging_plastik_kecil"] = 1
            else:
                temp_a = total_shipping_point / max_packaging_plastik_kecil
                result["packaging_plastik_kecil"] = floor(temp_a)
                if result["packaging_plastik_kecil"] != 0 or temp_a != 0:
                    temp_o = total_shipping_point % max_packaging_plastik_kecil
                    if temp_o != 0:
                        result["packaging_plastik_kecil"] += 1

    print(result)
    return result

@frappe.whitelist()
def update_pick_list_status(pick_list,status):
    get_pick_list = frappe.get_doc("Catering Pick List",pick_list)
    if get_pick_list:
        get_pick_list.delivery_status = status
        get_pick_list.save()
        frappe.response["code"] = 200
        frappe.response["http_status_code"] = 200
        frappe.response["message"] = "Success"
        frappe.response["data"] = get_pick_list
    else:
        frappe.response["code"] = 404
        frappe.response["http_status_code"] = 404
        frappe.response["message"] = "Pick List Not Found"
        frappe.response["data"] = None