from .exceptions import BitgetAPIException

class Common:
    def __init__(self, client):
        self.client = client

    async def get_assets_overview(self):
        """
        Get assets overview.

        Returns:
            dict: Bitget API JSON response containing assets overview.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/account/all-account-balance"
        return await self.client._send_request("GET", request_path, params={})

    async def get_bot_account_assets(self, accountType=None):
        """
        Get bot account assets.

        Args:
            accountType (str, optional): Bot account type: `futures` or `spot`.

        Returns:
            dict: Bitget API JSON response containing bot account assets.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/account/bot-assets"
        params = {}
        if accountType:
            params["accountType"] = accountType
        return await self.client._send_request("GET", request_path, params=params)

    async def get_funding_assets(self, coin=None):
        """
        Get funding assets.

        Args:
            coin (str, optional): Default all coin.

        Returns:
            dict: Bitget API JSON response containing funding assets.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/account/funding-assets"
        params = {}
        if coin:
            params["coin"] = coin
        return await self.client._send_request("GET", request_path, params=params)

    async def batch_create_virtual_subaccount_and_apikey(self, subaccounts):
        """
        Create the virtual sub-account and apikey in batch.

        Args:
            subaccounts (list): A list of dictionaries, where each dictionary represents a subaccount to create.
                Each dictionary should contain:
                - subAccountName (str): Virtual sub-account alias (8-character English letters).
                - passphrase (str): Passcode (English letters of 8-32 characters + numbers).
                - label (str): Sub-account note (Length 20).
                - ipList (list[str], optional): Virtual sub-account ApiKey IP whitelist (Max. 30).
                - permList (list[str], optional): Sub-account permissions: `spot_trade` (Spot trade), `margin_trade` (Spot Margin trade), `contract_trade` (Futures trade read-write), `read` (Read permissions).

        Returns:
            dict: Bitget API JSON response containing details of created subaccounts and API keys.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/user/batch-create-subaccount-and-apikey"
        return await self.client._send_request("POST", request_path, body=subaccounts)

    async def get_bgb_convert_coins(self):
        """
        Get a list of Convert Bgb Currencies.

        Returns:
            dict: Bitget API JSON response containing BGB convert coins.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/market/bgb-convert-coins"
        return await self.client._send_request("GET", request_path, params={})

    async def convert(self, fromCoin, fromCoinSize, cnvtPrice, toCoin, toCoinSize, traceId):
        """
        Convert.

        Args:
            fromCoin (str): Quote currency.
            fromCoinSize (str): Number of currencies.
            cnvtPrice (str): Results obtained by request for quotation.
            toCoin (str): Target currency.
            toCoinSize (str): Number of target currencies converted.
            traceId (str): RFQ id, valid for 8 seconds.

        Returns:
            dict: Bitget API JSON response containing conversion details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/convert/trade"
        body = {
            "fromCoin": fromCoin,
            "fromCoinSize": fromCoinSize,
            "cnvtPrice": cnvtPrice,
            "toCoin": toCoin,
            "toCoinSize": toCoinSize,
            "traceId": traceId
        }
        return await self.client._send_request("POST", request_path, body=body)

    async def convert_bgb(self, coinList):
        """
        Convert BGB.

        Args:
            coinList (list[str]): List of coins to swap.

        Returns:
            dict: Bitget API JSON response containing BGB conversion details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/convert/bgb-convert"
        body = {"coinList": coinList}
        return await self.client._send_request("POST", request_path, body=body)

    async def create_virtual_subaccount(self, subAccountList):
        """
        Create virtual sub-accounts in batch. (Requires API key binding IP address).

        Args:
            subAccountList (list[str]): List of virtual aliases (8-character English letters, globally unique).

        Returns:
            dict: Bitget API JSON response containing details of successful and failed subaccount creations.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/user/create-virtual-subaccount"
        body = {"subAccountList": subAccountList}
        return await self.client._send_request("POST", request_path, body=body)

    async def create_virtual_subaccount_apikey(self, subAccountUid, passphrase, label, permType, ipList=None, permList=None):
        """
        Create the virtual sub-account apikey. Only supports API Key calls from the main account, and the API Key needs to be bound to an IP address.

        Args:
            subAccountUid (str): Sub-account uid.
            passphrase (str): Passcode (English letters of 8-32 characters + numbers).
            label (str): Note (Length 20).
            permType (str): Permission type.
            ipList (list[str], optional): IP whitelist (Up to 30, if not then ip whitelist is set to empty).
            permList (list[str], optional): Sub-account permissions: `spot_trade` (Spot trade), `margin_trade` (Spot Margin trade), `contract_trade` (Futures trade read-write), `transfer` (Wallet transfer), `read` (Read permissions).

        Returns:
            dict: Bitget API JSON response containing virtual subaccount API key details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/user/create-virtual-subaccount-apikey"
        body = {
            "subAccountUid": subAccountUid,
            "passphrase": passphrase,
            "label": label,
            "permType": permType
        }
        if ipList:
            body["ipList"] = ipList
        if permList:
            body["permList"] = permList
        return await self.client._send_request("POST", request_path, body=body)

    async def get_convert_history(self, startTime=None, endTime=None, limit=None, idLessThan=None):
        """
        Get Convert History.

        Args:
            startTime (str): Start time, Unix millisecond timestamps.
            endTime (str): End time, Unix millisecond timestamps. The maximum interval between startTime and endTime is 90 days.
            limit (str, optional): Default 20 Maximum 100.
            idLessThan (str, optional): ID of the last record endId.

        Returns:
            dict: Bitget API JSON response containing convert history.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/convert/record"
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

    async def get_futures_transaction_records(self, startTime, endTime, productType=None, marginCoin=None, limit=None, idLessThan=None):
        """
        Get futures transaction records.

        Args:
            startTime (str): Start time (time stamp in milliseconds).
            endTime (str): The maximum interval between startTime and endTime (time stamp in milliseconds) is 30 days.
            productType (str, optional): Product type: `USDT-FUTURES` (USDT professional futures), `COIN-FUTURES` (Mixed futures), `USDC-FUTURES` (USDC professional futures). Default `USDT-FUTURES`.
            marginCoin (str, optional): Default all margin coin.
            limit (str, optional): Default: 500, maximum: 500.
            idLessThan (str, optional): The last recorded ID.

        Returns:
            dict: Bitget API JSON response containing futures transaction records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/tax/future-record"
        params = {"startTime": startTime, "endTime": endTime}
        if productType:
            params["productType"] = productType
        if marginCoin:
            params["marginCoin"] = marginCoin
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_margin_transaction_history(self, startTime, endTime, marginType=None, coin=None, limit=None, idLessThan=None):
        """
        Get margin transaction records.

        Args:
            startTime (str): Start time (time stamp in milliseconds).
            endTime (str): The maximum interval between startTime and endTime (time stamp in milliseconds) is 30 days.
            marginType (str, optional): Leverage type: `isolated` (Isolated margin) or `crossed` (Cross margin, default).
            coin (str, optional): Default all coin type.
            limit (str, optional): Default: 500, maximum: 500.
            idLessThan (str, optional): The last recorded ID.

        Returns:
            dict: Bitget API JSON response containing margin transaction history.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/tax/margin-record"
        params = {"startTime": startTime, "endTime": endTime}
        if marginType:
            params["marginType"] = marginType
        if coin:
            params["coin"] = coin
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_p2p_transaction_records(self, startTime, endTime, coin=None, limit=None, idLessThan=None):
        """
        Get P2P transaction records.

        Args:
            startTime (str): Start time (time stamp in milliseconds).
            endTime (str): The maximum interval between startTime and endTime (time stamp in milliseconds) is 30 days.
            coin (str, optional): Default all coin type.
            limit (str, optional): Default: 500, maximum: 500.
            idLessThan (str, optional): The last recorded ID.

        Returns:
            dict: Bitget API JSON response containing P2P transaction records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/tax/p2p-record"
        params = {"startTime": startTime, "endTime": endTime}
        if coin:
            params["coin"] = coin
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def query_announcements(self, language, annType=None, startTime=None, endTime=None, cursor=None, limit=None):
        """
        Search for announcements within one month.

        Args:
            language (str): Language type: `zh_CN` (Chinese), `en_US` (English). Returns English if the language chosen is not supported.
            annType (str, optional): Announcement type: `latest_news` (Latest events), `coin_listings` (New coin listings), `product_updates` (Product update), `security` (Security), `api_trading` (Api trading), `maintenance_system_updates` (maintenance/system upgrades), `symbol_delisting` (Delisting information).
            startTime (str, optional): Start time of the query, Unix millisecond timestamp, e.g. 1690196141868. Search by announcement time.
            endTime (str, optional): End time of the query, Unix millisecond timestamp, e.g. 1690196141868. Search by announcement time.
            cursor (str, optional): Cursor ID. It is not required for the first call. For subsequent calls, pass the last annId in the previous response.
            limit (str, optional): Number of entries per page. By default, it is 10 entries, and the maximum is 10 entries.

        Returns:
            dict: Bitget API JSON response containing announcements.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/public/annoucements"
        params = {"language": language}
        if annType:
            params["annType"] = annType
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if cursor:
            params["cursor"] = cursor
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_spot_transaction_records(self, startTime, endTime, coin=None, limit=None, idLessThan=None):
        """
        Get spot transaction records.

        Args:
            startTime (str): Start time, Unix millisecond timestamps.
            endTime (str): The maximum interval between startTime and endTime (time stamp in milliseconds) is 30 days.
            coin (str, optional): Default all coin type.
            limit (str, optional): Default: 500, maximum: 500.
            idLessThan (str, optional): The last recorded ID.

        Returns:
            dict: Bitget API JSON response containing spot transaction records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/tax/spot-record"
        params = {"startTime": startTime, "endTime": endTime}
        if coin:
            params["coin"] = coin
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_business_line_all_symbol_trade_rate(self, symbol, businessType):
        """
        Get Trade Rate for all symbols in a business line.

        Args:
            symbol (str): Trading pair name, e.g. BTCUSDT.
            businessType (str): Business type: `mix`, `contract`, `spot`, `Spot margin`, `leverage`.

        Returns:
            dict: Bitget API JSON response containing trade rates.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/common/all-trade-rate"
        params = {"symbol": symbol, "businessType": businessType}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_convert_coins(self):
        """
        Get a list of Flash Currencies.

        Returns:
            dict: Bitget API JSON response containing convert coins.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/convert/currencies"
        return await self.client._send_request("GET", request_path, params={})

    async def get_futures_active_buy_sell_volume_data(self, symbol, period=None):
        """
        Get Futures Active Buy Sell Volume Data.

        Args:
            symbol (str): Trading pair.
            period (str, optional): Default: 5m. Supported values: `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `6h`, `12h`, `1d`.

        Returns:
            dict: Bitget API JSON response containing futures active buy/sell volume data.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/market/taker-buy-sell"
        params = {"symbol": symbol}
        if period:
            params["period"] = period
        return await self.client._send_request("GET", request_path, params=params)

    async def get_futures_active_long_short_account_data(self, symbol, period=None):
        """
        Get Futures Active Long Short Account Data.

        Args:
            symbol (str): Trading pair.
            period (str, optional): Default: 5m. Supported values: `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `6h`, `12h`, `1d`.

        Returns:
            dict: Bitget API JSON response containing futures active long/short account data.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/market/account-long-short"
        params = {"symbol": symbol}
        if period:
            params["period"] = period
        return await self.client._send_request("GET", request_path, params=params)

    async def get_futures_active_long_short_position_data(self, symbol, period=None):
        """
        Get Futures Active Long Short Position Data.

        Args:
            symbol (str): Trading pair.
            period (str, optional): Default: 5m. Supported values: `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `6h`, `12h`, `1d`.

        Returns:
            dict: Bitget API JSON response containing futures active long/short position data.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/market/position-long-short"
        params = {"symbol": symbol}
        if period:
            params["period"] = period
        return await self.client._send_request("GET", request_path, params=params)

    async def get_futures_long_and_short_ratio_data(self, symbol, period=None):
        """
        Get Futures Long and Short Ratio Data.

        Args:
            symbol (str): Trading pair.
            period (str, optional): Default: 5m. Supported values: `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `6h`, `12h`, `1Dutc`.

        Returns:
            dict: Bitget API JSON response containing futures long and short ratio data.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/market/long-short"
        params = {"symbol": symbol}
        if period:
            params["period"] = period
        return await self.client._send_request("GET", request_path, params=params)

    async def get_leveraged_long_short_ratio_data(self, symbol, period=None, coin=None):
        """
        Get the long-short position ratio for a specific coin in cross and isolated margin accounts.

        Args:
            symbol (str): Trading pair.
            period (str, optional): Default: `24h`. Supported values: `24h`, `30d`.
            coin (str, optional): Base coin or quote coin, default: base coin.

        Returns:
            dict: Bitget API JSON response containing leveraged long-short ratio data.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/margin/market/long-short-ratio"
        params = {"symbol": symbol}
        if period:
            params["period"] = period
        if coin:
            params["coin"] = coin
        return await self.client._send_request("GET", request_path, params=params)

    async def get_isolated_margin_borrowing_ratio_data(self, symbol, period=None):
        """
        Get the ratio of borrowed amount in the base currency (left) and borrowed amount in the quote currency (right) in isolated margin accounts, converted to USDT.

        Args:
            symbol (str): Trading pair.
            period (str, optional): Default: `24h`. Supported values: `24h`, `30d`.

        Returns:
            dict: Bitget API JSON response containing isolated margin borrowing ratio data.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/market/isolated-borrow-rate"
        params = {"symbol": symbol}
        if period:
            params["period"] = period
        return await self.client._send_request("GET", request_path, params=params)

    async def get_margin_loan_growth_rate_data(self, symbol, period=None, coin=None):
        """
        Get the growth rate of borrowed funds for a specific coin in cross and isolated margin accounts.

        Args:
            symbol (str): Trading pair.
            period (str, optional): Default: `24h`. Supported values: `24h`, `30d`.
            coin (str, optional): Base coin or quote coin, default: base coin.

        Returns:
            dict: Bitget API JSON response containing margin loan growth rate data.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/mix/market/margin-loan-ratio"
        params = {"symbol": symbol}
        if period:
            params["period"] = period
        if coin:
            params["coin"] = coin
        return await self.client._send_request("GET", request_path, params=params)

    async def get_merchant_advertisement_list(self, side, coin, fiat, startTime=None, endTime=None, idLessThan=None, limit=None, status=None, advNo=None, language=None, orderBy=None, payMethodId=None, sourceType=None):
        """
        Get Merchant Advertisement List.

        Args:
            side (str): TX type: `buy` (Buy) or `sell` (Sell).
            coin (str): Digital currency.
            fiat (str): Fiat currency.
            startTime (str, optional): Start time, Unix millisecond timestamp.
            endTime (str, optional): End time, Unix millisecond timestamp. Maximum interval between start time and end time is 90 days.
            idLessThan (str, optional): The minAdvId returned from the previous query. Returns the data whose advId is less than the specified input parameter.
            limit (str, optional): Number of queries: Default: 20, max:20.
            status (str, optional): Advertisement order status: `online`, `offline`, `editing`, `completed`.
            advNo (str, optional): Advertisement order number.
            language (str, optional): Language: `zh-CN` (Chinese), `en-US` (English).
            orderBy (str, optional): Sort Fields: `createTime` (Create time), `price` (Price Descending, by createTime by default).
            payMethodId (str, optional): Payment method ID.
            sourceType (str, optional): Query range: `owner` (query owner advertisement, default), `competitior` (query other merchant advertisement), `ownerAndCompetitior` (query all advertisement).

        Returns:
            dict: Bitget API JSON response containing merchant advertisement list.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/p2p/advList" # Corrected endpoint based on markdown
        params = {
            "side": side,
            "coin": coin,
            "fiat": fiat
        }
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if idLessThan:
            params["idLessThan"] = idLessThan
        if limit:
            params["limit"] = limit
        if status:
            params["status"] = status
        if advNo:
            params["advNo"] = advNo
        if language:
            params["language"] = language
        if orderBy:
            params["orderBy"] = orderBy
        if payMethodId:
            params["payMethodId"] = payMethodId
        if sourceType:
            params["sourceType"] = sourceType
        return await self.client._send_request("GET", request_path, params=params)

    async def get_merchant_information(self):
        """
        Get Merchant Information.

        Returns:
            dict: Bitget API JSON response containing merchant information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/p2p/merchantInfo"
        return await self.client._send_request("GET", request_path, params={})

    async def get_merchant_p2p_orders(self, startTime, advNo, endTime=None, idLessThan=None, limit=None, status=None, side=None, coin=None, language=None, fiat=None, orderNo=None):
        """
        Merchant queries P2P orders.

        Args:
            startTime (str): Start time, Unix millisecond timestamp.
            advNo (str): Advertisement order number.
            endTime (str, optional): End time, Unix millisecond timestamp. Maximum interval between start time and end time is 90 days.
            idLessThan (str, optional): The minOrderId returned from the previous query. Returns p2p order data less than the specified entry parameter.
            limit (str, optional): Number of queries, default 100.
            status (str, optional): P2P order status: `pending_pay`, `Paid`, `Appeal`, `Completed`, `cancelled`.
            side (str, optional): TX type: `buy` or `sell`.
            coin (str, optional): Digital currency name, e.g. USDT.
            language (str, optional): Language: `zh-CN` (Chinese), `en-US` (English).
            fiat (str, optional): Fiat currency name, e.g. USD.
            orderNo (str, optional): Order number.

        Returns:
            dict: Bitget API JSON response containing merchant P2P orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/p2p/orderList" # Corrected endpoint based on markdown
        params = {
            "startTime": startTime,
            "advNo": advNo
        }
        if endTime:
            params["endTime"] = endTime
        if idLessThan:
            params["idLessThan"] = idLessThan
        if limit:
            params["limit"] = limit
        if status:
            params["status"] = status
        if side:
            params["side"] = side
        if coin:
            params["coin"] = coin
        if language:
            params["language"] = language
        if fiat:
            params["fiat"] = fiat
        if orderNo:
            params["orderNo"] = orderNo
        return await self.client._send_request("GET", request_path, params=params)

    async def get_p2p_merchant_list(self, online=None, idLessThan=None, limit=None):
        """
        Get P2P merchant list.

        Args:
            online (str, optional): Whether online? `yes` (online) or `no` (offline).
            idLessThan (str, optional): The minMerchantId returned from the previous query. Returns data whose ID is less than the entry parameter.
            limit (str, optional): Number of queries. The default value is 100.

        Returns:
            dict: Bitget API JSON response containing P2P merchant list.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/p2p/merchantList"
        params = {}
        if online:
            params["online"] = online
        if idLessThan:
            params["idLessThan"] = idLessThan
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_quoted_price(self, fromCoin, toCoin, fromCoinSize=None, toCoinSize=None):
        """
        Get Quoted Price.

        Args:
            fromCoin (str): Quote currency.
            toCoin (str): Target currency.
            fromCoinSize (str, optional): Number of coins to inquire about. `fromCoinSize` and `toCoinSize` are only allowed to be passed in at the same time.
            toCoinSize (str, optional): Number of target coins. `fromCoinSize` and `toCoinSize` are only allowed to be passed in at the same time.

        Returns:
            dict: Bitget API JSON response containing quoted price details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/convert/quoted-price"
        params = {"fromCoin": fromCoin, "toCoin": toCoin}
        if fromCoinSize:
            params["fromCoinSize"] = fromCoinSize
        if toCoinSize:
            params["toCoinSize"] = toCoinSize
        return await self.client._send_request("GET", request_path, params=params)

    async def get_server_time(self):
        """
        Get server time.

        Returns:
            dict: Bitget API JSON response containing server time.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/public/time"
        return await self.client._send_request("GET", request_path, params={})

    async def get_spot_fund_flow(self, symbol, period=None):
        """
        Get spot fund flow.

        Args:
            symbol (str): Trading pairs, e.g. BTCUSDT.
            period (str, optional): Query period: `15m` (default), `30m`, `1h`, `2h`, `4h`, `1d`.

        Returns:
            dict: Bitget API JSON response containing spot fund flow data.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/market/fund-flow"
        params = {"symbol": symbol}
        if period:
            params["period"] = period
        return await self.client._send_request("GET", request_path, params=params)

    async def get_spot_whale_net_flow_data(self, symbol):
        """
        Get spot whale net flow data.

        Args:
            symbol (str): Trading pair.

        Returns:
            dict: Bitget API JSON response containing spot whale net flow data.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/market/fund-net-flow"
        params = {"symbol": symbol}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_trade_data_support_symbols(self):
        """
        Get trade data support symbols.

        Returns:
            dict: Bitget API JSON response containing trade data support symbols.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/market/support-symbols"
        return await self.client._send_request("GET", request_path, params={})

    async def get_trade_rate(self, symbol, businessType):
        """
        Get Trade Rate.

        Args:
            symbol (str): Trading pair name, e.g. BTCUSDT.
            businessType (str): Business type: `mix`, `contract`, `spot`, `Spot margin`, `leverage`.

        Returns:
            dict: Bitget API JSON response containing trade rates.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/common/trade-rate"
        params = {"symbol": symbol, "businessType": businessType}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_virtual_subaccounts(self, limit=None, idLessThan=None, status=None):
        """
        Get a list of virtual sub-accounts.

        Args:
            limit (str, optional): Entries per page. Default: 100, maximum: 500.
            idLessThan (str, optional): Final sub-account ID, required for paging.
            status (str, optional): Sub-account status: `normal` (Normal) or `freeze` (Freeze).

        Returns:
            dict: Bitget API JSON response containing virtual subaccount list.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/user/virtual-subaccount-list"
        params = {}
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        if status:
            params["status"] = status
        return await self.client._send_request("GET", request_path, params=params)

    async def get_subaccount_apikey_list(self, subAccountUid):
        """
        Get subaccount API key list.
        Only supports API Key calls from the main account, and the API Key needs to be bound to an IP address.
        Support to get virtual sub-account or general sub-account API Key list.

        Args:
            subAccountUid (str): Sub-account UID.

        Returns:
            dict: Bitget API JSON response containing subaccount API key list.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/user/virtual-subaccount-apikey-list"
        params = {"subAccountUid": subAccountUid}
        return await self.client._send_request("GET", request_path, params=params)

    async def modify_virtual_subaccount(self, subAccountUid, permList, status):
        """
        Modify the virtual sub-account.

        Args:
            subAccountUid (str): Sub-account UID.
            permList (list[str]): Permissions: `spot_trade` (Spot trade), `contract_trade` (Futures trade read-write), `read` (Read permissions).
            status (str): Sub-account status: `normal` (Normal) or `freeze` (Freeze).

        Returns:
            dict: Bitget API JSON response containing the modification result.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/user/modify-virtual-subaccount"
        body = {
            "subAccountUid": subAccountUid,
            "permList": permList,
            "status": status
        }
        return await self.client._send_request("POST", request_path, body=body)

    async def modify_virtual_subaccount_apikey(self, subAccountUid, subAccountApiKey, passphrase, label, ipList=None, permList=None):
        """
        Modify the virtual sub-account or general sub-account API Key.
        Only supports API Key calls from the main account, and the API Key needs to be bound to an IP address.

        Args:
            subAccountUid (str): Sub-account UID.
            subAccountApiKey (str): Sub-account API Key.
            passphrase (str): Passcode (English letters of 8-32 characters + numbers).
            label (str): Note (Length 20).
            ipList (list[str], optional): IP whitelist (Up to 30, if not then IP whitelist is set to empty).
            permList (list[str], optional): Sub-account permissions: `spot_trade` (Spot trade), `margin_trade` (Spot Margin trade), `contract_trade` (Futures trade read-write), `transfer` (Wallet transfer), `read` (Read permissions). If this parameter is not passed, it will be ignored, and the existing permissions will be retained. If an empty value is passed, the existing permissions of this API Key will be removed.

        Returns:
            dict: Bitget API JSON response containing the modified API key details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/user/modify-virtual-subaccount-apikey"
        body = {
            "subAccountUid": subAccountUid,
            "subAccountApiKey": subAccountApiKey,
            "passphrase": passphrase,
            "label": label
        }
        if ipList:
            body["ipList"] = ipList
        if permList:
            body["permList"] = permList
        return await self.client._send_request("POST", request_path, body=body)