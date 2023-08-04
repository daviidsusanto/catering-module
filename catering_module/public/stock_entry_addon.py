import frappe
from frappe.model.document import Document
import json
import math

def validate_qty(doc,name):
    if doc.work_order:
        for i in doc.items:
            if i.t_warehouse:
                if i.qty_hasil_real > i.qty:
                    i.yields = i.qty_hasil_real / i.qty
                    i.qty_kelebihan = i.qty_hasil_real - i.qty

                if i.qty_hasil_real < i.qty:
                    i.yields = i.qty_hasil_real / i.qty
                    unfinished = frappe.db.sql("""
                        SELECT two.name
                        FROM `tabWork Order Item` twoi
                        LEFT JOIN `tabWork Order` two 
                        ON twoi.parent  = two.name 
                        WHERE twoi.item_code = %s AND two.status = "Not Started" AND two.slot_pengiriman = %s
                    """,(i.item_code,frappe.get_value("Work Order",{"name":doc.work_order},"slot_pengiriman")))
                    yields = i.qty_hasil_real / i.qty
                    frappe.msgprint("<b>Item Name:</b> {}, <b>Yield% :</b> {:.2f}, <b>Unfinished Work Order :</b> {}".format(i.item_code,yields,unfinished))
        # doc.save()
    
def auto_create_se_for_kelebihan_qty(doc,name):
    if doc.work_order:
        list_items = []
        for i in doc.items:
            if i.t_warehouse:
                if i.qty_hasil_real > i.qty:
                    list_items.append({
                        "item_code": i.item_code,
                        "qty_hasil_real": i.qty_hasil_real,
                        "qty_kelebihan": i.qty_kelebihan,
                        "qty": i.qty,
                        "t_warehouse": i.t_warehouse,
                    })
        if list_items:
            se = frappe.new_doc("Stock Entry")
            se.stock_entry_type = "Material Receipt"
            for i in list_items:
                se.append("items",{
                    "t_warehouse": i["t_warehouse"],
                    "item_code": i["item_code"],
                    "qty_hasil_real": i["qty_kelebihan"],
                    "qty": i["qty_kelebihan"],
                    "expense_account": frappe.db.get_value("Item", i["item_code"],"coa_selisih_kelebihan_produksi")
                })
            se.save()
            se.submit()

