frappe.ui.form.on('Sales Order', {
	on_submit: function(frm) {
	  frappe.call({
            method: "frappe.www.printview.get_rendered_raw_commands",
            args: {
              doc: frm.doc,
              print_format: "Sticker Master Box",
            },
            callback: function (r) {
              if (!r.exc) {
                var data = [r.message.raw_commands];
                frappe.ui.form
                  .qz_init()
                  .then(function () {
                    qz.security.setCertificatePromise(function (resolve, reject) {
                      fetch(
                        "/api/method/catering_module.public.qz_signing.qz_certificate",
                        {
                          withCredential: true,
                        }
                      )
                        .then((_) => _.text())
                        .then(resolve)
                        .catch(reject);
                    });
        
                    // qz.security.setSignatureAlgorithm("SHA512"); // Since 2.1
                    qz.security.setSignaturePromise(function (toSign) {
                      return function (resolve, reject) {
                        fetch(
                          "/api/method/catering_module.public.qz_signing.sign_message?request=" +
                            toSign,
                          {
                            withCredential: true,
                          }
                        )
                          .then((_) => _.text())
                          .then(resolve)
                          .catch(reject);
                      };
                    });
        
                    return qz.websocket.connect();
                  })
                  .then(function () {
                    let config = qz.configs.create("Datamax-O'Neil E-4205A Mark III");
                    return qz.print(config, data);
                  })
                  .then(frappe.ui.form.qz_success)
                  .catch((err) => {
                    frappe.ui.form.qz_fail(err);
                  });
                  return qz.websocket.disconnect();
                  
              }
            },
          });
    }
})
