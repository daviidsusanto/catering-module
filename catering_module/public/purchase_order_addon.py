import frappe
from frappe.model.document import Document
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from urllib import response
from datetime import datetime

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

def send_whatsapp_notif_to_supplier(doc,name):
    setup = frappe.get_doc("API Setup")
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

        parameters = ""
        for i in doc.items:
            parameters += "- " + str(i.qty) + " " + i.uom + " " + i.item_code + "\\n"

        base_url = setup.whatsapp_url

        data = {
            "identityId": 1, 
            "phoneNumber": "081381000322", 
            "name": doc.supplier, 
            "templateId": setup.template_id, 
            "parameters": [datetime.strptime(doc.transaction_date,'%Y-%m-%d').strftime('%d-%m-%Y'),parameters]
        }

        response = session.post(base_url, headers=headers, data=json.dumps(data))
        res = response.json()