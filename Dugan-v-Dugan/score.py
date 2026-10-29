#!/usr/bin/env python3
"""Compare paired, human-rated model runs; public development results are exploratory."""
from __future__ import annotations

import argparse
import math
import random
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

from bench import load, canonical

DIMENSIONS = ("grounding", "method_transfer", "evidence_update", "attribution", "dissent")


def rated_units(run: Path, ratings: Path, metric: str) -> tuple[dict, dict]:
    manifest = load(run / "manifest.json")
    if manifest.get("mock") is not False or manifest.get("status") != "complete":
        raise ValueError("scoring requires a completed model run; mock runs are excluded")
    key = load(run / "blinding-key.json")
    records = {r["request_id"]: r for r in load(run / "records.json")}
    votes: dict[str, dict[str, float]] = defaultdict(dict)
    document = load(ratings)
    if metric not in DIMENSIONS or document.get("schema") != "dvd-ratings/0.1":
        raise ValueError("invalid rating schema or metric")
    for row in document["ratings"]:
        item, reviewer = row["item_id"], row["reviewer_id"]
        if item not in key or not isinstance(reviewer, str) or not reviewer.strip():
            raise ValueError("unknown item or missing reviewer ID")
        if reviewer in votes[item]:
            raise ValueError("duplicate reviewer/item pair")
        if set(row["scores"]) != set(DIMENSIONS):
            raise ValueError("all rubric dimensions are required")
        for value in row["scores"].values():
            if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 4:
                raise ValueError("scores must be finite numbers in [0,4]")
        votes[item][reviewer] = row["scores"][metric]
    units = {}
    for item, identity in key.items():
        if identity["stage"] != "peer":
            continue
        if len(votes[item]) < 2:
            raise ValueError(f"two distinct reviewer IDs required for final item {item}")
        record = records[identity["request_id"]]
        unit = (identity["case_id"], identity["profile_id"], identity["seed"], record["evaluator_fork_kind"])
        if unit in units:
            raise ValueError("duplicate paired evaluation unit")
        units[unit] = {"family": identity["family"], "score": mean(votes[item].values()),
                       "reviewer_range": max(votes[item].values()) - min(votes[item].values())}
    if not units:
        raise ValueError("no final-stage units")
    return manifest, units


def paired_effect(left: dict, right: dict, *, seed: int = 19, samples: int = 2000) -> dict[str, Any]:
    if not left or set(left) != set(right):
        raise ValueError("complete matched units required; missing pairs cannot be silently dropped")
    if samples < 100:
        raise ValueError("at least 100 bootstrap samples required")
    families: dict[str, list[float]] = defaultdict(list)
    for key in left:
        if left[key]["family"] != right[key]["family"]:
            raise ValueError("case-family mismatch")
        families[left[key]["family"]].append(right[key]["score"] - left[key]["score"])
    effects = [mean(families[name]) for name in sorted(families)]
    interval = None
    if len(effects) > 1:
        rng = random.Random(seed)
        draws = sorted(mean(rng.choices(effects, k=len(effects))) for _ in range(samples))
        interval = [draws[int(0.025 * (samples - 1))], draws[int(0.975 * (samples - 1))]]
    return {"paired_units": len(left), "families": len(effects),
            "mean_right_minus_left": mean(effects), "family_bootstrap_95_percentile": interval,
            "unit_of_resampling": "case family; profiles, seeds and forks averaged within family",
            "warning": "Exploratory interval conditional on this suite and raters; no claim about author identity."}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left_run", type=Path)
    parser.add_argument("left_ratings", type=Path)
    parser.add_argument("right_run", type=Path)
    parser.add_argument("right_ratings", type=Path)
    parser.add_argument("--metric", choices=DIMENSIONS, default="method_transfer")
    args = parser.parse_args()
    try:
        lm, left = rated_units(args.left_run, args.left_ratings, args.metric)
        rm, right = rated_units(args.right_run, args.right_ratings, args.metric)
        for field in ("suite_sha256", "profiles_sha256", "runner_sha256", "seed", "limits"):
            if field not in lm or field not in rm or lm[field] != rm[field]:
                raise ValueError(f"unmatched run setting: {field}")
        for field in ("base_model", "base_revision"):
            if lm["model"][field] != rm["model"][field]:
                raise ValueError(f"unmatched base model: {field}")
        result = paired_effect(left, right)
        result.update(metric=args.metric, left_arm=lm["arm"], right_arm=rm["arm"],
                      max_reviewer_range=max(x["reviewer_range"] for x in list(left.values()) + list(right.values())))
        print(canonical(result))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    main()
