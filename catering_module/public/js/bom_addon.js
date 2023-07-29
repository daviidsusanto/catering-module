frappe.ui.form.on('BOM Item', {
	qty_recipe: function(frm,cdt,cdn) {
		var child = locals[cdt][cdn];
        if(child.item_code){
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                  doctype: 'Item',
                  filters: { name: child.item_code },
                  fieldname: '*'
                },
                callback: function(response) {
                    var data = response.message;
                    var q_factor = data.q_factor;
                    var q_req = child.qty_recipe * (1 + (q_factor/100));
                    frappe.model.set_value(cdt, cdn, "qty", q_req);
                }
              });
        }
	},
});