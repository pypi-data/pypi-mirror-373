import requests
import hmac
import hashlib
import time
import json
import asyncio
import aiohttp
import websockets as ws_lib

import base64

from bitget_api_client.modules.exceptions import BitgetAPIAuthException, BitgetAPIParameterException, BitgetAPIException, BitgetAPINetworkException

from .modules.websocket_client import WebSocketClient, RateLimiter


class BitgetApiClient:
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.base_url = "https://api.bitget.com"
        self.websocket_base_url = "wss://ws.bitget.com/v2/ws"
        self.ws_client = WebSocketClient(self.websocket_base_url, api_key, secret_key, passphrase)
        self.session = aiohttp.ClientSession() # Initialize aiohttp client session
        self.rest_limiter = RateLimiter(100) # 100 requests per second for REST API
        self.affiliate = Affiliate(self)
        self.broker = Broker(self)
        self.common = Common(self)
        self.contract = Contract(self)
        self.copytrading = CopyTrading(self)
        self.earn = Earn(self)
        self.instloan = Instloan(self)
        self.margin = Margin(self)
        self.spot = Spot(self)
        self.uta = Uta(self)

    async def close(self):
        await self.session.close()

    def _sign(self, message):
        hmac_key = self.secret_key.encode('utf-8')
        signature = base64.b64encode(hmac.new(hmac_key, message.encode('utf-8'), hashlib.sha256).digest()).decode()
        return signature

    async def _send_request(self, method, request_path, params=None, body=None):
        await self.rest_limiter.wait_for_permission() # Apply rate limiting
        timestamp = str(int(time.time() * 1000))
        
        # Construct query string for URL and for signing
        query_string_for_url = ""
        query_string_for_sign = ""
        if params:
            # Sort parameters alphabetically by key for consistent signing
            sorted_params = sorted(params.items(), key=lambda x: x[0])
            query_string_for_url = '&'.join([f"{k}={v}" for k, v in sorted_params])
            query_string_for_sign = query_string_for_url # For signing, it's just the string without '?'

        # Construct the message for signing based on method and presence of query/body
        message_for_sign = timestamp + str.upper(method) + request_path
        if query_string_for_sign:
            message_for_sign += "?" + query_string_for_sign
        if body:
            message_for_sign += json.dumps(body) # body should be a dict, json.dumps it here

        signature = self._sign(message_for_sign) # Pass the constructed message

        headers = {
            "ACCESS-KEY": self.api_key,
            "ACCESS-SIGN": signature,
            "ACCESS-PASSPHRASE": self.passphrase,
            "ACCESS-TIMESTAMP": timestamp,
            "Content-Type": "application/json",
            "locale": "en-US"
        }

        url = self.base_url + request_path
        if query_string_for_url:
            url += "?" + query_string_for_url

        response = None # Initialize response to None

        try:
            if method == "GET":
                async with self.session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    json_response = await response.json()
            elif method == "POST":
                async with self.session.post(url, headers=headers, json=body) as response:
                    response.raise_for_status()
                    json_response = await response.json()
            else:
                raise ValueError("Unsupported HTTP method")
            
            # Check for Bitget-specific error codes in the JSON response
            if "code" in json_response and json_response["code"] != "00000":
                error_code = json_response["code"]
                error_message = f"Bitget API Error (Code: {error_code}): {json_response.get('msg', 'Unknown Bitget API error')}"
                http_status_code = response.status # aiohttp uses .status for HTTP status code

                # Categorize and raise specific exceptions
                if error_code in ["40001", "40002", "40003", "40004", "40005", "40006", "40008", "40009", "40011", "40012", "40013", "40036", "40037", "40038", "40039", "40040", "40041", "40048", "40049", "49000", "49001", "49002", "49003", "49004", "49005", "49006", "49009"]:
                    raise BitgetAPIAuthException(error_message, code=error_code, http_status_code=http_status_code)
                elif error_code in ["40017", "00171", "00172", "40019", "40020", "40053", "40057", "40058", "40059", "40070", "40071", "40808", "40809", "40810", "40811", "40812", "40813", "40913", "41101", "41103", "43058", "43123", "48001", "48002", "49024", "49025", "49026", "50011", "50061", "60006", "70006", "70007", "70008", "80001", "59013", "59014", "70101", "70102", "70103", "70104", "400172"]:
                    raise BitgetAPIParameterException(error_message, code=error_code, http_status_code=http_status_code)
                else:
                    raise BitgetAPIException(error_message, code=error_code, http_status_code=http_status_code)
            
            return json_response

        except aiohttp.ClientError as e:
            # Catch network-related errors (e.g., connection refused, timeout)
            status_code = getattr(e, 'status', None) # aiohttp.ClientError might have a status attribute
            raise BitgetAPINetworkException(f"Network error: {e}", http_status_code=status_code)
        except ValueError as e:
            # Catch errors during JSON decoding or unsupported HTTP method
            status_code = response.status if response is not None else None
            raise BitgetAPIException(f"Failed to decode JSON response or unsupported HTTP method: {e}", http_status_code=status_code)
        except Exception as e:
            # Catch any other unexpected errors
            status_code = response.status if response is not None else None
            raise BitgetAPIException(f"An unexpected error occurred: {e}", http_status_code=status_code)

    def _send_websocket_request(self, message):
        return self.ws_client.send_message(message)


from .modules.affiliate import Affiliate
from .modules.broker import Broker
from .modules.common import Common
from .modules.contract import Contract
from .modules.copytrading import CopyTrading
from .modules.spot import Spot
from .modules.uta import Uta
from .modules.earn import Earn
from .modules.instloan import Instloan
from .modules.margin import Margin
