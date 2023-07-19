frappe.ui.form.on('BOM Item', {
	qty: function(frm,cdt,cdn) {
		var child = locals[cdt][cdn];
        if(child.item_code){
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                  doctype: 'Item',
                  filters: { name: child.item_code },
                  fieldname: 'q_factor'
                },
                callback: function(response) {
                    var data = response.message;
                    var q_factor = data.q_factor;
                    var q_req = child.qty * (1 + q_factor);
                    frappe.model.set_value(cdt, cdn, "qty_required", q_req);
                }
              });
        }
	},
});