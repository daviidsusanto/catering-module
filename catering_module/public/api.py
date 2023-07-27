import frappe 

@frappe.whitelist()
def list_work_order(tgl_pengiriman, slot_pengiriman):
    output = []
    sales_order = frappe.db.get_list("Sales Order", pluck="name", filters=[["delivery_date","=",tgl_pengiriman],["slot_pengiriman","=",slot_pengiriman],["docstatus","=",1]])
    if sales_order:
        work_orders = frappe.db.get_list("Work Order", pluck="name", filters=[["sales_order", "in", sales_order]])
        for i in work_orders:
            required_items_data = []
            wo = frappe.get_doc("Work Order",i)
            for j in wo.required_items:
                required_items_data.append({
                    "item_code": j.item_code,
                    "required_qty": j.required_qty,
                })
            output.append({
                "name": wo.name,
                "production_item": wo.production_item,
                "items": required_items_data,
                "delivery_date": tgl_pengiriman,
                "slot_pengiriman": slot_pengiriman,
                "item_group": frappe.get_value("Item", {"item_code": wo.production_item},"item_group")
            })

    frappe.response['data'] = output