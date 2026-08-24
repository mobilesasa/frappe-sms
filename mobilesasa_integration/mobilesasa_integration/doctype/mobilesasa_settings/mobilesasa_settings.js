// The settings screen's three verbs: apply, test, and show the balance.
// Everything talks to whitelisted methods in mobilesasa_settings.py.

frappe.ui.form.on("Mobilesasa Settings", {
	refresh(frm) {
		frm.add_custom_button(__("Apply to SMS Settings"), () => {
			frappe.call({
				method: "mobilesasa_integration.mobilesasa_integration.doctype.mobilesasa_settings.mobilesasa_settings.apply_to_sms_settings",
				freeze: true,
				callback: (r) => {
					const res = r.message || {};
					frappe.msgprint({
						message: res.message || __("Done."),
						indicator: res.ok ? "green" : "red",
					});
				},
			});
		}).addClass("btn-primary");

		frm.add_custom_button(__("Send Test SMS"), () => {
			frappe.prompt(
				{ fieldname: "phone", fieldtype: "Data", label: __("Phone number"), reqd: 1 },
				(values) => {
					frappe.call({
						method: "mobilesasa_integration.mobilesasa_integration.doctype.mobilesasa_settings.mobilesasa_settings.send_test_sms",
						args: { phone: values.phone },
						freeze: true,
						callback: (r) => {
							const res = r.message || {};
							frappe.msgprint({
								message: res.message || __("Done."),
								indicator: res.ok ? "green" : "red",
							});
						},
					});
				},
				__("Send a test"),
				__("Send")
			);
		});

		// Balance, best effort: an unreachable API renders a sentence, not a
		// broken screen.
		const wrapper = frm.get_field("configured_html").$wrapper;
		wrapper.html(`<p class="text-muted">${__("Checking balance…")}</p>`);
		frappe.call({
			method: "mobilesasa_integration.mobilesasa_integration.doctype.mobilesasa_settings.mobilesasa_settings.get_balance",
			callback: (r) => {
				const res = r.message || {};
				if (res.ok) {
					wrapper.html(
						`<p><strong>${frappe.utils.escape_html(String(res.balance))}</strong> ${__("SMS units remaining")}</p>
						 <p><a href="https://account.mobilesasa.com/dashboard/units/ledger/fund" target="_blank" rel="noopener">${__("Top up")}</a></p>`
					);
				} else {
					wrapper.html(`<p class="text-muted">${frappe.utils.escape_html(res.message || "")}</p>`);
				}
			},
			error: () => wrapper.html(`<p class="text-muted">${__("Not connected yet.")}</p>`),
		});
	},
});
