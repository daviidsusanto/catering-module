import frappe
import json
import requests, traceback
from datetime import *
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


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
    delivery_date_plus_one = datetime.today().date() + timedelta(days=1)
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
                    "height": frappe.get_value("Catering Masterbox", item.item_category, "dimension_height"),
                    "length": frappe.get_value("Catering Masterbox", item.item_category, "dimension_length"),
                    "weight": frappe.get_value("Catering Masterbox", item.item_category, "dimension_weight"),
                    "width": frappe.get_value("Catering Masterbox", item.item_category, "dimension_width")
                })

            origin_latitude, origin_longitude = frappe.get_value("Distribution Point", so.distribution_point, "latlong").split(',') if frappe.get_value(
                "Distribution Point", so.distribution_point, "latlong") else [0,0]
            destination_latitude, destination_longitude = frappe.get_value("Address", so.shipping_address_name, "latlong").split(',') if frappe.get_value(
                "Address", so.shipping_address_name, "latlong") else [0,0]

            data.update({
                "shipper_contact_name": frappe.get_value("Distribution Point", so.distribution_point, "staff_name"),
                "shipper_contact_phone": frappe.get_value("Distribution Point", so.distribution_point, "staff_phone"), 
                "shipper_contact_email":"noreply@omara.com", 
                "shipper_organization": "Omara", 
                "origin_contact_name": frappe.get_value("Distribution Point", so.distribution_point, "staff_name"), 
                "origin_contact_phone": frappe.get_value("Distribution Point", so.distribution_point, "staff_phone"), 
                "origin_address": frappe.get_value("Distribution Point", so.distribution_point, "address"), 
                "origin_note": "",
                "origin_coordinate": {
                    "latitude": float(origin_latitude),
                    "longitude": float(origin_longitude)
                },
                "destination_contact_name": so.nama_pic_penerima, 
                "destination_contact_phone": so.no_telepon_pic_penerima,
                "destination_contact_email": "",
                "destination_address": frappe.get_value("Address", so.shipping_address_name, "address_line1"), 
                "destination_note": so.address_notes,
                "destination_coordinate":{
                    "latitude": float(destination_latitude), 
                    "longitude": float(destination_longitude)
                },
                "courier_company": "grab",
                "courier_type": so.courier_type,
                "delivery_type": "scheduled",
                "delivery_date": so.delivery_date.strftime("%Y-%m-%d"),
                "delivery_time": str(so.jam_pengiriman),
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


@frappe.whitelist(True)
def enqueue_schedule_orders():
    return frappe.enqueue("catering_module.public.biteship_api.schedule_orders",
                queue = 'long',
                timeout = 7200,
                is_async = False
            )
