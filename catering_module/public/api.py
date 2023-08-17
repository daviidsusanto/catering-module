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
    output = {}
    if data.get('customer_phone_no'):
        if not frappe.db.exists("Customer", {"phone_number": data.get('customer_phone_no')}):
            cust = create_new_cust(data)
            so = make_so(data, cust.name)
        else:
            cust = frappe.get_doc("Customer", {"phone_number": data.get('customer_phone_no')})
            check_address(data, cust)
            so = make_so(data, cust.name)

        output = so

    frappe.response['data'] = output


def create_new_cust(data):
    cust = frappe.new_doc("Customer")
    cust.phone_number = data.get('customer_phone_no')
    cust.customer_name = data.get('customer_name')
    cust.customer_type = data.get('customer_type')
    cust.customer_group = data.get('customer_group')
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
        new_address.phone = data.get('customer_phone_no')
        # new_address.append('links',{
        #     'link_doctype': 'Customer',
        #     'link_name': cust.name
        # })
        new_address.save()
        cust.db_set("customer_primary_address", new_address.name, update_modified=False)
    else:
        cust.db_set("customer_primary_address", address_exist[0].name, update_modified=False)


def make_so(data, cust_id):
    so = frappe.new_doc("Sales Order")
    so.customer = cust_id
    so.order_type = "Sales"
    so.transaction_date = frappe.utils.today()
    so.address_notes = data.get('address_notes')
    so.nama_pic_penerima = data.get('nama_pic_penerima')
    so.no_telepon_pic_penerima = data.get('no_telepon_pic_penerima')
    so.distribution_point = data.get('distribution_point')
    so.online_shop_invoice_no = data.get('online_shop_invoice_no')
    so.slot_pengiriman = data.get('slot_pengiriman')
    so.delivery_date = data.get('delivery_date')
    so.jam_pengiriman = data.get('jam_pengiriman')
    so.order_notes = data.get('order_notes')
    if data.get('custom_design'):
        for i in data.get('custom_design'):
            so.append('custom_design', {
                'design_type': i.get('design_type'),
                'design_file_original': i.get('design_file_original'),
                'design_file_with_order_data': i.get('design_file_with_order_data')
            })
    if data.get('order_details'):
        for j in data.get('order_details'):
            if not j.get('is_free_item'):
                so.append('items', {
                    'item_code': j.get('item_code'),
                    'qty': j.get('qty'),
                    'is_free_item': True,
                    'rate': 0,
                    'amount': 0
                })
            else:
                so.append('items', {
                    'item_code': j.get('item_code'),
                    'qty': j.get('qty'),
                    'is_free_item': False,
                    'rate': j.get('rate')
                })
    promotions = frappe.get_all("Promotion Program", fields=["*"])
    if promotions:
        for k in promotions:
            so.append('taxes', {
                'charge_type': k['type'],
                'account_head': k['account_head'],
                'cost_center': k['cost_center'],
                'description': k['description'],
                'tax_amount': 15 / 100
            })
    # SHIPPING FEE
    so.append('taxes', {
        'charge_type': 'Actual',
        'account_head': '5110.001 - Biaya BBM - AK',
        'cost_center': 'Main - AK',
        'description': 'Ongkir',
        'tax_amount': data.get('ongkir_amount') if data.get('ongkir_amount') else 0
    })
    so.save()
    return so