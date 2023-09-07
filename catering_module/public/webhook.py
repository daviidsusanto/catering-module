import frappe 
import requests
import random
import string
import json

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
                cash_on_delivery_fee = 0
                ):
    if event == "order.price":
        #update price on so
        pass
    if event == "order.status":
        #update status on so
        pass
    if event == "order.waybill_id":
        #update waybill number on so
        pass