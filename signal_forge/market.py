from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from statistics import median
from typing import Any

MARKETS = {"h2h": "1X2", "totals": "Goals O/U", "spreads": "Handicap"}


@dataclass(frozen=True)
class Signal:
    event_id: str
    sport_key: str
    commence_time: str
    home_team: str
    away_team: str
    market: str
    selection: str
    bookmaker: str
    odds: float
    fair_probability: float
    expected_value: float
    consensus_books: int
    paper_stake: float

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _selection_label(market_key: str, outcome: dict[str, Any]) -> str | None:
    name = outcome.get("name")
    if not name:
        return None
    if market_key == "h2h":
        return str(name)
    point = outcome.get("point")
    if point is None:
        return None
    point = float(point)
    if market_key == "spreads":
        return f"{name} {point:+g}"
    return f"{name} {point:g}"


def _group_key(market_key: str, outcome: dict[str, Any]) -> str | None:
    if market_key == "h2h":
        return "1x2"
    point = outcome.get("point")
    if point is None:
        return None
    point = float(point)
    return f"{market_key}:{abs(point):g}" if market_key == "spreads" else f"{market_key}:{point:g}"


def _fair_probabilities(outcomes: list[dict[str, Any]]) -> dict[str, float] | None:
    prices = {item.get("name"): float(item.get("price", 0)) for item in outcomes}
    if len(prices) < 2 or any(price <= 1 for price in prices.values()):
        return None
    implied = {name: 1 / price for name, price in prices.items()}
    overround = sum(implied.values())
    return {name: probability / overround for name, probability in implied.items()}


def find_signals(events: list[dict[str, Any]], sport_key: str, min_books: int, min_edge: float, bankroll: float, max_stake_pct: float) -> list[Signal]:
    signals: list[Signal] = []
    for event in events:
        rows_by_market: dict[tuple[str, str], list[tuple[str, dict[str, float], dict[str, float]]]] = {}
        for bookmaker in event.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                market_key = market.get("key")
                if market_key not in MARKETS:
                    continue
                grouped: dict[str, list[dict[str, Any]]] = {}
                for outcome in market.get("outcomes", []):
                    line_key = _group_key(market_key, outcome)
                    label = _selection_label(market_key, outcome)
                    if line_key and label:
                        grouped.setdefault(line_key, []).append({"name": label, "price": outcome.get("price")})
                for line_key, outcomes in grouped.items():
                    fair = _fair_probabilities(outcomes)
                    quotes = {item["name"]: float(item["price"]) for item in outcomes if item["price"] is not None}
                    if fair:
                        rows_by_market.setdefault((market_key, line_key), []).append(
                            (bookmaker.get("title", bookmaker.get("key", "Unknown")), fair, quotes)
                        )
        for (market_key, _), market_rows in rows_by_market.items():
            if len(market_rows) < min_books:
                continue
            selections = set.intersection(*(set(row[1]) for row in market_rows))
            for selection in selections:
                fair_probability = median(row[1][selection] for row in market_rows)
                bookmaker, _, quote = max(
                    (row for row in market_rows if selection in row[2]), key=lambda row: row[2][selection]
                )
                odds = quote[selection]
                expected_value = fair_probability * odds - 1
                if expected_value < min_edge:
                    continue
                kelly = max(0.0, expected_value / (odds - 1))
                fraction = min(kelly * 0.25, max_stake_pct)
                signals.append(Signal(
                    event_id=event["id"], sport_key=sport_key, commence_time=event["commence_time"],
                    home_team=event["home_team"], away_team=event["away_team"], market=MARKETS[market_key],
                    selection=selection, bookmaker=bookmaker, odds=odds, fair_probability=fair_probability,
                    expected_value=expected_value, consensus_books=len(market_rows), paper_stake=bankroll * fraction,
                ))
    return sorted(signals, key=lambda signal: signal.expected_value, reverse=True)


def render_report(signals: list[Signal], scanned_at: datetime) -> str:
    heading = f"📊 GT-K1000X — market scan\nEurope top leagues · {scanned_at:%Y-%m-%d %H:%M UTC}"
    if not signals:
        return heading + "\n\nNo qualifying signals passed the current price and consensus filters."
    lines = [heading, "", "Signals are market estimates; manage risk and verify quoted prices before acting."]
    for index, signal in enumerate(signals, 1):
        lines.extend(("", f"{index}. {signal.home_team} vs {signal.away_team} ({signal.market})",
            f"   Pick: {signal.selection} @ {signal.odds:.2f} ({signal.bookmaker})",
            f"   Fair p: {signal.fair_probability:.1%} | EV: {signal.expected_value:.1%} | Consensus: {signal.consensus_books} books",
            f"   Stake cap reference: {signal.paper_stake:.2f}"))
    return "\n".join(lines)
