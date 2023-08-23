# Copyright (c) 2023, Satu Meja and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from urllib import response
from datetime import datetime

class PromotionProgram(Document):
	pass

	def validate(self):
		self.validate_promotion_name()
	
	def validate_promotion_name(self):
		session = requests.Session()
		retry = Retry(connect=3, backoff_factor=1)
		adapter = HTTPAdapter(max_retries=retry)
		session.mount('http://', adapter)
		session.mount('https://', adapter)
		session.keep_alive = False
		setup = frappe.get_doc("API Setup")
		if not setup.oauth_url_promotion or not setup.client_id_promotion or not setup.client_secret_promotion or not setup.grant_type_promotion or not setup.active_3:
			frappe.throw("API Setup is not set or inactive.")

		token = get_oauth()

		headers = {
			"Authorization": "Bearer " + token 
		}
		id_campaign = self.id_campaign
		base_url = setup.promotion_url + id_campaign

		response = session.get(base_url, headers = headers).json()
		if not response.get("name") or response.get("name") != self.description:
			frappe.throw("Description {} with ID Campaign {} is not found in voucher system please check again".format(self.description,self.id_campaign))

def get_oauth():
	session = requests.Session()
	retry = Retry(connect=3, backoff_factor=1)
	adapter = HTTPAdapter(max_retries=retry)
	session.mount('http://', adapter)
	session.mount('https://', adapter)
	session.keep_alive = False

	setup = frappe.get_doc("API Setup")

	base_url = setup.oauth_url_promotion
	headers = {
		"Content-Type": "application/json"
	}
	data = {
		"client_id": setup.client_id_promotion,
		"client_secret": setup.client_secret_promotion,
		"grant_type": setup.grant_type_promotion
	}

	response = session.post(base_url,headers=headers, data=json.dumps(data)).json()

	return response['accessToken']
