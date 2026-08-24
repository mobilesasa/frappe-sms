"""Vendored copy of shared/sdk-python (mobilesasa). Keep in sync by copying,
not importing: a Frappe app must be installable from its own tree alone."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

__version__ = "1.0.0"


def ok(response: dict) -> bool:
    """True when the envelope says the call succeeded."""
    return response.get("status") is True and response.get("responseCode") == "0200"


class Client:
    def __init__(
        self,
        token: str,
        user_agent: str = "mobilesasa-frappe/1.0.0",
        base_url: str = "https://api.mobilesasa.com",
    ) -> None:
        self.token = token.strip()
        self.base_url = base_url.rstrip("/")
        self.user_agent = user_agent

    def send(self, sender_id: str, phone: str, message: str) -> dict:
        return self._post("/v1/send/message", {
            "senderID": sender_id, "phone": phone, "message": message,
        })

    def balance(self) -> dict:
        return self._request("GET", "/v1/get-balance/")

    def _post(self, path: str, body: dict) -> dict:
        return self._request("POST", path, body)

    def _request(self, method: str, path: str, body: dict | None = None) -> dict:
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(
            self.base_url + path,
            data=data,
            method=method,
            headers={
                "Authorization": "Bearer " + self.token,
                "Accept": "application/json",
                "User-Agent": self.user_agent,
                **({"Content-Type": "application/json"} if data else {}),
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read()
        except urllib.error.HTTPError as e:
            raw = e.read()
        except urllib.error.URLError as e:
            return {"status": False, "responseCode": "0000",
                    "message": f"Network error: {e.reason}"}
        try:
            decoded = json.loads(raw)
        except ValueError:
            return {"status": False, "responseCode": "0000",
                    "message": "Unreadable response from the API"}
        return decoded if isinstance(decoded, dict) else {
            "status": False, "responseCode": "0000", "message": "Unexpected response shape"}
