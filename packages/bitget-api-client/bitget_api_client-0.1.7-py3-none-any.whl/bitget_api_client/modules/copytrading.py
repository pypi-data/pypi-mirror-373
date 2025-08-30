from .exceptions import BitgetAPIException

class CopyTrading:
    def __init__(self, client):
        self.client = client

    async def add_or_modify_following_configurations(self, traderId, settings, autoCopy=None, mode=None):
        """
        Add or Modify Following Configurations.

        Args:
            traderId (str): Trader user ID.
            settings (list[dict]): List of settings. Each dictionary should contain:
                - symbol (str): Trading pair.
                - traceType (str): Copy trade type: `percent` (Set the percentage of the copy trade amount to the trader's elite trade amount), `amount` (The fixed volume specified for copy trading), `count` (Number of copy trade orders with fixed volume, only take effect when parameter mode is advanced).
                - maxHoldSize (str): Maximum following buying quantity.
                - traceValue (str): Copy trade investment amount.
                - stopLossRatio (str, optional): The stop-loss ratio can only be a positive integer. 10 means 10%.
                - stopSurplusRatio (str, optional): The take-profit ratio can only be a positive integer. 10 means 10%.
            autoCopy (str, optional): Whether to automatically follow new symbol opened by traders (only take effect when parameter mode is basic): `on` (auto) or `off` (no).
            mode (str, optional): Follow mode: `basic` (basic mode) or `advanced` (advanced mode, default).

        Returns:
            dict: Bitget API JSON response indicating success.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/spot-follower/settings"
        body = {
            "traderId": traderId,
            "settings": settings
        }
        if autoCopy:
            body["autoCopy"] = autoCopy
        if mode:
            body["mode"] = mode
        return await self.client._send_request("POST", request_path, body=body)

    async def set_mix_copy_trade_settings(self, traderId, settings, autoCopy=None, mode=None):
        """
        Set Copy Trade Settings.

        Args:
            traderId (str): ID of the elite trader that you followed.
            settings (list[dict]): Settings of copy trading (based on trading pair). Maximum: 10. Each dictionary should contain:
                - symbol (str): Trading pair.
                - productType (str): Product type: `USDT-FUTURES` (USDT professional futures), `COIN-FUTURES` (Mixed futures), `USDC-FUTURES` (USDC professional futures).
                - marginType (str): Margin type (only take effect when parameter mode is advanced): `trader` (margin type of the elite trader that you followed) or `specify` (your own margin type).
                - marginCoin (str, optional): Margin currency.
                - leverType (str): Leverage type (only take effect when parameter mode is advanced): `position` (use position leverage), `specify` (use the specified leverage), `trader` (use the leverage of the elite trader).
                - longLeverage (str, optional): Leverage of long positions (only take effect when parameter mode is advanced).
                - shortLeverage (str, optional): Leverage of short positions (only take effect when parameter mode is advanced).
                - traceType (str): Copy trade position type: `percent` (Set the percentage of the copy trade amount to the trader's elite trade amount), `amount` (the fixed volume specified for copy trading), `count` (number of copy trade orders with fixed volume, only take effect when parameter mode is advanced).
                - traceValue (str): Copy trade position value.
                - maxHoldSize (str, optional): Maximum number of orders.
                - stopSurplusRatio (str, optional): Take-profit ratio. Positive integers within 1-400, Value exceeding this number is invalid.
                - stopLossRatio (str, optional): Stop-loss ratio. Positive integers within 1-400, Value exceeding this number is invalid.
            autoCopy (str, optional): Whether to automatically follow new symbol opened by traders (only take effect when parameter mode is basic): `on` (auto) or `off` (no).
            mode (str, optional): Follow mode: `basic` (basic mode) or `advanced` (advanced mode, default).

        Returns:
            dict: Bitget API JSON response indicating success or failure.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/mix-follower/settings"
        body = {
            "traderId": traderId,
            "settings": settings
        }
        if autoCopy:
            body["autoCopy"] = autoCopy
        if mode:
            body["mode"] = mode
        return await self.client._send_request("POST", request_path, body=body)

    async def cancel_follow(self, traderId):
        """
        Cancel Follow.

        Args:
            traderId (str): Trader user ID.

        Returns:
            dict: Bitget API JSON response indicating success.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/spot-follower/cancel-trader"
        body = {"traderId": traderId}
        return await self.client._send_request("POST", request_path, body=body)

    async def unfollow_mix_trader(self, traderId):
        """
        Unfollow the Trader.

        Args:
            traderId (str): Trader user ID.

        Returns:
            dict: Bitget API JSON response indicating success or failure.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/mix-follower/cancel-trader"
        body = {"traderId": traderId}
        return await self.client._send_request("POST", request_path, body=body)

    async def change_copy_trade_symbol_setting(self, settingList):
        """
        Change Copy Trade Symbol Setting.

        Args:
            settingList (list[dict]): Setting overview. Maximum: 50. Each dictionary should contain:
                - symbol (str): Trading pair.
                - productType (str): Product type: `USDT-FUTURES` (USDT professional futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC professional futures).
                - settingType (str): Setting type: `ADD`, `DELETE`, `UPDATE`.
                - stopSurplusRatio (str, optional): Take-profit ratio. Positive integers within 1-400. Value exceeding this number is invalid.
                    When a type is deleted: this value is invalid.
                    When a type is added: when the take-profit ratio is empty, then the take-profit ratio is not set by default.
                    When a type is updated: if the value is empty, it means that no change is made; if it is 0, it means that the previously set take-profit is canceled; if it is greater than 0, it means that the take-profit is added or updated. One of `stopSurplusRatio` and `stopLossRatio` must be passed when the type is updated.
                - stopLossRatio (str, optional): Stop-loss ratio. Positive integers within 1-400. Value exceeding this number is invalid.
                    When a type is deleted: this value is invalid.
                    When a type is added: when the stop-loss ratio is empty, then the stop-loss ratio is not set by default.
                    When a type is updated: if the value is empty, it means that no change is made; if it is 0, it means that the previously set take-profit is canceled; if it is greater than 0, it means that the stop-loss is added or updated. One of `stopSurplusRatio` and `stopLossRatio` must be passed when the type is updated.

        Returns:
            dict: Bitget API JSON response containing setting results.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/mix-trader/config-setting-symbols"
        body = {"settingList": settingList}
        return await self.client._send_request("POST", request_path, body=body)

    async def change_global_copy_trade_setting(self, enable=None, showTotalEquity=None, showTpsl=None):
        """
        Change Global Copy Trade Setting.

        Args:
            enable (str, optional): One of the three must be passed. Activates elite trading or not? `YES` or `NO`.
            showTotalEquity (str, optional): One of the three must be passed. Displays total assets (USDT) or not? `YES` or `NO`.
            showTpsl (str, optional): One of the three must be passed. TP/SL price of orders will be displayed publicly. `YES` or `NO`.

        Returns:
            dict: Bitget API JSON response indicating success or not.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/mix-trader/config-settings-base"
        body = {}
        if enable:
            body["enable"] = enable
        if showTotalEquity:
            body["showTotalEquity"] = showTotalEquity
        if showTpsl:
            body["showTpsl"] = showTpsl
        return await self.client._send_request("POST", request_path, body=body)

    async def set_spot_copytrade_symbols(self, symbolList, settingType):
        """
        Set Copytrade Symbols.

        Args:
            symbolList (list[str]): Collection with single currency pairs. Maximum 50.
            settingType (str): Setting type: `add` (add new) or `delete` (delete).

        Returns:
            dict: Bitget API JSON response indicating success.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/spot-trader/config-setting-symbols"
        body = {"symbolList": symbolList, "settingType": settingType}
        return await self.client._send_request("POST", request_path, body=body)

    async def close_positions(self, productType, trackingNo=None, symbol=None, marginCoin=None, marginMode=None, holdSide=None):
        """
        Interface for followers to close positions. Can close positions based on order ID, trading pair, direction, position mode, and margin.

        Args:
            productType (str): Product type: `USDT-FUTURES` (USDT professional futures), `COIN-FUTURES` (Mixed futures), `USDC-FUTURES` (USDC professional futures).
            trackingNo (str, optional): Tracking numbers of buying orders grouped by trading pair. (If you pass the `trackingNo` and ensure that the `symbol`, `marginCoin`, `marginMode`, and `holdSide` are not empty, you need to ensure that the `trackingNo` corresponds to them.)
            symbol (str, optional): Trading pair.
            marginCoin (str, optional): Margin coin.
            marginMode (str, optional): Position mode: `isolated` (isolated margin) or `cross` (cross margin).
            holdSide (str, optional): Position direction.
                1. In the buying and selling (one-way position) mode: you don’t have to fill it in, if you fill it in, it will be ignored.
                2. In the opening and closing position (hedge mode): This parameter must be filled in.
                `long`: long position in hedging mode; `short`: short position in hedging mode.

        Returns:
            dict: Bitget API JSON response containing order IDs.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/mix-follower/close-positions"
        body = {"productType": productType}
        if trackingNo:
            body["trackingNo"] = trackingNo
        if symbol:
            body["symbol"] = symbol
        if marginCoin:
            body["marginCoin"] = marginCoin
        if marginMode:
            body["marginMode"] = marginMode
        if holdSide:
            body["holdSide"] = holdSide
        return await self.client._send_request("POST", request_path, body=body)

    async def close_tracking_order(self, productType, trackingNo=None, symbol=None):
        """
        Tracking orders could only be closed by this API.

        Args:
            productType (str): Product type: `USDT-FUTURES` (USDT professional futures), `COIN-FUTURES` (Mixed futures), `USDC-FUTURES` (USDC professional futures). If only `productType` is passed, all positions under that line of business will be closed.
            trackingNo (str, optional): Track order number. Tracking ID from the current elite trade interface. If a symbol is also passed, make sure the order ID pair corresponds to it.
            symbol (str, optional): Trading pair. Supports capital and lower-case letters.

        Returns:
            dict: Bitget API JSON response containing tracking order details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/mix-trader/order-close-positions"
        body = {"productType": productType}
        if trackingNo:
            body["trackingNo"] = trackingNo
        if symbol:
            body["symbol"] = symbol
        return await self.client._send_request("POST", request_path, body=body)

    async def copy_settings(self, traderId, copyAmount, copyAllPostions=None, autoCopy=None, equityGuardian=None, equityGuardianMode=None, equity=None, marginMode=None, leverage=None, multiple=None):
        """
        Set up order following for the new version of followers.
        Currently, the interface only supports intelligent proportion and does not support multivariate exploration.
        Criteria for the new version of followers: Users who registered after January 26, 2024, or users who registered before January 26, 2024 and have manually upgraded.

        Args:
            traderId (str): ID of the elite trader that you followed.
            copyAmount (str): Copy trading amount, must be a positive integer not less than 50, denominated in USDT.
            copyAllPostions (str, optional): Whether to follow all positions of the trader: `yes` (Follow all positions) or `no` (Do not follow all positions). If not provided, the default value is `no`.
            autoCopy (str, optional): Whether to automatically follow new symbol opened by traders (only takes effect when mode is basic): `on` (Automatic following) or `off` (Not automatically following). If not provided, the default value is `on`.
            equityGuardian (str, optional): Equity protection switch: `on` (Enabled) or `off` (Disabled). If not provided, the default value is `off`.
            equityGuardianMode (str, optional): Equity protection mode, triggered when `equityGuardian`=`on`: `amount` (Fixed amount protection) or `percentage` (Percentage-based protection). If not provided, the default value is `amount`.
            equity (str, optional): Equity protection trigger value. Required when `equityGuardian`=`on`. Must be a positive integer. If `equityGuardianMode`=`percentage`, range is [1-100], representing 1%-100%. If `equityGuardianMode`=`amount`, it represents a fixed loss amount.
            marginMode (str, optional): Margin mode: `follow_trader` (Follow the trader's leverage), `crossed_margin` (Cross margin), `isolated_margin` (Isolated margin). If not provided, the default value is `follow_trader`.
            leverage (str, optional): Leverage mode, effective when `marginMode`=`follow_trader`: `follow_trader` (Follow trader) or `fixed_leverage` (Use fixed leverage). Default: `follow_trader`.
            multiple (str, optional): Leverage multiple, ranging from [1,125]. Default: 10.

        Returns:
            dict: Bitget API JSON response indicating success or failure.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/mix-follower/copy-settings"
        body = {
            "traderId": traderId,
            "copyAmount": copyAmount
        }
        if copyAllPostions:
            body["copyAllPostions"] = copyAllPostions
        if autoCopy:
            body["autoCopy"] = autoCopy
        if equityGuardian:
            body["equityGuardian"] = equityGuardian
        if equityGuardianMode:
            body["equityGuardianMode"] = equityGuardianMode
        if equity:
            body["equity"] = equity
        if marginMode:
            body["marginMode"] = marginMode
        if leverage:
            body["leverage"] = leverage
        if multiple:
            body["multiple"] = multiple
        return await self.client._send_request("POST", request_path, body=body)

    async def create_copy_apikey(self, passphrase):
        """
        Create Copy ApiKey.
        This interface is used for the new version of Copy Traders to create a Copy API Key, which is of HMAC type. Old version Copy Traders will receive an error message "This interface is only applicable to the new Copy model" when calling the interface.
        The new version of Copy Traders have user identifiers on the following side. These traders support selecting both [Futures Trading] and [Copy Trading] when engaging in contract transactions.
        The Copy Trading API Key can only be created once. If a user attempts to create another one while already having a Copy API Key, an error will be returned stating "You have already created a Copy API Key."
        For elite traders, please strictly adhere to the list of trading pairs specified in the [Available trading pairs and parameters for elite traders](https://www.bitget.com/zh-CN/support/articles/12560603808895) when placing orders using the Copy Trading API Key. Trading pairs outside the announced list are not available for copy trading.

        Args:
            passphrase (str): Password length must be 8 to 32 characters, consisting of English letters and numbers.

        Returns:
            dict: Bitget API JSON response containing API key details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/mix-trader/create-copy-api"
        body = {"passphrase": passphrase}
        return await self.client._send_request("POST", request_path, body=body)

    async def modify_tracking_order_tpsl(self, trackingNo, productType, stopSurplusPrice=None, stopLossPrice=None):
        """
        Modify Tracking Order TPSL.

        Args:
            trackingNo (str): Elite trade order ID.
            productType (str): Product type: `USDT-FUTURES` (USDT professional futures), `COIN-FUTURES` (Mixed futures), `USDC-FUTURES` (USDC professional futures).
            stopSurplusPrice (str, optional): TP price. One of `stopSurplusPrice` and `stopLossPrice` must be passed. When it is empty, it is ignored or not updated, no matter take-profit exists or not. When it is 0, it means the original take-profit is canceled if there is a take-profit already. When it is greater than or equal to 0, it means take-profit is updated or set.
            stopLossPrice (str, optional): SL price. One of `stopSurplusPrice` and `stopLossPrice` must be passed. When it is empty, it is ignored or not updated, no matter stop-loss exists or not. When it is 0, it means the original stop-loss is canceled if there is a stop-loss already. When it is greater than or equal to 0, it means stop-loss is updated or set.

        Returns:
            dict: Bitget API JSON response indicating success or failure.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/mix-trader/order-modify-tpsl"
        body = {
            "trackingNo": trackingNo,
            "productType": productType
        }
        if stopSurplusPrice:
            body["stopSurplusPrice"] = stopSurplusPrice
        if stopLossPrice:
            body["stopLossPrice"] = stopLossPrice
        return await self.client._send_request("POST", request_path, body=body)

    async def get_copy_trade_settings(self, traderId):
        """
        Get Copy Trade Settings.

        Args:
            traderId (str): ID of the elite trader that you followed.

        Returns:
            dict: Bitget API JSON response containing copy trade settings.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/mix-follower/query-settings"
        params = {"traderId": traderId}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_trader_current_trading_pair(self, traderId):
        """
        Get Trader's Current Trading Pair.

        Args:
            traderId (str): Trader ID.

        Returns:
            dict: Bitget API JSON response containing current trading pair list.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/spot-follower/query-trader-symbols"
        params = {"traderId": traderId}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_copy_trade_symbol_settings(self, productType):
        """
        Get Copy Trade Symbol Settings.

        Args:
            productType (str): Product type: `USDT-FUTURES` (USDT professional futures), `COIN-FUTURES` (Mixed futures), `USDC-FUTURES` (USDC professional futures).

        Returns:
            dict: Bitget API JSON response containing copy trade symbol settings.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/mix-trader/config-query-symbols"
        params = {"productType": productType}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_copytrade_configuration(self):
        """
        Get Copytrade Configuration.

        Returns:
            dict: Bitget API JSON response containing copytrade configuration details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/spot-trader/config-query-settings"
        return await self.client._send_request("GET", request_path, params={})

    async def get_current_copy_trade_orders(self, symbol=None, traderId=None, idLessThan=None, idGreaterThan=None, startTime=None, endTime=None, limit=None):
        """
        Get Current Copy Trade Orders.

        Args:
            symbol (str, optional): Trading pair.
            traderId (str, optional): Trader ID.
            idLessThan (str, optional): Before requesting this ID.
            idGreaterThan (str, optional): After requesting this ID.
            startTime (str, optional): Start time.
            endTime (str, optional): End time.
            limit (str, optional): The default is 20, with a maximum support of 50. More than 20 items will be returned.

        Returns:
            dict: Bitget API JSON response containing current copy trade orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/spot-follower/query-current-orders"
        params = {}
        if symbol:
            params["symbol"] = symbol
        if traderId:
            params["traderId"] = traderId
        if idLessThan:
            params["idLessThan"] = idLessThan
        if idGreaterThan:
            params["idGreaterThan"] = idGreaterThan
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_current_tracking_orders(self, productType, idLessThan=None, idGreaterThan=None, startTime=None, endTime=None, limit=None, symbol=None, traderId=None):
        """
        Query one or all current tracking orders.

        Args:
            productType (str): Product type: `USDT-FUTURES` (USDT professional futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC professional futures).
            idLessThan (str, optional): Separate page content before this ID is requested (older data), and the value input should be the end ID of the corresponding interface.
            idGreaterThan (str, optional): Separate page content after this ID is requested (newer data), and the value input should be the end ID of the corresponding interface.
            startTime (str, optional): Start timestamp (Copy trade creation time). Milliseconds format of timestamp Unix. The maximum time span supported is three months. The default end time is three months if no value is set for the end time.
            endTime (str, optional): End timestamp (Copy trade creation time). Milliseconds format of timestamp Unix. The maximum time span supported is three months. The default start time is three months ago if no value is set for the start time.
            limit (str, optional): Number of queries: Default: 20, maximum: 100.
            symbol (str, optional): Trading pairs, case sensitive.
            traderId (str, optional): Trader ID.

        Returns:
            dict: Bitget API JSON response containing current tracking orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/mix-follower/query-current-orders"
        params = {"productType": productType}
        if idLessThan:
            params["idLessThan"] = idLessThan
        if idGreaterThan:
            params["idGreaterThan"] = idGreaterThan
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if symbol:
            params["symbol"] = symbol
        if traderId:
            params["traderId"] = traderId
        return await self.client._send_request("GET", request_path, params=params)

    async def get_tracking_order_summary(self):
        """
        Get Tracking Order Summary.

        Returns:
            dict: Bitget API JSON response containing tracking order summary.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/mix-trader/order-total-detail"
        return await self.client._send_request("GET", request_path, params={})

    async def get_data_indicator_statistics(self):
        """
        Get Data Indicator Statistics.

        Returns:
            dict: Bitget API JSON response containing data indicator statistics.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/spot-trader/order-total-detail"
        return await self.client._send_request("GET", request_path, params={})

    async def get_follow_configuration(self, traderId):
        """
        Get Follow Configuration.

        Args:
            traderId (str): Trader user ID.

        Returns:
            dict: Bitget API JSON response containing follow configuration details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/spot-follower/query-settings"
        params = {"traderId": traderId}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_follow_limit(self, productType, symbol=None):
        """
        Get Follow Limit.

        Args:
            productType (str): Product type: `USDT-FUTURES` (USDT professional futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC professional futures).
            symbol (str, optional): Trading pair.

        Returns:
            dict: Bitget API JSON response containing follow limit details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/mix-follower/query-quantity-limit"
        params = {"productType": productType}
        if symbol:
            params["symbol"] = symbol
        return await self.client._send_request("GET", request_path, params=params)

    async def get_history_profit_share_detail(self, coin=None, idLessThan=None, idGreaterThan=None, startTime=None, endTime=None, limit=None):
        """
        Get History Profit Share Detail.

        Args:
            coin (str, optional): Settlement currency.
            idLessThan (str, optional): Separate page content before this ID is requested (older data), and the value input should be the endid of the corresponding interface.
            idGreaterThan (str, optional): Separate page content after this ID is requested (newer data), and the value input should be the endid of the corresponding interface.
            startTime (str, optional): Start timestamp. Milliseconds format of timestamp Unix. The maximum time span supported is three months. The default end time is three months if no value is set for the end time.
            endTime (str, optional): End timestamp. Milliseconds format of timestamp Unix. The maximum time span supported is three months. The default start time is three months ago if no value is set for the start time.
            limit (str, optional): Number of queries: Default: 100, maximum: 100.

        Returns:
            dict: Bitget API JSON response containing profit share details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/mix-trader/profit-history-details"
        params = {}
        if coin:
            params["coin"] = coin
        if idLessThan:
            params["idLessThan"] = idLessThan
        if idGreaterThan:
            params["idGreaterThan"] = idGreaterThan
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_history_profit_sharing_details(self, idLessThan=None, idGreaterThan=None, startTime=None, endTime=None, limit=None, coin=None):
        """
        Get History Profit Sharing Details.

        Args:
            idLessThan (str, optional): Request the paging content before this ID (older data), and the passed value is the endId of the corresponding interface.
            idGreaterThan (str, optional): Request the paging content after this ID (updated data). The value passed is the endId of the corresponding interface.
            startTime (str, optional): Start time.
            endTime (str, optional): End time.
            limit (str, optional): Number of queries: Default 100, maximum 100.
            coin (str, optional): Profit sharing settlement currency.

        Returns:
            dict: Bitget API JSON response containing history profit sharing details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/spot-trader/profit-history-details"
        params = {}
        if idLessThan:
            params["idLessThan"] = idLessThan
        if idGreaterThan:
            params["idGreaterThan"] = idGreaterThan
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if coin:
            params["coin"] = coin
        return await self.client._send_request("GET", request_path, params=params)

    async def get_spot_trader_profit_summary(self):
        """
        Get basic information on traders' profits and a summary of historical profits.

        Returns:
            dict: Bitget API JSON response containing profit summary.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/spot-trader/profit-summarys"
        return await self.client._send_request("GET", request_path, params={})

    async def get_mix_trader_profit_history_summary(self):
        """
        Get basic information on traders' profits and a summary of historical profits.

        Returns:
            dict: Bitget API JSON response containing profit summary.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/mix-trader/profit-history-summarys"
        return await self.client._send_request("GET", request_path, params={})

    async def get_history_tracking_orders(self, symbol=None, traderId=None, idLessThan=None, idGreaterThan=None, startTime=None, endTime=None, limit=None):
        """
        Get History Tracking Orders.

        Args:
            symbol (str, optional): Trading pair.
            traderId (str, optional): Trader ID.
            idLessThan (str, optional): Before requesting this ID.
            idGreaterThan (str, optional): After requesting this ID.
            startTime (str, optional): Start time.
            endTime (str, optional): End time.
            limit (str, optional): The default is 20, with a maximum support of 50. More than 20 items will be returned.

        Returns:
            dict: Bitget API JSON response containing history tracking orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/spot-follower/query-history-orders"
        params = {}
        if symbol:
            params["symbol"] = symbol
        if traderId:
            params["traderId"] = traderId
        if idLessThan:
            params["idLessThan"] = idLessThan
        if idGreaterThan:
            params["idGreaterThan"] = idGreaterThan
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_my_followers(self, pageNo=None, pageSize=None, startTime=None, endTime=None):
        """
        Get My Followers.

        Args:
            pageNo (str, optional): Page number (default: 1).
            pageSize (str, optional): Entries per page (default: 20, maximum: 100).
            startTime (str, optional): Start timestamp. Milliseconds format of timestamp Unix. The maximum time span supported is three months. The default end time is three months if no value is set for the end time.
            endTime (str, optional): End timestamp. Milliseconds format of timestamp Unix. The maximum time span supported is three months. The default start time is three months ago if no value is set for the start time.

        Returns:
            dict: Bitget API JSON response containing follower details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/mix-trader/config-query-followers"
        params = {}
        if pageNo:
            params["pageNo"] = pageNo
        if pageSize:
            params["pageSize"] = pageSize
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        return await self.client._send_request("GET", request_path, params=params)

    async def get_my_traders(self, startTime=None, endTime=None, pageNo=None, pageSize=None):
        """
        Get My Traders.

        Args:
            startTime (str, optional): Start timestamp. Milliseconds format of timestamp Unix. The maximum time span supported is three months. The default end time is three months if no value is set for the end time.
            endTime (str, optional): End timestamp. Milliseconds format of timestamp Unix. The maximum time span supported is three months. The default start time is three months ago if no value is set for the start time.
            pageNo (str, optional): Current page number. Default to 1.
            pageSize (str, optional): Number of queries. Default to 20 entries and supports a maximum of 50 entries.

        Returns:
            dict: Bitget API JSON response containing trader details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/mix-follower/query-traders"
        params = {}
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if pageNo:
            params["pageNo"] = pageNo
        if pageSize:
            params["pageSize"] = pageSize
        return await self.client._send_request("GET", request_path, params=params)

    async def get_spot_my_followers(self, pageNo=None, pageSize=None, startTime=None, endTime=None):
        """
        Get My Follower List.

        Args:
            pageNo (str, optional): Page number (default 1).
            pageSize (str, optional): Page size (default 30, max 1000).
            startTime (str, optional): Start time.
            endTime (str, optional): End time.

        Returns:
            dict: Bitget API JSON response containing follower list.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/spot-trader/config-query-followers"
        params = {}
        if pageNo:
            params["pageNo"] = pageNo
        if pageSize:
            params["pageSize"] = pageSize
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        return await self.client._send_request("GET", request_path, params=params)

    async def get_spot_my_traders(self, startTime=None, endTime=None, pageNo=None, pageSize=None):
        """
        Get My Trader List.

        Args:
            pageNo (str, optional): Page number (default 1).
            pageSize (str, optional): The default is 20, and the maximum supported is 50.
            startTime (str, optional): Start time.
            endTime (str, optional): End time.

        Returns:
            dict: Bitget API JSON response containing trader list.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/spot-follower/query-traders"
        params = {}
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if pageNo:
            params["pageNo"] = pageNo
        if pageSize:
            params["pageSize"] = pageSize
        return await self.client._send_request("GET", request_path, params=params)

    async def get_profit_share_detail(self, coin=None, pageSize=None, pageNo=None):
        """
        Get Profit Share Detail.

        Args:
            coin (str, optional): Settlement currency of profit share.
            pageSize (str, optional): Number of inquiries. Default: 20, maximum: 100.
            pageNo (str, optional): Current page number. Default to 1.

        Returns:
            dict: Bitget API JSON response containing profit share details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/mix-trader/profit-details"
        params = {}
        if coin:
            params["coin"] = coin
        if pageSize:
            params["pageSize"] = pageSize
        if pageNo:
            params["pageNo"] = pageNo
        return await self.client._send_request("GET", request_path, params=params)

    async def get_unrealized_profit_sharing_details(self, coin=None, pageNo=None, pageSize=None):
        """
        Get Unrealized Profit Sharing Details.

        Args:
            coin (str, optional): Settlement currency of profit share.
            pageNo (str, optional): Page number.
            pageSize (str, optional): The number of queries. The default is 20, and the maximum supported is 50.

        Returns:
            dict: Bitget API JSON response containing unrealized profit sharing details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/spot-trader/profit-details"
        params = {}
        if coin:
            params["coin"] = coin
        if pageNo:
            params["pageNo"] = pageNo
        if pageSize:
            params["pageSize"] = pageSize
        return await self.client._send_request("GET", request_path, params=params)

    async def remove_follower(self, followerUid):
        """
        Remove Follower.

        Args:
            followerUid (str): Follower UID.

        Returns:
            dict: Bitget API JSON response indicating success.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/mix-trader/config-remove-follower"
        body = {"followerUid": followerUid}
        return await self.client._send_request("POST", request_path, body=body)

    async def remove_followers(self, followerUid):
        """
        Remove Followers.

        Args:
            followerUid (str): Follower UID.

        Returns:
            dict: Bitget API JSON response indicating success.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/spot-trader/config-remove-follower"
        body = {"followerUid": followerUid}
        return await self.client._send_request("POST", request_path, body=body)

    async def sell_and_sell_in_batch(self, trackingNoList, symbol):
        """
        Sell And Sell in Batch.

        Args:
            trackingNoList (str): Tracking numbers of buying orders grouped by trading pair; all successful or all failed; up to 50 order tracking numbers.
            symbol (str): Trading pair.

        Returns:
            dict: Bitget API JSON response indicating success.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/spot-follower/order-close-tracking"
        body = {"trackingNoList": trackingNoList, "symbol": symbol}
        return await self.client._send_request("POST", request_path, body=body)

    async def set_take_profit_and_stop_loss(self, trackingNo, stopSurplusPrice=None, stopLossPrice=None):
        """
        Set Take Profit And Stop Loss.

        Args:
            trackingNo (str): Tracking Order number.
            stopSurplusPrice (str, optional): TP price. One of `stopSurplusPrice` and `stopLossPrice` must be passed. When it is empty, it is ignored or not updated, no matter take-profit exists or not. When it is 0, it means the original take-profit is canceled if there is a take-profit already. When it is greater than or equal to 0, it means take-profit is updated or set.
            stopLossPrice (str, optional): SL price. One of `stopSurplusPrice` and `stopLossPrice` must be passed. When it is empty, it is ignored or not updated, no matter stop-loss exists or not. When it is 0, it means the original stop-loss is canceled if there is a stop-loss already. When it is greater than or equal to 0, it means stop-loss is updated or set.

        Returns:
            dict: Bitget API JSON response indicating success.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/spot-follower/setting-tpsl"
        body = {"trackingNo": trackingNo}
        if stopSurplusPrice:
            body["stopSurplusPrice"] = stopSurplusPrice
        if stopLossPrice:
            body["stopLossPrice"] = stopLossPrice
        return await self.client._send_request("POST", request_path, body=body)

    async def set_tpsl(self, trackingNo, productType, symbol=None, stopSurplusPrice=None, stopLossPrice=None):
        """
        Set TPSL.

        Args:
            trackingNo (str): Order tracking number.
            productType (str): Product type: `USDT-FUTURES` (USDT professional futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC professional futures).
            symbol (str, optional): Trading pair.
            stopSurplusPrice (str, optional): Take profit price. When it is empty, it is ignored or not updated, no matter take-profit exists or not. When it is 0, it means the original take-profit is canceled if there is a take-profit already. When it is greater than or equal to 0, it means take-profit is updated or set.
            stopLossPrice (str, optional): Stop loss price. When it is empty, it is ignored or not updated, no matter stop-loss exists or not. When it is 0, it means the original stop-loss is canceled if there is a stop-loss already. When it is greater than or equal to 0, it means stop-loss is updated or set.

        Returns:
            dict: Bitget API JSON response indicating success or failure.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/mix-follower/setting-tpsl"
        body = {"trackingNo": trackingNo, "productType": productType}
        if symbol:
            body["symbol"] = symbol
        if stopSurplusPrice:
            body["stopSurplusPrice"] = stopSurplusPrice
        if stopLossPrice:
            body["stopLossPrice"] = stopLossPrice
        return await self.client._send_request("POST", request_path, body=body)

    async def stop_the_order(self, trackingNoList):
        """
        Stop The Order.

        Args:
            trackingNoList (str): Order tracking number groups. Up to 50. Atomic execution results, either all successful or all failed.

        Returns:
            dict: Bitget API JSON response indicating success.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/spot-follower/stop-order"
        body = {"trackingNoList": trackingNoList}
        return await self.client._send_request("POST", request_path, body=body)

    async def get_profit_share_group_by_coin_date(self, pageSize=None, pageNo=None):
        """
        Get Profit Share Group by Coin & Date.

        Args:
            pageSize (str, optional): Number of inquiries. Defaults to 20 entries and supports a maximum of 50 entries.
            pageNo (str, optional): Current page number. Default to 1.

        Returns:
            dict: Bitget API JSON response containing profit share grouped by coin and date.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/copy/mix-trader/profits-group-coin-date"
        params = {}
        if pageSize:
            params["pageSize"] = pageSize
        if pageNo:
            params["pageNo"] = pageNo
        return await self.client._send_request("GET", request_path, params=params)