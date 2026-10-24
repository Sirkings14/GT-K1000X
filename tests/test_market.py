import unittest
from datetime import datetime, timezone

from signal_forge.market import find_signals, render_report


EVENT = {
    "id": "match-1", "commence_time": "2026-10-25T15:00:00Z", "home_team": "Alpha", "away_team": "Beta",
    "bookmakers": [
        {"title": "Book A", "markets": [
            {"key": "h2h", "outcomes": [{"name": "Alpha", "price": 2.0}, {"name": "Draw", "price": 3.5}, {"name": "Beta", "price": 4.0}]},
            {"key": "totals", "outcomes": [{"name": "Over", "price": 2.0, "point": 2.5}, {"name": "Under", "price": 2.0, "point": 2.5}]},
        ]},
        {"title": "Book B", "markets": [
            {"key": "h2h", "outcomes": [{"name": "Alpha", "price": 2.05}, {"name": "Draw", "price": 3.4}, {"name": "Beta", "price": 3.7}]},
            {"key": "totals", "outcomes": [{"name": "Over", "price": 2.05, "point": 2.5}, {"name": "Under", "price": 1.95, "point": 2.5}]},
        ]},
        {"title": "Book C", "markets": [
            {"key": "h2h", "outcomes": [{"name": "Alpha", "price": 2.55}, {"name": "Draw", "price": 3.35}, {"name": "Beta", "price": 3.55}]},
            {"key": "totals", "outcomes": [{"name": "Over", "price": 2.3, "point": 2.5}, {"name": "Under", "price": 1.8, "point": 2.5}]},
        ]},
    ],
}


class MarketTests(unittest.TestCase):
    def test_finds_h2h_and_totals_signals_with_stake_cap(self):
        signals = find_signals([EVENT], "soccer_epl", min_books=3, min_edge=0.04, bankroll=1000, max_stake_pct=0.01)
        self.assertTrue(signals)
        self.assertEqual(signals[0].selection, "Alpha")
        self.assertEqual(signals[0].odds, 2.55)
        self.assertLessEqual(signals[0].paper_stake, 10)
        self.assertIn("Goals O/U", {signal.market for signal in signals})

    def test_report_marks_no_signal(self):
        text = render_report([], datetime.now(timezone.utc))
        self.assertIn("No qualifying signals", text)


if __name__ == "__main__":
    unittest.main()
