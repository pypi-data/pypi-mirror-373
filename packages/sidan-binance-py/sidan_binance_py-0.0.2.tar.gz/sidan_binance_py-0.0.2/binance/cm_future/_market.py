from binance.error import ParameterArgumentError
from binance.lib.utils import check_required_parameter


def ticker_24hr(self, symbol: str = None, pair: str = None, **kwargs):
    """24hr Ticker Price Change Statistics

    GET /dapi/v1/ticker/24hr

    https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#24hr-ticker-price-change-statistics

    Args:
        symbol (str, optional): the trading pair
        symbols (list, optional): list of trading pairs
    """

    if symbol and pair:
        raise ParameterArgumentError("symbol and symbols cannot be sent together.")

    params = {
        "symbol": symbol,
        "pair": pair,
        **kwargs,
    }
    return self.query("/dapi/v1/ticker/24hr", params)


def depth(self, symbol: str, **kwargs):
    """Get orderbook.

    GET /dapi/v1/depth

    https://developers.binance.com/docs/derivatives/coin-margined-futures/market-data/Order-Book

    Args:
        symbol (str): the trading pair
    Keyword Args:
        limit (int, optional): Default 500; Valid limits:[5, 10, 20, 50, 100, 500, 1000]
    """

    check_required_parameter(symbol, "symbol")
    params = {"symbol": symbol, **kwargs}
    return self.query("/dapi/v1/depth", params)
