import frappe 
import requests
import random
import string
import json
from catering_module.public.whatsapp_api import whatsapp_send_notif_order


@frappe.whitelist()
def biteship_order_hook(
                event,
                courier_tracking_id,
                courier_waybill_id,
                order_id,
                status,
                courier_company = None,
                courier_type = None,
                courier_driver_name = None,
                courier_driver_phone = None,
                courier_link = None,
                order_price = 0,
                proof_of_delivery_fee = 0,
                shippment_fee = 0,
                price = 0,
                cash_on_delivery_fee = 0
                ):
    try:
        if frappe.request.method != "POST":
            frappe.response["code"] = 405
            frappe.response["http_status_code"] = 405
            frappe.response["message"] = "Method Not Allowed"
            frappe.response["data"] = None
            return 

        if not order_id:
            frappe.response["code"] = 400
            frappe.response["http_status_code"] = 400
            frappe.response["message"] = "Order ID is Mandatory"
            frappe.response["data"] = None
            return 

        so_name = frappe.get_value("Sales Order",{"order_id": order_id},"name")
        if not so_name:
            frappe.response["code"] = 404
            frappe.response["http_status_code"] = 404
            frappe.response["message"] = "Order ID Not Found in system"
            frappe.response["data"] = {'order_id': order_id}
            return 

        sales_order = frappe.get_doc("Sales Order",so_name)
        if sales_order:
            if event == "order.status":
                sales_order.courier_tracking_id = courier_tracking_id
                sales_order.courier_waybill_id = courier_waybill_id
                sales_order.courier_company = courier_company
                sales_order.courier_type = courier_type
                sales_order.courier_driver_name = courier_driver_name
                sales_order.courier_driver_phone = courier_driver_phone
                sales_order.courier_link = courier_link
                sales_order.order_price = order_price
                sales_order.biteship_status = status
                sales_order.save()
                if status == "dropping_off":
                    whatsapp_send_notif_order(
                        sales_order.no_telepon_pic_penerima,
                        sales_order.online_shop_invoice_no,
                        sales_order.delivery_date.strftime("%d-%m-%Y"),
                        sales_order.courier_waybill_id,
                        sales_order.courier_driver_name,
                        sales_order.courier_driver_phone,
                        sales_order.courier_link
                    )
                frappe.response["code"] = 200
                frappe.response["message"] = "success"
                frappe.response["data"] = {'order_id': order_id, 'event': event}

            if event == "order.price":
                sales_order.courier_tracking_id = courier_tracking_id
                sales_order.courier_waybill_id = courier_waybill_id
                sales_order.biteship_status = status
                sales_order.order_price = price
                sales_order.cash_on_delivery_fee = cash_on_delivery_fee
                sales_order.proof_of_delivery_fee = proof_of_delivery_fee
                sales_order.shippment_fee = shippment_fee
                sales_order.save()
                frappe.response["code"] = 200
                frappe.response["message"] = "success"
                frappe.response["data"] = {'order_id': order_id, 'event': event}
            
            if event == "order.waybill_id":
                sales_order.courier_tracking_id = courier_tracking_id
                sales_order.courier_waybill_id = courier_waybill_id
                sales_order.biteship_status = status
                sales_order.save()
                frappe.response["code"] = 200
                frappe.response["message"] = "success"
                frappe.response["data"] = {'order_id': order_id, 'event': event}

    except Exception as e:
        frappe.response["code"] = 400
        frappe.response["http_status_code"] = 400
        frappe.response["message"] = "Request Failed"
        frappe.response["data"] = e