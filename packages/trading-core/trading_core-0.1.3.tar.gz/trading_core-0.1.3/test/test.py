import os
import sys
from trading_core.utilities.LoadJsonConfig import LoadJsonConfig
from datasource.binance.main import binance_stream

if __name__ == "__main__":
    config_path = os.getenv("CONFIG_PATH", "config.json")
    config = LoadJsonConfig(config_path)
    binance_stream(config)