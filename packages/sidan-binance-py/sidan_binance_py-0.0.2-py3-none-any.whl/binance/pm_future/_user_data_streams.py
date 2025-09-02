import json
import threading

from binance.lib.websocket import WebSocket


class PMFutureWebSocket(WebSocket):
    def __init__(self, base_url=None, api_key=None, api_secret=None, **kwargs):
        super().__init__(
            base_url=base_url,
            ws_url="wss://fstream.binance.com/pm/ws",
            api_key=api_key,
            api_secret=api_secret,
            listen_key_url_path="/papi/v1/listenKey",
            **kwargs,
        )
        self.on_events = {}

    def on_message(self, ws, message):
        """Handle incoming WebSocket messages."""
        print(f"Received message: {message}")

        try:
            data = json.loads(message)  # Parse the JSON message
            event_type = data.get("e")  # Get the event type
            # if event_type is in self.on_events, then call the values of the dict (as a callback function)
            if event_type in self.on_events:
                callback = self.on_events[event_type]
                callback(data)
            else:
                print(f"Current handled event type: {self.on_events}")
                print(f"Unhandled event type: {event_type}")
        except Exception as e:
            print(f"Error processing message: {e}")


def connect_user_data_streams(self):
    self.ws_client.create_listen_key()
    self.ws_client.start_websocket()
    # Start the keep-alive thread
    threading.Thread(target=self.ws_client.keep_alive, daemon=True).start()


def stop_user_data_streams(self):
    self.ws_client.stop()


def on_user_data_streams_event(self, event: str, callback):
    """
    Handle incoming events from the WebSocket.

    Args:
        event (str): The event type to listen for.
        callback (function): The function to call when the event occurs. It takes the argument of event details
    """
    self.ws_client.on_events[event] = callback
