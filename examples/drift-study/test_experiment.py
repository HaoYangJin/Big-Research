"""Checks against known mathematical answers and temporal isolation invariants."""
import dataclasses
import json
from pathlib import Path
import unittest

import experiment as e


CONFIG = json.loads(Path(__file__).with_name("config.json").read_text())


class ExperimentChecks(unittest.TestCase):
    def test_known_static_coefficients(self):
        rows = [e.Row(t+1, (t+1)/8, x, 2+3*x, 3, 0)
                for t, x in enumerate((-2, -1, 0, 1, 2, 3))]
        a, b = e.fit(rows, list(range(len(rows))), "static")
        self.assertAlmostEqual(a, 2.0, places=11)
        self.assertAlmostEqual(b, 3.0, places=11)

    def test_known_trend_coefficients(self):
        xs = (-2, 1, -1, 2, 0.5, -3, 4, -0.5)
        rows = [e.Row(t, t/8, x, 2+3*x+4*(t/8)*x, 1, 0)
                for t, x in enumerate(xs, 1)]
        coef = e.fit(rows, list(range(len(rows))), "trend_interaction")
        for got, truth in zip(coef, (2, 3, 4)):
            self.assertAlmostEqual(got, truth, places=10)

    def test_disjoint_equal_budgets_and_time_order(self):
        for seed in (1000, 1077, 1299):
            for protocol in CONFIG["protocols"]:
                train, test, future = e.split_indices(CONFIG, seed, protocol)
                self.assertEqual((len(train), len(test), len(future)), (640, 160, 160))
                self.assertFalse(set(train) & set(test))
                self.assertFalse((set(train) | set(test)) & set(future))
                self.assertGreater(min(future), max(train+test))
                if protocol == "chronological_holdout":
                    self.assertLess(max(train), min(test))
                else:
                    self.assertGreater(max(train), min(test))

    def test_future_labels_cannot_affect_fit(self):
        rows = e.generate(CONFIG, 1000, "gradual_strong")
        for protocol in CONFIG["protocols"]:
            train, _, future = e.split_indices(CONFIG, 1000, protocol)
            poisoned = [dataclasses.replace(r, y=1e12) if i in future else r for i, r in enumerate(rows)]
            for model in CONFIG["models"]:
                self.assertEqual(e.fit(rows, train, model), e.fit(poisoned, train, model))

    def test_common_random_numbers_and_jump_boundary(self):
        stationary = e.generate(CONFIG, 1000, "stationary")
        strong = e.generate(CONFIG, 1000, "gradual_strong")
        jump = e.generate(CONFIG, 1000, "future_jump")
        self.assertEqual(stationary, e.generate(CONFIG, 1000, "stationary"))
        for a, b in zip(stationary, strong):
            self.assertEqual(a.x, b.x)
            self.assertAlmostEqual(b.y-a.y, 2*a.u*a.x, places=12)
        self.assertEqual(jump[799].beta, 1)
        self.assertEqual(jump[800].beta, 3)

    def test_singular_design_fails_explicitly(self):
        with self.assertRaises(ArithmeticError):
            e.solve([[1.0, 1.0], [1.0, 1.0]], [1.0, 1.0])

    def test_analytic_reference_has_hand_calculated_gaps(self):
        reference = e.analytic_reference(CONFIG)["values"]
        self.assertAlmostEqual(reference["random_holdout"]["gap_approx"], 1.12, places=10)
        self.assertAlmostEqual(reference["chronological_holdout"]["gap_approx"], 0.96, places=10)


if __name__ == "__main__":
    unittest.main(verbosity=2)
