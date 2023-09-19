frappe.pages['qz'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Qz',
		single_column: true
	});
	const route = frappe.get_route();
	const doctype = route[1];
	const docname = route[2];
	const print_format = route[3];
	const nama_printer = route[4];
	frappe.call({
		method: "frappe.www.printview.get_rendered_raw_commands",
		args: {
			"doc": doctype,
			"name": docname,
			"print_format": print_format,
		},
		callback: function (r) {
			if (!r.exc) {
				console.log(r.message);
				var data = [r.message];
				frappe.ui.form.qz_connect()
				.then(function () {
					let config = qz.configs.create(nama_printer);
					return qz.print(config, data);
				})
				.then(frappe.ui.form.qz_success)
				.catch(err => {
					frappe.ui.form.qz_fail(err);
				});
			}
		},
	});
}