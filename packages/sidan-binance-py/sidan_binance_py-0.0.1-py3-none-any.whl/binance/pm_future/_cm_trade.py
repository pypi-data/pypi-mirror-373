from binance.error import ParameterArgumentError
from binance.lib.utils import check_required_parameter, check_required_parameters


def cm_new_order(self, symbol: str, side: str, type: str, **kwargs):
    r"""New Order (TRADE)

        Post a new order

        POST /papi/v1/cm/order

    https://developers.binance.com/docs/derivatives/portfolio-margin/trade/New-CM-Order

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
            priceMatch (str, optional): only avaliable for LIMIT/STOP/TAKE_PROFIT order; can be set to OPPONENT/ OPPONENT_5/ OPPONENT_10/ OPPONENT_20: /QUEUE/ QUEUE_5/ QUEUE_10/ QUEUE_20; Can't be passed together with price
            newClientOrderId (str, optional): A unique id among open orders. Automatically generated if not sent. Can only be string following the rule: ^[\.A-Z\:/a-z0-9_-]{1,36}$
            newOrderRespType (str, optional): "ACK", "RESULT", default "ACK"
            selfTradePreventionMode (str, optional): NONE:No STP / EXPIRE_TAKER:expire taker order when STP triggers/ EXPIRE_MAKER:expire taker order when STP triggers/ EXPIRE_BOTH:expire both orders when STP triggers; default NONE
            recvWindow (int, optional): The value cannot be greater than 60000
            timestamp (int, optional)
    """

    check_required_parameters([[symbol, "symbol"], [side, "side"], [type, "type"]])
    params = {"symbol": symbol, "side": side, "type": type, **kwargs}
    url_path = "/papi/v1/cm/order"
    return self.sign_request("POST", url_path, params)


def cm_cancel_order(
    self, symbol: str, order_id: str = None, orig_client_order_id: str = None, **kwargs
):
    """
    https://developers.binance.com/docs/derivatives/portfolio-margin/trade/Cancel-CM-Order
    """

    check_required_parameter(symbol, "symbol")

    if order_id is None and orig_client_order_id is None:
        raise ParameterArgumentError("orderId or origClientOrderId must be sent.")

    if order_id and orig_client_order_id:
        raise ParameterArgumentError("symbol and symbols cannot be sent together.")

    params = {
        "symbol": symbol,
        "orderId": order_id,
        "origClientOrderId": orig_client_order_id,
        **kwargs,
    }
    url_path = "/papi/v1/cm/order"
    return self.sign_request("DELETE", url_path, params)


def cm_get_order(self, symbol, **kwargs):
    """Query Order (USER_DATA)

    Check an order's status.

    GET /papi/v1/cm/order

    https://developers.binance.com/docs/derivatives/portfolio-margin/trade/Query-CM-Order

    Args:
        symbol (str)
    Keyword Args:
        orderId (int, optional)
        origClientOrderId (str, optional)
        recvWindow (int, optional): The value cannot be greater than 60000
    """
    check_required_parameter(symbol, "symbol")

    url_path = "/papi/v1/cm/order"
    payload = {"symbol": symbol, **kwargs}
    return self.sign_request("GET", url_path, payload)
