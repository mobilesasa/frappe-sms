# Mobilesasa Settings: the one screen this app owns.
#
# The app deliberately does NOT replace Frappe's sending path. ERPNext's own
# SMS Settings is a perfectly good generic gateway; what people get wrong is
# filling its five fields in. So this doctype holds the two values a human
# actually knows (token, sender), and apply_to_sms_settings() writes the rest.
# Uninstalling the app leaves SMS Settings behind, still working.

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.password import get_decrypted_password

from mobilesasa_integration import sdk

API_BASE = "https://api.mobilesasa.com"


class MobilesasaSettings(Document):
	pass


def _client() -> sdk.Client:
	token = get_decrypted_password(
		"Mobilesasa Settings", "Mobilesasa Settings", "api_token", raise_exception=False
	) or ""
	if not token:
		frappe.throw(_("Add your Mobile Sasa API token first."))
	return sdk.Client(token, user_agent="mobilesasa-frappe/" + sdk.__version__)


@frappe.whitelist()
def get_balance():
	"""SMS unit balance, for the settings screen."""
	frappe.only_for("System Manager")
	res = _client().balance()
	if sdk.ok(res) and "balance" in res:
		return {"ok": True, "balance": res["balance"]}
	return {"ok": False, "message": res.get("message", _("Could not reach Mobile Sasa."))}


@frappe.whitelist()
def send_test_sms(phone: str):
	"""Prove the pipe before a customer notification depends on it."""
	frappe.only_for("System Manager")
	settings = frappe.get_single("Mobilesasa Settings")
	if not settings.sender_id:
		frappe.throw(_("Set a sender ID first."))
	res = _client().send(
		settings.sender_id,
		phone,
		_("Test message from {0} via Mobile Sasa. Your site is connected.").format(
			frappe.local.site
		),
	)
	if sdk.ok(res):
		return {"ok": True, "message": _("Sent. Check the handset.")}
	return {"ok": False, "message": res.get("message", _("Send failed."))}


@frappe.whitelist()
def apply_to_sms_settings():
	"""Write ERPNext's SMS Settings so every SMS feature routes through
	Mobile Sasa. Idempotent: running it again rewrites the same values."""
	frappe.only_for("System Manager")
	settings = frappe.get_single("Mobilesasa Settings")
	token = get_decrypted_password(
		"Mobilesasa Settings", "Mobilesasa Settings", "api_token", raise_exception=False
	) or ""
	if not token or not settings.sender_id:
		frappe.throw(_("Set the API token and sender ID first."))

	sms = frappe.get_doc("SMS Settings")
	sms.sms_gateway_url = API_BASE + "/v1/send/messageget"
	sms.message_parameter = "message"
	sms.receiver_parameter = "phone"
	# GET, not POST: /v1/send/messageget is the query-parameter endpoint.
	if hasattr(sms, "use_post"):
		sms.use_post = 0
	sms.set("parameters", [])
	sms.append("parameters", {"parameter": "senderID", "value": settings.sender_id})
	sms.append("parameters", {"parameter": "api_token", "value": token})
	sms.save(ignore_permissions=False)
	frappe.db.commit()
	return {"ok": True, "message": _("SMS Settings written. Every ERPNext SMS now goes through Mobile Sasa.")}
