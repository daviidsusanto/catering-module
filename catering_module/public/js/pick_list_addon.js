// frappe.ui.form.on('Pick List', {
// 	refresh: function(frm) {
//         frm.trigger('remove_get_items_button');
// 	},
//     purpose: function(frm) {
//         frm.trigger('remove_get_items_button');
// 	},
//     remove_get_items_button: (frm) => {
//         frm.remove_custom_button('Get Items');
//     },

//     add_get_items_button: (frm) => {
//         if(frm.doc.purpose == "Delivery" && frm.doc.docstatus == 0){
//             let get_query_filters = {
//                 docstatus: 1,
//                 per_delivered: ['<', 100],
//                 status: ['!=', ''],
//                 customer: frm.doc.customer,
//                 order_type_2: ['=', "Online Shop"] 
//             };
//             frm.add_custom_button(__('Get Item'), () => {
//                 erpnext.utils.map_current_doc({
//                     method: 'catering_module.public.pick_list_addon.create_pick_list',
//                     source_doctype: 'Sales Order',
//                     target: frm,
//                     setters: {
//                         delivery_date: null,
//                         slot_pengiriman: null,
//                         distribution_point: null,
//                     },
//                     date_field: 'transaction_date',
//                     get_query_filters: get_query_filters
//                 });
//             });
//         }
//     }
// });