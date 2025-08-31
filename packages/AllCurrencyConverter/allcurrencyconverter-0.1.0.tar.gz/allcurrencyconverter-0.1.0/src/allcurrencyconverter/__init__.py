import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent / "allcurrencyconverter"
sys.path.insert(0, str(root))


from .adapter import ExchangeRatesAPIAdapter
from .converter import CurrencyConverter


__all__ = ["__version__", "ExchangeRatesAPIAdapter", "CurrencyConverter"]

__version__ = "0.1.0"
