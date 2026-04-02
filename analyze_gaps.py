"""
Gap-level analysis tool.

Collects real-time gap data between EURUSD and EURUSD_otc without placing
any trades, then reports statistics on gap distribution so you can pick the
best threshold.

Usage:
    python analyze_gaps.py --ssid "42[...]" --minutes 30
"""

import asyncio
import argparse
import statistics
from datetime import datetime, timezone
from BinaryOptionsToolsV2.pocketoption import PocketOptionAsync

from bot.price_tracker import PriceTracker
from bot.config import BotConfig


async def collect_gaps(ssid: str, duration_minutes: float, sample_interval: float = 0.5):
    cfg = BotConfig()
    api = PocketOptionAsync(ssid)
    await asyncio.sleep(5)

    balance = await api.balance()
    print(f"[*] Connected — Balance: {balance}")
    print(f"[*] Collecting gap samples for {duration_minutes} minutes "
          f"(every {sample_interval}s)...\n")

    tracker = PriceTracker()

    gaps: list[float] = []
    abs_gaps: list[float] = []

    async def sampler():
        await tracker.wait_for_prices(cfg.real_asset, cfg.otc_asset)
        end_time = asyncio.get_event_loop().time() + duration_minutes * 60

        while asyncio.get_event_loop().time() < end_time:
            real = tracker.get(cfg.real_asset)
            otc = tracker.get(cfg.otc_asset)
            if real is not None and otc is not None:
                gap = real - otc
                gaps.append(gap)
                abs_gaps.append(abs(gap))
                print(
                    f"  Samples: {len(gaps):>6}  |  Gap: {gap:+.6f}  |  "
                    f"Max |gap|: {max(abs_gaps):.6f}",
                    end="\r",
                )
            await asyncio.sleep(sample_interval)

    watch1 = asyncio.create_task(tracker.watch(api, cfg.real_asset))
    watch2 = asyncio.create_task(tracker.watch(api, cfg.otc_asset))
    await sampler()
    watch1.cancel()
    watch2.cancel()

    return gaps, abs_gaps


def report(gaps: list[float], abs_gaps: list[float]):
    if not gaps:
        print("No data collected.")
        return

    print(f"\n\n{'='*55}")
    print(f"  Gap Analysis Report  ({len(gaps)} samples)")
    print(f"{'='*55}")
    print(f"  Mean gap       : {statistics.mean(gaps):+.6f}")
    print(f"  Mean |gap|     : {statistics.mean(abs_gaps):.6f}")
    print(f"  Median |gap|   : {statistics.median(abs_gaps):.6f}")
    print(f"  Stdev          : {statistics.stdev(gaps):.6f}")
    print(f"  Max gap        : {max(gaps):+.6f}")
    print(f"  Min gap        : {min(gaps):+.6f}")
    print(f"  Max |gap|      : {max(abs_gaps):.6f}")

    # Show how many signals each threshold would give
    thresholds = [0.0003, 0.0005, 0.0008, 0.0010, 0.0013, 0.0015, 0.0020, 0.0030]
    print(f"\n  {'Threshold':<12} {'Signals':>8} {'% of time':>10}")
    print(f"  {'-'*32}")
    for t in thresholds:
        count = sum(1 for g in abs_gaps if g >= t)
        pct = count / len(abs_gaps) * 100
        print(f"  {t:<12.4f} {count:>8} {pct:>9.2f}%")

    print()


def main():
    p = argparse.ArgumentParser(description="Collect and analyze EURUSD vs OTC gap data")
    p.add_argument("--ssid", type=str, default="", help="Session ID")
    p.add_argument("--minutes", type=float, default=10, help="Minutes to collect data")
    p.add_argument("--interval", type=float, default=0.5, help="Seconds between samples")
    args = p.parse_args()

    ssid = args.ssid or input("Enter your SSID: ").strip()
    gaps, abs_gaps = asyncio.run(collect_gaps(ssid, args.minutes, args.interval))
    report(gaps, abs_gaps)


if __name__ == "__main__":
    main()
