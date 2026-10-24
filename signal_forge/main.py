from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .clients import fetch_odds, send_telegram
from .config import Settings
from .market import find_signals, render_report


def persist(signals: list[dict], scanned_at: datetime) -> None:
    path = Path("data/signals.jsonl")
    path.parent.mkdir(exist_ok=True)
    with path.open("a", encoding="utf-8") as ledger:
        for signal in signals:
            ledger.write(json.dumps({"scanned_at": scanned_at.isoformat(), **signal}) + "\n")


def main() -> None:
    settings = Settings.from_env()
    scanned_at = datetime.now(timezone.utc)
    signals = []
    for sport_key in settings.sport_keys:
        events = fetch_odds(settings.odds_api_key, sport_key, settings.regions)
        signals.extend(find_signals(
            events, sport_key, settings.min_bookmakers, settings.min_edge,
            settings.paper_bankroll, settings.max_stake_pct,
        ))
    signals = sorted(signals, key=lambda signal: signal.expected_value, reverse=True)[:settings.max_signals]
    persist([signal.as_dict() for signal in signals], scanned_at)
    send_telegram(settings.telegram_bot_token, settings.telegram_chat_id, render_report(signals, scanned_at))
    print(f"Delivered {len(signals)} signal(s) across {len(settings.sport_keys)} leagues.")


if __name__ == "__main__":
    main()
