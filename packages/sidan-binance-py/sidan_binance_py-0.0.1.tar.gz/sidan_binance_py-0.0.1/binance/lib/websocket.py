import time

import requests
from binance.websocket.websocket_client import BinanceWebsocketClient


class WebSocket:
    def __init__(
        self,
        api_key=None,
        private_key=None,
        base_url=None,
        ws_url=None,
        listen_key_url_path=None,
        **kwargs,
    ):
        self.api_key = api_key
        self.private_key = private_key
        self.base_url = base_url
        self.ws_url = ws_url
        self.listen_key_url_path = listen_key_url_path
        self.listen_key = None
        self.ws = None
        self.stop_flag = False

    def extend_listen_key(self):
        """Extend the validity of the listenKey."""
        url = f"{self.base_url}{self.listen_key_url_path}"
        headers = {"X-MBX-APIKEY": self.api_key}
        response = requests.put(url, headers=headers)
        if response.status_code == 200:
            print("ListenKey extended successfully.")
        else:
            raise Exception(f"Failed to extend listenKey: {response.json()}")

    def delete_listen_key(self):
        """Delete the listenKey."""
        url = f"{self.base_url}{self.listen_key_url_path}"
        headers = {"X-MBX-APIKEY": self.api_key}
        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            print("ListenKey deleted successfully.")
        else:
            print(f"Failed to delete listenKey: {response.json()}")

    def create_listen_key(self):
        """Create a new listenKey."""
        url_path = f"{self.base_url}{self.listen_key_url_path}"
        headers = {"X-MBX-APIKEY": self.api_key}
        response = requests.post(url_path, headers=headers)
        if response.status_code == 200:
            self.listen_key = response.json()["listenKey"]
            print(f"ListenKey created: {self.listen_key}")
        else:
            raise Exception(f"Failed to create listenKey: {response.json()}")

    def start_websocket(self):
        ws_url = f"{self.ws_url}/{self.listen_key}"
        client = BinanceWebsocketClient(
            stream_url=ws_url,
            on_message=self.on_message,
            on_close=self.on_close,
        )
        self.ws = client

    def on_close(self, ws, close_status_code, close_msg):
        print(f"WebSocket connection closed: {close_status_code}, {close_msg}")
        if not self.stop_flag:  # Attempt to reconnect if not explicitly stopped
            print("Reconnecting WebSocket...")
            self.start_websocket()

    def keep_alive(self):
        """Keep the listenKey alive by extending it every 30 minutes."""

        listen_key_lifetime = 0

        while not self.stop_flag:
            time.sleep(30)
            listen_key_lifetime += 30

            if listen_key_lifetime >= 1800:  # 30 minutes
                try:
                    self.extend_listen_key()
                    listen_key_lifetime = 0
                except Exception as e:
                    print(f"Error extending listenKey: {e}")

    def stop(self):
        """Stop the WebSocket connection and delete the listenKey."""
        self.stop_flag = True
        if self.ws:
            self.ws.close()
        self.delete_listen_key()
