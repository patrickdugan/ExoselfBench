import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import bench
import score


class ScoreTests(unittest.TestCase):
    def test_known_paired_effect(self):
        left = {"a": {"family": "f1", "score": 1}, "b": {"family": "f2", "score": 2}}
        right = {"a": {"family": "f1", "score": 2}, "b": {"family": "f2", "score": 3}}
        result = score.paired_effect(left, right)
        self.assertEqual(result["mean_right_minus_left"], 1)
        self.assertEqual(result["family_bootstrap_95_percentile"], [1, 1])

    def test_missing_pair_fails(self):
        with self.assertRaises(ValueError):
            score.paired_effect({"a": {"family": "f", "score": 1}}, {})

    def test_family_macro_average(self):
        left = {i: {"family": "f1" if i < 3 else "f2", "score": 0} for i in range(4)}
        right = {i: {"family": "f1" if i < 3 else "f2", "score": 0 if i < 3 else 4} for i in range(4)}
        self.assertEqual(score.paired_effect(left, right)["mean_right_minus_left"], 2)

    def test_single_family_no_interval(self):
        unit = {"a": {"family": "f", "score": 1}}
        self.assertIsNone(score.paired_effect(unit, unit)["family_bootstrap_95_percentile"])

    def test_mock_scoring_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            bench.save(root / "manifest.json", {"status": "complete", "mock": True})
            with self.assertRaises(ValueError):
                score.rated_units(root, root / "ratings.json", "method_transfer")

    def fixture(self, root):
        bench.save(root / "manifest.json", {"status": "complete", "mock": False})
        bench.save(root / "blinding-key.json", {"i": {"request_id": "r", "stage": "peer", "case_id": "c", "profile_id": "p", "seed": 1, "family": "f"}})
        bench.save(root / "records.json", [{"request_id": "r", "evaluator_fork_kind": "relevant"}])
        return {"schema": "dvd-ratings/0.1", "ratings": [{"item_id": "i", "reviewer_id": r, "scores": {m: 2 for m in score.DIMENSIONS}} for r in ("r1", "r2")]}

    def test_two_raters_required(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ratings = self.fixture(root)
            ratings["ratings"].pop()
            bench.save(root / "ratings.json", ratings)
            with self.assertRaises(ValueError):
                score.rated_units(root, root / "ratings.json", "method_transfer")

    def test_ratings_parsed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ratings = self.fixture(root)
            bench.save(root / "ratings.json", ratings)
            _, units = score.rated_units(root, root / "ratings.json", "method_transfer")
            self.assertEqual(next(iter(units.values()))["score"], 2)

    def test_duplicate_reviewer_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ratings = self.fixture(root)
            ratings["ratings"][1]["reviewer_id"] = "r1"
            bench.save(root / "ratings.json", ratings)
            with self.assertRaises(ValueError):
                score.rated_units(root, root / "ratings.json", "method_transfer")


if __name__ == "__main__":
    unittest.main()
