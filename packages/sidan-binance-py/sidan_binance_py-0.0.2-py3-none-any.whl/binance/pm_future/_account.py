def balance(self, **kwargs):
    """
    https://developers.binance.com/docs/derivatives/portfolio-margin/account
    """

    url_path = "/papi/v1/balance"
    payload = {**kwargs}
    return self.sign_request("GET", url_path, payload)
