"""Demo script: anchor health system + 5 optimal additions.

Runs the optimizer in two stages:
  1. Anchor selection from entities with 250+ providers (1 round)
  2. Add 5 entities from pool with 100+ providers

Outputs a formatted console table and detailed JSON for reporting.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import pandas as pd

from network_optimizer import (
    NetworkOptimizer,
    OptimizerConfig,
    compute_coverage,
    load_all,
    load_weights,
)

COVERAGE_THRESHOLD = 90.0  # Minimum coverage % to count as "covered"


def run_optimizer(
    pool: pd.DataFrame,
    members: pd.DataFrame,
    thresholds: dict,
    weights: dict[str, float],
    min_entity_size: int | None,
    max_rounds: int,
    initial_network: pd.DataFrame | None = None,
    max_entity_size: int | None = None,
) -> dict:
    """Run the optimizer and return structured results."""
    # Filter pool
    filtered_pool = pool.copy()
    if min_entity_size is not None:
        entity_sizes = filtered_pool.groupby("entity").size()
        qualifying = set(entity_sizes[entity_sizes >= min_entity_size].index)
        filtered_pool = filtered_pool[filtered_pool["entity"].isin(qualifying)].reset_index(drop=True)
        if initial_network is not None:
            initial_network = initial_network[initial_network["entity"].isin(qualifying)].reset_index(drop=True)

    if max_entity_size is not None:
        entity_sizes = filtered_pool.groupby("entity").size()
        qualifying = set(entity_sizes[entity_sizes <= max_entity_size].index)
        # Preserve entities already in initial_network
        if initial_network is not None:
            existing = set(initial_network["entity"].unique())
            qualifying = qualifying | existing
        filtered_pool = filtered_pool[filtered_pool["entity"].isin(qualifying)].reset_index(drop=True)

    net = initial_network if initial_network is not None else filtered_pool.iloc[:0].copy()

    config = OptimizerConfig(
        max_rounds=max_rounds,
        patience=5,
        enable_swaps=False,
        n_jobs=12,
        search_mode="steepest",
        metric_weights=weights,
        verbosity=0,
    )

    optimizer = NetworkOptimizer(filtered_pool, members, thresholds, net, config)
    result = optimizer.optimize()

    # Get final coverage
    coverage = compute_coverage(members, thresholds, result.network)

    return {
        "score": round(result.score, 2),
        "access_score": round(result.access_score, 2),
        "network_entities": sorted(result.network_entities),
        "num_entities": len(result.network_entities),
        "num_providers": len(result.network),
        "entities_added": result.entities_added,
        "elapsed": round(result.elapsed, 1),
        "num_candidates": filtered_pool["entity"].nunique(),
        "min_entity_size": min_entity_size,
        "coverage": coverage,
    }


def format_table(anchor: dict, additions: list[dict], total_time: float) -> str:
    """Format results as a console table."""
    lines = []
    lines.append("")
    lines.append("=== Network Build Demo ===")
    lines.append("")

    # Anchor
    lines.append(f"  Anchor Selection (min 250 providers, {anchor['num_candidates']} candidates)")
    lines.append("  " + "─" * 58)
    a = anchor["entities_added"][0]
    lines.append(
        f"  #1  {a:<40s} {anchor['num_providers']:>6,} providers    "
        f"Score: {anchor['score']:>6.2f}%  (+{anchor['score']:>5.2f})  Access: {anchor['access_score']:>5.2f}%"
    )
    lines.append("")

    # Additions
    lines.append(f"  Additional Entities (min {additions[0]['min_entity_size']} providers, {additions[0]['num_candidates']} candidates)")
    lines.append("  " + "─" * 58)

    prev_score = anchor["score"]
    anchor["access_score"]
    for i, r in enumerate(additions, start=2):
        entity = r["entities_added"][0]
        delta = round(r["score"] - prev_score, 2)
        lines.append(
            f"  #{i}  {entity:<40s} {r['num_providers']:>6,} providers    "
            f"Score: {r['score']:>6.2f}%  (+{delta:>5.2f})  Access: {r['access_score']:>5.2f}%"
        )
        prev_score = r["score"]
        r["access_score"]

    # Summary
    final = additions[-1]
    total_entities = 1 + len(additions)
    lines.append("")
    lines.append("  " + "═" * 60)
    lines.append(
        f"  Summary: {total_entities} entities, {final['num_providers']:,} providers, "
        f"{final['score']:.2f}% score, {final['access_score']:.2f}% access  ({total_time}s)"
    )
    lines.append("")
    return "\n".join(lines)


def build_report(anchor: dict, additions: list[dict], coverage: list[dict]) -> dict:
    """Build detailed JSON report."""
    prev_score = anchor["score"]

    additions_detail = []
    for r in additions:
        delta = round(r["score"] - prev_score, 2)
        additions_detail.append({
            "entity": r["entities_added"][0],
            "providers": r["num_providers"],
            "score": r["score"],
            "delta": delta,
            "access_score": r["access_score"],
            "elapsed": r["elapsed"],
        })
        prev_score = r["score"]

    covered = [c for c in coverage if c["coverage_percentage"] >= COVERAGE_THRESHOLD]
    gaps = [c for c in coverage if c["coverage_percentage"] < COVERAGE_THRESHOLD]

    return {
        "anchor": {
            "entity": anchor["entities_added"][0],
            "providers": anchor["num_providers"],
            "score": anchor["score"],
            "access_score": anchor["access_score"],
            "candidates_evaluated": anchor["num_candidates"],
        },
        "additions": additions_detail,
        "summary": {
            "total_entities": 1 + len(additions),
            "total_providers": additions[-1]["num_providers"],
            "final_score": additions[-1]["score"],
            "final_access": additions[-1]["access_score"],
            "total_elapsed": round(sum(r["elapsed"] for r in [anchor] + additions), 1),
            "coverage_threshold": COVERAGE_THRESHOLD,
            "pairs_covered": len(covered),
            "pairs_total": len(coverage),
        },
        "coverage": coverage,
        "coverage_gaps": gaps,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Network build demo: anchor + 5 optimal additions")
    parser.add_argument("--pool", type=Path, required=True, help="Provider pool CSV")
    parser.add_argument("--members", type=Path, required=True, help="Members CSV")
    parser.add_argument("--thresholds", type=Path, required=True, help="Thresholds JSON")
    parser.add_argument("--weights", type=Path, default=None, help="Weights JSON path")
    parser.add_argument("--output", type=Path, default=None, help="Output JSON path")
    args = parser.parse_args()

    overall_start = time.time()
    print("Loading data...")
    weights = load_weights(args.weights)
    pool, members, thresholds, _ = load_all(
        args.pool, args.members, args.thresholds, None
    )
    print(f"  Pool: {len(pool)} providers, {pool['entity'].nunique()} entities")
    print(f"  Members: {len(members)} across {members['county'].nunique()} counties")
    print(f"  Thresholds: {sum(sum(c.values()) for s in thresholds.values() for c in s.values())} requirements")

    # Stage 1: Anchor selection (min 250 providers)
    print("\n--- Stage 1: Anchor Selection (min 250 providers) ---")
    t0 = time.time()
    anchor_result = run_optimizer(
        pool, members, thresholds, weights,
        min_entity_size=250,
        max_rounds=1,
    )
    anchor_entity = anchor_result["entities_added"][0]
    anchor_df = pool[pool["entity"].str.lower() == anchor_entity].reset_index(drop=True)
    print(f"  Selected: {anchor_entity} ({len(anchor_df)} providers, score {anchor_result['score']}%)")

    # Stage 2: Add 5 entities (min 25, max 249 providers)
    print("\n--- Stage 2: Add 5 Entities (min 25, max 249 providers) ---")
    additions = []
    current_network = anchor_df
    prev_score = anchor_result["score"]

    for i in range(5):
        t0 = time.time()
        r = run_optimizer(
            pool, members, thresholds, weights,
            min_entity_size=25,
            max_rounds=1,
            initial_network=current_network,
            max_entity_size=249,
        )
        if not r["entities_added"]:
            print(f"  Round {i + 2}: No improving candidate found, stopping.")
            break

        entity = r["entities_added"][0]
        delta = round(r["score"] - prev_score, 2)
        elapsed = round(time.time() - t0, 1)
        r["elapsed"] = elapsed
        additions.append(r)
        print(f"  Round {i + 2}: +{entity} ({r['num_providers']} providers) → score {r['score']}% (+{delta})")

        # Update network
        entity_df = pool[pool["entity"].str.lower() == entity].reset_index(drop=True)
        current_network = pd.concat([current_network, entity_df], ignore_index=True)
        prev_score = r["score"]

    # Output
    print(format_table(anchor_result, additions, round(time.time() - overall_start, 1)))

    # Coverage details
    final_coverage = compute_coverage(members, thresholds, current_network)
    report = build_report(anchor_result, additions, final_coverage)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2)
        print(f"Report written to {args.output}")
    else:
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
