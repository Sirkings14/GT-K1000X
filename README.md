# GT-K1000X — Signal Forge

A transparent, **paper-only** football value scanner that sends daily Telegram reports. It does not place bets, scrape bookmaker sites, or guarantee profit.

## What it does

- Fetches 1X2 football odds from The Odds API.
- Removes bookmaker overround, then uses the median fair probability across multiple books.
- Line-shops the best available decimal price and filters by expected value.
- Computes a capped quarter-Kelly **paper stake reference** and writes every emitted signal to an audit ledger.
- Sends either qualifying research signals or an explicit no-signal report to Telegram.

## Launch

1. Install Python 3.11+.
2. Copy `.env.example` to `.env` and set `ODDS_API_KEY`, `TELEGRAM_BOT_TOKEN`, and `TELEGRAM_CHAT_ID`.
3. Run `python -m unittest discover -s tests -v`.
4. Run `python -m signal_forge.main`.

Add those same values as GitHub Actions secrets, then enable the daily workflow. It runs at 08:00 UTC and supports manual dispatch.

## Guardrails

This is research tooling, not betting advice. Positive expected value estimated from public prices is uncertain; validate with a large, timestamped sample and positive closing-line value before considering any real-money use. Obey local law and only use money you can afford to lose.

## Research lineage

No third-party source code was copied. The architecture was informed by MIT-licensed projects including [value-bet-model](https://github.com/mperi1208/value-bet-model), [value-betting-scanner](https://github.com/zakariae-boui/value-betting-scanner), and [smart-odds](https://github.com/sparegk/smart-odds). Their claims are not independently verified and are not a forecast of performance.
