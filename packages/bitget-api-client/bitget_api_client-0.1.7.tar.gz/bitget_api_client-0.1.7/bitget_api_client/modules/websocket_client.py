import asyncio
import time
import json
import websockets as ws_lib
import base64
import hmac
import hashlib
from typing import Optional, Any, Protocol, runtime_checkable, Iterable, AsyncIterable, cast

from .exceptions import BitgetAPIWebSocketException

# Protocol for WebSocket client
@runtime_checkable
class _WSProto(Protocol):
    @property
    def closed(self) -> bool: ...
    async def send(self, message: Any, text: Optional[bool] = None) -> None: ...
    async def recv(self) -> Any: ...
    async def close(self, code: int = ..., reason: str = ...) -> None: ...

class RateLimiter:
    def __init__(self, rate_limit_per_second):
        self.rate_limit_per_second = rate_limit_per_second
        self.interval = 1.0 / rate_limit_per_second
        self.last_request_time = 0
        self.lock = asyncio.Lock()

    async def wait_for_permission(self):
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_request_time
            if elapsed < self.interval:
                await asyncio.sleep(self.interval - elapsed)
            self.last_request_time = time.time()

class WebSocketClient:
    def __init__(self, url, api_key, secret_key, passphrase):
        self.url = url
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self._last_pong_time = time.time()
        self._websocket: Optional[_WSProto] = None  # websockets client protocol instance
        self._ping_task = None # To hold the asyncio task for sending pings
        self.ws_limiter = RateLimiter(10) # 10 messages per second for WebSocket

    def _is_open(self) -> bool:
        """
        Checks if the WebSocket connection is currently open.

        Returns:
            bool: True if the connection is open, False otherwise.
        """
        return self._websocket is not None and not getattr(self._websocket, "closed", True)

    async def _send_ping(self):
        """
        Sends a ping message to the WebSocket server periodically to keep the connection alive.
        This task runs indefinitely until the WebSocket connection is closed.
        """
        while self._websocket is not None and not getattr(self._websocket, "closed", True):
            try:
                assert self._websocket is not None
                await self._websocket.send("ping")
                # print("Sent ping") # For debugging
            except ws_lib.exceptions.ConnectionClosedOK:
                print("WebSocket connection closed, stopping ping.")
                break
            except Exception as e:
                print(f"Error sending ping: {e}")
            await asyncio.sleep(30) # Send ping every 30 seconds as per documentation

    async def _receive_messages(self):
        """
        Continuously receives messages from the WebSocket connection.
        Processes received messages, handles pongs, and raises exceptions for API errors.
        """
        while self._websocket is not None and not getattr(self._websocket, "closed", True):
            try:
                message = await self._websocket.recv()
                # Process the message similar to _on_message
                if message == "pong":
                    self._last_pong_time = time.time()
                    # print("Received pong") # For debugging
                    continue

                try:
                    json_message = json.loads(message)
                    if "event" in json_message and json_message["event"] == "error":
                        error_code = json_message.get("code")
                        error_message = f"Bitget WebSocket API Error (Code: {error_code}): {json_message.get('msg', 'Unknown WebSocket error')}"
                        raise BitgetAPIWebSocketException(error_message, code=error_code)
                    elif "code" in json_message and json_message["code"] != "0": # Assuming '0' is success for WebSocket
                        error_code = json_message.get("code")
                        error_message = f"Bitget WebSocket API Error (Code: {error_code}): {json_message.get('msg', 'Unknown WebSocket error')}"
                        raise BitgetAPIWebSocketException(error_message, code=error_code)
                    # print(f"Received: {message}") # Keep for debugging if needed
                    # Implement message parsing and handling
                except json.JSONDecodeError:
                    # print(f"Received non-JSON message: {message}") # For debugging
                    pass # Non-JSON messages might be pings or other non-error messages
                except BitgetAPIWebSocketException as e:
                    print(f"Bitget WebSocket API Error: {e}")
                    # Depending on desired behavior, you might want to re-raise or handle differently
                except Exception as e:
                    print(f"Unexpected error in _receive_messages processing: {e}")

            except ws_lib.exceptions.ConnectionClosedOK:
                print("WebSocket connection closed normally.")
                break
            except Exception as e:
                print(f"Error receiving message: {e}")
                if self._ping_task and not self._ping_task.done():
                    self._ping_task.cancel()
                break

    async def connect(self):
        """
        Establishes a WebSocket connection to the Bitget API.
        Sends a login message upon successful connection and starts a background task to receive messages.

        Raises:
            ConnectionError: If the WebSocket connection fails to establish.
            BitgetAPIWebSocketException: If a WebSocket API error occurs during login.
        """
        if self._websocket is not None and not getattr(self._websocket, "closed", True):
            return # Already connected

        try:
            self._websocket = cast(_WSProto, await ws_lib.connect(self.url))
            self._last_pong_time = time.time()

            # Start ping task
            if self._ping_task is None or self._ping_task.done():
                self._ping_task = asyncio.create_task(self._send_ping())

            # Send login message
            timestamp = str(int(time.time() * 1000))
            message_for_sign = timestamp + "GET" + "/user/verify"
            hmac_key = self.secret_key.encode('utf-8')
            signature = base64.b64encode(hmac.new(hmac_key, message_for_sign.encode('utf-8'), hashlib.sha256).digest()).decode()

            login_message = {
                "op": "login",
                "args": [
                    {
                        "apiKey": self.api_key,
                        "passphrase": self.passphrase,
                        "timestamp": timestamp,
                        "sign": signature
                    }
                ]
            }
            await self.send_message(login_message)

            # Start receiving messages in a separate task
            asyncio.create_task(self._receive_messages())

        except Exception as e:
            if self._ping_task and not self._ping_task.done():
                self._ping_task.cancel()
            raise ConnectionError(f"Failed to establish WebSocket connection: {e}")

    async def send_message(self, message):
        """
        Sends a message over the WebSocket connection.
        Applies rate limiting and attempts to re-establish connection if necessary.

        Args:
            message (dict): The message to send, which will be JSON serialized.

        Returns:
            dict: A dictionary indicating the status of the message sending operation.

        Raises:
            ConnectionError: If the WebSocket connection cannot be established or maintained.
        """
        await self.ws_limiter.wait_for_permission()  # Apply rate limiting

        # Ensure connection is established
        if self._websocket is None or getattr(self._websocket, "closed", True):
            try:
                await self.connect()
            except ConnectionError as e:
                raise ConnectionError(f"Failed to establish WebSocket connection before sending message: {e}")

        ws = self._websocket # ws is guaranteed to be not None and not closed here
        assert ws is not None
        try:
            await ws.send(json.dumps(message))
            return {"status": "message sent"}
        except Exception as e:
            raise ConnectionError(f"Failed to send WebSocket message: {e}")

    async def close(self):
        """
        Closes the WebSocket connection and cancels any running ping tasks.
        """
        if self._websocket is not None:
            await self._websocket.close()
            self._websocket = None
        if self._ping_task and not self._ping_task.done():
            self._ping_task.cancel()
