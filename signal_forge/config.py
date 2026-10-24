from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_SPORT_KEYS = (
    "soccer_epl",
    "soccer_spain_la_liga",
    "soccer_germany_bundesliga",
    "soccer_italy_serie_a",
    "soccer_france_ligue_one",
)


def load_dotenv(path: Path = Path(".env")) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


@dataclass(frozen=True)
class Settings:
    odds_api_key: str
    telegram_bot_token: str
    telegram_chat_id: str
    sport_keys: tuple[str, ...] = DEFAULT_SPORT_KEYS
    regions: str = "uk,eu"
    min_bookmakers: int = 3
    min_edge: float = 0.04
    max_stake_pct: float = 0.01
    paper_bankroll: float = 1000.0
    max_signals: int = 5

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        sport_keys = tuple(
            key.strip() for key in os.getenv("SPORT_KEYS", ",".join(DEFAULT_SPORT_KEYS)).split(",") if key.strip()
        )
        values = {
            "odds_api_key": os.getenv("ODDS_API_KEY", ""),
            "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
            "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID", ""),
            "sport_keys": sport_keys,
            "regions": os.getenv("REGIONS", "uk,eu"),
            "min_bookmakers": int(os.getenv("MIN_BOOKMAKERS", "3")),
            "min_edge": float(os.getenv("MIN_EDGE", "0.04")),
            "max_stake_pct": float(os.getenv("MAX_STAKE_PCT", "0.01")),
            "paper_bankroll": float(os.getenv("PAPER_BANKROLL", "1000")),
            "max_signals": int(os.getenv("MAX_SIGNALS", "5")),
        }
        missing = [name for name in ("odds_api_key", "telegram_bot_token", "telegram_chat_id") if not values[name]]
        if missing:
            raise ValueError("Missing required settings: " + ", ".join(missing))
        if not sport_keys:
            raise ValueError("SPORT_KEYS must contain at least one sport key")
        return cls(**values)
