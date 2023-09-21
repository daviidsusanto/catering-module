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
        qz.security.setCertificatePromise(function (resolve, reject) {
          fetch(
            "http://dev-erpnext.amarakitchen.work:2052/api/method/catering_module.public.qz_signing.qz_certificate",
            {
              method: "POST",
              headers: {
                Authorization: "token 5e51c01b702e376:72edc7ad1f72fe5",
              },
              cache: "no-store",
            }
          )
            .then(function (response) {
              if (response.ok) {
                return response.text();
              } else {
                reject("Failed to fetch certificate");
              }
            })
            .then(function (data) {
              resolve(data);
            })
            .catch(function (error) {
              reject(error);
            });
        });

        // qz.security.setSignatureAlgorithm("SHA512"); // Since 2.1
        qz.security.setSignaturePromise(function (toSign) {
          return function (resolve, reject) {
            fetch(
              "http://dev-erpnext.amarakitchen.work:2052/api/method/catering_module.public.qz_signing.sign_message?message=" +
                toSign,
              {
                method: "POST",
                headers: {
                  Authorization: "token 5e51c01b702e376:72edc7ad1f72fe5",
                },
                cache: "no-store",
              }
            )
              .then(function (response) {
                if (response.ok) {
                  return response.text();
                } else {
                  reject("Failed to fetch signature");
                }
              })
              .then(function (data) {
                resolve(data);
              })
              .catch(function (error) {
                reject(error);
              });
          };
        });
        frappe.ui.form
          .qz_connect()
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
