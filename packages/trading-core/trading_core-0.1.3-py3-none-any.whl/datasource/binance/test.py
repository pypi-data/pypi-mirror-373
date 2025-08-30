import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from trading_core.utilities.LoadJsonConfig import LoadJsonConfig

from main import binance_stream
if __name__ == "__main__":
    config_path = os.getenv("CONFIG_PATH", "config.json")
    config = LoadJsonConfig(config_path)
    binance_stream(config)