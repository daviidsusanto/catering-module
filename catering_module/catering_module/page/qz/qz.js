frappe.pages["qz"].on_page_load = function (wrapper) {
  var page = frappe.ui.make_app_page({
    parent: wrapper,
    title: "Qz",
    single_column: true,
  });
  const route = frappe.get_route();
  const doctype = route[1];
  const docname = route[2];
  const print_format = route[3];
  const nama_printer = route[4];
  frappe.call({
    method: "frappe.www.printview.get_rendered_raw_commands",
    args: {
      doc: doctype,
      name: docname,
      print_format: print_format,
    },
    callback: function (r) {
      if (!r.exc) {
        console.log(r.message);
        var data = [r.message];
        frappe.ui.form
          .qz_init()
          .then(function () {
            qz.security.setCertificatePromise(function (resolve, reject) {
              frappe.call({
                method: "catering_module.public.qz_signing.qz_certificate",
                success: resolve,
                error: reject,
              });
            });

            // qz.security.setSignatureAlgorithm("SHA512"); // Since 2.1
            qz.security.setSignaturePromise(function (toSign) {
              return function (resolve, reject) {
                frappe.call({
                  method: "catering_module.public.qz_signing.sign_message",
                  args: { message: toSign },
                  success: resolve,
                  error: reject,
                });
              };
            });

            return qz.websocket.connect();
          })
          .then(function () {
            let config = qz.configs.create(nama_printer);
            return qz.print(config, data);
          })
          .then(frappe.ui.form.qz_success)
          .catch((err) => {
            frappe.ui.form.qz_fail(err);
          });
      }
    },
  });
};
