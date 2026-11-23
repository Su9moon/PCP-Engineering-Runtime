from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from poc_fixture.pricing import apply_discount_cents, subtotal_cents


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


class DiscountTests(unittest.TestCase):
    def test_applies_basis_point_discount(self) -> None:
        self.assertEqual(apply_discount_cents(1000, 2500), 750)

    def test_half_up_rounding_boundaries(self) -> None:
        self.assertEqual(apply_discount_cents(1, 5000), 1)
        self.assertEqual(apply_discount_cents(1, 5001), 0)

    def test_zero_and_full_discount(self) -> None:
        self.assertEqual(apply_discount_cents(123, 0), 123)
        self.assertEqual(apply_discount_cents(123, 10000), 0)

    def test_rejects_invalid_inputs(self) -> None:
        for amount, rate in [
            (-1, 0),
            (1.5, 0),
            (1, -1),
            (1, 10001),
            (1, 2.5),
            (True, 0),
            (1, True),
        ]:
            with self.subTest(amount=amount, rate=rate):
                with self.assertRaises(ValueError):
                    apply_discount_cents(amount, rate)


if __name__ == "__main__":
    unittest.main()
