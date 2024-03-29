import frappe
import json
import requests, traceback
from datetime import *
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from catering_module.public.whatsapp_api import *


def base_api(url, type, data=None):
    try:
        # TODO: create logger
        logger = frappe.logger("biteship_api", allow_site=True, file_count=10000)

        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        session.keep_alive = False

        setup = frappe.get_doc("API Setup")
        if setup.active_biteship:
            if setup.biteship_url and setup.api_key_biteship:
                url = setup.biteship_url + url
                headers = {
                    "authorization": setup.api_key_biteship,
                    "content-type": "application/json"
                }
                # TODO: Handling POST Method
                if type.upper() == "POST":
                    response = session.post(url, headers=headers, data=data, timeout=15).json()
                    return response
                elif type.upper() == "GET":
                    response = session.get(url, headers=headers, timeout=10).json()
                    return response
            else:
                frappe.throw("Please set Biteship API on API Setup")
        else:
            frappe.throw("Biteship API is not active")
    except Exception as e:
        frappe.db.rollback()
        logger.info("Error: {}".format(traceback.format_exc()))
        frappe.throw("Error: {}".format(e))


def defaultconverter(o):
    import datetime
    if len(str(o)) > 10:
        if isinstance(o, datetime.datetime):
            return o.__str__()
    else:
        if isinstance(o, datetime.date):
            return o.__str__()


def schedule_orders():
    logger = frappe.logger("schedule_orders", allow_site=True, file_count=100)
    res = {}
    url = "/v1/orders"
    delivery_date_plus_one = datetime.today().date()
    all_so = frappe.get_all("Sales Order", fields=["*"], filters={
        "delivery_date": delivery_date_plus_one.strftime("%Y-%m-%d"),
        "order_id": "",
        "biteship_status": ""
    })
    if all_so:
        for row in all_so:
            data = {}
            items = []
            so = frappe.get_doc("Sales Order", row.name)
            for item in so.items:
                items.append({
                    "id": item.item_code,
                    "name": item.item_name,
                    "image": frappe.get_value("Item", item.item_code, "image"),
                    "description": frappe.get_value("Item", item.item_code, "description"),
                    "value": item.amount,
                    "quantity": item.qty,
                    "height": frappe.get_value("Shipping Packaging", item.item_category, "dimension_height"),
                    "length": frappe.get_value("Shipping Packaging", item.item_category, "dimension_depth"),
                    "weight": frappe.get_value("Shipping Packaging", item.item_category, "dimension_weight"),
                    "width": frappe.get_value("Shipping Packaging", item.item_category, "dimension_width")
                })

            data.update({
                "shipper_contact_name": frappe.get_value("Distribution Point", so.distribution_point, "staff_name"),
                "shipper_contact_phone": frappe.get_value("Distribution Point", so.distribution_point, "staff_phone"), 
                "shipper_contact_email": frappe.db.get_single_value("Catering Module Settings", "shipper_contact_email"), 
                "shipper_organization": frappe.db.get_single_value("Catering Module Settings", "shipper_organization"), 
                "origin_contact_name": frappe.get_value("Distribution Point", so.distribution_point, "staff_name"), 
                "origin_contact_phone": frappe.get_value("Distribution Point", so.distribution_point, "staff_phone"), 
                "origin_address": frappe.get_value("Distribution Point", so.distribution_point, "address"), 
                "origin_note": "",
                "origin_coordinate": {
                    "latitude": float(frappe.get_value("Distribution Point", so.distribution_point, "gps_lat_distribution_point")),
                    "longitude": float(frappe.get_value("Distribution Point", so.distribution_point, "gps_long_distribution_point"))
                },
                "destination_contact_name": so.nama_pic_penerima, 
                "destination_contact_phone": so.no_telepon_pic_penerima,
                "destination_contact_email": frappe.get_value("Customer", so.customer, "email"),
                "destination_address": frappe.get_value("Address", so.shipping_address_name, "address_line1"), 
                "destination_note": so.address_notes,
                "destination_coordinate":{
                    "latitude": float(frappe.get_value("Address", so.shipping_address_name, "gps_lat_customer")), 
                    "longitude": float(frappe.get_value("Address", so.shipping_address_name, "gps_long_customer"))
                },
                "courier_company": so.courier_company,
                "courier_type": so.courier_type,
                "delivery_type": "scheduled",
                "delivery_date": so.delivery_date.strftime("%Y-%m-%d"),
                "delivery_time": str(so.jam_pengiriman - timedelta(minutes=int(frappe.db.get_single_value("Catering Module Settings", "schedule_delivery_biteship")))),
                "order_note": so.order_notes,
                "items": items
            })
            logger.info("so_name: {}-{}".format(so.name, data))
            res = base_api(url, 'POST', json.dumps(data, default=defaultconverter))
            logger.info("res: {}".format(res))
            if res.get('success'):
                so.db_set('order_id', res.get('id'), update_modified=False, notify=True, commit=True)
                so.db_set('courier_tracking_id', res.get('courier').get('tracking_id'), update_modified=False, notify=True, commit=True)
                so.db_set('courier_waybill_id', res.get('courier').get('waybill_id'), update_modified=False, notify=True, commit=True)
                so.db_set('courier_company', res.get('courier').get('company'), update_modified=False, notify=True, commit=True)
                so.db_set('courier_driver_name', res.get('courier').get('name'), update_modified=False, notify=True, commit=True)
                so.db_set('courier_driver_phone', res.get('courier').get('phone'), update_modified=False, notify=True, commit=True)
                so.db_set('courier_link', res.get('courier').get('link'), update_modified=False, notify=True, commit=True)
                so.db_set('biteship_status', res.get('status'), update_modified=False, notify=True, commit=True)
                so.db_set('shippment_fee', res.get('price'), update_modified=False, notify=True, commit=True)
            else:
                logger.info('Error: {}-{}'.format(res.get('error'), res.get('code')))

    return res


def request_order(name):
    logger = frappe.logger("request_order_now", allow_site=True, file_count=100)
    res = {}
    so = frappe.get_doc("Sales Order", name)
    url = "/v1/orders"
    items = []
    for item in so.items:
        items.append({
            "id": item.item_code,
            "name": item.item_name,
            "image": frappe.get_value("Item", item.item_code, "image"),
            "description": frappe.get_value("Item", item.item_code, "description"),
            "value": item.amount,
            "quantity": item.qty,
            "height": frappe.get_value("Shipping Packaging", item.item_category, "dimension_height"),
            "length": frappe.get_value("Shipping Packaging", item.item_category, "dimension_depth"),
            "weight": frappe.get_value("Shipping Packaging", item.item_category, "dimension_weight"),
            "width": frappe.get_value("Shipping Packaging", item.item_category, "dimension_width")
        })

    data = {
        "shipper_contact_name": frappe.get_value("Distribution Point", so.distribution_point, "staff_name"),
        "shipper_contact_phone": frappe.get_value("Distribution Point", so.distribution_point, "staff_phone"), 
        "shipper_contact_email": frappe.db.get_single_value("Catering Module Settings", "shipper_contact_email"), 
        "shipper_organization": frappe.db.get_single_value("Catering Module Settings", "shipper_organization"), 
        "origin_contact_name": frappe.get_value("Distribution Point", so.distribution_point, "staff_name"), 
        "origin_contact_phone": frappe.get_value("Distribution Point", so.distribution_point, "staff_phone"), 
        "origin_address": frappe.get_value("Distribution Point", so.distribution_point, "address"), 
        "origin_note": "",
        "origin_coordinate": {
            "latitude": float(frappe.get_value("Distribution Point", so.distribution_point, "gps_lat_distribution_point")),
            "longitude": float(frappe.get_value("Distribution Point", so.distribution_point, "gps_long_distribution_point"))
        },
        "destination_contact_name": so.nama_pic_penerima, 
        "destination_contact_phone": so.no_telepon_pic_penerima,
        "destination_contact_email": frappe.get_value("Customer", so.customer, "email"),
        "destination_address": frappe.get_value("Address", so.shipping_address_name, "address_line1"), 
        "destination_note": so.address_notes,
        "destination_coordinate":{
            "latitude": float(frappe.get_value("Address", so.shipping_address_name, "gps_lat_customer")), 
            "longitude": float(frappe.get_value("Address", so.shipping_address_name, "gps_long_customer"))
        },
        "courier_company": so.courier_company,
        "courier_type": so.courier_type,
        "delivery_type": "scheduled",
        "delivery_date": datetime.now(),
        "delivery_time": datetime.now(),
        "order_note": so.order_notes,
        "items": items
    }
    logger.info("so_name: {}-{}".format(so.name, data))
    res = base_api(url, 'POST', json.dumps(data, default=defaultconverter))
    logger.info("res: {}".format(res))
    if res.get('success'):
        so.db_set('order_id', res.get('id'), update_modified=False, notify=True, commit=True)
        so.db_set('courier_tracking_id', res.get('courier').get('tracking_id'), update_modified=False, notify=True, commit=True)
        so.db_set('courier_waybill_id', res.get('courier').get('waybill_id'), update_modified=False, notify=True, commit=True)
        so.db_set('courier_company', res.get('courier').get('company'), update_modified=False, notify=True, commit=True)
        so.db_set('courier_driver_name', res.get('courier').get('name'), update_modified=False, notify=True, commit=True)
        so.db_set('courier_driver_phone', res.get('courier').get('phone'), update_modified=False, notify=True, commit=True)
        so.db_set('courier_link', res.get('courier').get('link'), update_modified=False, notify=True, commit=True)
        so.db_set('biteship_status', res.get('status'), update_modified=False, notify=True, commit=True)
        so.db_set('shippment_fee', res.get('price'), update_modified=False, notify=True, commit=True)
    else:
        logger.info('Error: {}-{}'.format(res.get('error'), res.get('code')))
                    
def delivery_schedule():
    orders = frappe.get_all("Sales Order",fields=["name"],filters={"order_type_2": "Online Shop","delivery_date": frappe.utils.nowdate(),"custom_courier_status":"","order_id":"","docstatus":"1"})
    if orders:
        for order in orders:
            so = frappe.get_doc("Sales Order",order)
            jam_pengiriman = datetime.strptime(str(so.jam_pengiriman), '%H:%M:%S')
            now = datetime.strptime(str(frappe.utils.nowtime().split('.')[0]), '%H:%M:%S')
            if int((jam_pengiriman - now).total_seconds()) <= int(frappe.db.get_single_value("Catering Module Settings", "schedule_cancel_biteship"))*60:
                check_pl = frappe.db.sql("""
                            SELECT a.name, a.delivery_status 
                            FROM `tabCatering Pick List` a
                            LEFT JOIN `tabSales Order Pick List` b
                            ON a.name = b.parent 
                            WHERE b.sales_order = %s
                        """,format(so.name),as_dict=True)
                if check_pl:
                    if check_pl[0].delivery_status == "Delivered":
                        request_order(so.name)
                    else:
                        so.db_set("custom_courier_status", "Delay", update_modified=False, notify=True, commit=True)

                        whatsapp_send_delay_notif(
                            frappe.get_value("Distribution Point",so.distribution_point,"staff_phone"),
                            frappe.utils.nowdate(),
                            so.jam_pengiriman,
                            so.name
                        ) 

@frappe.whitelist(True)
def enqueue_orders():
    return frappe.enqueue("catering_module.public.biteship_api.delivery_schedule",
                queue = 'long',
                timeout = 7200,
                is_async = False
            )

# @frappe.whitelist(True)
# def enqueue_schedule_orders():
#     return frappe.enqueue("catering_module.public.biteship_api.schedule_orders",
#                 queue = 'long',
#                 timeout = 7200,
#                 is_async = False
#             )


def delete_order(id, cancellation_reason):
    logger = frappe.logger("delete_order", allow_site=True, file_count=100)
    res = {}
    data = {
        "cancellation_reason": cancellation_reason
    }
    url = "/v1/orders/{}".format(id)
    res = base_api(url, 'DELETE', json.dumps(data))
    res.update({
        "sales_order_id": id
    })
    logger.info("res: {}".format(res))


@frappe.whitelist()
def late_delivery_handling():
    all_pick_list = frappe.get_all("Catering Pick List", fields=["*"], filters={"status": "Undelivered"})
    if all_pick_list:
        for row in all_pick_list:
            pl = frappe.get_doc("Catering Pick List", row.name)
            for item in pl.locations:
                so = frappe.get_doc("Sales Order", item.sales_order)
                if so.delivery_date == frappe.utils.nowdate():
                    if (datetime.strptime(so.jam_pengiriman, '%H:%M:%S') - datetime.strptime(frappe.utils.nowtime(), '%H:%M:%S').total_seconds() <= 
                        int(frappe.db.get_single_value("Catering Module Settings", "schedule_cancel_biteship"))*60):
                        __delete_order = delete_order(so.order_id, "Change Courier")
                        so.db_set("custom_courier_status", "Delay", update_modified=False, notify=True, commit=True)
                        whatsapp_send_late_delivery_notif(
                            so.no_telepon_pic_penerima,
                            so.online_shop_invoice_no,
                            so.delivery_date.strftime("%d-%m-%Y"),
                            so.estimasi_jam_pengiriman,
                            so.courier_waybill_id,
                            so.courier_driver_name,
                            so.courier_driver_phone,
                            so.courier_link
                        ) 