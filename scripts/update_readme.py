#!/usr/bin/env python3
"""Append one numbered README update per Eastern calendar day.

Run with Python 3.9+ from any directory. GitHub Actions handles scheduling
and committing. Use --readme PATH and --date YYYY-MM-DD for a local preview.
"""

import argparse
import re
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo


def add_daily_update(content: str, day: date) -> str:
    """Preserve existing text and skip dates already added by this script."""
    suffix = f" - {day.isoformat()} (automated daily update)"
    if re.search(r"^Update [0-9]+" + re.escape(suffix) + r"\r?$", content, re.MULTILINE):
        return content

    numbers = re.findall(r"^[ \t]*Update ([0-9]+)(?=[ \t\r\n]|$)", content, re.MULTILINE)
    next_number = max((int(number) for number in numbers), default=0) + 1
    newline = "\r\n" if "\r\n" in content else "\n"
    separator = "" if not content or content.endswith("\n") else newline
    return content + separator + f"Update {next_number}{suffix}" + newline


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readme", type=Path, default=Path(__file__).resolve().parents[1] / "README.md")
    parser.add_argument("--date", type=date.fromisoformat, help="Override the Eastern calendar date")
    parser.add_argument("--scheduled", action="store_true", help="Skip runs before noon Eastern")
    args = parser.parse_args()
    now = datetime.now(ZoneInfo("America/New_York"))
    if args.scheduled and now.hour < 12:
        print("Before noon Eastern; no README change needed.")
        return
    day = args.date or now.date()

    with args.readme.open(encoding="utf-8", newline="") as source:
        content = source.read()
    updated = add_daily_update(content, day)
    if updated == content:
        print(f"README already has an automated update for {day}.")
        return
    with args.readme.open("w", encoding="utf-8", newline="") as destination:
        destination.write(updated)
    print(updated.splitlines()[-1])


if __name__ == "__main__":
    main()
