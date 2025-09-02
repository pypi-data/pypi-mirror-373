from binance.api import API
from binance.pm_future._user_data_streams import PMFutureWebSocket


class PMFuture(API):
    def __init__(self, api_key=None, api_secret=None, **kwargs):
        base_url = "https://papi.binance.com"
        super().__init__(
            api_key=api_key, api_secret=api_secret, base_url=base_url, **kwargs
        )
        self.ws_client = PMFutureWebSocket(
            base_url=base_url,
            api_key=api_key,
            api_secret=api_secret,
            **kwargs,
        )

    # PM-ACCOUNT
    from binance.pm_future._account import balance

    # CM-TRADE
    from binance.pm_future._cm_trade import cm_cancel_order, cm_get_order, cm_new_order

    # UM-TRADE
    from binance.pm_future._um_trade import um_cancel_order, um_get_order, um_new_order

    # PM-USER-DATA-STREAMS
    from binance.pm_future._user_data_streams import (
        connect_user_data_streams,
        on_user_data_streams_event,
        stop_user_data_streams,
    )

    # # UM-MARKET
    # from binance.portfolio_margin._market import um_24hr, um_depth
