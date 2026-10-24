import unittest
from datetime import datetime, timezone

from signal_forge.market import find_signals, render_report


EVENT = {
    "id": "match-1", "commence_time": "2026-10-25T15:00:00Z", "home_team": "Alpha", "away_team": "Beta",
    "bookmakers": [
        {"title": "Book A", "markets": [{"key": "h2h", "outcomes": [{"name": "Alpha", "price": 2.0}, {"name": "Draw", "price": 3.5}, {"name": "Beta", "price": 4.0}]}]},
        {"title": "Book B", "markets": [{"key": "h2h", "outcomes": [{"name": "Alpha", "price": 2.05}, {"name": "Draw", "price": 3.4}, {"name": "Beta", "price": 3.7}]}]},
        {"title": "Book C", "markets": [{"key": "h2h", "outcomes": [{"name": "Alpha", "price": 2.55}, {"name": "Draw", "price": 3.35}, {"name": "Beta", "price": 3.55}]}]},
    ],
}


class MarketTests(unittest.TestCase):
    def test_finds_a_value_signal_and_caps_stake(self):
        signals = find_signals([EVENT], min_books=3, min_edge=0.04, bankroll=1000, max_stake_pct=0.01)
        self.assertTrue(signals)
        self.assertEqual(signals[0].selection, "Alpha")
        self.assertEqual(signals[0].odds, 2.55)
        self.assertLessEqual(signals[0].paper_stake, 10)

    def test_report_marks_output_as_research(self):
        text = render_report([], "soccer_epl", datetime.now(timezone.utc))
        self.assertIn("No qualifying paper signals", text)


if __name__ == "__main__":
    unittest.main()
