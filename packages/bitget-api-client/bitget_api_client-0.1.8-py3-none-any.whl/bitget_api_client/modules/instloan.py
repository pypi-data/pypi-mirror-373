from .exceptions import BitgetAPIException

class Instloan:
    def __init__(self, client):
        self.client = client

    async def bind_unbind_sub_account_uid_to_risk_unit(self, uid, operate, riskUnitId=None):
        """
        Bind/Unbind Sub-account UID to Risk Unit.

        Args:
            uid (str): Sub UID (limit 50 UIDS for one Risk Unit).
            operate (str): `bind` Bind or `unbind` Unbind.
            riskUnitId (str, optional): Risk Unit ID (Required for parent account calls, not required for risk unit account calls).

        Returns:
            dict: Bitget API JSON response. The `data` field will be "success" on success.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/ins-loan/bind-uid"
        body = {
            "uid": uid,
            "operate": operate
        }
        if riskUnitId:
            body["riskUnitId"] = riskUnitId
        return await self.client._send_request("POST", request_path, body=body)

    async def get_loan_orders(self, orderId=None, startTime=None, endTime=None):
        """
        Get Loan Orders.

        Args:
            orderId (str, optional): Loan order ID. If not passed, then return all orders, sort by loanTime in descend.
            startTime (str, optional): The start timestamp (ms). The maximum time span supported is 30 days. If the start time is not provided, it defaults to the current time minus 30 days.
            endTime (str, optional): The end timestamp (ms). The maximum time span supported is 30 days. If the end time is not provided, the default end time is 30 days from the start.

        Returns:
            dict: Bitget API JSON response containing loan orders information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/ins-loan/loan-order"
        params = {}
        if orderId:
            params["orderId"] = orderId
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        return await self.client._send_request("GET", request_path, params=params)

    async def get_ltv(self, riskUnitId=None):
        """
        Get LTV (Loan-to-Value).

        Args:
            riskUnitId (str, optional): Risk Sub-unit ID (Required for parent account calls, not required for risk sub-unit account calls).

        Returns:
            dict: Bitget API JSON response containing LTV and risk unit information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/ins-loan/ltv-convert"
        params = {}
        if riskUnitId:
            params["riskUnitId"] = riskUnitId
        return await self.client._send_request("GET", request_path, params=params)

    async def get_margin_coin_info(self, productId):
        """
        Get Margin Coin Info.

        Args:
            productId (str): Product ID.

        Returns:
            dict: Bitget API JSON response containing margin coin information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/ins-loan/ensure-coins-convert"
        params = {"productId": productId}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_product_info(self, productId):
        """
        Get Product Info.

        Args:
            productId (str): Product ID.

        Returns:
            dict: Bitget API JSON response containing product information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/ins-loan/product-infos"
        params = {"productId": productId}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_repayment_orders(self, startTime=None, endTime=None, limit=None):
        """
        Get Repayment Orders.

        Args:
            startTime (str, optional): The start timestamp (ms).
            endTime (str, optional): The end timestamp (ms).
            limit (str, optional): Limit default 100; max 100.

        Returns:
            dict: Bitget API JSON response containing repayment orders information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/ins-loan/repaid-history"
        params = {}
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_risk_unit(self):
        """
        Get Risk Unit.
        Only the parent account API Key can use this endpoint.

        Returns:
            dict: Bitget API JSON response containing Risk Unit IDs.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/ins-loan/risk-unit"
        return await self.client._send_request("GET", request_path, params={})

    async def get_spot_symbols(self, productId):
        """
        Get Spot Symbols.

        Args:
            productId (str): Product ID.

        Returns:
            dict: Bitget API JSON response containing spot trading pairs.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/ins-loan/symbols"
        params = {"productId": productId}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_transferable_amount(self, coin, userId=None):
        """
        Get transferable amount.

        Args:
            coin (str): Coin name.
            userId (str, optional): User ID (Master account or sub-accounts).

        Returns:
            dict: Bitget API JSON response containing transferable amount information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/ins-loan/transfered"
        params = {
            "coin": coin
        }
        if userId:
            params["userId"] = userId
        return await self.client._send_request("GET", request_path, params=params)