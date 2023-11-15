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
                    unfinished = frappe.db.sql("""
                        SELECT  two.name, twoi.item_code, two.bom_no, twoi.name as 'woi_name', twoi.required_qty from `tabWork Order` two 
                        LEFT JOIN`tabCustom Production Plan` tcpp 
                        ON two.custom_production_plan  = tcpp.name
                        LEFT JOIN `tabWork Order Item` twoi 
                        ON two.name = twoi.parent
                        WHERE two.custom_production_plan = %s AND two.status = 'Not Started' AND twoi.item_code = %s
                    """,(frappe.get_value("Work Order",{'name': doc.work_order},'custom_production_plan'),i.item_code), as_dict= 1)
                    formatted_string = ', '.join(item['name'] for item in unfinished)
                    
                    qty_required_on_bom = 0
                    yields_bom = 0
                    for x in unfinished:
                        qty_required_on_bom += x["required_qty"]

                    yields_bom = i.qty_hasil_real / qty_required_on_bom

                    for y in unfinished:
                        if yields_bom and i.qty_hasil_real < qty_required_on_bom :
                            frappe.db.sql(
                                """UPDATE `tabWork Order Item`
                                set qty_for_print = %s, yield = %s WHERE name = %s""",
                                ((y['required_qty'] * yields_bom), yields_bom, y['woi_name']),
                            )
                    i.yields = yields_bom

                    frappe.msgprint("<b>Item Name:</b> {}, <b>Yield% :</b> {:.2f}, <b>Unfinished Work Order :</b> {}".format(i.item_code,yields_bom,formatted_string))

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

