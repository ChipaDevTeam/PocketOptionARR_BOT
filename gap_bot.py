from BinaryOptionsToolsV2.pocketoption import PocketOptionAsync
from BinaryOptionsToolsV2.tracing import start_logs
import asyncio

# ─── Configuration ───────────────────────────────────────────────
SSID = ""  # Will be prompted if empty
REAL_ASSET = "EURUSD"
OTC_ASSET = "EURUSD_otc"
GAP_THRESHOLD = 0.00150        # Minimum price gap to trigger a trade
TRADE_AMOUNT = 1.0           # Trade amount in $
TRADE_DURATION = 60          # Trade duration in seconds (1 min)
COOLDOWN_SECONDS = 60        # Cooldown between trades to avoid rapid fire
LOG_LEVEL = "INFO"

# ─── Shared state ────────────────────────────────────────────────
latest_price = {
    REAL_ASSET: None,
    OTC_ASSET: None,
}
last_trade_time = 0.0


async def watch_symbol(api: PocketOptionAsync, symbol: str):
    """Subscribe to a symbol and keep updating its latest price."""
    stream = await api.subscribe_symbol(symbol)
    async for candle in stream:
        latest_price[symbol] = float(candle["close"])


async def trade_loop(api: PocketOptionAsync):
    """Main loop: compare prices, detect gap, place trades."""
    global last_trade_time

    print(f"\n{'='*60}")
    print(f"  Gap Arbitrage Bot")
    print(f"  Pair: {REAL_ASSET} vs {OTC_ASSET}")
    print(f"  Threshold: ±{GAP_THRESHOLD}")
    print(f"  Trade: ${TRADE_AMOUNT} / {TRADE_DURATION}s")
    print(f"{'='*60}\n")

    # Wait until we have prices for both symbols
    while latest_price[REAL_ASSET] is None or latest_price[OTC_ASSET] is None:
        await asyncio.sleep(0.5)

    print("[*] Prices received for both symbols. Monitoring gap...\n")

    while True:
        real_price = latest_price[REAL_ASSET]
        otc_price = latest_price[OTC_ASSET]

        if real_price is None or otc_price is None:
            await asyncio.sleep(0.5)
            continue

        gap = real_price - otc_price
        now = asyncio.get_event_loop().time()

        # Log current state every tick
        direction_hint = ""
        if abs(gap) >= GAP_THRESHOLD:
            direction_hint = " <<< SIGNAL"
        print(
            f"  EURUSD: {real_price:.5f}  |  OTC: {otc_price:.5f}  |  "
            f"Gap: {gap:+.5f}{direction_hint}",
            end="\r",
        )

        if abs(gap) >= GAP_THRESHOLD and (now - last_trade_time) >= COOLDOWN_SECONDS:
            last_trade_time = now

            if gap > 0:
                # Real price is higher → OTC should correct UP → CALL
                print(
                    f"\n[TRADE] GAP {gap:+.5f} >= +{GAP_THRESHOLD} → "
                    f"CALL on {OTC_ASSET}  (${TRADE_AMOUNT}, {TRADE_DURATION}s)"
                )
                try:
                    (trade_id, data) = await api.buy(
                        asset=OTC_ASSET,
                        amount=TRADE_AMOUNT,
                        time=TRADE_DURATION,
                        check_win=False,
                    )
                    print(f"[OK]    Trade placed — ID: {trade_id}")
                    # Check result in background
                    asyncio.create_task(report_result(api, trade_id, "CALL", gap))
                except Exception as e:
                    print(f"[ERR]   Failed to place CALL: {e}")

            else:
                # Real price is lower → OTC should correct DOWN → PUT
                print(
                    f"\n[TRADE] GAP {gap:+.5f} <= -{GAP_THRESHOLD} → "
                    f"PUT  on {OTC_ASSET}  (${TRADE_AMOUNT}, {TRADE_DURATION}s)"
                )
                try:
                    (trade_id, data) = await api.sell(
                        asset=OTC_ASSET,
                        amount=TRADE_AMOUNT,
                        time=TRADE_DURATION,
                        check_win=False,
                    )
                    print(f"[OK]    Trade placed — ID: {trade_id}")
                    asyncio.create_task(report_result(api, trade_id, "PUT", gap))
                except Exception as e:
                    print(f"[ERR]   Failed to place PUT: {e}")

        await asyncio.sleep(0.25)


async def report_result(api: PocketOptionAsync, trade_id: str, direction: str, gap: float):
    """Wait for a trade to finish and print the result."""
    try:
        result = await api.check_win(trade_id)
        outcome = result.get("result", "unknown")
        print(
            f"\n[RESULT] {direction} (gap {gap:+.5f}) → {outcome.upper()}  "
            f"| data: {result}"
        )
    except Exception as e:
        print(f"\n[RESULT] Could not check trade {trade_id}: {e}")


async def main(ssid: str):
    # start_logs(".", LOG_LEVEL, terminal=True)

    api = PocketOptionAsync(ssid)
    await asyncio.sleep(5)  # Let the connection establish

    balance = await api.balance()
    print(f"[*] Connected — Balance: {balance}")

    # Launch price watchers + trade loop concurrently
    await asyncio.gather(
        watch_symbol(api, REAL_ASSET),
        watch_symbol(api, OTC_ASSET),
        trade_loop(api),
    )


if __name__ == "__main__":
    ssid = SSID or input("Enter your SSID: ").strip()
    asyncio.run(main(ssid))
