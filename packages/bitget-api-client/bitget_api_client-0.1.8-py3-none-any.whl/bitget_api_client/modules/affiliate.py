from .exceptions import BitgetAPIException

class Affiliate:
    def __init__(self, client):
        self.client = client

    async def get_agent_direct_commissions(self, startTime=None, endTime=None, idLessThan=None, limit=None, uid=None, coin=None, symbol=None):
        """
        Get Agent Direct commissions.

        Args:
            startTime (str, optional): Start time, maximum range of 90 days.
            endTime (str, optional): End time, maximum range of 90 days.
            idLessThan (str, optional): Retrieve data before this ID.
            limit (str, optional): Limit number of data (default 100, max 1000).
            uid (str, optional): UID.
            coin (str, optional): Coin, e.g: BTC.
            symbol (str, optional): Symbol e.g: BGBUSDT_SPBL `spot` BTCUSDT_SPBL-MABL `spot margin` BTCUSDT_UMCBL `USDT-Futures` BTCUSD_DMCBL `COIN-Futures` BTCPERP_CMCBL `USDC-Futures`.

        Returns:
            dict: Bitget API JSON response containing direct commissions.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/broker/v1/agent/customer-commissions"
        params = {}
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if idLessThan:
            params["idLessThan"] = idLessThan
        if limit:
            params["limit"] = limit
        if uid:
            params["uid"] = uid
        if coin:
            params["coin"] = coin
        if symbol:
            params["symbol"] = symbol
        
        return await self.client._send_request("GET", request_path, params=params)

    async def get_agent_customer_trade_volume_list(self, startTime=None, endTime=None, pageNo=None, pageSize=None, uid=None):
        """
        Get Agent Customer Trade Volume List.

        Args:
            startTime (str, optional): Start time (ms).
            endTime (str, optional): End time (ms).
            pageNo (str, optional): Page number.
            pageSize (str, optional): Page size, 100 default, Max 1000.
            uid (str, optional): UID.

        Returns:
            dict: Bitget API JSON response containing customer trade volume list.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/broker/v1/agent/customerTradeVolumnList"
        body = {}
        if startTime:
            body["startTime"] = startTime
        if endTime:
            body["endTime"] = endTime
        if pageNo:
            body["pageNo"] = pageNo
        if pageSize:
            body["pageSize"] = pageSize
        if uid:
            body["uid"] = uid

        return await self.client._send_request("POST", request_path, body=body)

    async def get_agent_customer_list(self, startTime=None, endTime=None, pageNo=None, pageSize=None, uid=None, referralCode=None):
        """
        Get Agent Customer List.

        Args:
            startTime (str, optional): Start time (ms).
            endTime (str, optional): End time (ms).
            pageNo (str, optional): Page number.
            pageSize (str, optional): Page size, 100 default, Max 1000.
            uid (str, optional): UID.
            referralCode (str, optional): Referral code.

        Returns:
            dict: Bitget API JSON response containing customer list.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/broker/v1/agent/customerList"
        body = {}
        if startTime:
            body["startTime"] = startTime
        if endTime:
            body["endTime"] = endTime
        if pageNo:
            body["pageNo"] = pageNo
        if pageSize:
            body["pageSize"] = pageSize
        if uid:
            body["uid"] = uid
        if referralCode:
            body["referralCode"] = referralCode

        return await self.client._send_request("POST", request_path, body=body)

    async def get_agent_customer_kyc_result(self, startTime=None, endTime=None, pageNo=None, pageSize=None, uid=None):
        """
        Get Agent Customer Kyc Result.

        Args:
            startTime (str, optional): Start time, maximum range of 90 days.
            endTime (str, optional): End time, maximum range of 90 days.
            pageNo (str, optional): Page number.
            pageSize (str, optional): Page size, 100 default, Max 1000.
            uid (str, optional): UID.

        Returns:
            dict: Bitget API JSON response containing customer KYC result.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/broker/v1/agent/customer-kyc-result"
        params = {}
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if pageNo:
            params["pageNo"] = pageNo
        if pageSize:
            params["pageSize"] = pageSize
        if uid:
            params["uid"] = uid

        return await self.client._send_request("GET", request_path, params=params)

    async def get_agent_customer_deposit_list(self, startTime=None, endTime=None, pageNo=None, pageSize=None, uid=None):
        """
        Get Agent Customer Deposit List.

        Args:
            startTime (str, optional): Start time (ms).
            endTime (str, optional): End time (ms).
            pageNo (str, optional): Page number.
            pageSize (str, optional): Page size, 100 default, Max 1000.
            uid (str, optional): UID.

        Returns:
            dict: Bitget API JSON response containing customer deposit list.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/broker/v1/agent/customerDepositList"
        body = {}
        if startTime:
            body["startTime"] = startTime
        if endTime:
            body["endTime"] = endTime
        if pageNo:
            body["pageNo"] = pageNo
        if pageSize:
            body["pageSize"] = pageSize
        if uid:
            body["uid"] = uid

        return await self.client._send_request("POST", request_path, body=body)

    async def get_agent_customer_assets_list(self, pageNo=None, pageSize=None, uid=None):
        """
        Get Agent Customer Assets List.

        Args:
            pageNo (str, optional): Page number.
            pageSize (str, optional): Page size, 100 default, Max 1000.
            uid (str, optional): UID.

        Returns:
            dict: Bitget API JSON response containing customer assets list.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/broker/v1/agent/customerAccountAssetsList"
        body = {}
        if pageNo:
            body["pageNo"] = pageNo
        if pageSize:
            body["pageSize"] = pageSize
        if uid:
            body["uid"] = uid

        return await self.client._send_request("POST", request_path, body=body)

    async def get_agent_commission_detail(self, startTime=None, endTime=None, limit=None, idLessThan=None):
        """
        Get Agent Commission Detail.

        Args:
            startTime (str, optional): Start time Unix millisecond timestamp.
            endTime (str, optional): End time Unix millisecond timestamp.
            limit (str, optional): max:100, default: 100.
            idLessThan (str, optional): Requests the content on the page before this ID (older data), the value input should be the endld of the corresponding interface.

        Returns:
            dict: Bitget API JSON response containing agent commission details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/broker/v1/agent/commission-distribution"
        params = {}
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)