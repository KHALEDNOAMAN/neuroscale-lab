"""Benchmark indexed versus unindexed SQLite feature queries with distributions."""
from __future__ import annotations

import argparse
import sqlite3
import statistics
import time
from pathlib import Path


def timed(con: sqlite3.Connection, query: str, level: int, repeats: int) -> list[float]:
    values = []
    for _ in range(repeats):
        start = time.perf_counter()
        con.execute(query, (level,)).fetchall()
        values.append(time.perf_counter() - start)
    return values


def summary(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    return {"median_seconds": statistics.median(values), "mean_seconds": statistics.mean(values), "p95_seconds": ordered[max(0, int(0.95 * len(ordered)) - 1)], "n": len(values)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--warmups", type=int, default=5)
    parser.add_argument("--repeats", type=int, default=40)
    args = parser.parse_args()
    query = "SELECT feature_name, AVG(feature_value) FROM feature_record WHERE workload_level = ? GROUP BY feature_name"
    levels = [1, 2, 3, 4]

    con = sqlite3.connect(args.path)
    for level in levels:
        timed(con, query + " /* warmup-indexed */", level, args.warmups)
    indexed_values = [v for level in levels for v in timed(con, query + " /* indexed */", level, args.repeats)]
    indexed_plan = con.execute("EXPLAIN QUERY PLAN " + query, (4,)).fetchall()
    con.execute("DROP INDEX IF EXISTS ix_feature_lookup"); con.commit(); con.close()

    con = sqlite3.connect(args.path)
    for level in levels:
        timed(con, query + " /* warmup-unindexed */", level, args.warmups)
    unindexed_values = [v for level in levels for v in timed(con, query + " /* unindexed */", level, args.repeats)]
    unindexed_plan = con.execute("EXPLAIN QUERY PLAN " + query, (4,)).fetchall()
    con.execute("CREATE INDEX ix_feature_lookup ON feature_record(workload_level, feature_name)"); con.commit(); con.close()

    result = {"indexed": summary(indexed_values), "unindexed": summary(unindexed_values), "indexed_plan": indexed_plan, "unindexed_plan": unindexed_plan, "levels": levels, "warmups": args.warmups, "repeats_per_level": args.repeats}
    print(result)


if __name__ == "__main__": main()
