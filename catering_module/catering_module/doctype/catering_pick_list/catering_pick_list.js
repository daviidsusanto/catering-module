// Copyright (c) 2023, Satu Meja and contributors
// For license information, please see license.txt

frappe.ui.form.on('Catering Pick List', {
	purpose: function(frm) {
		if(frm.doc.purpose == "Delivery" && frm.doc.docstatus == 0){
			let get_query_filters = {
				docstatus: 1,
				per_delivered: ['<', 100],
				status: ['!=', ''],
				customer: frm.doc.customer,
				order_type_2: ['=', "Online Shop"] 
			};
			frm.add_custom_button(__('Get Items'), function(){
				erpnext.utils.map_current_doc({
					method: 'catering_module.catering_module.doctype.catering_pick_list.catering_pick_list.create_pick_list',
					source_doctype: 'Sales Order',
					target: frm,
					setters: {
						delivery_date: null,
						slot_pengiriman: null,
						distribution_point: null,
					},
					date_field: 'delivery_date',
					get_query_filters: get_query_filters,
					delivery_date : get_query_filters.delivery_date,
				});
			});
		} else {
			frm.remove_custom_button('Get Items');
		}
	},
	refresh: function(frm) {
		if(frm.doc.purpose == "Delivery" && frm.doc.docstatus == 0){
			let get_query_filters = {
				docstatus: 1,
				per_delivered: ['<', 100],
				status: ['!=', ''],
				customer: frm.doc.customer,
				order_type_2: ['=', "Online Shop"] 
			};
			frm.add_custom_button(__('Get Items'), function(){
				erpnext.utils.map_current_doc({
					method: 'catering_module.catering_module.doctype.catering_pick_list.catering_pick_list.create_pick_list',
					source_doctype: 'Sales Order',
					target: frm,
					setters: {
						delivery_date: null,
						slot_pengiriman: null,
						distribution_point: null,
					},
					date_field: 'delivery_date',
					get_query_filters: get_query_filters,
				});
			});
		} else {
			frm.remove_custom_button('Get Items');
		}
	}
});
