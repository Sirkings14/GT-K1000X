# GT-K1000X — Football Market Signal Engine

A football market-signal service for the Premier League, La Liga, Bundesliga, Serie A, and Ligue 1. It sends a daily Telegram report; it does not automate bet placement.

## Markets scanned

- **1X2:** home win, draw, away win.
- **Goals O/U:** bookmaker totals such as over/under 2.5.
- **Handicaps:** bookmaker spread/handicap markets.

The Odds API feed currently powers quoted prices. Double chance, cards, corners, and player props are excluded until a provider delivers actual prices for those markets; a model probability alone cannot establish a tradable edge.

## How a signal is ranked

The engine removes each bookmaker's margin, takes the median fair probability across at least three books, finds the best available price, requires a configurable expected-value threshold, and limits each stake reference to capped quarter-Kelly sizing. Every delivered signal is timestamped for audit and later closing-line-value review.

## Run through GitHub only

Add `ODDS_API_KEY`, `TELEGRAM_BOT_TOKEN`, and `TELEGRAM_CHAT_ID` as GitHub Actions secrets. Then manually run **Actions → Daily football market scan → Run workflow**. The schedule runs at 08:00 UTC daily.

With `uk,eu`, the feed uses two odds credits per league for one market call. The five-league daily scan therefore uses roughly ten credits per run. Set `REGIONS=uk` to reduce usage if needed.

## Risk

Market signals are uncertain and quoted prices can move or be unavailable. Verify the price and availability yourself, obey local law, and never risk more than you can afford to lose.

## Research lineage

No third-party source code was copied. The architecture was informed by MIT-licensed projects including [value-bet-model](https://github.com/mperi1208/value-bet-model), [value-betting-scanner](https://github.com/zakariae-boui/value-betting-scanner), and [smart-odds](https://github.com/sparegk/smart-odds).
