from binance.lib.utils import check_required_parameter, check_required_parameters


def new_order(self, symbol: str, side: str, type: str, **kwargs):
    r"""New Order (TRADE)

    Post a new order

    POST /dapi/v1/order

    https://developers.binance.com/docs/derivatives/coin-margined-futures/trade

    Args:
        symbol (str)
        side (str)
        type (str)
    Keyword Args:
        positionSide (str, optional): Default BOTH for One-way Mode ; LONG or SHORT for Hedge Mode. It must be sent in Hedge Mode.
        timeInForce (str, optional)
        quantity (float, optional): quantity measured by contract number, Cannot be sent with closePosition=true
        reduceOnly (str, optional): "true" or "false". default "false". Cannot be sent in Hedge Mode; cannot be sent with closePosition=true(Close-All)
        price (float, optional)
        newClientOrderId (str, optional): A unique id among open orders. Automatically generated if not sent. Can only be string following the rule: ^[\.A-Z\:/a-z0-9_-]{1,36}$
        stopPrice (float, optional): Used with STOP/STOP_MARKET or TAKE_PROFIT/TAKE_PROFIT_MARKET orders.
        closePosition (str, optional): true, false；Close-All,used with STOP_MARKET or TAKE_PROFIT_MARKET.
        activationPrice (float, optional): Used with TRAILING_STOP_MARKET orders, default as the latest price(supporting different workingType)
        callbackRate (float, optional): Used with TRAILING_STOP_MARKET orders, min 0.1, max 5 where 1 for 1%
        workingType (str, optional): stopPrice triggered by: "MARK_PRICE", "CONTRACT_PRICE". Default "CONTRACT_PRICE"
        priceProtect (str, optional): "TRUE" or "FALSE", default "FALSE". Used with STOP/STOP_MARKET or TAKE_PROFIT/TAKE_PROFIT_MARKET orders.
        newOrderRespType (str, optional): "ACK", "RESULT", default "ACK"
        priceMatch (str, optional): only avaliable for LIMIT/STOP/TAKE_PROFIT order; can be set to OPPONENT/ OPPONENT_5/ OPPONENT_10/ OPPONENT_20: /QUEUE/ QUEUE_5/ QUEUE_10/ QUEUE_20; Can't be passed together with price
        selfTradePreventionMode (str, optional): NONE:No STP / EXPIRE_TAKER:expire taker order when STP triggers/ EXPIRE_MAKER:expire taker order when STP triggers/ EXPIRE_BOTH:expire both orders when STP triggers; default NONE
        recvWindow (int, optional): The value cannot be greater than 60000
        timestamp (int, optional)
    """

    check_required_parameters([[symbol, "symbol"], [side, "side"], [type, "type"]])
    params = {"symbol": symbol, "side": side, "type": type, **kwargs}
    url_path = "/dapi/v1/order"
    return self.sign_request("POST", url_path, params)


def all_orders(self, **kwargs):
    # """Margin account borrow/repay (MARGIN)

    # Margin account borrow/repay(MARGIN)

    # POST /sapi/v1/margin/borrow-repay

    # https://developers.binance.com/docs/margin_trading/borrow-and-repay/Margin-Account-Borrow-Repay

    # Args:
    #     asset (str): The asset being transferred, e.g., BTC.
    #     isIsolated (str): for isolated margin or not,"TRUE", "FALSE", default "FALSE".
    #     symbol (str): isolated symbol
    #     amount (float):
    #     type (str): BORROW or REPAY
    # Keyword Args:
    #     recvWindow (int, optional): The value cannot be greater than 60000
    # """

    # symbol	STRING	NO
    # pair	STRING	NO
    # orderId	LONG	NO
    # startTime	LONG	NO
    # endTime	LONG	NO
    # limit	INT	NO	Default 50; max 100.
    # recvWindow	LONG	NO
    # timestamp	LONG	YES

    # check_required_parameters(
    #     [
    #         [asset, "asset"],
    #         [amount, "amount"],
    #         [type, "type"],
    #         [isIsolated, "isIsolated"],
    #         [symbol, "symbol"],
    #     ]
    # )

    payload = {
        **kwargs,
    }
    return self.sign_request("GET", "/dapi/v1/allOrders", payload)


def get_order(self, symbol, **kwargs):
    """Query Order (USER_DATA)

    Check an order's status.

    GET /dapi/v1/order

    https://developers.binance.com/docs/derivatives/coin-margined-futures/trade/Query-Order

    Args:
        symbol (str)
    Keyword Args:
        orderId (int, optional)
        origClientOrderId (str, optional)
        recvWindow (int, optional): The value cannot be greater than 60000
    """
    check_required_parameter(symbol, "symbol")

    url_path = "/dapi/v1/order"
    payload = {"symbol": symbol, **kwargs}
    return self.sign_request("GET", url_path, payload)
