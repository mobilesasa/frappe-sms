# Mobile Sasa Integration for Frappe / ERPNext

Sends every ERPNext SMS (notifications, OTP login, SMS Center) through
[Mobile Sasa](https://mobilesasa.com): Kenyan sender IDs, KES billing,
M-Pesa top-up.

The app is a thin, honest layer over ERPNext's own SMS Settings:

- **Mobilesasa Settings** (single doctype): paste an API token, pick your
  sender ID, press *Apply to SMS Settings* — the gateway fields are written
  for you, correctly, once.
- **Send Test SMS** from the same screen proves the pipe before a customer
  notification depends on it.
- **Balance** is shown on the settings screen, fetched live.

No sending path is replaced or monkey-patched: once SMS Settings is written,
every Frappe SMS feature works exactly as documented. Removing this app
leaves SMS Settings behind, still working.

## Install

```
bench get-app https://github.com/mobilesasa/frappe-sms
bench --site yoursite install-app mobilesasa_integration
```

Manual configuration (no app needed) is documented at
https://docs.mobilesasa.com/integrations/erpnext
