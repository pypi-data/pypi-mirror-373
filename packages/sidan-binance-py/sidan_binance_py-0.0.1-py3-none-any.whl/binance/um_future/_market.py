from typing import Optional
from binance.lib.utils import check_required_parameter


def ticker_24hr(self, symbol: Optional[str] = None, **kwargs):
    """24hr Ticker Price Change Statistics

    GET /fapi/v1/ticker/24hr

    https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/24hr-Ticker-Price-Change-Statistics

    Args:
        symbol (str, optional): the trading pair
    """

    params = {
        "symbol": symbol,
        **kwargs,
    }
    return self.query("/fapi/v1/ticker/24hr", params)


def depth(self, symbol: str, **kwargs):
    """Get orderbook.

    GET /fapi/v1/depth

    https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Order-Book

    Args:
        symbol (str): the trading pair
    Keyword Args:
        limit (int, optional): Default 500; Valid limits:[5, 10, 20, 50, 100, 500, 1000]
    """

    check_required_parameter(symbol, "symbol")
    params = {"symbol": symbol, **kwargs}
    return self.query("/fapi/v1/depth", params)
