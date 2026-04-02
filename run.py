import asyncio
import argparse
from BinaryOptionsToolsV2.pocketoption import PocketOptionAsync
from BinaryOptionsToolsV2.tracing import start_logs

from bot.config import BotConfig
from bot.price_tracker import PriceTracker
from bot.strategy import GapStrategy, Signal
from bot.trader import Trader
from bot.stats import TradeLogger


async def run_bot(ssid: str, cfg: BotConfig):
    """Connect, stream prices, and trade on gap signals."""
    if cfg.log_level:
        start_logs(cfg.log_dir, cfg.log_level, terminal=cfg.log_to_terminal)

    api = PocketOptionAsync(ssid)
    await asyncio.sleep(5)

    balance = await api.balance()
    print(f"[*] Connected — Balance: {balance}")
    print(f"\n{'='*55}")
    print(f"  Gap Arbitrage Bot")
    print(f"{cfg.summary()}")
    print(f"{'='*55}\n")

    tracker = PriceTracker()
    strategy = GapStrategy(cfg.gap_threshold)
    logger = TradeLogger(cfg.results_file)
    trader = Trader(
        api,
        otc_asset=cfg.otc_asset,
        amount=cfg.amount,
        duration=cfg.duration,
        cooldown=cfg.cooldown,
        logger=logger,
    )

    async def trade_loop():
        await tracker.wait_for_prices(cfg.real_asset, cfg.otc_asset)
        print("[*] Prices received. Monitoring gap...\n")

        while True:
            real = tracker.get(cfg.real_asset)
            otc = tracker.get(cfg.otc_asset)
            if real is None or otc is None:
                await asyncio.sleep(0.25)
                continue

            signal = strategy.evaluate(real, otc)

            tag = " <<< SIGNAL" if signal.signal is not Signal.NONE else ""
            print(
                f"  {cfg.real_asset}: {real:.5f}  |  OTC: {otc:.5f}  |  "
                f"Gap: {signal.gap:+.5f}{tag}",
                end="\r",
            )

            await trader.execute(signal)
            await asyncio.sleep(0.25)

    await asyncio.gather(
        tracker.watch(api, cfg.real_asset),
        tracker.watch(api, cfg.otc_asset),
        trade_loop(),
    )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="PocketOption Gap Arbitrage Bot")
    p.add_argument("--ssid", type=str, default="", help="Session ID (prompted if empty)")
    p.add_argument("--threshold", type=float, default=None, help="Gap threshold (e.g. 0.0015)")
    p.add_argument("--amount", type=float, default=None, help="Trade amount in $")
    p.add_argument("--duration", type=int, default=None, help="Option expiry in seconds")
    p.add_argument("--cooldown", type=float, default=None, help="Seconds between trades")
    p.add_argument("--results", type=str, default=None, help="CSV file for trade results")
    p.add_argument("--log-level", type=str, default=None, help="Log level (DEBUG/INFO/WARN)")
    return p.parse_args()


def main():
    args = parse_args()

    cfg = BotConfig()
    if args.threshold is not None:
        cfg.gap_threshold = args.threshold
    if args.amount is not None:
        cfg.amount = args.amount
    if args.duration is not None:
        cfg.duration = args.duration
    if args.cooldown is not None:
        cfg.cooldown = args.cooldown
    if args.results is not None:
        cfg.results_file = args.results
    if args.log_level is not None:
        cfg.log_level = args.log_level

    ssid = args.ssid or input("Enter your SSID: ").strip()
    asyncio.run(run_bot(ssid, cfg))


if __name__ == "__main__":
    main()
