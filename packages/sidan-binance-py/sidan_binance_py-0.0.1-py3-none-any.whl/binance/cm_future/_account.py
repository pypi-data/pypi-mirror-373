def balance(self, **kwargs):
    url_path = "/dapi/v1/balance"
    payload = {**kwargs}
    return self.sign_request("GET", url_path, payload)
