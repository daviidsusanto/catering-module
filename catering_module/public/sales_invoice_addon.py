import frappe
from frappe.model.document import Document
import json

def change_coa_free_item(doc,name):
    for i in doc.items:
        if i.is_free_item:
            promotion_program = frappe.get_value("Promotion Program",i.promotion_name,"account_head")
            if promotion_program:
                i.expense_account = promotion_program