from __future__ import annotations
import csv
import os
from datetime import datetime, timezone


class TradeLogger:
    """Appends every trade result to a CSV file for later analysis."""

    FIELDS = [
        "timestamp",
        "trade_id",
        "direction",
        "gap",
        "real_price",
        "otc_price",
        "outcome",
        "amount",
        "duration",
    ]

    def __init__(self, path: str = "trade_results.csv"):
        self._path = path
        self._ensure_header()

    def _ensure_header(self):
        if not os.path.exists(self._path):
            with open(self._path, "w", newline="") as f:
                csv.writer(f).writerow(self.FIELDS)

    def record(
        self,
        trade_id: str,
        direction: str,
        gap: float,
        real_price: float,
        otc_price: float,
        outcome: str,
        amount: float,
        duration: int,
    ):
        row = [
            datetime.now(timezone.utc).isoformat(),
            trade_id,
            direction,
            f"{gap:.6f}",
            f"{real_price:.5f}",
            f"{otc_price:.5f}",
            outcome,
            f"{amount:.2f}",
            duration,
        ]
        with open(self._path, "a", newline="") as f:
            csv.writer(f).writerow(row)


def load_results(path: str = "trade_results.csv") -> list[dict]:
    """Read the CSV back as a list of dicts — useful for analysis."""
    if not os.path.exists(path):
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def print_stats(path: str = "trade_results.csv"):
    """Print a quick summary of win/loss by gap range."""
    rows = load_results(path)
    if not rows:
        print("No trades recorded yet.")
        return

    total = len(rows)
    wins = sum(1 for r in rows if r["outcome"].lower() == "win")
    losses = total - wins
    win_rate = (wins / total * 100) if total else 0

    print(f"\n{'='*50}")
    print(f"  Trade Results  ({path})")
    print(f"{'='*50}")
    print(f"  Total : {total}")
    print(f"  Wins  : {wins}")
    print(f"  Losses: {losses}")
    print(f"  Rate  : {win_rate:.1f}%")

    # Breakdown by gap bucket
    buckets: dict[str, dict] = {}
    for r in rows:
        gap = abs(float(r["gap"]))
        if gap < 0.0005:
            bucket = "<0.0005"
        elif gap < 0.0010:
            bucket = "0.0005-0.0010"
        elif gap < 0.0015:
            bucket = "0.0010-0.0015"
        elif gap < 0.0020:
            bucket = "0.0015-0.0020"
        else:
            bucket = ">=0.0020"

        b = buckets.setdefault(bucket, {"wins": 0, "total": 0})
        b["total"] += 1
        if r["outcome"].lower() == "win":
            b["wins"] += 1

    print(f"\n  {'Gap Range':<18} {'Trades':>7} {'Wins':>7} {'Rate':>7}")
    print(f"  {'-'*42}")
    for bucket in ["<0.0005", "0.0005-0.0010", "0.0010-0.0015", "0.0015-0.0020", ">=0.0020"]:
        if bucket in buckets:
            b = buckets[bucket]
            rate = b["wins"] / b["total"] * 100 if b["total"] else 0
            print(f"  {bucket:<18} {b['total']:>7} {b['wins']:>7} {rate:>6.1f}%")
    print()
