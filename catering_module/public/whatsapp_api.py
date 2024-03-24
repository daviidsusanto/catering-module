import frappe
import json
import requests, traceback
from datetime import *
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


def get_oauth():
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.keep_alive = False

    setup = frappe.get_doc("API Setup")

    base_url = setup.oauth_url
    data = {
        "client_id": setup.client_id,
        "client_secret": setup.client_secret,
        "grant_type": setup.grant_type
    }
    response = session.post(base_url, data=data).json()

    return response['access_token']


def whatsapp_send_notif_order(phone_no, no_invoice, tgl_pengiriman, jam_pengiriman, nama_kurir, kontak_kurir, tracking_link):
    setup = frappe.get_doc("API Setup")
    if not setup.oauth_url or not setup.client_id or not setup.client_secret or not setup.grant_type or not setup.active_2:
        frappe.throw("API Setup is not set or inactive.")

    if setup.active_2:
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        session.keep_alive = False

        oauth = get_oauth()

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + oauth
        }

        parameters = """No Invoice: {}\\nTgl Pengiriman: {}\\nJam Pengiriman: {}\\n\\nNama Kurir: {}\\nKontak Kurir: {}\\n\\nKakak bisa tracking progress pengiriman dengan klik link berikut:\\n{}""".format(
            no_invoice, tgl_pengiriman, jam_pengiriman, nama_kurir, kontak_kurir, tracking_link)

        base_url = setup.whatsapp_url
        data = {
            "identityId": 1,
            "phoneNumber": phone_no,
            "name": no_invoice,
            "templateId": setup.template_id_order,
            "parameters": [parameters]
        }

        response = session.post(base_url, headers=headers, data=json.dumps(data))
        res = response.json()

def whatsapp_send_late_delivery_notif(phone_no, no_invoice, tgl_pengiriman, jam_pengiriman, nama_kurir, kontak_kurir, tracking_link):
    setup = frappe.get_doc("API Setup")
    if not setup.oauth_url or not setup.client_id or not setup.client_secret or not setup.grant_type or not setup.active_2:
        frappe.throw("API Setup is not set or inactive.")

    if setup.active_2:
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        session.keep_alive = False

        oauth = get_oauth()

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + oauth
        }

        parameters = """No Invoice: {}\\nTgl Pengiriman: {}\\nJam Pengiriman: {}\\n\\nNama Kurir: {}\\nKontak Kurir: {}\\n\\nKakak bisa tracking progress pengiriman dengan klik link berikut:\\n{}""".format(
            no_invoice, tgl_pengiriman, jam_pengiriman, nama_kurir, kontak_kurir, tracking_link)

        base_url = setup.whatsapp_url
        data = {
            "identityId": 1,
            "phoneNumber": phone_no,
            "name": no_invoice,
            "templateId": setup.template_id_order,
            "parameters": [parameters]
        }

        response = session.post(base_url, headers=headers, data=json.dumps(data))
        res = response.json()

def whatsapp_send_delay_notif(phone_no, tgl_pengiriman, jam_pengiriman, order_id):
    setup = frappe.get_doc("API Setup")
    if not setup.oauth_url or not setup.client_id or not setup.client_secret or not setup.grant_type or not setup.active_2:
        frappe.throw("API Setup is not set or inactive.")

    if setup.active_2:
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        session.keep_alive = False

        oauth = get_oauth()

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + oauth
        }

        parameters = """Delay Order Dengan Detail Seperti Berikut: \\n\\nTgl Pengiriman: {}\\nJam Pengiriman: {}\\nOrder ID: {}\\n""".format(
            tgl_pengiriman, jam_pengiriman, order_id)

        base_url = setup.whatsapp_url
        data = {
            "identityId": 1,
            "phoneNumber": phone_no,
            "name": "Delay Order",
            "templateId": setup.template_delay_order,
            "parameters": [parameters]
        }

        response = session.post(base_url, headers=headers, data=json.dumps(data))
        res = response.json()
