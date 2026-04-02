"""
Quick script to view trade result statistics from the CSV log.

Usage:
    python view_stats.py
    python view_stats.py --file my_results.csv
"""

import argparse
from bot.stats import print_stats


def main():
    p = argparse.ArgumentParser(description="View trade result statistics")
    p.add_argument("--file", type=str, default="trade_results.csv", help="CSV results file")
    args = p.parse_args()
    print_stats(args.file)


if __name__ == "__main__":
    main()
