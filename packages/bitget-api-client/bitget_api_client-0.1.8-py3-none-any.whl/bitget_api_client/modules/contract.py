from .exceptions import BitgetAPIException

class Contract:
    def __init__(self, client):
        self.client = client

    async def adjust_position_margin(self, symbol, productType, marginCoin, holdSide, amount):
        """
        Add or reduce the margin (only for isolated margin mode).

        Args:
            symbol (str): Trading pair.
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            marginCoin (str): Margin coin (must be capitalized).
            holdSide (str): Position direction: `long` (long position) or `short` (short position).
            amount (str): Margin amount, positive means increase, and negative means decrease.

        Returns:
            dict: Bitget API JSON response indicating success.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/account/set-margin"
        body = {
            "symbol": symbol,
            "productType": productType,
            "marginCoin": marginCoin,
            "holdSide": holdSide,
            "amount": amount
        }
        return await self.client._send_request("POST", request_path, body=body)

    async def batch_cancel(self, productType, orderIdList=None, symbol=None, marginCoin=None):
        """
        Batch cancel orders.
        Order cancelling interface, can be used to cancel by product type and trading pair.

        Args:
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            orderIdList (list[dict], optional): Order ID list. Maximum length: 50. Each dictionary should contain either `orderId` (str) or `clientOid` (str).
            symbol (str, optional): Trading pair, e.g. ETHUSDT. Required when `orderIdList` is set.
            marginCoin (str, optional): Margin coin (must be capitalized).

        Returns:
            dict: Bitget API JSON response containing success and failure lists of cancelled orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/order/batch-cancel-orders" # Corrected endpoint based on markdown
        body = {
            "productType": productType
        }
        if orderIdList:
            body["orderIdList"] = orderIdList
        if symbol:
            body["symbol"] = symbol
        if marginCoin:
            body["marginCoin"] = marginCoin
        return await self.client._send_request("POST", request_path, body=body)

    async def batch_order(self, symbol, productType, marginCoin, marginMode, orderList):
        """
        Place multiple new futures contract orders in a batch.
        Supports TP/SL feature. If the current underlying asset does not exist in the position, it is intended to preset the TP/SL. If the current underlying exists in the position, it is intended to modify the TP/SL.
        Ignore the `tradeSide` parameter when position mode is in `one-way-mode`.

        Args:
            symbol (str): Trading pair.
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            marginCoin (str): Margin coin (must be capitalized).
            marginMode (str): Position mode: `isolated` (isolated margin) or `crossed` (crossed margin).
            orderList (list[dict]): List of order details. Maximum length: 50. Each dictionary should contain:
                - size (str): Amount.
                - price (str, optional): Price of the order. Required if the order type is `limit`.
                - side (str): Order direction: `buy` or `sell`.
                - tradeSide (str, optional): Direction. Only required in hedge-mode.
                - orderType (str): Order type: `limit` or `market`.
                - force (str, optional): Order expiration date. Required if the orderType is `limit`, default value is `gtc`.
                - clientOid (str, optional): Custom order ID.
                - reduceOnly (str, optional): Whether or not to just reduce the position: `YES`, `NO`. Default: `NO`. Applicable only in **one-way-position** mode.
                - presetStopSurplusPrice (str, optional): Take-profit value. No take-profit is set if the field is empty.
                - presetStopLossPrice (str, optional): Stop-loss value. No stop-loss is set if the field is empty.
                - stpMode (str, optional): STP Mode (Self Trade Prevention): `none`, `cancel_taker`, `cancel_maker`, `cancel_both`.

        Returns:
            dict: Bitget API JSON response containing success and failure lists of placed orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/order/batch-place-order"
        body = {
            "symbol": symbol,
            "productType": productType,
            "marginCoin": marginCoin,
            "marginMode": marginMode,
            "orderList": orderList
        }
        return await self.client._send_request("POST", request_path, body=body)

    async def cancel_all_orders(self, productType, marginCoin=None, requestTime=None, receiveWindow=None):
        """
        Cancel all orders.

        Args:
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            marginCoin (str, optional): Margin coin (must be capitalized).
            requestTime (str, optional): Request time, Unix millisecond timestamp.
            receiveWindow (str, optional): Valid window period, Unix millisecond timestamp.

        Returns:
            dict: Bitget API JSON response containing success and failure lists of cancelled orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/order/cancel-all-orders"
        body = {"productType": productType}
        if marginCoin:
            body["marginCoin"] = marginCoin
        if requestTime:
            body["requestTime"] = requestTime
        if receiveWindow:
            body["receiveWindow"] = receiveWindow
        return await self.client._send_request("POST", request_path, body=body)

    async def cancel_order(self, symbol, productType, orderId=None, clientOid=None, marginCoin=None):
        """
        Cancel a pending order.

        Args:
            symbol (str): Trading pair.
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            orderId (str, optional): Order ID. Either `orderId` or `clientOid` is required. If both are present, `orderId` prevails.
            clientOid (str, optional): Customize order ID. Either `orderId` or `clientOid` is required. If both are present, `orderId` prevails.
            marginCoin (str, optional): Margin coin (must be capitalized).

        Returns:
            dict: Bitget API JSON response containing order ID and client order ID.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/order/cancel-order"
        body = {
            "symbol": symbol,
            "productType": productType
        }
        if orderId:
            body["orderId"] = orderId
        if clientOid:
            body["clientOid"] = clientOid
        if marginCoin:
            body["marginCoin"] = marginCoin
        return await self.client._send_request("POST", request_path, body=body)

    async def cancel_trigger_order(self, productType, orderIdList=None, symbol=None, marginCoin=None, planType=None):
        """
        Cancel trigger order.
        Interface for cancelling trigger orders, can be used to cancel by `productType`, `symbol` and/or trigger ID list.
        All orders that fall under that `productType` and `symbol` will be cancelled.

        Args:
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            orderIdList (list[dict], optional): Trigger order ID list. If it is passed, `symbol` must not be null and must be aligned with `symbol`/`productType`/`planType`. Each dictionary should contain either `orderId` (str) or `clientOid` (str).
            symbol (str, optional): Trading pair, e.g. ETHUSDT.
            marginCoin (str, optional): Margin coin (must be capitalized).
            planType (str, optional): Trigger order type: `normal_plan` (plan order, default), `profit_plan` (batch profit order), `loss_plan` (batch loss order), `pos_profit` (position profit order), `pos_loss` (position loss order), `moving_plan` (trailing order).

        Returns:
            dict: Bitget API JSON response containing success and failure lists of cancelled orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/order/cancel-plan-order"
        body = {"productType": productType}
        if orderIdList:
            body["orderIdList"] = orderIdList
        if symbol:
            body["symbol"] = symbol
        if marginCoin:
            body["marginCoin"] = marginCoin
        if planType:
            body["planType"] = planType
        return await self.client._send_request("POST", request_path, body=body)

    async def change_leverage(self, symbol, productType, marginCoin, leverage=None, longLeverage=None, shortLeverage=None, holdSide=None):
        """
        Adjust the leverage on the given symbol and productType.

        Args:
            symbol (str): Trading pair.
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            marginCoin (str): Margin coin (must be capitalized).
            leverage (str, optional): Leverage ratio. Applicable to cross-margin mode and one-way position scenarios in isolated margin mode.
            longLeverage (str, optional): Long position leverage. Only applicable to scenarios where different leverage ratios are set for different directions under hedge-mode in isolated margin mode.
            shortLeverage (str, optional): Short position leverage. Only applicable to scenarios where different leverage ratios are set for different directions under hedge-mode in isolated margin mode.
            holdSide (str, optional): Position direction: `long` or `short`. Required for hedge-mode in isolated margin mode when setting different leverages for long/short.

        Returns:
            dict: Bitget API JSON response containing leverage details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/account/set-leverage"
        body = {
            "symbol": symbol,
            "productType": productType,
            "marginCoin": marginCoin
        }
        if leverage:
            body["leverage"] = leverage
        if longLeverage:
            body["longLeverage"] = longLeverage
        if shortLeverage:
            body["shortLeverage"] = shortLeverage
        if holdSide:
            body["holdSide"] = holdSide
        return await self.client._send_request("POST", request_path, body=body)

    async def change_margin_mode(self, symbol, productType, marginCoin, marginMode):
        """
        Change margin mode.
        This interface cannot be used when the users have an open position or an order.

        Args:
            symbol (str): Trading pair. e.g. BTCUSDT.
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            marginCoin (str): Margin coin (must be capitalized).
            marginMode (str): Margin mode: `isolated` (isolated margin mode) or `crossed` (crossed margin mode).

        Returns:
            dict: Bitget API JSON response containing margin mode details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/account/set-margin-mode"
        body = {
            "symbol": symbol,
            "productType": productType,
            "marginCoin": marginCoin,
            "marginMode": marginMode
        }
        return await self.client._send_request("POST", request_path, body=body)

    async def change_position_mode(self, productType, posMode):
        """
        Adjust the position mode between 'one way mode' and 'hedge mode'.
        Note: The position mode can't be adjusted when there is an open position order under the product type.
        Changes the user's position mode for all symbol futures: hedging mode or one-way mode.
        When users hold positions or orders on any side of any trading pair in the specific product type, the request may fail.

        Args:
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            posMode (str): Position mode: `one_way_mode` (one-way mode) or `hedge_mode` (hedge mode).

        Returns:
            dict: Bitget API JSON response containing the position mode.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/account/set-position-mode"
        body = {
            "productType": productType,
            "posMode": posMode
        }
        return await self.client._send_request("POST", request_path, body=body)

    async def change_the_product_line_leverage(self, productType, leverage):
        """
        Adjust the leverage on the given productType.

        Args:
            productType (str): Product type: `USDT-FUTURES` (USDT professional futures), `COIN-FUTURES` (Mixed futures), `USDC-FUTURES` (USDC professional futures).
            leverage (str): Leverage (Only effective for symbols that have opened positions).

        Returns:
            dict: Bitget API JSON response indicating success or failure.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/account/set-all-leverage"
        body = {
            "productType": productType,
            "leverage": leverage
        }
        return await self.client._send_request("POST", request_path, body=body)

    async def flash_close_position(self, productType, symbol=None, holdSide=None):
        """
        Close position at market price.

        Args:
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            symbol (str, optional): Trading pair.
            holdSide (str, optional): Position direction.
                1. In one-way position mode (buy or sell): This field should be left blank. Will be ignored if filled in.
                2. In hedge-mode position (open or close): All positions will be closed if the field is left blank; Positions of the specified direction will be closed if the field is filled in.
                `long`: Long position; `short`: Short position.

        Returns:
            dict: Bitget API JSON response containing success and failure lists of closed orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/order/close-positions" # Corrected endpoint based on markdown
        body = {
            "productType": productType
        }
        if symbol:
            body["symbol"] = symbol
        if holdSide:
            body["holdSide"] = holdSide
        return await self.client._send_request("POST", request_path, body=body)

    async def get_account_bills(self, productType, marginCoin=None, startTime=None, endTime=None, bizType=None, bizSubType=None, limit=None, idLessThan=None):
        """
        Get Account bills (It only supports to get the data within 90days. The older data can be downloaded from web).

        Args:
            productType (str): Product type, e.g. "USDT-FUTURES" (USDT-M Futures), "COIN-FUTURES" (Coin-M Futures), "USDC-FUTURES" (USDC-M Futures).
            coin (str, optional): Currency. It's valid only when the `businessType` is "trans_from_exchange" or "trans_to_exchange".
            businessType (str, optional): Business type.
            onlyFunding (str, optional): The following four types of non-financial businessType will be excluded.,default：no， `yes`：excluded  `no`: included;  The following four businessType ：`append_margin`,`adjust_down_lever_append_margin`, `reduce_margin`, `auto_append_margin`.
            idLessThan (str, optional): Requests the content on the page before this ID (older data), the value input should be the endId of the corresponding interface.
            startTime (str, optional): Start time, ms. The interval between the `startTime` and the `endTime` should be <= 30 days.
            endTime (str, optional): End time, ms. The interval between the `startTime` and the `endTime` should be <= 30 days.
            limit (str, optional): Page size, max 100, default 20.

        Returns:
            dict: Bitget API JSON response containing account bills.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/account/account-bill"
        params = {"productType": productType}
        if marginCoin:
            params["marginCoin"] = marginCoin
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if bizType:
            params["bizType"] = bizType
        if bizSubType:
            params["bizSubType"] = bizSubType
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_account_list(self, productType):
        """
        Query all account information under a certain product type.

        Args:
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).

        Returns:
            dict: Bitget API JSON response containing account list.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/account/accounts"
        params = {"productType": productType}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_single_account(self, symbol, productType, marginCoin):
        """
        Get account details with the given `marginCoin` and `productType`.

        Args:
            symbol (str): Trading pair.
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            marginCoin (str): Margin coin.

        Returns:
            dict: Bitget API JSON response containing single account details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/account/account"
        params = {"symbol": symbol, "productType": productType, "marginCoin": marginCoin}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_subaccount_assets(self, productType):
        """
        Query the contract asset information of all sub-accounts.
        ND Brokers are not allowed to call this endpoint.

        Args:
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).

        Returns:
            dict: Bitget API JSON response containing subaccount assets.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/account/sub-account-assets"
        params = {"productType": productType}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_usdt_m_futures_interest_history(self, productType, coin=None, idLessThan=None, startTime=None, endTime=None, limit=None):
        """
        Get USDT-M futures interest history.

        Args:
            productType (str): Product type: `USDT-FUTURES` (USDT professional futures).
            coin (str, optional): Coin.
            idLessThan (str, optional): Requests the content on the page before this ID (older data), the value input should be the endId of the corresponding interface.
            startTime (str, optional): Start timestamp, Unix timestamp in milliseconds format.
            endTime (str, optional): End timestamp, Unix timestamp in milliseconds format.
            limit (str, optional): Number of queries: Default: 20, maximum: 100.

        Returns:
            dict: Bitget API JSON response containing USDT-M futures interest history.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/account/interest-history"
        params = {"productType": productType}
        if coin:
            params["coin"] = coin
        if idLessThan:
            params["idLessThan"] = idLessThan
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def my_estimated_open_count(self, symbol, productType, marginCoin, openAmount, openPrice, leverage=None):
        """
        Get estimated open count per UID.

        Args:
            symbol (str): Trading pair, e.g. ETHUSDT.
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            marginCoin (str): Margin coin.
            openAmount (str): Margin amount.
            openPrice (str): Price of the order.
            leverage (str, optional): Leverage, default 20.

        Returns:
            dict: Bitget API JSON response containing estimated open size.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/account/open-count"
        params = {
            "symbol": symbol,
            "productType": productType,
            "marginCoin": marginCoin,
            "openAmount": openAmount,
            "openPrice": openPrice
        }
        if leverage:
            params["leverage"] = leverage
        return await self.client._send_request("GET", request_path, params=params)

    async def set_isolated_position_auto_margin(self, symbol, autoMargin, marginCoin, holdSide):
        """
        Adjust isolated position auto margin.

        Args:
            symbol (str): Trading pair.
            autoMargin (str): Auto margin flag: `on` (auto margin on) or `off` (auto margin off).
            marginCoin (str): Margin coin (must be capitalized).
            holdSide (str): Position direction (no need in cross margin mode): `long` (long position) or `short` (short position).

        Returns:
            dict: Bitget API JSON response indicating success.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/account/set-auto-margin"
        body = {
            "symbol": symbol,
            "autoMargin": autoMargin,
            "marginCoin": marginCoin,
            "holdSide": holdSide
        }
        return await self.client._send_request("POST", request_path, body=body)

    async def set_usdt_m_futures_asset_mode(self, productType, assetMode):
        """
        Set USDT-M Futures Asset Mode.

        Args:
            productType (str): Product type: `USDT-FUTURES` (USDT professional futures).
            assetMode (str): Asset mode: `single` (Single asset mode) or `union` (Multi-assets mode).

        Returns:
            dict: Bitget API JSON response indicating success.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/account/set-asset-mode"
        body = {
            "productType": productType,
            "assetMode": assetMode
        }
        return await self.client._send_request("POST", request_path, body=body)

    async def simultaneous_stop_profit_and_stop_loss_plan_orders(self, marginCoin, productType, symbol, holdSide, stopSurplusTriggerPrice=None, stopSurplusSize=None, stopSurplusTriggerType=None, stopSurplusExecutePrice=None, stopLossTriggerPrice=None, stopLossSize=None, stopLossTriggerType=None, stopLossExecutePrice=None, stpMode=None, stopSurplusClientOid=None, stopLossClientOid=None):
        """
        Place a stop-profit and stop-loss plan order.

        Args:
            marginCoin (str): Margin currency.
            productType (str): Product type: `usdt-futures` (USDT professional futures), `coin-futures` (Mixed futures), `usdc-futures` (USDC professional futures).
            symbol (str): Trading pair, e.g. ETHUSDT.
            holdSide (str): Two-way position: (`long`: long position, `short`: short position); one-way position: (`buy`: long position, `sell`: short position).
            stopSurplusTriggerPrice (str, optional): Take Profit Trigger price.
            stopSurplusSize (str, optional): Order quantity (base coin). If filled, it's `profit_plan`; if not filled, it's `pos_profit`.
            stopSurplusTriggerType (str, optional): Take Profit Trigger type: `fill_price` (market price) or `mark_price` (mark price).
            stopSurplusExecutePrice (str, optional): Take Profit Execution price. If it is 0 or not filled in, it means market price execution. If it is greater than 0, it means limit price execution.
            stopLossTriggerPrice (str, optional): Stop Loss Trigger price.
            stopLossSize (str, optional): Order quantity (base coin). If filled, it's `loss_plan`; if not filled, it's `pos_loss`.
            stopLossTriggerType (str, optional): Stop Loss Trigger type: `fill_price` (market price) or `mark_price` (mark price).
            stopLossExecutePrice (str, optional): Stop Loss Execution price. If it is 0 or not filled in, it means market price execution. If it is greater than 0, it means limit price execution.
            stpMode (str, optional): STP Mode (Self Trade Prevention): `none` (not setting STP, default value), `cancel_taker` (cancel taker order), `cancel_maker` (cancel maker order), `cancel_both` (cancel both of taker and maker orders).
            stopSurplusClientOid (str, optional): Take-profit order custom order ID.
            stopLossClientOid (str, optional): Stop-loss order custom order ID.

        Returns:
            dict: Bitget API JSON response containing order details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/order/place-pos-tpsl"
        body = {
            "marginCoin": marginCoin,
            "productType": productType,
            "symbol": symbol,
            "holdSide": holdSide
        }
        if stopSurplusTriggerPrice:
            body["stopSurplusTriggerPrice"] = stopSurplusTriggerPrice
        if stopSurplusSize:
            body["stopSurplusSize"] = stopSurplusSize
        if stopSurplusTriggerType:
            body["stopSurplusTriggerType"] = stopSurplusTriggerType
        if stopSurplusExecutePrice:
            body["stopSurplusExecutePrice"] = stopSurplusExecutePrice
        if stopLossTriggerPrice:
            body["stopLossTriggerPrice"] = stopLossTriggerPrice
        if stopLossSize:
            body["stopLossSize"] = stopLossSize
        if stopLossTriggerType:
            body["stopLossTriggerType"] = stopLossTriggerType
        if stopLossExecutePrice:
            body["stopLossExecutePrice"] = stopLossExecutePrice
        if stpMode:
            body["stpMode"] = stpMode
        if stopSurplusClientOid:
            body["stopSurplusClientOid"] = stopSurplusClientOid
        if stopLossClientOid:
            body["stopLossClientOid"] = stopLossClientOid
        return await self.client._send_request("POST", request_path, body=body)

    async def stop_profit_and_stop_loss_plan_orders(self, marginCoin, productType, symbol, planType, triggerPrice, holdSide, size, triggerType=None, executePrice=None, rangeRate=None, clientOid=None, stpMode=None):
        """
        Place a stop-profit and stop-loss plan order.

        Args:
            marginCoin (str): Margin currency (Capitalized).
            productType (str): Product type: `usdt-futures` (USDT professional futures), `coin-futures` (Mixed futures), `usdc-futures` (USDC professional futures).
            symbol (str): Trading pair, e.g. ETHUSDT.
            planType (str): Take profit and stop loss type: `profit_plan` (take profit plan), `loss_plan` (stop loss plan), `moving_plan` (trailing stop), `pos_profit` (position take profit), `pos_loss` (position stop loss).
            triggerPrice (str): Trigger price.
            holdSide (str): Two-way position: (`long`: long position, `short`: short position); one-way position: (`buy`: long position, `sell`: short position).
            size (str): Order quantity (base coin). Required when `planType` is `profit_plan`, `loss_plan` or `moving_plan`, and should be greater than 0; NOT required when `planType` is `pos_profit` or `pos_loss`.
            triggerType (str, optional): Trigger type: `fill_price` (market price) or `mark_price` (mark price).
            executePrice (str, optional): Execution price. If it is 0 or not filled in, it means market price execution. If it is greater than 0, it means limit price execution. Do not fill in this parameters when `planType` is `moving_plan`, it only executes in market price.
            rangeRate (str, optional): Callback range. Required only in `planType` is `moving_plan`.
            clientOid (str, optional): Customize order ID.
            stpMode (str, optional): STP Mode (Self Trade Prevention): `none` (not setting STP, default value), `cancel_taker` (cancel taker order), `cancel_maker` (cancel maker order), `cancel_both` (cancel both of taker and maker orders).

        Returns:
            dict: Bitget API JSON response containing order details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/order/place-tpsl-order"
        body = {
            "marginCoin": marginCoin,
            "productType": productType,
            "symbol": symbol,
            "planType": planType,
            "triggerPrice": triggerPrice,
            "holdSide": holdSide,
            "size": size
        }
        if triggerType:
            body["triggerType"] = triggerType
        if executePrice:
            body["executePrice"] = executePrice
        if rangeRate:
            body["rangeRate"] = rangeRate
        if clientOid:
            body["clientOid"] = clientOid
        if stpMode:
            body["stpMode"] = stpMode
        return await self.client._send_request("POST", request_path, body=body)

    async def trigger_sub_order(self, planType, planOrderId, productType):
        """
        Get trigger executed futures orders.

        Args:
            planType (str): Trigger order type: `normal_plan` (average trigger order) or `track_plan` (trailing stop order).
            planOrderId (str): Trigger order ID.
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).

        Returns:
            dict: Bitget API JSON response containing trigger executed futures orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/order/plan-sub-order"
        params = {"planType": planType, "planOrderId": planOrderId, "productType": productType}
        return await self.client._send_request("GET", request_path, params=params)

    async def vip_fee_rate(self):
        """
        Get VIP fee rate.

        Returns:
            dict: Bitget API JSON response containing VIP fee rate details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/market/vip-fee-rate"
        return await self.client._send_request("GET", request_path, params={})

    async def place_order(self, symbol, productType, marginMode, marginCoin, size, side, orderType, price=None, tradeSide=None, force=None, clientOid=None, reduceOnly=None, presetStopSurplusPrice=None, presetStopLossPrice=None, presetStopSurplusExecutePrice=None, presetStopLossExecutePrice=None, stpMode=None):
        """
        Place a new futures contract order.
        Ignore the `tradeSide` parameter when position mode is in `one-way-mode`.
        In “hedge-mode”, when there is limit close order occupying the position, if the size of next market close order and limit close orders exceeds the position size, it will return an “insufficient position error” instead of cancelling the current limit order and executing the market order.
        `hedge position mode`: `Open long`: "side"=`buy`, "tradeSide"=`open`; `Close long`: "side"=`buy`, "tradeSide"=`close`; `Open short`: "side"=`sell`, "tradeSide"=`open`; `Close short`: "side"=`sell`, "tradeSide"=`close`; `one-way position mode`: "side"=`buy` and `sell`, `tradeSide`: ignore.
        In `one-way-mode` position mode, if the total size of the new reduce-only order and the existing reduce-only orders exceeds the position size, the system will cancel the existing reduce-only orders sequentially based on their creation order until the total size of the new and existing reduce-only orders is less than or equal to the position size. Additionally, the response for the latest reduce-only order request will not include an `orderId`. You can use the `clientOid` set in the request to query order details or retrieve the orderId from the current pending orders.
        When in `hedge Mode`, if a limit close order is occupying a position, and a subsequent market close order (its quantity plus the limit order's quantity) exceeds the total position size, it will not report an insufficient position error. It also won't cancel the limit order that's occupying the position. Instead, the quantity of the limit close order will be preserved, and the market order will close only the quantity remaining after subtracting the limit order's quantity from the total position size. For example: If you have a position of 100, a limit order occupies 70, and you then place a market close order for 50, it will not report an insufficient position error, nor will it cancel the occupying limit order to execute the market order. Instead, it will directly close a quantity of 30.
        When in `hedge Mode`,if the existing quantity is equal to the limit close position order of the held position, a newly added close position order will automatically cancel the limit order that has occupied the position.
        For elite traders, please strictly adhere to the list of trading pairs specified in the [Available trading pairs and parameters for elite traders](https://www.bitget.com/zh-CN/support/articles/12560603808895) when placing orders using the Copy Trading API Key. Trading pairs outside the announced list are not available for copy trading.

        Args:
            symbol (str): Trading pair, e.g. ETHUSDT.
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            marginMode (str): Position mode: `isolated` (isolated margin) or `crossed` (crossed margin).
            marginCoin (str): Margin coin (capitalized).
            size (str): Amount (base coin). To get the decimal places of size: [Get Contract Config](https://www.bitget.com/api-doc/contract/market/Get-All-Symbols-Contracts).
            side (str): Trade side: `buy` (Buy/Long position direction) or `sell` (Sell/Short position direction).
            orderType (str): Order type: `limit` or `market`.
            price (str, optional): Price of the order. Required if the `orderType` is `limit`. To get the decimal places of size: [Get Contract Config](https://www.bitget.com/api-doc/contract/market/Get-All-Symbols-Contracts).
            tradeSide (str, optional): Trade type. Only required in hedge-mode: `open` (Open position) or `close` (Close position).
            force (str, optional): Order expiration date. Required if the `orderType` is `limit`: `ioc` (Immediate or cancel), `fok` (Fill or kill), `gtc` (Good till canceled, default value), `post_only` (Post only).
            clientOid (str, optional): Customize order ID.
            reduceOnly (str, optional): Whether or not to just reduce the position: `YES`, `NO`. Default: `NO`. Applicable only in **one-way-position** mode.
            presetStopSurplusPrice (str, optional): Take-profit value. No take-profit is set if the field is empty.
            presetStopLossPrice (str, optional): Stop-loss value. No stop-loss is set if the field is empty.
            presetStopSurplusExecutePrice (str, optional): Preset stop - profit execution price.
            presetStopLossExecutePrice (str, optional): Preset stop-loss execution price.
            stpMode (str, optional): STP Mode (Self Trade Prevention): `none` (not setting STP, default value), `cancel_taker` (cancel taker order), `cancel_maker` (cancel maker order), `cancel_both` (cancel both of taker and maker orders).

        Returns:
            dict: Bitget API JSON response containing order details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/order/place-order"
        body = {
            "symbol": symbol,
            "productType": productType,
            "marginMode": marginMode,
            "marginCoin": marginCoin,
            "size": size,
            "side": side,
            "orderType": orderType
        }
        if price:
            body["price"] = price
        if tradeSide:
            body["tradeSide"] = tradeSide
        if force:
            body["force"] = force
        if clientOid:
            body["clientOid"] = clientOid
        if reduceOnly:
            body["reduceOnly"] = reduceOnly
        if presetStopSurplusPrice:
            body["presetStopSurplusPrice"] = presetStopSurplusPrice
        if presetStopLossPrice:
            body["presetStopLossPrice"] = presetStopLossPrice
        if presetStopSurplusExecutePrice:
            body["presetStopSurplusExecutePrice"] = presetStopSurplusExecutePrice
        if presetStopLossExecutePrice:
            body["presetStopLossExecutePrice"] = presetStopLossExecutePrice
        if stpMode:
            body["stpMode"] = stpMode
        return await self.client._send_request("POST", request_path, body=body)

    async def place_trigger_order(self, planType, symbol, productType, marginMode, marginCoin, size, triggerPrice, triggerType, side, orderType, price=None, callbackRatio=None, tradeSide=None, clientOid=None, reduceOnly=None, stopSurplusTriggerPrice=None, stopSurplusExecutePrice=None, stopSurplusTriggerType=None, stopLossTriggerPrice=None, stopLossExecutePrice=None, stopLossTriggerType=None, stpMode=None):
        """
        Place an trigger or trailing stop order with TP/SL setting feature.

        Args:
            planType (str): Trigger order type: `normal_plan` (Trigger order) or `track_plan` (Trailing stop order).
            symbol (str): Trading pair, e.g. ETHUSDT.
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            marginMode (str): Position mode: `isolated` (isolated margin) or `crossed` (cross margin).
            marginCoin (str): Margin coin.
            size (str): Amount (base coin).
            triggerPrice (str): Trigger price.
            triggerType (str): Trigger type: `mark_price` (Mark price) or `fill_price` (Lastest price). Required when placing a trigger order or a trailing stop order.
            side (str): Order direction: `buy` or `sell`.
            orderType (str): Order type: `limit` or `market`. For `track_plan`, it is required and must be `market`.
            price (str, optional): Price. For `track_plan`, it must be empty. For `normal_plan`, it is required when `orderType` is `limit`; It must be empty when `orderType` is `market`.
            callbackRatio (str, optional): Callback rate (applies to trailing stop orders only). Required for trailing stop orders and the rate cannot be greater than 10.
            tradeSide (str, optional): Direction: `open` (Open) or `close` (Close). Only required in hedge position mode.
            clientOid (str, optional): Customize order ID.
            reduceOnly (str, optional): Whether or not to just reduce the position: `yes` or `no` (default). Only applicable in buy/sell (one-way position) mode.
            stopSurplusTriggerPrice (str, optional): Take-profit trigger price/Take-profit ratio. For `normal_plan`, it represents the take-profit trigger price. For `track_plan`, it represents the take-profit percentage, with a maximum of 999.99 and a minimum of 0.01. If left empty or set to 0, no take-profit will be set by default.
            stopSurplusExecutePrice (str, optional): Take-profit execute price. For `track_plan`, it must be empty. For a `normal_plan` that has `stopSurplusTriggerPrice` parameter set, if it is empty or set to 0, it represents a market order execution; if not empty and greater than 0, it represents a limit order execution.
            stopSurplusTriggerType (str, optional): Take-profit trigger type: `fill_price` (Lastest price) or `mark_price` (Mark price). For orders that have `stopSurplusTriggerPrice` parameter set, it is required. For `track_plan`, it only accepts `fill_price`.
            stopLossTriggerPrice (str, optional): Stop-loss trigger price/Stop-loss ratio. For `normal_plan`, it represents the stop-loss trigger price. For `track_plan`, it represents the stop-loss percentage, with a maximum of 999.99 and a minimum of 0.01. If left empty or set to 0, no stop-loss will be set by default.
            stopLossExecutePrice (str, optional): Stop-loss execute price. For `track_plan`, it must be empty. For a `normal_plan` that has `stopLossTriggerPrice` parameter set, if it is empty or set to 0, it represents a market order execution; if not empty and greater than 0, it represents a limit order execution.
            stopLossTriggerType (str, optional): Stop-loss trigger type: `fill_price` (Lastest price) or `mark_price` (Mark price). For orders that have `stopLossTriggerPrice` parameter set, it is required. For `track_plan`, it only accepts `fill_price`.
            stpMode (str, optional): STP Mode: `none` (not setting STP, default), `cancel_taker` (cancel taker order), `cancel_maker` (cancel maker order), `cancel_both` (cancel both of taker and maker orders).

        Returns:
            dict: Bitget API JSON response containing order details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/order/place-plan-order"
        body = {
            "planType": planType,
            "symbol": symbol,
            "productType": productType,
            "marginMode": marginMode,
            "marginCoin": marginCoin,
            "size": size,
            "triggerPrice": triggerPrice,
            "triggerType": triggerType,
            "side": side,
            "orderType": orderType
        }
        if price:
            body["price"] = price
        if callbackRatio:
            body["callbackRatio"] = callbackRatio
        if tradeSide:
            body["tradeSide"] = tradeSide
        if clientOid:
            body["clientOid"] = clientOid
        if reduceOnly:
            body["reduceOnly"] = reduceOnly
        if stopSurplusTriggerPrice:
            body["stopSurplusTriggerPrice"] = stopSurplusTriggerPrice
        if stopSurplusExecutePrice:
            body["stopSurplusExecutePrice"] = stopSurplusExecutePrice
        if stopSurplusTriggerType:
            body["stopSurplusTriggerType"] = stopSurplusTriggerType
        if stopLossTriggerPrice:
            body["stopLossTriggerPrice"] = stopLossTriggerPrice
        if stopLossExecutePrice:
            body["stopLossExecutePrice"] = stopLossExecutePrice
        if stopLossTriggerType:
            body["stopLossTriggerType"] = stopLossTriggerType
        if stpMode:
            body["stpMode"] = stpMode
        return await self.client._send_request("POST", request_path, body=body)

    async def reversal(self, symbol, marginCoin, productType, side, size=None, tradeSide=None, clientOid=None):
        """
        Reversal.
        `side` and `tradeSide`:
        - In `one-way-mode`, do NOT add the `tradeSide` parameter in request.
        - In `hedge-mode`, `tradeSide` is required.
            - Reversal the current long position and open a short position: `side`=`buy`, `tradeSide`=`open`.
            - Reversal the current short position and open a long position: `side`=`sell`, `tradeSide`=`open`.
        `size`: represents the reversal size.
        - In `one-way-mode`, the whole position will be reversed if no `size` was set in the request.
        - In `hedge-mode`:
            - If the `size` set is less than the current position size, the `size` of position will be closed and the same size reversal position will be opened.
            - If the `size` set is equal to or more than the current position size, the whole position will be reversed.

        Args:
            symbol (str): Trading pair, e.g. ETHUSDT.
            marginCoin (str): Margin coin, e.g: USDT.
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            side (str): Order direction: `buy` or `sell`.
            size (str, optional): Amount.
            tradeSide (str, optional): Direction. Required in open and close (hedge mode) position. For one-way positions, this field will be ignored.
            clientOid (str, optional): Customize order ID.

        Returns:
            dict: Bitget API JSON response containing order details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/order/click-backhand"
        body = {
            "symbol": symbol,
            "marginCoin": marginCoin,
            "productType": productType,
            "side": side
        }
        if size:
            body["size"] = size
        if tradeSide:
            body["tradeSide"] = tradeSide
        if clientOid:
            body["clientOid"] = clientOid
        return await self.client._send_request("POST", request_path, body=body)

    async def get_ticker(self, symbol, productType):
        """
        Get ticker data of the given `productType` and `symbol`.

        Args:
            symbol (str): Trading pair.
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).

        Returns:
            dict: Bitget API JSON response containing ticker data.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/market/ticker"
        params = {"symbol": symbol, "productType": productType}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_all_positions(self, productType, marginCoin=None):
        """
        Returns information about all current positions with the given `productType`.

        Args:
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            marginCoin (str, optional): Margin coin (capitalized), e.g. USDT.

        Returns:
            dict: Bitget API JSON response containing all positions.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/position/all-position"
        params = {"productType": productType}
        if marginCoin:
            params["marginCoin"] = marginCoin
        return await self.client._send_request("GET", request_path, params=params)

    async def get_all_tickers(self, productType):
        """
        Get all ticker data of the given `productType`.

        Args:
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).

        Returns:
            dict: Bitget API JSON response containing all ticker data.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/market/tickers"
        params = {"productType": productType}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_candlestick_data(self, symbol, productType, granularity, startTime=None, endTime=None, kLineType=None, limit=None):
        """
        Get candlestick data.
        By default, 100 records are returned. If there is no data, an empty array is returned. The queryable data history varies depending on the k-line granularity.
        The rules are as follows:
        1m, 3m, and 5m can be checked for up to one month;
        15m can be checked for up to 52 days;
        30m can be searched for up to 62 days;
        1H can be checked for up to 83 days;
        2H can be checked for up to 120 days;
        4H can be checked for up to 240 days;
        6H can be checked for up to 360 days.

        Args:
            symbol (str): Trading pair.
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            granularity (str): K-line particle size: `1m`, `3m`, `5m`, `15m`, `30m`, `1H`, `4H`, `6H`, `12H`, `1D`, `3D`, `1W`, `1M`, `6Hutc`, `12Hutc`, `1Dutc`, `3Dutc`, `1Wutc`, `1Mutc`.
            startTime (str, optional): The start time is to query the k-lines after this time. The millisecond format of the Unix timestamp.
            endTime (str, optional): The end time is to query the k-lines before this time. The millisecond format of the Unix timestamp.
            kLineType (str, optional): Candlestick chart types: `MARKET` (tick), `MARK` (mark), `INDEX` (index). `MARKET` by default.
            limit (str, optional): Default: 100, maximum: 1000.

        Returns:
            dict: Bitget API JSON response containing candlestick data.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/market/candles"
        params = {
            "symbol": symbol,
            "productType": productType,
            "granularity": granularity
        }
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if kLineType:
            params["kLineType"] = kLineType
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_contract_config(self, productType, symbol=None):
        """
        Get future contract details.

        Args:
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            symbol (str, optional): Trading pair, based on the symbolName, i.e. BTCUSDT.

        Returns:
            dict: Bitget API JSON response containing contract configuration details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/market/contracts"
        params = {"productType": productType}
        if symbol:
            params["symbol"] = symbol
        return await self.client._send_request("GET", request_path, params=params)

    async def get_contract_oi_limit(self, productType, symbol=None):
        """
        Get future contract OI Limit.

        Args:
            productType (str): Product type: `USDT-FUTURES` (USDT professional futures), `COIN-FUTURES` (Mixed futures), `USDC-FUTURES` (USDC professional futures).
            symbol (str, optional): Trading pair, based on the symbolName, i.e. BTCUSDT.

        Returns:
            dict: Bitget API JSON response containing contract OI limit details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/market/oi-limit"
        params = {"productType": productType}
        if symbol:
            params["symbol"] = symbol
        return await self.client._send_request("GET", request_path, params=params)

    async def get_current_funding_rate(self, productType, symbol=None):
        """
        Get the current funding rate of the contract.

        Args:
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            symbol (str, optional): Trading pair.

        Returns:
            dict: Bitget API JSON response containing current funding rate details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/market/current-fund-rate"
        params = {"productType": productType}
        if symbol:
            params["symbol"] = symbol
        return await self.client._send_request("GET", request_path, params=params)

    async def get_discount_rate(self):
        """
        Get Discount Rate.

        Returns:
            dict: Bitget API JSON response containing discount rate details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/market/discount-rate"
        return await self.client._send_request("GET", request_path, params={})

    async def get_historical_candlestick(self, symbol, productType, granularity, startTime=None, endTime=None, limit=None):
        """
        Query all historical K-line data and return a maximum of 200 pieces of data.

        Args:
            symbol (str): Trading pair.
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            granularity (str): K-line particle size: `1m`, `3m`, `5m`, `15m`, `30m`, `1H`, `4H`, `6H`, `12H`, `1D`, `3D`, `1W`, `1M`, `6Hutc`, `12Hutc`, `1Dutc`, `3Dutc`, `1Wutc`, `1Mutc`.
            startTime (str, optional): The start time is to query the k-lines after this time. The millisecond format of the Unix timestamp.
            endTime (str, optional): The end time is to query the k-lines before this time. The millisecond format of the Unix timestamp.
            limit (str, optional): Default: 100, maximum: 200.

        Returns:
            dict: Bitget API JSON response containing historical candlestick data.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/market/history-candles"
        params = {
            "symbol": symbol,
            "productType": productType,
            "granularity": granularity
        }
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_historical_funding_rates(self, symbol, productType, pageSize=None, pageNo=None):
        """
        Get the historical funding rate of the contract.

        Args:
            symbol (str): Trading pair.
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            pageSize (str, optional): Number of queries: Default: 20, maximum: 100.
            pageNo (str, optional): Page number.

        Returns:
            dict: Bitget API JSON response containing historical funding rates.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/market/history-fund-rate"
        params = {
            "symbol": symbol,
            "productType": productType
        }
        if pageSize:
            params["pageSize"] = pageSize
        if pageNo:
            params["pageNo"] = pageNo
        return await self.client._send_request("GET", request_path, params=params)

    async def get_historical_index_price_candlestick(self, symbol, productType, granularity, startTime=None, endTime=None, limit=None):
        """
        Query the historical K-line data of contract index price, and return a maximum of 200 pieces of data.

        Args:
            symbol (str): Trading pair.
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            granularity (str): K-line particle size: `1m`, `3m`, `5m`, `15m`, `30m`, `1H`, `4H`, `6H`, `12H`, `1D`, `3D`, `1W`, `1M`, `6Hutc`, `12Hutc`, `1Dutc`, `3Dutc`, `1Wutc`, `1Mutc`.
            startTime (str, optional): The start time is to query the k-lines after this time. The millisecond format of the Unix timestamp.
            endTime (str, optional): The end time is to query the k-lines before this time. The millisecond format of the Unix timestamp.
            limit (str, optional): Default: 100, maximum: 200.

        Returns:
            dict: Bitget API JSON response containing historical index price candlestick data.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/market/history-index-candles"
        params = {
            "symbol": symbol,
            "productType": productType,
            "granularity": granularity
        }
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_historical_mark_price_candlestick(self, symbol, productType, granularity, startTime=None, endTime=None, limit=None):
        """
        Get historical mark price candle data.

        Args:
            symbol (str): Trading pair.
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            granularity (str): K-line particle size: `1m`, `3m`, `5m`, `15m`, `30m`, `1H`, `4H`, `6H`, `12H`, `1D`, `3D`, `1W`, `1M`, `6Hutc`, `12Hutc`, `1Dutc`, `3Dutc`, `1Wutc`, `1Mutc`.
            startTime (str, optional): The start time is to query the k-lines after this time. The millisecond format of the Unix timestamp.
            endTime (str, optional): The end time is to query the k-lines before this time. The millisecond format of the Unix timestamp.
            limit (str, optional): Default: 100, maximum: 200.

        Returns:
            dict: Bitget API JSON response containing historical mark price candlestick data.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/market/history-mark-candles"
        params = {
            "symbol": symbol,
            "productType": productType,
            "granularity": granularity
        }
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_historical_transaction_details(self, productType, orderId=None, symbol=None, startTime=None, endTime=None, idLessThan=None, limit=None):
        """
        Get order fill history.

        Args:
            productType (str): Product type: `USDT-FUTURES` (USDT professional futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC professional futures). It does not support to query the data in demo trading.
            orderId (str, optional): Order ID. Either `orderId` or `clientOid` is required. If both are entered, `orderId` prevails.
            symbol (str, optional): Trading pair, e.g. ETHUSDT.
            startTime (str, optional): Start timestamp. Unix timestamp in milliseconds format. The maximum time span supported is a week. The default end time is a week if no value is set for the end time. (For Managed Sub-Account, the StartTime cannot be earlier than the binding time).
            endTime (str, optional): End timestamp. Unix timestamp in milliseconds format. The maximum time span supported is a week. The default start time is a week ago if no value is set for the start time.
            idLessThan (str, optional): Requests the content on the page before this ID (older data), the value input should be the endId of the corresponding interface.
            limit (str, optional): Number of queries: Maximum: 100, default: 100.

        Returns:
            dict: Bitget API JSON response containing order fill history.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/order/fill-history"
        params = {"productType": productType}
        if orderId:
            params["orderId"] = orderId
        if symbol:
            params["symbol"] = symbol
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if idLessThan:
            params["idLessThan"] = idLessThan
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_interest_exchange_rate(self):
        """
        Get Interest exchange rate.

        Returns:
            dict: Bitget API JSON response containing interest exchange rate details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/market/exchange-rate"
        return await self.client._send_request("GET", request_path, params={})

    async def get_interest_rate_history(self, coin):
        """
        Get Interest rate history.

        Args:
            coin (str): Coin asset.

        Returns:
            dict: Bitget API JSON response containing interest rate history.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/market/union-interest-rate-history"
        params = {"coin": coin}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_mark_index_market_prices(self, symbol, productType):
        """
        Get market/index/mark prices.

        Args:
            symbol (str): Trading pair.
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).

        Returns:
            dict: Bitget API JSON response containing mark/index/market prices.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/market/symbol-price"
        params = {"symbol": symbol, "productType": productType}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_merge_market_depth(self, symbol, productType, precision=None, limit=None):
        """
        Get merge depth data.

        Args:
            symbol (str): Trading pair.
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            precision (str, optional): Price accuracy, according to the selected accuracy as the step size to return the cumulative depth.
                Enumeration value: `scale0` (not merged, default), `scale1`, `scale2`, `scale3`.
                If a scale that does not exist for the currency pair is requested, it will be processed according to the maximum scale.
            limit (str, optional): Fixed gear enumeration value: `1`, `5`, `15`, `50`, `max`. The default gear is 100. Passing `max` returns the maximum gear of the trading pair.

        Returns:
            dict: Bitget API JSON response containing merge market depth data.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/market/merge-depth"
        params = {"symbol": symbol, "productType": productType}
        if precision:
            params["precision"] = precision
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_next_funding_time(self, symbol, productType):
        """
        Get the next settlement time of the contract and the settlement period of the contract.

        Args:
            symbol (str): Trading pair.
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).

        Returns:
            dict: Bitget API JSON response containing next funding time details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/market/funding-time"
        params = {"symbol": symbol, "productType": productType}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_open_interest(self, symbol, productType):
        """
        Get the total positions of a certain trading pair on the platform.

        Args:
            symbol (str): Trading pair.
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).

        Returns:
            dict: Bitget API JSON response containing open interest data.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/market/open-interest"
        params = {"symbol": symbol, "productType": productType}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_recent_transactions(self, symbol, productType, limit=None):
        """
        Get the record of last 100 transactions.

        Args:
            symbol (str): Trading pair.
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            limit (str, optional): Number of queries: Default: 100, maximum: 100.

        Returns:
            dict: Bitget API JSON response containing recent transactions.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/market/fills"
        params = {"symbol": symbol, "productType": productType}
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_history_order(self, productType, orderId=None, clientOid=None, symbol=None, idLessThan=None, orderSource=None, startTime=None, endTime=None, limit=None):
        """
        Get history order.
        It only supports to get the data within 90 days. The older data can be downloaded from web.

        Args:
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            orderId (str, optional): Order ID. If both `orderId` and `clientOid` are entered, `orderId` prevails.
            clientOid (str, optional): Customize order ID. If both `orderId` and `clientOid` are entered, `orderId` prevails.
            symbol (str, optional): Trading pair, e.g. ETHUSDT.
            idLessThan (str, optional): Requests the content on the page before this ID (older data), the value input should be the endId of the previous request response.
            orderSource (str, optional): Order sources: `normal`, `market`, `profit_market`, `loss_market`, `Trader_delegate`, `trader_profit`, `trader_loss`, `reverse`, `trader_reverse`, `profit_limit`, `loss_limit`, `liquidation`, `delivery_close_long`, `delivery_close_short`, `pos_profit_limit`, `pos_profit_market`, `pos_loss_limit`, `pos_loss_market`.
            startTime (str, optional): Start timestamp. Unix millisecond timestamp. (For Managed Sub-Account, the StartTime cannot be earlier than the binding time).
            endTime (str, optional): End timestamp. Unix millisecond timestamp.
            limit (str, optional): Number of queries: Maximum: 100, default: 100.

        Returns:
            dict: Bitget API JSON response containing history orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/order/orders-history"
        params = {"productType": productType}
        if orderId:
            params["orderId"] = orderId
        if clientOid:
            params["clientOid"] = clientOid
        if symbol:
            params["symbol"] = symbol
        if idLessThan:
            params["idLessThan"] = idLessThan
        if orderSource:
            params["orderSource"] = orderSource
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_history_trigger_order(self, planType, productType, orderId=None, clientOid=None, planStatus=None, symbol=None, idLessThan=None, startTime=None, endTime=None, limit=None):
        """
        Query one or all previous common orders and trigger orders.

        Args:
            planType (str): Order type: `normal_plan` (trigger order), `track_plan` (trailing stop order), `profit_loss` (take profit and stop loss orders, including the `profit_plan`, `loss_plan`, `moving_plan`, `pos_profit` and `pos_loss`).
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            orderId (str, optional): Order ID. Either `orderId` or `clientOid` is required. If both are entered, `orderId` prevails.
            clientOid (str, optional): Customize order ID. Either `orderId` or `clientOid` is required. If both are entered, `orderId` prevails.
            planStatus (str, optional): Trigger order status: `executed` (the order triggered), `fail_execute` (Failed to trigger), `cancelled` (Cancelled). If not specified, all states will be queried.
            symbol (str, optional): Trading pair, e.g. ETHUSDT.
            idLessThan (str, optional): Requests the content on the page before this ID (older data), the value input should be the endId of the corresponding interface.
            startTime (str, optional): Start timestamp. Unix timestamp in milliseconds format. The maximum time span supported is three months. The default end time is three months if no value is set for the end time. (For Managed Sub-Account, the StartTime cannot be earlier than the binding time).
            endTime (str, optional): End timestamp. Unix timestamp in milliseconds format. The maximum time span supported is three months. The default start time is three months ago if no value is set for the start time.
            limit (str, optional): Number of queries: Default: 100, maximum: 100.

        Returns:
            dict: Bitget API JSON response containing history trigger orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/order/orders-plan-history"
        params = {"planType": planType, "productType": productType}
        if orderId:
            params["orderId"] = orderId
        if clientOid:
            params["clientOid"] = clientOid
        if planStatus:
            params["planStatus"] = planStatus
        if symbol:
            params["symbol"] = symbol
        if idLessThan:
            params["idLessThan"] = idLessThan
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def modify_order(self, symbol, productType, newClientOid, orderId=None, clientOid=None, newSize=None, newPrice=None, newPresetStopSurplusPrice=None, newPresetStopLossPrice=None):
        """
        Modify a pending order, such as its TP/SL and/or price/size.
        Modifying size and price will cancel the old order; then create a **new order** asynchronously, modify the preset TPSL will not cancel the old order.
        Modifying size and price, please pass in both, not just one of them.
        Modify the order price, size and preset TPSL according to orderId or clientOId.
        It is only allowed to modify the new status limit order. If the size, price and TPSL all is set in the request, then the TPSL will not work.
        Modify the limit order price and size, please be sure to provide newClientOid, because the orderId of the new order cannot be returned synchronously, so you need to use newClientOid to help you query order information.
        Modifying the order size needs to meet the minimum order quantity.
        If you only modify the TPSL, please do not pass price and size. If you only pass one of TP or SL, the other one will be cancelled.

        Args:
            symbol (str): Trading pair, e.g. ETHUSDT.
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            newClientOid (str): New customized order ID after order modification.
            orderId (str, optional): Order ID. Either `orderId` or `clientOid` is required. If both are entered, `orderId` prevails.
            clientOid (str, optional): Customize order ID. Either `orderId` or `clientOid` is required. If both are entered, `orderId` prevails.
            newSize (str, optional): Amount of the modified transaction. The amount stays unchanged if the field if left blank.
            newPrice (str, optional): Modified price for placing new orders.
                1. When the existing order type is Limit, the original price will be maintained if the field is left empty.
                2. When the existing order type is Limit market, the field should not be set.
            newPresetStopSurplusPrice (str, optional): Modifying take-profit.
                1. If the original order has take-profit set and the field is empty, the original value will be kept.
                2. If the original order has take-profit set and the field is filled in with a value, TP will be updated; if the original order has take-profit set and the field is not set, a new take-profit value will be added. If there was a TP value and a 0 is filled in the filled, the existing TP will be deleted.
            newPresetStopLossPrice (str, optional): Modifying stop-loss.
                1. If the original order has stop-loss set and the field is empty, the original value will be kept.
                2. If the original order has stop-loss set and the field is filled in with a value, TP will be updated; if the original order has stop-loss set and the field is not set, a new stop-loss value will be added. If there was a SL value and a 0 is filled in the filled, the existing SL will be deleted.

        Returns:
            dict: Bitget API JSON response containing order ID and client order ID.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/order/modify-order"
        body = {
            "symbol": symbol,
            "productType": productType,
            "newClientOid": newClientOid
        }
        if orderId:
            body["orderId"] = orderId
        if clientOid:
            body["clientOid"] = clientOid
        if newSize:
            body["newSize"] = newSize
        if newPrice:
            body["newPrice"] = newPrice
        if newPresetStopSurplusPrice:
            body["newPresetStopSurplusPrice"] = newPresetStopSurplusPrice
        if newPresetStopLossPrice:
            body["newPresetStopLossPrice"] = newPresetStopLossPrice
        return await self.client._send_request("POST", request_path, body=body)

    async def modify_the_stop_profit_and_stop_loss_plan_order(self, marginCoin, productType, symbol, triggerPrice, size, orderId=None, clientOid=None, triggerType=None, executePrice=None, rangeRate=None):
        """
        Modify the stop-profit and stop-loss plan order.

        Args:
            marginCoin (str): Margin currency.
            productType (str): Product type: `usdt-futures` (USDT professional futures), `coin-futures` (Mixed futures), `usdc-futures` (USDC professional futures).
            symbol (str): Trading pair, e.g. ETHUSDT.
            triggerPrice (str): Trigger price.
            size (str): Order quantity. For the position take profit and position stop loss orders, the size should be `""`.
            orderId (str, optional): Take profit and stop loss order number. `orderId` and `clientOid` must provide one.
            clientOid (str, optional): Take profit and stop loss client order number. `orderId` and `clientOid` must provide one.
            triggerType (str, optional): Trigger type: `fill_price` (transaction price) or `mark_price` (mark price).
            executePrice (str, optional): Execution price. If it is 0 or not filled in, it means market price execution. If it is greater than 0, it means limit price execution. When `planType` (stop-profit and stop-loss type) is `moving_plan` (moving take-profit and stop-loss), it is not filled in and is fixed to the market price. implement.
            rangeRate (str, optional): Callback range.

        Returns:
            dict: Bitget API JSON response containing order details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/order/modify-tpsl-order"
        body = {
            "marginCoin": marginCoin,
            "productType": productType,
            "symbol": symbol,
            "triggerPrice": triggerPrice,
            "size": size
        }
        if orderId:
            body["orderId"] = orderId
        if clientOid:
            body["clientOid"] = clientOid
        if triggerType:
            body["triggerType"] = triggerType
        if executePrice:
            body["executePrice"] = executePrice
        if rangeRate is not None:
            body["rangeRate"] = rangeRate
        return await self.client._send_request("POST", request_path, body=body)

    async def modify_trigger_order(self, productType, orderId=None, clientOid=None, newSize=None, newPrice=None, newCallbackRatio=None, newTriggerPrice=None, newTriggerType=None, newStopSurplusTriggerPrice=None, newStopSurplusExecutePrice=None, newStopSurplusTriggerType=None, newStopLossTriggerPrice=None, newStopLossExecutePrice=None, newStopLossTriggerType=None):
        """
        Modify a pending trigger order, such as its TP/SL and/or triggerPrice.

        Args:
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            orderId (str, optional): Trigger order ID. Either `orderId` or `clientOid` is required. If both are entered, `orderId` prevails.
            clientOid (str, optional): Customized trigger order ID. Either `orderId` or `clientOid` is required. If both are entered, `orderId` prevails.
            newSize (str, optional): Amount of the modified transaction. If it is empty, the amount remains unchanged.
            newPrice (str, optional): Modified price for executing orders.
                1. When the original order is a trigger order and its type is Limit, the original price remains unchanged when this field is empty. Must be empty if the order type is Market.
                2. When the original order is a trailing order, it must be empty.
            newCallbackRatio (str, optional): Modified callback rate (for trailing stop orders only).
                1. When the original order is a trailing stop order, it must be filled in, and the rate must not be greater than 10.
                2. When the original order is a trigger order, it must be empty.
            newTriggerPrice (str, optional): Modified trigger price.
                1. When the original order is a trigger order or a trailing stop order, if the field is not set, the price stays unchanged; if it is set, the price updates.
            newTriggerType (str, optional): Modified trigger type.
                1. When the original order is a trigger order or a trailing stop order, if the field is not set, the type stays unchanged; if it is set, the type updates. Setting this parameter requires the setting of `newTriggerPrice`.
                `fill_price`: filled price; `mark_price`: mark price.
            newStopSurplusTriggerPrice (str, optional): Modified take-profit trigger price.
                1. If the field is left empty: when the original order has the TP set, the original value will be maintained.
                2. If it is not empty: when the original order has the TP set, the TP will update; when the original order doesn't have the TP set, the TP will be added. If 0 is filled in, the original TP setting will be removed.
            newStopSurplusExecutePrice (str, optional): Modified take-profit strike price.
                1. This parameter must be empty when the original order is a trailing stop order.
                2. For a trigger order, if this field is filled in, the price will update; if not filled in, the price stays unchanged; if 0 is filled in, the price setting will be removed.
            newStopSurplusTriggerType (str, optional): Modified take-profit trigger type. Default to the transaction price.
                1. This parameter must be empty when the original order is a trailing stop order.
                2. For a trigger order that has `newStopSurplusTriggerPrice` parameter set, it is required.
                `fill_price`: filled price; `mark_price`: mark price.
            newStopLossTriggerPrice (str, optional): Modified stop-loss trigger price.
                1. If the field is left empty: when the original order has the SL set, the original value will be maintained.
                2. If it is not empty: when the original order has the SL set, the SL will update; when the original order doesn't have the SL set, the SL will be added. If 0 is filled in, the original SL setting will be removed.
            newStopLossExecutePrice (str, optional): Modified stop-loss strike price.
                1. This parameter must be empty when the original order is a trailing stop order.
                2. For a trigger order, if this field is filled in, the price will update; if not filled in, the price stays unchanged; if 0 is filled in, the SL setting will be removed.
            newStopLossTriggerType (str, optional): Modified stop-loss trigger type. Default to the transaction price.
                1. This parameter must be empty when the original order is a trailing stop order.
                2. For a trigger order that has `newStopLossTriggerPrice` parameter set, it is required.
                `fill_price`: filled price; `mark_price`: mark price.

        Returns:
            dict: Bitget API JSON response containing order details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/order/modify-plan-order"
        body = {"productType": productType}
        if orderId:
            body["orderId"] = orderId
        if clientOid:
            body["clientOid"] = clientOid
        if newSize:
            body["newSize"] = newSize
        if newPrice:
            body["newPrice"] = newPrice
        if newCallbackRatio:
            body["newCallbackRatio"] = newCallbackRatio
        if newTriggerPrice:
            body["newTriggerPrice"] = newTriggerPrice
        if newTriggerType:
            body["newTriggerType"] = newTriggerType
        if newStopSurplusTriggerPrice:
            body["newStopSurplusTriggerPrice"] = newStopSurplusTriggerPrice
        if newStopSurplusExecutePrice:
            body["newStopSurplusExecutePrice"] = newStopSurplusExecutePrice
        if newStopSurplusTriggerType:
            body["newStopSurplusTriggerType"] = newStopSurplusTriggerType
        if newStopLossTriggerPrice:
            body["newStopLossTriggerPrice"] = newStopLossTriggerPrice
        if newStopLossExecutePrice:
            body["newStopLossExecutePrice"] = newStopLossExecutePrice
        if newStopLossTriggerType:
            body["newStopLossTriggerType"] = newStopLossTriggerType
        return await self.client._send_request("POST", request_path, body=body)

    async def get_order_detail(self, symbol, productType, orderId=None, clientOid=None):
        """
        Get order detail.

        Args:
            symbol (str): Product ID (must be capitalized).
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            orderId (str, optional): Order ID. Either `orderId` or `clientOid` is required.
            clientOid (str, optional): Custom order ID. Either `orderId` or `clientOid` is required.

        Returns:
            dict: Bitget API JSON response containing order details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/order/detail"
        params = {"symbol": symbol, "productType": productType}
        if orderId:
            params["orderId"] = orderId
        if clientOid:
            params["clientOid"] = clientOid
        return await self.client._send_request("GET", request_path, params=params)

    async def get_order_fill_details(self, productType, orderId=None, symbol=None, idLessThan=None, startTime=None, endTime=None, limit=None):
        """
        Get order fill details.

        Args:
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            orderId (str, optional): Order ID.
            symbol (str, optional): Trading pair, e.g. ETHUSDT.
            idLessThan (str, optional): Requests the content on the page before the `tradeId` (older data).
            startTime (str, optional): Start time (time stamp in milliseconds). The maximum time span supported is three months. The default end time is three months if no value is set for the end time. (For Managed Sub-Account, the StartTime cannot be earlier than the binding time).
            endTime (str, optional): End time (time stamp in milliseconds). The maximum time span supported is three months. The default start time is three months ago if no value is set for the start time.
            limit (str, optional): Number of queries: Default: 100, maximum: 100.

        Returns:
            dict: Bitget API JSON response containing order fill details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/order/fills"
        params = {"productType": productType}
        if orderId:
            params["orderId"] = orderId
        if symbol:
            params["symbol"] = symbol
        if idLessThan:
            params["idLessThan"] = idLessThan
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_pending_orders(self, productType, orderId=None, clientOid=None, symbol=None, status=None, idLessThan=None, startTime=None, endTime=None, limit=None):
        """
        Query all existing pending orders.

        Args:
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            orderId (str, optional): Order ID. If both `orderId` and `clientOid` are entered, `orderId` prevails.
            clientOid (str, optional): Customize order ID. If both `orderId` and `clientOid` are entered, `orderId` prevails.
            symbol (str, optional): Trading pair, e.g. ETHUSDT.
            status (str, optional): Order status: `live` (pending orders) or `partially_filled` (Partially filled). If not specified, all ordered with a status of live (not filled yet) will be returned.
            idLessThan (str, optional): Requests the content on the page before this ID (older data), the value input should be the endId of the corresponding interface.
            startTime (str, optional): Start timestamp. Unix timestamp in milliseconds format. The maximum time span supported is three months. The default end time is three months if no value is set for the end time.
            endTime (str, optional): End timestamp. Unix timestamp in milliseconds format. The maximum time span supported is three months. The default start time is three months ago if no value is set for the start time.
            limit (str, optional): Number of queries: Maximum: 100, default: 100.

        Returns:
            dict: Bitget API JSON response containing pending orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/order/orders-pending"
        params = {"productType": productType}
        if orderId:
            params["orderId"] = orderId
        if clientOid:
            params["clientOid"] = clientOid
        if symbol:
            params["symbol"] = symbol
        if status:
            params["status"] = status
        if idLessThan:
            params["idLessThan"] = idLessThan
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_pending_trigger_order(self, planType, productType, orderId=None, clientOid=None, symbol=None, idLessThan=None, startTime=None, endTime=None, limit=None):
        """
        Query one or all current trigger orders.

        Args:
            planType (str): Trigger order type: `normal_plan` (average trigger order), `track_plan` (trailing stop order), `profit_loss` (take profit and stop loss orders, including the `profit_plan`, `loss_plan`, `moving_plan`, `pos_profit` and `pos_loss`).
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            orderId (str, optional): Trigger order ID. Either `orderId` or `clientOid` is required. If both are entered, `orderId` prevails.
            clientOid (str, optional): Customized trigger order ID. Either `orderId` or `clientOid` is required. If both are entered, `orderId` prevails.
            symbol (str, optional): Trading pair, e.g. ETHUSDT.
            idLessThan (str, optional): Requests the content on the page before this ID (older data), the value input should be the endId of the corresponding interface.
            startTime (str, optional): Start timestamp. Unix timestamp in milliseconds format. The maximum time span supported is three months. The default end time is three months if no value is set for the end time.
            endTime (str, optional): End timestamp. Unix timestamp in milliseconds format. The maximum time span supported is three months. The default start time is three months ago if no value is set for the start time.
            limit (str, optional): Number of queries: Default: 100, maximum: 100.

        Returns:
            dict: Bitget API JSON response containing pending trigger orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/order/orders-plan-pending"
        params = {"planType": planType, "productType": productType}
        if orderId:
            params["orderId"] = orderId
        if clientOid:
            params["clientOid"] = clientOid
        if symbol:
            params["symbol"] = symbol
        if idLessThan:
            params["idLessThan"] = idLessThan
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_position_adl_rank(self, productType):
        """
        Query Account Position ADL Rank.

        Args:
            productType (str): Product type, default:`USDT-FUTURES`, `USDT-FUTURES` (USDT professional futures), `COIN-FUTURES` (Mixed futures), `USDC-FUTURES` (USDC professional futures).

        Returns:
            dict: Bitget API JSON response containing position ADL rank.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/position/adlRank"
        params = {"productType": productType}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_position_tier(self, productType, symbol):
        """
        Get the position gradient configuration of a certain trading pair.

        Args:
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            symbol (str): Trading pair.

        Returns:
            dict: Bitget API JSON response containing position tier configuration.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/market/query-position-lever"
        params = {"productType": productType, "symbol": symbol}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_single_position(self, productType, symbol, marginCoin):
        """
        Returns position information of a single symbol, response including estimated liquidation price.

        Args:
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            symbol (str): Trading pair, e.g. BTCUSDT.
            marginCoin (str): Margin coin (capitalized), e.g. USDT.

        Returns:
            dict: Bitget API JSON response containing single position details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/position/single-position"
        params = {"productType": productType, "symbol": symbol, "marginCoin": marginCoin}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_historical_position(self, symbol=None, productType=None, idLessThan=None, startTime=None, endTime=None, limit=None):
        """
        Check position history.
        (Only check the data within 3 months).

        Args:
            symbol (str, optional): Trading pair.
            productType (str, optional): Product type, default:`USDT-FUTURES`. If `symbol` parameter is requested, then this parameter will not take effect.
                `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).
            idLessThan (str, optional): Requests the content on the page before this ID (older data), the value input should be the endId of the corresponding interface.
            startTime (str, optional): Start time (timestamp in milliseconds). Wildest time range is 3 months. If this field is empty then the default time range is 3 months.
            endTime (str, optional): End time (timestamp in milliseconds). Wildest time range is 3 months. If this field is empty then the default time range is 3 months.
            limit (str, optional): Default 20, Max 100.

        Returns:
            dict: Bitget API JSON response containing historical position data.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/position/history-position"
        params = {}
        if symbol:
            params["symbol"] = symbol
        if productType:
            params["productType"] = productType
        if idLessThan:
            params["idLessThan"] = idLessThan
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_history_transactions(self, symbol, productType, limit=None, idLessThan=None, startTime=None, endTime=None):
        request_path = "/api/v2/mix/market/fills-history"
        params = {"symbol": symbol, "productType": productType}
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        return await self.client._send_request("GET", request_path, params=params)