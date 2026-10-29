import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import bench


class BenchTests(unittest.TestCase):
    def setUp(self):
        self.suite = bench.load(ROOT / "data/cases.json")
        self.profiles = bench.load(ROOT / "config/profiles.json")["profiles"]

    def run_fixture(self, **kwargs):
        options = dict(arm="rag", seed=19, limit=2, max_calls=30)
        options.update(kwargs)
        return bench.experiment(self.suite, self.profiles, bench.mock_backend, **options)

    def test_suite_valid(self):
        bench.validate_suite(self.suite)
        self.assertEqual(len(self.suite["cases"]), 12)

    def test_duplicate_case_rejected(self):
        self.suite["cases"].append(self.suite["cases"][0])
        with self.assertRaises(ValueError):
            bench.validate_suite(self.suite)

    def test_duplicate_evidence_rejected(self):
        self.suite["cases"][0]["branches"][0]["evidence"][0]["id"] = "E0"
        with self.assertRaises(ValueError):
            bench.validate_suite(self.suite)

    def test_missing_sham_rejected(self):
        self.suite["cases"][0]["branches"] = self.suite["cases"][0]["branches"][:1]
        with self.assertRaises(ValueError):
            bench.validate_suite(self.suite)

    def test_strict_json(self):
        for text in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}'):
            with self.assertRaises(ValueError):
                bench.parse_json(text)

    def test_deterministic_protocol(self):
        self.assertEqual(self.run_fixture(), self.run_fixture())

    def test_call_cap_before_backend(self):
        seen = []
        with self.assertRaises(ValueError):
            bench.experiment(self.suite, self.profiles, lambda r: seen.append(r),
                             arm="base", seed=1, limit=2, max_calls=29)
        self.assertEqual(seen, [])

    def test_expected_turn_counts(self):
        rows = self.run_fixture()
        self.assertEqual(len(rows), 30)
        self.assertEqual(sum(r["stage"] == "initial" for r in rows), 6)
        self.assertEqual(sum(r["stage"] == "evidence" for r in rows), 12)
        self.assertEqual(sum(r["stage"] == "peer" for r in rows), 12)

    def test_evaluator_guidance_is_hidden(self):
        for row in self.run_fixture():
            text = bench.canonical(row["request"])
            self.assertNotIn("judge_notes", text)
            self.assertNotIn("evaluator_fork_kind", text)
            self.assertNotIn('"kind": "sham"', text)

    def test_forks_independent(self):
        rows = self.run_fixture()
        for row in rows:
            if row["stage"] == "evidence":
                task = row["request"]["task"]
                evidence_ids = {e["id"] for e in task["evidence"]}
                self.assertFalse({"E1", "E2"} <= evidence_ids)
                self.assertEqual(task["peers"], [])

    def test_peer_round_frozen(self):
        calls = []
        def backend(request):
            calls.append(request["request_id"])
            result = bench.mock_backend(request)
            result["response"]["justification"] = request["request_id"]
            return result
        rows = bench.experiment(self.suite, self.profiles, backend,
                                arm="base", seed=19, limit=1, max_calls=15)
        for row in rows:
            if row["stage"] == "peer":
                peers = row["request"]["task"]["peers"]
                self.assertEqual(len(peers), 2)
                for peer in peers:
                    previous_id = peer["response"]["justification"]
                    self.assertIn(":evidence:", previous_id)
                    self.assertLess(calls.index(previous_id), calls.index(row["request_id"]))

    def test_no_fake_fidelity_score(self):
        report = bench.metrics(self.run_fixture(), True)
        self.assertEqual(report["mode"], "mock_plumbing_only")
        self.assertIsNone(report["author_fidelity"])
        self.assertIsNone(report["reasoning_quality"])

    def test_invalid_probability(self):
        response = bench.mock_backend({})["response"]
        for p in (-1, 2, True, float("nan"), float("inf")):
            response["probability"] = p
            with self.assertRaises(ValueError):
                bench.validate_response(response, [])

    def test_unknown_citations(self):
        response = bench.mock_backend({})["response"]
        response["evidence_ids"] = ["invented"]
        with self.assertRaises(ValueError):
            bench.validate_response(response, [])

    def test_simulation_attribution_required(self):
        response = bench.mock_backend({})["response"]
        response["author_status"] = "Patrick personally approved"
        with self.assertRaises(ValueError):
            bench.validate_response(response, [])

    def test_budget_usage_and_type(self):
        request = {"limits": {"max_output_tokens": 10}, "task": {"evidence": []}}
        value = bench.mock_backend({})
        for n in (11, -1, True):
            value["usage"]["output_tokens"] = n
            with self.assertRaises(ValueError):
                bench.check_envelope(value, request)

    def test_unbound_sources_rejected(self):
        with self.assertRaises(ValueError):
            bench.read_sources(ROOT / "config/sources.example.json", self.profiles)

    def test_source_pins_and_retrieval(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            text = "x" * 50 + " source agency proof "
            (root / "book.txt").write_text(text, encoding="utf-8")
            entry = {"path": "book.txt", "sha256": bench.digest(text.encode()), "review_status": "unreviewed"}
            manifest = {"sources": {p["id"]: dict(entry) for p in self.profiles}}
            bench.save(root / "sources.json", manifest)
            sources = bench.read_sources(root / "sources.json", self.profiles)
            hits = bench.retrieve(sources[self.profiles[0]["id"]], "agency proof", "p", 50)
            self.assertIn("agency", hits[0]["text"])
            self.assertLessEqual(len(hits[0]["text"]), 50)
            (root / "book.txt").write_text("changed", encoding="utf-8")
            with self.assertRaises(ValueError):
                bench.read_sources(root / "sources.json", self.profiles)

    def test_blinding_keeps_context_hides_metadata(self):
        packet, key = bench.blind_packet(self.run_fixture(), 19)
        self.assertEqual(len(packet), len(key))
        for row in packet:
            self.assertNotIn("profile_id", row)
            self.assertNotIn("arm", row)
            self.assertNotIn("model", row)
            if row["stage"] == "peer":
                self.assertTrue(row["peers"])
                self.assertIsNotNone(row["previous_response"])

    def test_alias_substitution_does_not_cascade(self):
        rows = self.run_fixture()
        row = next(r for r in rows if r["stage"] == "evidence" and r["evaluator_fork_kind"] == "relevant")
        row["response"]["justification"] = "E0 then E1"
        row["response"]["evidence_ids"] = ["E0", "E1"]
        packet, _ = bench.blind_packet([row], 19)
        self.assertEqual(packet[0]["answer"]["justification"], "E1 then E2")
        self.assertEqual(packet[0]["answer"]["evidence_ids"], ["E1", "E2"])

    def test_local_stdio_backend(self):
        value = bench.mock_backend({})
        command = [sys.executable, "-c", f"import sys; sys.stdin.read(); print({json.dumps(bench.canonical(value))})"]
        backend = bench.command_backend({"command": command, "base_model": "test-fixture", "base_revision": "fixture-v1"})
        self.assertEqual(backend({"test": 1}), value)

    def test_backend_template_not_runnable(self):
        with self.assertRaises(ValueError):
            bench.command_backend(bench.load(ROOT / "config/backend.example.json"))

    def test_backend_nonzero(self):
        backend = bench.command_backend({"command": [sys.executable, "-c", "raise SystemExit(7)"],
                                         "base_model": "test", "base_revision": "v1"})
        with self.assertRaises(RuntimeError):
            backend({})

    def test_cli_demo_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "run"
            self.assertEqual(bench.main(["demo", "--limit", "1", "--out", str(out)]), 0)
            self.assertEqual(bench.load(out / "manifest.json")["status"], "complete")
            self.assertEqual(bench.main(["demo", "--limit", "1", "--out", str(out)]), 2)

    def test_failure_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "run"
            self.assertEqual(bench.main(["demo", "--max-calls", "1", "--out", str(out)]), 2)
            self.assertEqual(bench.load(out / "manifest.json")["status"], "failed")


if __name__ == "__main__":
    unittest.main()
