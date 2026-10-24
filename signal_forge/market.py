from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from statistics import median
from typing import Any


@dataclass(frozen=True)
class Signal:
    event_id: str
    commence_time: str
    home_team: str
    away_team: str
    selection: str
    bookmaker: str
    odds: float
    fair_probability: float
    expected_value: float
    consensus_books: int
    paper_stake: float

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _fair_probabilities(outcomes: list[dict[str, Any]]) -> dict[str, float] | None:
    prices = {item.get("name"): float(item.get("price", 0)) for item in outcomes}
    if len(prices) < 2 or any(price <= 1 for price in prices.values()):
        return None
    implied = {name: 1 / price for name, price in prices.items()}
    overround = sum(implied.values())
    return {name: probability / overround for name, probability in implied.items()}


def find_signals(events: list[dict[str, Any]], min_books: int, min_edge: float, bankroll: float, max_stake_pct: float) -> list[Signal]:
    signals: list[Signal] = []
    for event in events:
        market_rows: list[tuple[str, dict[str, float], dict[str, float]]] = []
        for bookmaker in event.get("bookmakers", []):
            h2h = next((market for market in bookmaker.get("markets", []) if market.get("key") == "h2h"), None)
            if not h2h:
                continue
            fair = _fair_probabilities(h2h.get("outcomes", []))
            quoted = {item.get("name"): float(item.get("price", 0)) for item in h2h.get("outcomes", [])}
            if fair:
                market_rows.append((bookmaker.get("title", bookmaker.get("key", "Unknown")), fair, quoted))
        if len(market_rows) < min_books:
            continue
        names = set.intersection(*(set(row[1]) for row in market_rows))
        for selection in names:
            fair_probability = median(row[1][selection] for row in market_rows)
            bookmaker, _, quote = max((row for row in market_rows if selection in row[2]), key=lambda row: row[2][selection])
            odds = quote[selection]
            expected_value = fair_probability * odds - 1
            if expected_value < min_edge:
                continue
            kelly = max(0.0, expected_value / (odds - 1))
            fraction = min(kelly * 0.25, max_stake_pct)
            signals.append(Signal(
                event_id=event["id"], commence_time=event["commence_time"], home_team=event["home_team"],
                away_team=event["away_team"], selection=selection, bookmaker=bookmaker, odds=odds,
                fair_probability=fair_probability, expected_value=expected_value, consensus_books=len(market_rows),
                paper_stake=bankroll * fraction,
            ))
    return sorted(signals, key=lambda signal: signal.expected_value, reverse=True)


def render_report(signals: list[Signal], sport_key: str, scanned_at: datetime) -> str:
    heading = f"📊 Signal Forge — paper scan\n{sport_key} · {scanned_at:%Y-%m-%d %H:%M UTC}"
    if not signals:
        return heading + "\n\nNo qualifying paper signals. Filters are working; no action recommended."
    lines = [heading, "", "Educational research only — not betting advice."]
    for index, signal in enumerate(signals, 1):
        lines.extend(("", f"{index}. {signal.home_team} vs {signal.away_team}",
            f"   Pick: {signal.selection} @ {signal.odds:.2f} ({signal.bookmaker})",
            f"   Fair p: {signal.fair_probability:.1%} | EV: {signal.expected_value:.1%} | Consensus: {signal.consensus_books} books",
            f"   Paper stake reference: {signal.paper_stake:.2f}"))
    lines.append("\nTrack closing prices and results before risking money.")
    return "\n".join(lines)
