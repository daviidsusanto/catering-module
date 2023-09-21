import frappe
import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

@frappe.whitelist()
def sign_message():
    message = frappe.request.args['message']
    # Load signature
    b64_private_key = os.environ['QZ_PRIVATE_KEY']
    private_key = base64.b64decode(b64_private_key)
    key = serialization.load_pem_private_key(private_key, None, backend=default_backend())
    # Create the signature
    signature = key.sign(message.encode('utf-8'), padding.PKCS1v15(), hashes.SHA512())  # Use hashes.SHA1() for QZ Tray 2.0 and older
    # Echo the signature
    frappe.response.type="download"
    frappe.response.content_type="text/plain"
    frappe.response.filename="certificate.crt"
    frappe.response.display_content_as="inline"
    frappe.response.filecontent=base64.b64encode(signature).decode("ascii")

@frappe.whitelist()
def qz_certificate():
    b64_private_key = os.environ['QZ_CERTIFICATE']
    cert = base64.b64decode(b64_private_key)
    # Create the signature
    # Echo the signature
    frappe.response.type="download"
    frappe.response.content_type="text/plain"
    frappe.response.display_content_as="inline"
    frappe.response.filename="signed.txt"
    frappe.response.filecontent=cert
