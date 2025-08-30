from .exceptions import BitgetAPIException

class Earn:
    def __init__(self, client):
        self.client = client

    def borrow(self, loanCoin, pledgeCoin, daily, pledgeAmount=None, loanAmount=None):
        """
        Borrow coin.

        Args:
            loanCoin (str): Coin to loan, e.g. `ETH`.
            pledgeCoin (str): Pledge coin (Collateral), e.g. `USDT`.
            daily (str): Mortgage term: `SEVEN` (7 days), `THIRTY` (30 days), `FLEXIBLE` (Flexible).
            pledgeAmount (str, optional): Pledge (Collateral) amount. `pledgeAmount` and `loanAmount` must send one.
            loanAmount (str, optional): Loan amount. `pledgeAmount` and `loanAmount` must send one.

        Returns:
            dict: Bitget API JSON response containing order ID.

        Raises:
            ValueError: If neither `pledgeAmount` nor `loanAmount` is provided.
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/earn/loan/borrow"
        body = {
            "loanCoin": loanCoin,
            "pledgeCoin": pledgeCoin,
            "daily": daily
        }
        if pledgeAmount:
            body["pledgeAmount"] = pledgeAmount
        if loanAmount:
            body["loanAmount"] = loanAmount
        
        # Ensure either pledgeAmount or loanAmount is provided
        if pledgeAmount is None and loanAmount is None:
            raise ValueError("Either 'pledgeAmount' or 'loanAmount' must be provided.")

        return self.client._send_request("POST", request_path, body=body)

    def get_earn_account_assets(self, coin=None):
        """
        Earn account overview.

        Args:
            coin (str, optional): Assets coin.

        Returns:
            dict: Bitget API JSON response containing Earn account assets.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/earn/account/assets"
        params = {}
        if coin:
            params["coin"] = coin
        return self.client._send_request("GET", request_path, params=params)

    def get_currency_list(self, coin=None):
        """
        Get loan-able currency list.

        Args:
            coin (str, optional): Coin, e.g. `BTC`.

        Returns:
            dict: Bitget API JSON response containing currency list.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/earn/loan/public/coinInfos"
        params = {}
        if coin:
            params["coin"] = coin
        return self.client._send_request("GET", request_path, params=params)

    def get_debts(self):
        """
        Get the list of repay history.

        Returns:
            dict: Bitget API JSON response containing debt list.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/earn/loan/debts"
        return self.client._send_request("GET", request_path, params={})

    def get_est_interest_and_borrowable(self, loanCoin, pledgeCoin, daily, pledgeAmount):
        """
        Get Est. hourly interest rate and Borrowable amount.

        Args:
            loanCoin (str): Coin to loan, e.g. `BTC`.
            pledgeCoin (str): Collateral coin, e.g. `ETH`.
            daily (str): Mortgage term: `SEVEN` (7 days), `THIRTY` (30 days), `FLEXIBLE` (Flexible).
            pledgeAmount (str): Pledge amount.

        Returns:
            dict: Bitget API JSON response containing estimated interest and borrowable amount.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/earn/loan/public/hour-interest"
        params = {
            "loanCoin": loanCoin,
            "pledgeCoin": pledgeCoin,
            "daily": daily,
            "pledgeAmount": pledgeAmount
        }
        return self.client._send_request("GET", request_path, params=params)

    def get_liquidation_records(self, startTime, endTime, orderId=None, loanCoin=None, pledgeCoin=None, status=None, pageNo=None, pageSize=None):
        """
        Get the list of repay history.

        Args:
            startTime (str): Start time, ms, only supports querying the data of the past three months.
            endTime (str): End time, ms.
            orderId (str, optional): Order ID.
            loanCoin (str, optional): Loan coin.
            pledgeCoin (str, optional): Pledge (Collateral) coin.
            status (str, optional): Status: `COMPLETE` (completed liquidation) or `WAIT` (liquidating).
            pageNo (str, optional): Page No, default 1.
            pageSize (str, optional): Page size, default 10, max 100.

        Returns:
            dict: Bitget API JSON response containing liquidation records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/earn/loan/reduces"
        params = {
            "startTime": startTime,
            "endTime": endTime
        }
        if orderId:
            params["orderId"] = orderId
        if loanCoin:
            params["loanCoin"] = loanCoin
        if pledgeCoin:
            params["pledgeCoin"] = pledgeCoin
        if status:
            params["status"] = status
        if pageNo:
            params["pageNo"] = pageNo
        if pageSize:
            params["pageSize"] = pageSize
        return self.client._send_request("GET", request_path, params=params)

    def get_loan_history(self, startTime, endTime, orderId=None, loanCoin=None, pledgeCoin=None, status=None, pageNo=None, pageSize=None):
        """
        Get the list of loan history.

        Args:
            startTime (str): Start time, ms, only supports querying the data of the past three months.
            endTime (str): End time, ms.
            orderId (str, optional): Order ID.
            loanCoin (str, optional): Loan coin.
            pledgeCoin (str, optional): Pledge (Collateral) coin.
            status (str, optional): Status: `ROLLBACK` (failure), `FORCE` (force liquidation), `REPAY` (already repaid).
            pageNo (str, optional): Page No, default 1.
            pageSize (str, optional): Page size default 10, max 100.

        Returns:
            dict: Bitget API JSON response containing loan history.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/earn/loan/borrow-history"
        params = {
            "startTime": startTime,
            "endTime": endTime
        }
        if orderId:
            params["orderId"] = orderId
        if loanCoin:
            params["loanCoin"] = loanCoin
        if pledgeCoin:
            params["pledgeCoin"] = pledgeCoin
        if status:
            params["status"] = status
        if pageNo:
            params["pageNo"] = pageNo
        if pageSize:
            params["pageSize"] = pageSize
        return self.client._send_request("GET", request_path, params=params)

    def get_loan_orders(self, orderId=None, loanCoin=None, pledgeCoin=None):
        """
        Get on-going loan orders.

        Args:
            orderId (str, optional): Order ID.
            loanCoin (str, optional): Coin to loan.
            pledgeCoin (str, optional): Pledge (Collateral) coin.

        Returns:
            dict: Bitget API JSON response containing loan orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/earn/loan/ongoing-orders"
        params = {}
        if orderId:
            params["orderId"] = orderId
        if loanCoin:
            params["loanCoin"] = loanCoin
        if pledgeCoin:
            params["pledgeCoin"] = pledgeCoin
        return self.client._send_request("GET", request_path, params=params)

    def get_pledge_rate_history(self, startTime, endTime, orderId=None, reviseSide=None, pledgeCoin=None, pageNo=None, pageSize=None):
        """
        Get pledge rate history.

        Args:
            startTime (str): Start time, ms, only supports querying the data of the past three months.
            endTime (str): End time, ms.
            orderId (str, optional): Order ID.
            reviseSide (str, optional): Revise side: `down` (supplement collateral to turn down) or `up` (withdraw collateral to turn up).
            pledgeCoin (str, optional): Pledge (Collateral) coin.
            pageNo (str, optional): Page No, default 1.
            pageSize (str, optional): Page size default 10, max 100.

        Returns:
            dict: Bitget API JSON response containing pledge rate history.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/earn/loan/revise-history"
        params = {
            "startTime": startTime,
            "endTime": endTime
        }
        if orderId:
            params["orderId"] = orderId
        if reviseSide:
            params["reviseSide"] = reviseSide
        if pledgeCoin:
            params["pledgeCoin"] = pledgeCoin
        if pageNo:
            params["pageNo"] = pageNo
        if pageSize:
            params["pageSize"] = pageSize
        return self.client._send_request("GET", request_path, params=params)

    def get_repay_history(self, startTime, endTime, orderId=None, loanCoin=None, pledgeCoin=None, pageNo=None, pageSize=None):
        """
        Get the list of repay history.

        Args:
            startTime (str): Start time, ms, only supports querying the data of the past three months.
            endTime (str): End time, ms.
            orderId (str, optional): Order ID.
            loanCoin (str, optional): Loan coin.
            pledgeCoin (str, optional): Pledge (Collateral) coin.
            pageNo (str, optional): Page No default 1.
            pageSize (str, optional): Page size default 10, max 100.

        Returns:
            dict: Bitget API JSON response containing repay history.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/earn/loan/repay-history"
        params = {
            "startTime": startTime,
            "endTime": endTime
        }
        if orderId:
            params["orderId"] = orderId
        if loanCoin:
            params["loanCoin"] = loanCoin
        if pledgeCoin:
            params["pledgeCoin"] = pledgeCoin
        if pageNo:
            params["pageNo"] = pageNo
        if pageSize:
            params["pageSize"] = pageSize
        return self.client._send_request("GET", request_path, params=params)

    def modify_pledge_rate(self, orderId, amount, pledgeCoin, reviseType):
        """
        Withdraw or supplement collateral.

        Args:
            orderId (str): Order ID.
            amount (str): Amount to withdraw or supplement.
            pledgeCoin (str): Pledge (Collateral) coin.
            reviseType (str): Repay Type: `OUT` (Withdraw collateral) or `IN` (supplement collateral).

        Returns:
            dict: Bitget API JSON response containing loan and pledge coin details and adjusted pledge rate.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/earn/loan/revise-pledge"
        body = {
            "orderId": orderId,
            "amount": amount,
            "pledgeCoin": pledgeCoin,
            "reviseType": reviseType
        }
        return self.client._send_request("POST", request_path, body=body)

    def redeem_savings(self, productId, periodType, amount, orderId=None):
        """
        Redeem savings.
        The interval of each redeem should be more than 1min, or it would return error.

        Args:
            productId (str): Product ID.
            periodType (str): Period type: `flexible` (flexible period) or `fixed` (fixed period).
            amount (str): Subscribe amount.
            orderId (str, optional): Assets Order ID. Get this for `/assets` orderId.

        Returns:
            dict: Bitget API JSON response containing redemption order ID and status.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/earn/savings/redeem"
        body = {
            "productId": productId,
            "periodType": periodType,
            "amount": amount
        }
        if orderId:
            body["orderId"] = orderId
        return self.client._send_request("POST", request_path, body=body)

    def repay(self, orderId, repayAll, amount=None, repayUnlock=None):
        """
        Repay.

        Args:
            orderId (str): Order ID.
            repayAll (str): Repay all: `yes` or `no`.
            amount (str, optional): When `repayAll`=`no`: Repay amount.
            repayUnlock (str, optional): Whether redeem after repay, default: `yes`. `yes` or `no`.

        Returns:
            dict: Bitget API JSON response containing repayment details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/earn/loan/repay"
        body = {
            "orderId": orderId,
            "repayAll": repayAll
        }
        if amount:
            body["amount"] = amount
        if repayUnlock:
            body["repayUnlock"] = repayUnlock
        return self.client._send_request("POST", request_path, body=body)

    def get_savings_account(self):
        """
        Get savings account info.

        Returns:
            dict: Bitget API JSON response containing savings account information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/earn/savings/account"
        return self.client._send_request("GET", request_path, params={})

    def get_savings_product_list(self, coin=None, filter=None):
        """
        Get Savings Product List.

        Args:
            coin (str, optional): Coin, e.g. `BTC`.
            filter (str, optional): Filter conditions: `available` (Available for subscription), `held` (Held), `available_and_held` (Available for subscription and held), `all` (Query all, including those that have been removed from the shelves).

        Returns:
            dict: Bitget API JSON response containing savings product list.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/earn/savings/product"
        params = {}
        if coin:
            params["coin"] = coin
        if filter:
            params["filter"] = filter
        return self.client._send_request("GET", request_path, params=params)

    def get_savings_records(self, periodType, coin=None, orderType=None, startTime=None, endTime=None, limit=None, idLessThan=None):
        """
        Get savings records.

        Args:
            periodType (str): Period type: `flexible` (flexible current) or `fixed` (fixed term).
            coin (str, optional): Subscribe coin.
            orderType (str, optional): Record type: `subscribe` (subscription), `redeem` (redemption), `pay_interest` (interest payment), `deduction` (penalty interest, only supports regular periods).
            startTime (str, optional): Start timestamp (Copy trade creation time). Milliseconds format of timestamp Unix. The maximum time span supported is three months. The default end time is three months if no value is set for the end time.
            endTime (str, optional): End timestamp (Copy trade creation time). Milliseconds format of timestamp Unix. The maximum time span supported is three months. The default start time is three months ago if no value is set for the start time.
            limit (str, optional): Number of queries: Default: 20, maximum: 100.
            idLessThan (str, optional): Separate page content before this ID is requested (older data), and the value input should be the end ID of the last request.

        Returns:
            dict: Bitget API JSON response containing savings records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/earn/savings/records"
        params = {
            "periodType": periodType
        }
        if coin:
            params["coin"] = coin
        if orderType:
            params["orderType"] = orderType
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return self.client._send_request("GET", request_path, params=params)

    def get_savings_subscription_detail(self, productId, periodType):
        """
        Get subscription detail before subscribe savings.

        Args:
            productId (str): Product ID.
            periodType (str): Period type: `flexible` (flexible period) or `fixed` (fixed period).

        Returns:
            dict: Bitget API JSON response containing savings subscription details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/earn/savings/subscribe-info"
        params = {
            "productId": productId,
            "periodType": periodType
        }
        return self.client._send_request("GET", request_path, params=params)

    def get_savings_subscription_result(self, productId, periodType):
        """
        Get savings subscription info.

        Args:
            productId (str): Product ID.
            periodType (str): Period type: `flexible` (flexible period) or `fixed` (fixed period).

        Returns:
            dict: Bitget API JSON response containing savings subscription result.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/earn/savings/subscribe-result"
        params = {
            "productId": productId,
            "periodType": periodType
        }
        return self.client._send_request("GET", request_path, params=params)

    def get_savings_redemption_results(self, orderId, periodType):
        """
        Get savings redeem result.

        Args:
            orderId (str): Subscription order ID.
            periodType (str): Period type: `flexible` (flexible current) or `fixed` (fixed term).

        Returns:
            dict: Bitget API JSON response containing savings redemption result.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/earn/savings/redeem-result"
        params = {
            "orderId": orderId,
            "periodType": periodType
        }
        return self.client._send_request("GET", request_path, params=params)

    def get_sharkfin_account(self):
        """
        Get sharkfin account info.

        Returns:
            dict: Bitget API JSON response containing sharkfin account information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/earn/sharkfin/account"
        return self.client._send_request("GET", request_path, params={})

    def get_sharkfin_assets(self, status, startTime=None, endTime=None, limit=None, idLessThan=None):
        """
        Get sharkfin assets.

        Args:
            status (str): Shark status: `subscribed` (Subscribed, default) or `settled` (Settled).
            startTime (str, optional): Start timestamp (Sharkfin creation time). Milliseconds format of timestamp Unix. The maximum time span supported is three months. The default start time is three months ago if no value is set for the start time.
            endTime (str, optional): End timestamp (Sharkfin creation time). Milliseconds format of timestamp Unix. The maximum time span supported is three months. The default end time is now if no value is set for the end time.
            limit (str, optional): Number of queries: Default: 20, maximum: 100.
            idLessThan (str, optional): Separate page content before this ID is requested (older data), and the value input should be the end ID of the last request.

        Returns:
            dict: Bitget API JSON response containing sharkfin assets.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/earn/sharkfin/assets"
        params = {
            "status": status
        }
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return self.client._send_request("GET", request_path, params=params)

    def get_sharkfin_products(self, coin, limit=None, idLessThan=None):
        """
        Get sharkfin products.

        Args:
            coin (str): Shark coin.
            limit (str, optional): Number of queries: Default: 20, maximum: 100.
            idLessThan (str, optional): Separate page content before this ID is requested (older data), and the value input should be the end ID of the last request.

        Returns:
            dict: Bitget API JSON response containing sharkfin product list info.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/earn/sharkfin/product"
        params = {
            "coin": coin
        }
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return self.client._send_request("GET", request_path, params=params)

    def get_sharkfin_subscription_result(self, orderId):
        """
        Get sharkfin subscription result.

        Args:
            orderId (str): Order ID.

        Returns:
            dict: Bitget API JSON response containing sharkfin subscription result.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/earn/sharkfin/subscribe-result"
        params = {
            "orderId": orderId
        }
        return self.client._send_request("GET", request_path, params=params)

    def subscribe_savings(self, productId, periodType, amount):
        """
        Subscribe savings.

        Args:
            productId (str): Product ID.
            periodType (str): Period type: `flexible` (flexible period) or `fixed` (fixed period).
            amount (str): Subscribe amount.

        Returns:
            dict: Bitget API JSON response containing successful subscription order ID.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/earn/savings/subscribe"
        body = {
            "productId": productId,
            "periodType": periodType,
            "amount": amount
        }
        return self.client._send_request("POST", request_path, body=body)

    def subscribe_sharkfin(self, productId, amount):
        """
        Subscribe sharkfin.

        Args:
            productId (str): Product ID.
            amount (str): Subscription amount.

        Returns:
            dict: Bitget API JSON response containing order ID and status.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/earn/sharkfin/subscribe"
        body = {
            "productId": productId,
            "amount": amount
        }
        return self.client._send_request("POST", request_path, body=body)

    def get_sharkfin_records(self, type, coin=None, startTime=None, endTime=None, limit=None, idLessThan=None):
        """
        Get sharkfin records.

        Args:
            type (str): Transaction type: `subscription` (subscription), `redemption`, `interest` (interest payment).
            coin (str, optional): Subscribe coin.
            startTime (str, optional): Start timestamp (Copy trade creation time). Milliseconds format of timestamp Unix. The maximum time span supported is three months. The default start time is three months ago if no value is set for the start time.
            endTime (str, optional): End timestamp (Copy trade creation time). Milliseconds format of timestamp Unix. The maximum time span supported is three months. The default end time is now if no value is set for the end time.
            limit (str, optional): Number of queries: Default: 20, maximum: 100.
            idLessThan (str, optional): Separate page content before this ID is requested (older data), and the value input should be the end ID of the last request.

        Returns:
            dict: Bitget API JSON response containing sharkfin records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/earn/sharkfin/records"
        params = {
            "type": type
        }
        if coin:
            params["coin"] = coin
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return self.client._send_request("GET", request_path, params=params)

    def get_sharkfin_subscription_detail(self, productId):
        """
        Get subscription detail before subscribe sharkfin.

        Args:
            productId (str): Product ID.

        Returns:
            dict: Bitget API JSON response containing sharkfin subscription details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/earn/sharkfin/subscribe-info"
        params = {
            "productId": productId
        }
        return self.client._send_request("GET", request_path, params=params)

    def get_savings_assets(self, periodType, startTime=None, endTime=None, limit=None, idLessThan=None):
        """
        Get savings assets.

        Args:
            periodType (str): Period type: `flexible` (flexible demand deposit) or `fixed` (fixed time deposit).
            startTime (str, optional): Start timestamp (Savings creation time). Milliseconds format of timestamp Unix. The maximum time span supported is three months. The default start time is three months ago if no value is set for the start time.
            endTime (str, optional): End timestamp (Savings creation time). Milliseconds format of timestamp Unix. The maximum time span supported is three months. The default end time is now if no value is set for the end time.
            limit (str, optional): Number of queries: Default: 20, maximum: 100.
            idLessThan (str, optional): Separate page content before this ID is requested (older data), and the value input should be the end ID of the last request.

        Returns:
            dict: Bitget API JSON response containing savings assets list.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/earn/savings/assets"
        params = {
            "periodType": periodType
        }
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return self.client._send_request("GET", request_path, params=params)