from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def _request_json(url: str, method: str = "GET", payload: dict | None = None) -> dict | list:
    data = json.dumps(payload).encode("utf-8") if payload else None
    request = Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {error.code} calling {url}: {detail}") from error
    except URLError as error:
        raise RuntimeError(f"Network error calling {url}: {error.reason}") from error


def fetch_odds(api_key: str, sport_key: str, regions: str) -> list[dict]:
    query = urlencode({"apiKey": api_key, "regions": regions, "markets": "h2h", "oddsFormat": "decimal"})
    payload = _request_json(f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?{query}")
    if not isinstance(payload, list):
        raise RuntimeError(f"Unexpected odds payload: {payload}")
    return payload


def send_telegram(token: str, chat_id: str, text: str) -> None:
    response = _request_json(f"https://api.telegram.org/bot{token}/sendMessage", "POST", {"chat_id": chat_id, "text": text})
    if not isinstance(response, dict) or not response.get("ok"):
        raise RuntimeError(f"Telegram delivery failed: {response}")
