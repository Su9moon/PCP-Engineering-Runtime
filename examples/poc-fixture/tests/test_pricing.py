from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from poc_fixture.pricing import subtotal_cents


class SubtotalTests(unittest.TestCase):
    def test_sums_multiple_lines(self) -> None:
        self.assertEqual(subtotal_cents([(2, 125), (1, 300)]), 550)

    def test_empty_lines_are_zero(self) -> None:
        self.assertEqual(subtotal_cents([]), 0)

    def test_rejects_non_positive_quantity(self) -> None:
        with self.assertRaises(ValueError):
            subtotal_cents([(0, 100)])

    def test_rejects_negative_unit_price(self) -> None:
        with self.assertRaises(ValueError):
            subtotal_cents([(1, -1)])


if __name__ == "__main__":
    unittest.main()
