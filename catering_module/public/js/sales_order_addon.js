// frappe.ui.form.on('Sales Order', {
// 	validate: function(frm) {
// 		frappe.call({
//             method: "frappe.www.printview.get_rendered_raw_commands",
//             args: {
//                 doc: frm.doc,
//                 print_format: "Sales Order Raw Printing",
//             },
//             callback: function (r) {
//                 if (!r.exc) {
//                     let data = [r.message.raw_commands];
//                     frappe.ui.form.qz_connect()
//                     .then(function () {
//                         let config = qz.configs.create("Nama Printer");
//                         console.log(config)
//                         return qz.print(config, data);
//                     })
//                     .then(frappe.ui.form.qz_success)
//                     .catch(err => {
//                         frappe.ui.form.qz_fail(err);
//                     });
//                 }
//             },
//         });
// 	},
// });
