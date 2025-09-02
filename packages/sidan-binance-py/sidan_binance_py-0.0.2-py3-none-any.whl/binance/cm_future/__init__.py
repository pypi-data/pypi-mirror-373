from binance.api import API


class CMFuture(API):
    def __init__(self, api_key=None, api_secret=None, **kwargs):
        kwargs["base_url"] = "https://dapi.binance.com"
        super().__init__(api_key, api_secret, **kwargs)

    # CM-ACCOUNT
    from binance.cm_future._account import balance

    # CM-MARKET
    from binance.cm_future._market import depth, ticker_24hr

    # CM-TRADE
    from binance.cm_future._trade import all_orders, get_order, new_order
