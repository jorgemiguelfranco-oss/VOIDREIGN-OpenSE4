#!/usr/bin/env python3
"""Run six native Windows AI campaigns and audit actual per-turn empire statistics.

Unlike UI smoke tests this reads History/plr_1_stats.txt written by the game's
own score system: score, production, research, intelligence, levels, systems,
colonies, population, units, ships and bases. No OCR or inferred numbers.

Usage:
  python tools/qa_campaign_telemetry.py --package-dir dist/<stage> --turns 500
  python tools/qa_campaign_telemetry.py ... --strict-quality
The strict gate is intended to FAIL until every faction expands and builds.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

COLUMNS = (
    "empire", "date", "score", "production", "research", "intelligence",
    "tech_levels", "systems", "planets", "population", "units", "ships", "bases"
)
CASES = (
    ("Aurelian", 7), ("Veyran", 11), ("Khepri", 13),
    ("Meridian", 17), ("Outer", 19), ("Helion", 23)
)


def records(path: Path, empire: int = 1) -> list[dict[str, int]]:
    if not path.is_file():
        raise ValueError(f"No player statistics written: {path}")
    result = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != len(COLUMNS):
            raise ValueError(f"Malformed native stats line {line_no}: {line!r}")
        record = dict(zip(COLUMNS, map(int, parts)))
        if record["empire"] == empire:
            result.append(record)
    if not result:
        raise ValueError(f"No empire {empire} records found: {path}")
    if any(a["date"] >= b["date"] for a, b in zip(result, result[1:])):
        raise ValueError("Empire statistics dates are not strictly increasing")
    return result


def analyse(faction: str, seed: int, data: list[dict[str, int]],
            expected_turns: int) -> dict:
    first, last = data[0], data[-1]
    delta = {name: last[name] - first[name] for name in
             ("score", "production", "research", "intelligence", "tech_levels",
              "systems", "planets", "population", "units", "ships", "bases")}
    # The initial quick-start state may contain several colonies. Growth is
    # measured from the first recorded turn, not an assumed "one homeworld".
    last_expansion = next(
        (i + 1 for i in range(len(data) - 1, 0, -1)
         if data[i]["planets"] != data[i - 1]["planets"]),
        0,
    )
    stagnation = len(data) - last_expansion if last_expansion else len(data) - 1
    warnings: list[str] = []
    if len(data) < expected_turns:
        warnings.append(f"Campaign ended after {len(data)} of {expected_turns} requested turns (likely game-over, not a process crash)")
    peak = max(x["planets"] for x in data)
    if delta["planets"] <= 0:
        if peak > first["planets"]:
            warnings.append(f"Expanded to {peak} colonies but fell back to {last['planets']}")
        else:
            warnings.append("No new colonies gained")
    if stagnation >= 100:
        warnings.append(f"No changes to colony count for last {stagnation} turns")
    if delta["ships"] <= 0:
        warnings.append("No net ship-fleet growth")
    if delta["tech_levels"] <= 0:
        warnings.append("No technology-level progression")
    return {
        "faction": faction, "seed": seed, "turns_requested": expected_turns,
        "turns_recorded": len(data), "first_date": first["date"],
        "last_date": last["date"], "first": first, "last": last,
        "growth": delta, "max_colonies": max(x["planets"] for x in data),
        "max_ships": max(x["ships"] for x in data),
        "completed_requested_turns": len(data) == expected_turns,
        "stagnation_turns": stagnation, "warnings": warnings,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--package-dir", required=True, type=Path)
    p.add_argument("--turns", type=int, default=500)
    p.add_argument("--empires", type=int, default=3)
    p.add_argument("--systems", type=int, default=24)
    p.add_argument("--seed-offset", type=int, default=0)
    p.add_argument("--output", type=Path)
    p.add_argument("--strict-quality", action="store_true")
    p.add_argument("--timeout", type=int, default=180)
    args = p.parse_args()
    if not 100 <= args.turns <= 2000:
        p.error("--turns must be 100..2000")
    if not 1 <= args.empires <= 12 or not 10 <= args.systems <= 500:
        p.error("--empires must be 1..12 and --systems must be 10..500")
    package = args.package_dir.resolve()
    exe = package / "VOIDREIGN.exe"
    if not exe.is_file() or not (package / "game-data/Data/Components.txt").is_file():
        p.error("Package must contain native VOIDREIGN.exe and game-data/")
    output = (args.output or Path(tempfile.gettempdir()) / "voidreign-campaign-telemetry").resolve()
    repo = Path(__file__).resolve().parent.parent
    if output == repo or repo in output.parents:
        p.error("Telemetry output and screenshots must live outside the repository")
    output.mkdir(parents=True, exist_ok=True)
    result = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "package": str(package),
        "exe_sha256": hashlib.sha256(exe.read_bytes()).hexdigest(),
        "empires": args.empires, "systems": args.systems,
        "seed_offset": args.seed_offset, "campaigns": []
    }
    failed = False
    for faction, initial_seed in CASES:
        seed = initial_seed + args.seed_offset
        profile = output / faction.lower()
        profile.mkdir(parents=True, exist_ok=True)
        image = profile / "turn-final.png"
        cmd = [
            str(exe), f"--quick-start={faction}", f"--empires={args.empires}",
            f"--systems={args.systems}", f"--seed={seed}", f"--turns={args.turns}",
            "--frames=2", "--no-audio", f"--screenshot={image}"
        ]
        env = os.environ.copy()
        env["OPENSE4_USER_DIR"] = str(profile)
        try:
            completed = subprocess.run(cmd, cwd=package, env=env, timeout=args.timeout,
                                       capture_output=True, text=True, errors="replace")
            if completed.returncode != 0:
                raise RuntimeError(f"Native executable exit {completed.returncode}: "
                                   f"{completed.stderr[-800:]}")
            if not image.is_file() or image.stat().st_size < 20_000:
                raise RuntimeError("Windowed native screenshot missing/empty")
            data = records(profile / "History/plr_1_stats.txt")
            row = analyse(faction, seed, data, args.turns)
            row["screenshot"] = str(image)
            print(f"{faction:9s} T={row['turns_recorded']:4d} "
                  f"colonies {row['first']['planets']}->{row['last']['planets']}, "
                  f"ships {row['first']['ships']}->{row['last']['ships']}, "
                  f"tech {row['first']['tech_levels']}->{row['last']['tech_levels']}, "
                  f"late_stagnation={row['stagnation_turns']}, "
                  f"warnings={len(row['warnings'])}", flush=True)
        except Exception as e:
            failed = True
            row = {"faction": faction, "seed": seed, "error": str(e)}
            print(f"{faction:9s} FAILED: {e}", flush=True)
        result["campaigns"].append(row)

    json_file = output / "campaign-telemetry.json"
    json_file.write_text(json.dumps(result, indent=2), encoding="utf-8")
    csv_file = output / "campaign-telemetry.csv"
    with csv_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(("faction", "seed", "turns_recorded", "planets_first", "planets_last",
                         "ships_first", "ships_last", "tech_first", "tech_last",
                         "score_first", "score_last", "stagnation_turns", "warnings"))
        for c in result["campaigns"]:
            first = c.get("first", {})
            last = c.get("last", {})
            writer.writerow((
                c.get("faction"), c.get("seed"), c.get("turns_recorded"),
                first.get("planets"), last.get("planets"), first.get("ships"),
                last.get("ships"), first.get("tech_levels"), last.get("tech_levels"),
                first.get("score"), last.get("score"), c.get("stagnation_turns"),
                " | ".join(c.get("warnings", [c.get("error", "")]))
            ))
    print("JSON: ", json_file)
    print("CSV:  ", csv_file)
    issue_count = sum(len(c.get("warnings", [])) for c in result["campaigns"])
    early_ends = sum(1 for c in result["campaigns"] if "turns_recorded" in c and not c["completed_requested_turns"])
    print(f"ENGINE_ERRORS={int(failed)}  EARLY_ENDS={early_ends}  AI_QUALITY_WARNINGS={issue_count}")
    if failed or (args.strict_quality and issue_count):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
