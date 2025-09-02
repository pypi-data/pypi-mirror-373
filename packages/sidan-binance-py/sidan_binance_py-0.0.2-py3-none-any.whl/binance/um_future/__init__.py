from binance.api import API


class UMFuture(API):
    def __init__(self, api_key=None, api_secret=None, **kwargs):
        kwargs["base_url"] = "https://fapi.binance.com"
        super().__init__(api_key, api_secret, **kwargs)

    # UM-ACCOUNT
    from binance.um_future._account import balance

    # UM-MARKET
    from binance.um_future._market import depth, ticker_24hr

    # UM-TRADE
    from binance.um_future._trade import get_order, new_order, position_margin_history
