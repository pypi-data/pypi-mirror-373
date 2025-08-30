from .exceptions import BitgetAPIException

class Margin:
    def __init__(self, client):
        self.client = client

    async def cross_batch_cancel_orders(self, symbol, orderIdList):
        """
        Cross Batch Cancel Orders.

        Args:
            symbol (str): Trading pairs, like BTCUSDT.
            orderIdList (list): Order ID list. Each item in the list should be a dictionary containing either `orderId` (str, optional) or `clientOid` (str, optional).

        Returns:
            dict: Bitget API JSON response containing lists of successful and failed order cancellations.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/crossed/batch-cancel-order"
        body = {"symbol": symbol, "orderIdList": orderIdList}
        return await self.client._send_request("POST", request_path, body=body)

    async def cross_batch_orders(self, symbol, orderList):
        """
        Cross Batch Orders.

        Args:
            symbol (str): Trading pairs, like BTCUSDT.
            orderList (list): Order entries. Each item in the list should be a dictionary with the following keys:
                orderType (str): Order type (`limit` or `market`).
                loanType (str): Margin order model (`normal`, `autoLoan`, `autoRepay`, `autoLoanAndRepay`).
                force (str): Time in force (`gtc`, `post_only`, `fok`, `ioc`). Invalid when `orderType` is `market`.
                side (str): Direction (`sell` or `buy`).
                price (str, optional): Price.
                baseSize (str, optional): Must fill limit and market sell. Sell order presents quantity of based currency (the left coin).
                quoteSize (str, optional): Must fill market buy. Buy order presents quantity of quote currency (the right coin).
                clientOid (str, optional): Customized ID.
                stpMode (str, optional): STP Mode (`none`, `cancel_taker`, `cancel_maker`, `cancel_both`).

        Returns:
            dict: Bitget API JSON response containing lists of successful and failed orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/crossed/batch-place-order"
        body = {"symbol": symbol, "orderList": orderList}
        return await self.client._send_request("POST", request_path, body=body)

    async def cross_borrow(self, coin, borrowAmount, clientOid=None):
        """
        Cross Borrow.

        Args:
            coin (str): Borrowing coin.
            borrowAmount (str): Borrowing amount (up to 8 decimal places).
            clientOid (str, optional): Client customized order ID.

        Returns:
            dict: Bitget API JSON response containing loan order ID, coin, and borrowed amount.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/crossed/account/borrow"
        body = {"coin": coin, "borrowAmount": borrowAmount}
        if clientOid:
            body["clientOid"] = clientOid
        return await self.client._send_request("POST", request_path, body=body)

    async def cross_cancel_order(self, symbol, orderId=None, clientOid=None):
        """
        Cross Cancel Order.

        Args:
            symbol (str): Trading pairs, like BTCUSDT.
            orderId (str, optional): Order ID. Either `orderId` or `clientOid` must be provided.
            clientOid (str, optional): Client customized ID. Either `orderId` or `clientOid` must be provided.

        Returns:
            dict: Bitget API JSON response containing the order ID and client customized ID of the cancelled order.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/crossed/cancel-order"
        body = {"symbol": symbol}
        if orderId:
            body["orderId"] = orderId
        if clientOid:
            body["clientOid"] = clientOid
        return await self.client._send_request("POST", request_path, body=body)

    async def cross_flash_repay(self, coin=None):
        """
        Cross Flash Repay.

        Args:
            coin (str, optional): Repayment coin for the cross margin. If not provided, the cross margin account will be fully repaid.

        Returns:
            dict: Bitget API JSON response containing repayment ID and coin.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/crossed/account/flash-repay"
        body = {}
        if coin:
            body["coin"] = coin
        return await self.client._send_request("POST", request_path, body=body)

    async def cross_place_order(self, symbol, orderType, loanType, force, side, price=None, baseSize=None, quoteSize=None, clientOid=None, stpMode=None):
        """
        Cross Place Order.

        Args:
            symbol (str): Trading pairs, like BTCUSDT.
            orderType (str): Order type (`limit` or `market`).
            loanType (str): Margin order model (`normal`, `autoLoan`, `autoRepay`, `autoLoanAndRepay`).
            force (str): Time in force (`gtc`, `post_only`, `fok`, `ioc`). Invalid when `orderType` is `market`.
            side (str): Direction (`sell` or `buy`).
            price (str, optional): Price.
            baseSize (str, optional): Must fill limit and market sell. Sell order presents quantity of based currency (the left coin).
            quoteSize (str, optional): Must fill market buy. Buy order presents quantity of quote currency (the right coin).
            clientOid (str, optional): Customized ID. The idempotency time is 6 hours, only valid when orders are unfilled.
            stpMode (str, optional): STP Mode (`none`, `cancel_taker`, `cancel_maker`, `cancel_both`).

        Returns:
            dict: Bitget API JSON response containing the order ID and client customized ID.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/crossed/place-order"
        body = {
            "symbol": symbol,
            "orderType": orderType,
            "loanType": loanType,
            "force": force,
            "side": side
        }
        if price:
            body["price"] = price
        if baseSize:
            body["baseSize"] = baseSize
        if quoteSize:
            body["quoteSize"] = quoteSize
        if clientOid:
            body["clientOid"] = clientOid
        if stpMode:
            body["stpMode"] = stpMode
        return await self.client._send_request("POST", request_path, body=body)

    async def cross_repay(self, coin, repayAmount):
        """
        Cross Repay.

        Args:
            coin (str): Repayment coin.
            repayAmount (str): Number of repayments (up to 8 decimal places).

        Returns:
            dict: Bitget API JSON response containing remaining debt amount, repay ID, coin, and repayment amount.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/crossed/account/repay"
        body = {"coin": coin, "repayAmount": repayAmount}
        return await self.client._send_request("POST", request_path, body=body)

    async def get_cross_tier_configuration(self, coin):
        """
        Get Cross Tier Configuration.
        This interface will determine the user's VIP level based on the User ID sending the request, and then return the tier information based on the VIP level.

        Args:
            coin (str): Coin.

        Returns:
            dict: Bitget API JSON response containing tier configuration information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/crossed/tier-data"
        params = {"coin": coin}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_cross_max_borrowable(self, coin):
        """
        Get Cross Max Borrowable.

        Args:
            coin (str): Borrowing coins, such as BTC.

        Returns:
            dict: Bitget API JSON response containing the maximum borrowable amount and coin.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/crossed/account/max-borrowable-amount"
        params = {"coin": coin}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_cross_account_assets(self, coin=None):
        """
        Get Cross Account Assets.

        Args:
            coin (str, optional): Coin, like USDT.

        Returns:
            dict: Bitget API JSON response containing cross margin account assets.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/crossed/account/assets"
        params = {}
        if coin:
            params["coin"] = coin
        return await self.client._send_request("GET", request_path, params=params)

    async def get_cross_max_transferable(self, coin):
        """
        Get Cross Max Transferable.

        Args:
            coin (str): Token name.

        Returns:
            dict: Bitget API JSON response containing the maximum transferable amount and coin.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/crossed/account/max-transfer-out-amount"
        params = {"coin": coin}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_cross_risk_rate(self):
        """
        Get Cross Risk Rate.

        Returns:
            dict: Bitget API JSON response containing the risk rate (total assets/total liabilities under cross mode).

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/crossed/account/risk-rate"
        return await self.client._send_request("GET", request_path, params={})

    async def get_cross_borrow_history(self, startTime, loanId=None, coin=None, endTime=None, limit=None, idLessThan=None):
        """
        Get Cross Borrow History.

        Args:
            startTime (str): Start time, Unix millisecond timestamp.
            loanId (str, optional): Borrowing ID (exact match of single item).
            coin (str, optional): Coin.
            endTime (str, optional): End time, Unix millisecond timestamp. Maximum interval between start time and end time is 90 days.
            limit (str, optional): Number of queries. Default: 100, maximum: 500.
            idLessThan (str, optional): For turning pages. The first query is not passed. When querying data in the second page and the data beyond, the last loanId returned in the last query is used, and the result will return data with a value less than this one; the query response time will be shortened.

        Returns:
            dict: Bitget API JSON response containing borrow history.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/crossed/borrow-history"
        params = {"startTime": startTime}
        if loanId:
            params["loanId"] = loanId
        if coin:
            params["coin"] = coin
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_cross_repay_history(self, startTime, repayId=None, coin=None, endTime=None, limit=None, idLessThan=None):
        """
        Get Cross Repay History.

        Args:
            startTime (str): Start time, Unix millisecond timestamp.
            repayId (str, optional): Repayment ID.
            coin (str, optional): Coin.
            endTime (str, optional): End time, Unix millisecond timestamp. Maximum interval between start time and end time is 90 days.
            limit (str, optional): Number of queries. Default: 100, maximum: 500.
            idLessThan (str, optional): For turning pages. The first query is not passed. When querying data in the second page and the data beyond, the last repayId returned in the last query is used, and the result will return data with a value less than this one; the query response time will be shortened.

        Returns:
            dict: Bitget API JSON response containing repay history.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/crossed/repay-history"
        params = {"startTime": startTime}
        if repayId:
            params["repayId"] = repayId
        if coin:
            params["coin"] = coin
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_cross_financial_history(self, startTime, marginType=None, coin=None, endTime=None, limit=None, idLessThan=None):
        """
        Get Cross Financial History.

        Args:
            startTime (str): Start time, Unix millisecond timestamp.
            marginType (str, optional): Capital flow type (`transfer_in`, `transfer_out`, `borrow`, `repay`, `liquidation_fee`, `compensate`, `deal_in`, `deal_out`, `confiscated`, `exchange_in`, `exchange_out`, `sys_exchange_in`, `sys_exchange_out`).
            coin (str, optional): Coin.
            endTime (str, optional): End time, Unix millisecond timestamp. Maximum interval between start time and end time is 90 days.
            limit (str, optional): Number of queries. Default: 100, maximum: 500.
            idLessThan (str, optional): For turning pages. The first query is not passed. When querying data in the second page and the data beyond, the last marginId returned in the last query is used, and the result will return data with a value less than this one; the query response time will be shortened.

        Returns:
            dict: Bitget API JSON response containing financial records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/crossed/financial-records"
        params = {"startTime": startTime}
        if marginType:
            params["marginType"] = marginType
        if coin:
            params["coin"] = coin
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_cross_liquidation_history(self, startTime, endTime=None, limit=None, idLessThan=None):
        """
        Get Cross Liquidation History.

        Args:
            startTime (str): Start time, Unix millisecond timestamp.
            endTime (str, optional): End time, Unix millisecond timestamp. Maximum interval between start time and end time is 90 days.
            limit (str, optional): Number of queries. Default: 100, maximum: 500.
            idLessThan (str, optional): For turning pages. The first query is not passed. When querying data in the second page and the data beyond, the last liqId returned in the last query is used, and the result will return data with a value less than this one; the query response time will be shortened.

        Returns:
            dict: Bitget API JSON response containing liquidation history.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/crossed/liquidation-history"
        params = {"startTime": startTime}
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_cross_flash_repay_result(self, idList):
        """
        Get Cross Flash Repay Result.

        Args:
            idList (list): Set of IDs for close position requests (Max. 100 IDs).

        Returns:
            dict: Bitget API JSON response containing repayment ID and status.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/crossed/account/query-flash-repay-status"
        body = {"idList": idList}
        return await self.client._send_request("POST", request_path, body=body)

    async def get_cross_interest_rate_and_max_borrowable(self, coin):
        """
        Get Cross Interest Rate and Max Borrowable.
        This interface will determine the user's VIP level based on the User ID sending the request, and then return information such as interest rates and limits based on the VIP level.

        Args:
            coin (str): Trading pairs, like BTC, ETH.

        Returns:
            dict: Bitget API JSON response containing interest rate and max borrowable information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/crossed/interest-rate-and-limit"
        params = {"coin": coin}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_cross_current_orders(self, symbol, startTime, orderId=None, clientOid=None, endTime=None, limit=None, idLessThan=None):
        """
        Get Cross Current Orders.

        Args:
            symbol (str): Trading pairs, like BTCUSDT.
            startTime (str): Start time, Unix millisecond timestamp.
            orderId (str, optional): Order ID.
            clientOid (str, optional): Client customized ID.
            endTime (str, optional): End time, Unix millisecond timestamp.
            limit (str, optional): Number of queries. Default: 100 entries.
            idLessThan (str, optional): For turning pages. The first query is not passed. When querying data in the second page and the data beyond, the last loanId returned in the last query is used, and the result will return data with a value less than this one; the query response time will be shortened.

        Returns:
            dict: Bitget API JSON response containing current orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/crossed/open-orders"
        params = {"symbol": symbol, "startTime": startTime}
        if orderId:
            params["orderId"] = orderId
        if clientOid:
            params["clientOid"] = clientOid
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_cross_interest_history(self, startTime, coin=None, endTime=None, limit=None, idLessThan=None):
        """
        Get Cross Interest History.

        Args:
            startTime (str): Start time, Unix millisecond timestamp.
            coin (str, optional): Coin.
            endTime (str, optional): End time, Unix millisecond timestamp. Maximum interval between start time and end time is 90 days.
            limit (str, optional): Number of queries. Default: 100, maximum: 500.
            idLessThan (str, optional): For turning pages. The first query is not passed. When querying data in the second page and the data beyond, the last loanId returned in the last query is used, and the result will return data with a value less than this one; the query response time will be shortened.

        Returns:
            dict: Bitget API JSON response containing interest history.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/crossed/interest-history"
        params = {"startTime": startTime}
        if coin:
            params["coin"] = coin
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_cross_history_orders(self, symbol, startTime, orderId=None, enterPointSource=None, clientOid=None, endTime=None, limit=None, idLessThan=None):
        """
        Get Cross History Orders.

        Args:
            symbol (str): Trading pairs, like BTCUSDT.
            startTime (str): Start time, Unix millisecond timestamp.
            orderId (str, optional): Order ID.
            enterPointSource (str, optional): Order source (`WEB`, `API`, `SYS`, `ANDROID`, `IOS`).
            clientOid (str, optional): Client customized ID.
            endTime (str, optional): End time, Unix millisecond timestamp. Maximum interval between start time and end time is 90 days.
            limit (str, optional): Number of queries. Default: 100, maximum: 500.
            idLessThan (str, optional): For turning pages. It's not needed in the first query. When querying data in the second page and the data beyond, the last endId returned in the last query is used, and the result will return data with a value less than this one; the query response time will be shortened.

        Returns:
            dict: Bitget API JSON response containing history orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/crossed/history-orders"
        params = {"symbol": symbol, "startTime": startTime}
        if orderId:
            params["orderId"] = orderId
        if enterPointSource:
            params["enterPointSource"] = enterPointSource
        if clientOid:
            params["clientOid"] = clientOid
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_isolated_borrow_history(self, symbol, startTime, loanId=None, coin=None, endTime=None, limit=None, idLessThan=None):
        """
        Get Isolated Borrow History.

        Args:
            symbol (str): Trading pairs, BTCUSDT.
            startTime (str): Start time, Unix millisecond timestamps.
            loanId (str, optional): Borrowing ID (accurate matching of single entry).
            coin (str, optional): Coin.
            endTime (str, optional): End time, Unix millisecond timestamps. Maximum interval between start and end times is 90 days.
            limit (str, optional): Number of queries. Default: 100, maximum: 500.
            idLessThan (str, optional): For turning pages. No setting is needed when querying for the first time. Set to the smallest loanId returned from the last query when searching for data in the second page and other paged. Data smaller than the loanId entered will be returned. This is designed to shorten the query response time.

        Returns:
            dict: Bitget API JSON response containing isolated borrow history.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/isolated/borrow-history"
        params = {"symbol": symbol, "startTime": startTime}
        if loanId:
            params["loanId"] = loanId
        if coin:
            params["coin"] = coin
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_isolated_interest_history(self, symbol, startTime, coin=None, endTime=None, limit=None, idLessThan=None):
        """
        Get Isolated Interest History.

        Args:
            symbol (str): Trading pair.
            startTime (str): Start time, Unix millisecond timestamps.
            coin (str, optional): Coin.
            endTime (str, optional): End time, Unix millisecond timestamps. Maximum interval between start and end times is 90 days.
            limit (str, optional): Number of queries. Default: 100, maximum: 500.
            idLessThan (str, optional): For turning pages. No setting is needed when querying for the first time. Set to the smallest interestId returned from the last query when searching for data in the second page and other paged. Data smaller than the interestId entered will be returned. This is designed to shorten the query response time.

        Returns:
            dict: Bitget API JSON response containing isolated interest history.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/isolated/interest-history"
        params = {"symbol": symbol, "startTime": startTime}
        if coin:
            params["coin"] = coin
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_isolated_liquidation_history(self, symbol, startTime, endTime=None, limit=None, idLessThan=None):
        """
        Get Isolated Liquidation History.

        Args:
            symbol (str): Trading pair.
            startTime (str): Start time, Unix millisecond timestamps.
            endTime (str, optional): End time, Unix millisecond timestamps. Maximum interval between start and end times is 90 days.
            limit (str, optional): Number of queries. Default: 100, maximum: 500.
            idLessThan (str, optional): For turning pages. No setting is needed when querying for the first time. Set to the smallest liqId returned from the last query when searching for data in the second page and other paged. Data smaller than the liqId entered will be returned. This is designed to shorten the query response time.

        Returns:
            dict: Bitget API JSON response containing isolated liquidation history.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/isolated/liquidation-history"
        params = {"symbol": symbol, "startTime": startTime}
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_isolated_financial_history(self, symbol, startTime, marginType=None, coin=None, endTime=None, limit=None, idLessThan=None):
        """
        Get Isolated Financial History.

        Args:
            symbol (str): Trading pairs, BTCUSDT.
            startTime (str): Start time, Unix millisecond timestamps.
            marginType (str, optional): Capital flow type (`transfer_in`, `transfer_out`, `borrow`, `repay`, `liquidation_fee`, `compensate`, `deal_in`, `deal_out`, `confiscated`, `exchange_in`, `exchange_out`, `sys_exchange_in`, `sys_exchange_out`).
            coin (str, optional): Coin.
            endTime (str, optional): End time, Unix millisecond timestamps. Maximum interval between start and end times is 90 days.
            limit (str, optional): Number of queries. Default: 100, maximum: 500.
            idLessThan (str, optional): For turning pages. No setting is needed when querying for the first time. Set to the smallest marginId returned from the last query when searching for data in the second page and other paged. Data smaller than the marginId entered will be returned. This is designed to shorten the query response time.

        Returns:
            dict: Bitget API JSON response containing isolated financial records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/isolated/financial-records"
        params = {"symbol": symbol, "startTime": startTime}
        if marginType:
            params["marginType"] = marginType
        if coin:
            params["coin"] = coin
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def isolated_batch_cancel_orders(self, symbol, orderIdList=None):
        """
        Cancel Isolated Orders in Batch.

        Args:
            symbol (str): Trading pairs, BTCUSDT.
            orderIdList (list, optional): Order ID list. Each item in the list should be a dictionary containing either `orderId` (str, optional) or `clientOid` (str, optional). Either `orderId` or `clientOid` is required within each dictionary.

        Returns:
            dict: Bitget API JSON response containing lists of successful and failed order cancellations.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/isolated/batch-cancel-order"
        body = {"symbol": symbol}
        if orderIdList:
            body["orderIdList"] = orderIdList
        return await self.client._send_request("POST", request_path, body=body)

    async def get_cross_liquidation_orders(self, type=None, symbol=None, fromCoin=None, toCoin=None, startTime=None, endTime=None, limit=None, idLessThan=None):
        """
        Get Cross Liquidation Orders.

        Args:
            type (str, optional): Type (`swap` or `place_order`). Default is `place_order`.
            symbol (str, optional): Trading pairs, like BTCUSDT. This field only takes effect when `type=place_order`. Default all symbols.
            fromCoin (str, optional): Swap from coin. This field only takes effect when `type=swap`.
            toCoin (str, optional): Swap to coin. This field only takes effect when `type=swap`.
            startTime (str, optional): Start time, Unix millisecond timestamp.
            endTime (str, optional): End time, Unix millisecond timestamp. Maximum interval between start time and end time is 90 days.
            limit (str, optional): Number of queries. Default: 100, maximum: 500.
            idLessThan (str, optional): For turning pages. The first query is not passed. When querying data in the second page and the data beyond, the last endId returned in the last query is used, and the result will return data with a value less than this one; the query response time will be shortened.

        Returns:
            dict: Bitget API JSON response containing liquidation orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/crossed/liquidation-order"
        params = {}
        if type:
            params["type"] = type
        if symbol:
            params["symbol"] = symbol
        if fromCoin:
            params["fromCoin"] = fromCoin
        if toCoin:
            params["toCoin"] = toCoin
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_cross_order_fills(self, symbol, startTime, orderId=None, idLessThan=None, endTime=None, limit=None):
        """
        Get Cross Order Fills.

        Args:
            symbol (str): Trading pairs, like BTCUSDT.
            startTime (str): Start time, Unix millisecond timestamp.
            orderId (str, optional): Order ID.
            idLessThan (str, optional): Match order ID, relative parameters of turning pages. The first query is not passed. When querying data in the second page and the data beyond, the last fillId returned in the last query is used, and the result will return data with a value less than this one; the query response time will be shortened.
            endTime (str, optional): End time, Unix millisecond timestamp. Maximum interval between start time and end time is 90 days.
            limit (str, optional): Number of queries. Default: 100, maximum: 500.

        Returns:
            dict: Bitget API JSON response containing order fills.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/crossed/fills"
        params = {"symbol": symbol, "startTime": startTime}
        if orderId:
            params["orderId"] = orderId
        if idLessThan:
            params["idLessThan"] = idLessThan
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def isolated_place_order(self, symbol, orderType, loanType, force, side, price=None, baseSize=None, quoteSize=None, clientOid=None, stpMode=None):
        """
        Isolated Place Order.

        Args:
            symbol (str): Trading pairs, BTCUSDT.
            orderType (str): Order type (`limit` or `market`).
            loanType (str): Margin order model (`normal`, `autoLoan`, `autoRepay`, `autoLoanAndRepay`).
            force (str): Time in force (`gtc`, `post_only`, `fok`, `ioc`). Invalid when `orderType` is `market`.
            side (str): Direction (`sell` or `buy`).
            price (str, optional): Price.
            baseSize (str, optional): Limit and Market sell are required. Sell orders represent the number of baseCoins (left coin).
            quoteSize (str, optional): Market buy is required, the buy order represents the number of quote coins (right coin).
            clientOid (str, optional): Customized ID.
            stpMode (str, optional): STP Mode (`none`, `cancel_taker`, `cancel_maker`, `cancel_both`).

        Returns:
            dict: Bitget API JSON response containing the order ID and client customized ID.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/isolated/place-order"
        body = {
            "symbol": symbol,
            "orderType": orderType,
            "loanType": loanType,
            "force": force,
            "side": side
        }
        if price:
            body["price"] = price
        if baseSize:
            body["baseSize"] = baseSize
        if quoteSize:
            body["quoteSize"] = quoteSize
        if clientOid:
            body["clientOid"] = clientOid
        if stpMode:
            body["stpMode"] = stpMode
        return await self.client._send_request("POST", request_path, body=body)

    async def isolated_batch_orders(self, symbol, orderList):
        """
        Isolated Batch Orders.

        Args:
            symbol (str): Trading pairs, BTCUSDT.
            orderList (list): Order Entries. Each item in the list should be a dictionary with the following keys:
                orderType (str): Order type (`limit` or `market`).
                loanType (str): Margin order model (`normal`, `autoLoan`, `autoRepay`, `autoLoanAndRepay`).
                force (str): Time in force (`gtc`, `post_only`, `fok`, `ioc`). Invalid when `orderType` is `market`.
                side (str): Direction (`sell` or `buy`).
                price (str, optional): Price.
                baseSize (str, optional): Limit and Market sell are required. Sell orders represent the number of baseCoins (left coin).
                quoteSize (str, optional): Market buy is required, the buy order represents the number of quote coins (right coin).
                clientOid (str, optional): Customized ID.
                stpMode (str, optional): STP Mode (`none`, `cancel_taker`, `cancel_maker`, `cancel_both`).

        Returns:
            dict: Bitget API JSON response containing lists of successful and failed orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/isolated/batch-place-order"
        body = {
            "symbol": symbol,
            "orderList": orderList
        }
        return await self.client._send_request("POST", request_path, body=body)

    async def isolated_cancel_order(self, symbol, orderId=None, clientOid=None):
        """
        Isolated Cancel Order.

        Args:
            symbol (str): Trading pairs, BTCUSDT.
            orderId (str, optional): Order ID. Either `orderId` or `clientOid` is required.
            clientOid (str, optional): Client customized ID. Either `orderId` or `clientOid` is required.

        Returns:
            dict: Bitget API JSON response containing the order ID and client customized ID of the cancelled order.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/isolated/cancel-order"
        body = {"symbol": symbol}
        if orderId:
            body["orderId"] = orderId
        if clientOid:
            body["clientOid"] = clientOid
        return await self.client._send_request("POST", request_path, body=body)

    

    async def get_isolated_current_orders(self, symbol, startTime, orderId=None, clientOid=None, endTime=None, limit=None):
        """
        Get Isolated Current Orders.

        Args:
            symbol (str): Trading pairs, BTCUSDT.
            startTime (str): Start time, Unix millisecond timestamps.
            orderId (str, optional): Order ID.
            clientOid (str, optional): Client customized ID.
            endTime (str, optional): End time, Unix millisecond timestamps.
            limit (str, optional): Number of queries. The default value is 100 entries and the maximum value is 500 entries.

        Returns:
            dict: Bitget API JSON response containing current orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/isolated/open-orders"
        params = {"symbol": symbol, "startTime": startTime}
        if orderId:
            params["orderId"] = orderId
        if clientOid:
            params["clientOid"] = clientOid
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_isolated_orders_history(self, symbol, startTime, orderId=None, enterPointSource=None, clientOid=None, endTime=None, limit=None, idLessThan=None):
        """
        Get Isolated Orders History.

        Args:
            symbol (str): Trading pairs, BTCUSDT.
            startTime (str): Start time, Unix millisecond timestamps.
            orderId (str, optional): Order ID.
            enterPointSource (str, optional): Order source (`WEB`, `API`, `SYS`, `ANDROID`, `IOS`).
            clientOid (str, optional): Client customized ID.
            endTime (str, optional): End time, Unix millisecond timestamps. Maximum interval between start and end times is 90 days.
            limit (str, optional): Number of queries. Default: 100, maximum: 500.
            idLessThan (str, optional): For turning pages. No setting is needed when first querying. Set to the smallest orderId returned from the last query when searching for data in the second page and other paged. Data smaller than the orderId entered will be returned. This is designed to shorten the query response time.

        Returns:
            dict: Bitget API JSON response containing isolated orders history.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/isolated/history-orders"
        params = {"symbol": symbol, "startTime": startTime}
        if orderId:
            params["orderId"] = orderId
        if enterPointSource:
            params["enterPointSource"] = enterPointSource
        if clientOid:
            params["clientOid"] = clientOid
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_isolated_order_fills(self, symbol, startTime, orderId=None, idLessThan=None, endTime=None, limit=None):
        """
        Get Isolated Order Fills.

        Args:
            symbol (str): Trading pairs, BTCUSDT.
            startTime (str): Start time, Unix millisecond timestamps.
            orderId (str, optional): Order ID.
            idLessThan (str, optional): Match order ID. A parameter for paging. No setting is needed when querying for the first time. Set to the smallest orderId returned from the last query when searching for data in the second page and other paged. Data smaller than the orderId entered will be returned. This is designed to shorten the query response time.
            endTime (str, optional): End time, Unix millisecond timestamps. Maximum interval between start and end times is 90 days.
            limit (str, optional): Number of queries. Default: 100, maximum: 500.

        Returns:
            dict: Bitget API JSON response containing isolated order fills.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/isolated/fills"
        params = {"symbol": symbol, "startTime": startTime}
        if orderId:
            params["orderId"] = orderId
        if idLessThan:
            params["idLessThan"] = idLessThan
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_isolated_liquidation_orders(self, type=None, symbol=None, fromCoin=None, toCoin=None, startTime=None, endTime=None, limit=None, idLessThan=None):
        """
        Get Isolated Liquidation Orders.

        Args:
            type (str, optional): Type (`swap` or `place_order`). Default is `place_order`.
            symbol (str, optional): Trading pairs, like BTCUSDT. This field only takes effect when `type=place_order`. Default all symbols.
            fromCoin (str, optional): Swap from coin. This field only takes effect when `type=swap`.
            toCoin (str, optional): Swap to coin. This field only takes effect when `type=swap`.
            startTime (str, optional): Start time, Unix millisecond timestamp.
            endTime (str, optional): End time, Unix millisecond timestamp. Maximum interval between start time and end time is 90 days.
            limit (str, optional): Number of queries. Default: 100, maximum: 500.
            idLessThan (str, optional): For turning pages. The first query is not passed. When querying data in the second page and the data beyond, the last endId returned in the last query is used, and the result will return data with a value less than this one; the query response time will be shortened.

        Returns:
            dict: Bitget API JSON response containing isolated liquidation orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/isolated/liquidation-order"
        params = {}
        if type:
            params["type"] = type
        if symbol:
            params["symbol"] = symbol
        if fromCoin:
            params["fromCoin"] = fromCoin
        if toCoin:
            params["toCoin"] = toCoin
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_isolated_account_asset(self, symbol=None):
        """
        Get Isolated Account Asset.

        Args:
            symbol (str, optional): Trading pairs, like BTCUSDT.

        Returns:
            dict: Bitget API JSON response containing isolated account assets.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/isolated/account/assets"
        params = {}
        if symbol:
            params["symbol"] = symbol
        return await self.client._send_request("GET", request_path, params=params)

    async def isolated_borrow(self, symbol, coin, borrowAmount, clientOid=None):
        """
        Isolated Borrow.

        Args:
            symbol (str): Borrowing trading pairs, like BTCUSDT.
            coin (str): Borrowing coins, such as BTC.
            borrowAmount (str): Borrowing amount (up to 8 decimal places).
            clientOid (str, optional): Client customized ID.

        Returns:
            dict: Bitget API JSON response containing loan ID, symbol, coin, and borrowed amount.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/isolated/account/borrow"
        body = {"symbol": symbol, "coin": coin, "borrowAmount": borrowAmount}
        if clientOid:
            body["clientOid"] = clientOid
        return await self.client._send_request("POST", request_path, body=body)

    async def isolated_repay(self, symbol, coin, repayAmount, clientOid=None):
        """
        Isolated Repay.

        Args:
            symbol (str): Repayment trading pairs, like BTCUSDT.
            coin (str): Repayment coin.
            repayAmount (str): Number of repayments, up to 8 decimal places.
            clientOid (str, optional): Client customized ID.

        Returns:
            dict: Bitget API JSON response containing remaining debt amount, repay ID, symbol, coin, and repayment amount.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/isolated/account/repay"
        body = {"symbol": symbol, "coin": coin, "repayAmount": repayAmount}
        if clientOid:
            body["clientOid"] = clientOid
        return await self.client._send_request("POST", request_path, body=body)

    async def get_isolated_risk_rate(self, symbol=None, pageNum=None, pageSize=None):
        """
        Get Isolated Risk Rate.

        Args:
            symbol (str, optional): Trading pairs, like BTCUSDT.
            pageNum (str, optional): Page number. Default: 1.
            pageSize (str, optional): Size per page. Default 100, maximum 500.

        Returns:
            dict: Bitget API JSON response containing isolated risk rate information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/isolated/account/risk-rate"
        params = {}
        if symbol:
            params["symbol"] = symbol
        if pageNum:
            params["pageNum"] = pageNum
        if pageSize:
            params["pageSize"] = pageSize
        return await self.client._send_request("GET", request_path, params=params)

    async def get_isolated_interest_rate_and_max_borrowable(self, symbol):
        """
        Get Isolated Interest Rate and Max Borrowable.
        This interface will determine the user's VIP level based on the User ID sending the request, and then return information such as interest rates and limits based on the VIP level.

        Args:
            symbol (str): Trading pairs, like BTCUSDT.

        Returns:
            dict: Bitget API JSON response containing isolated interest rate and max borrowable information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/isolated/interest-rate-and-limit"
        params = {"symbol": symbol}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_isolated_tier_configuration(self, symbol):
        """
        Get Isolated Tier Configuration.
        This interface will determine the user's VIP level based on the User ID sending the request, and then return the tier information based on the VIP level.

        Args:
            symbol (str): Trading pairs, like BTCUSDT.

        Returns:
            dict: Bitget API JSON response containing isolated tier configuration information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/isolated/tier-data"
        params = {"symbol": symbol}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_isolated_max_borrowable(self, symbol):
        """
        Get Isolated Max Borrowable.

        Args:
            symbol (str): Trading pairs, like BTCUSDT.

        Returns:
            dict: Bitget API JSON response containing isolated maximum borrowable amount information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/isolated/account/max-borrowable-amount"
        params = {"symbol": symbol}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_isolated_max_transferable(self, symbol):
        """
        Get Isolated Max Transferable Amount.

        Args:
            symbol (str): Trading pairs, like BTCUSDT.

        Returns:
            dict: Bitget API JSON response containing isolated maximum transferable amount information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/isolated/account/max-transfer-out-amount"
        params = {"symbol": symbol}
        return await self.client._send_request("GET", request_path, params=params)

    async def isolated_flash_repay(self, symbolList=None):
        """
        Isolated Flash Repay.

        Args:
            symbolList (list, optional): Trading pair array under isolated mode. If it is not filled, all trading pairs will be confirmed by default. Up to 100 trading pairs in one request.

        Returns:
            dict: Bitget API JSON response containing repayment ID, symbol, and result.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/isolated/account/flash-repay"
        body = {}
        if symbolList:
            body["symbolList"] = symbolList
        return await self.client._send_request("POST", request_path, body=body)

    async def query_isolated_flash_repayment_result(self, idList):
        """
        Query Isolated Flash Repayment Result.

        Args:
            idList (list): Repayment ID list under isolated mode. Up to 100 trading pairs in one request.

        Returns:
            dict: Bitget API JSON response containing repayment ID and status.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/isolated/account/query-flash-repay-status"
        body = {"idList": idList}
        return await self.client._send_request("POST", request_path, body=body)

    async def get_isolated_repay_history(self, symbol, startTime, repayId=None, coin=None, endTime=None, limit=None, idLessThan=None):
        request_path = "/api/v2/margin/isolated/repay-history"
        params = {"symbol": symbol, "startTime": startTime}
        if repayId:
            params["repayId"] = repayId
        if coin:
            params["coin"] = coin
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_support_currencies(self):
        """
        Get Support Currencies.

        Returns:
            dict: Bitget API JSON response containing supported currencies information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/currencies"
        return await self.client._send_request("GET", request_path, params={})

    async def get_the_leverage_interest_rate(self, coin):
        """
        Get the leverage interest rate.

        Args:
            coin (str): Coin.

        Returns:
            dict: Bitget API JSON response containing leverage interest rate information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/interest-rate-record"
        params = {"coin": coin}
        return await self.client._send_request("GET", request_path, params=params)