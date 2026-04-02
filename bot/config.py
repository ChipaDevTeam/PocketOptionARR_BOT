from dataclasses import dataclass, field


@dataclass
class BotConfig:
    """All tunable parameters for the gap arbitrage bot."""

    # Assets
    real_asset: str = "EURUSD"
    otc_asset: str = "EURUSD_otc"

    # Strategy
    gap_threshold: float = 0.00150   # Minimum |gap| to trigger a trade
    cooldown: float = 60.0           # Seconds between trades

    # Trade sizing
    amount: float = 1.0              # USD per trade
    duration: int = 60               # Option expiry in seconds

    # Logging
    log_level: str = "INFO"
    log_to_terminal: bool = True
    log_dir: str = "."

    # Results CSV (appended after every trade)
    results_file: str = "trade_results.csv"

    def summary(self) -> str:
        return (
            f"  Pair       : {self.real_asset} vs {self.otc_asset}\n"
            f"  Threshold  : ±{self.gap_threshold}\n"
            f"  Amount     : ${self.amount}\n"
            f"  Duration   : {self.duration}s\n"
            f"  Cooldown   : {self.cooldown}s\n"
            f"  Results CSV: {self.results_file}"
        )
