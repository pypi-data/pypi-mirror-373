from .exceptions import BitgetAPIException

class Broker:
    def __init__(self, client):
        self.client = client

    async def create_subaccount(self, subaccountName, label=None):
        """
        Create subaccounts.

        Args:
            subaccountName (str): Subaccount name, i.e. email address.
            label (str, optional): Remark, length < 20.

        Returns:
            dict: Bitget API JSON response containing subaccount details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/broker/account/create-subaccount"
        body = {"subaccountName": subaccountName}
        if label:
            body["label"] = label

        return await self.client._send_request("POST", request_path, body=body)

    async def create_subaccount_apikey(self, subUid, passphrase, label, ipList, permType, permList):
        """
        Create ApiKey for the specified subaccount. Only applicable for ND broker main-account.

        Args:
            subUid (str): Sub account UID.
            passphrase (str): Passphrase, length between 6 and 32.
            label (str): Remark, length < 20.
            ipList (list[str]): IP whitelist, max 30 IP entries. It's optional when `permType` is `readonly`.
            permType (str): Permission type: `read_and_write` or `readonly`.
            permList (list[str]): Permission list: `contract_order`, `contract_position`, `spot_trade`, `margin_trade` (spot margin trade), `copytrading_trade`, `wallet_transfer` (permType should be `read_and_write`).

        Returns:
            dict: Bitget API JSON response containing subaccount API key details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/broker/manage/create-subaccount-apikey"
        body = {
            "subUid": subUid,
            "passphrase": passphrase,
            "label": label,
            "ipList": ipList,
            "permType": permType,
            "permList": permList
        }
        return await self.client._send_request("POST", request_path, body=body)

    async def create_subaccount_deposit_address(self, subUid, coin, chain=None):
        """
        Create deposit address for the specified subaccount. Only applicable for ND broker main-account.

        Args:
            subUid (str): Sub account UID.
            coin (str): Coin, e.g: BTC.
            chain (str, optional): Chain name, default will use the main-chain of the 'coin'.

        Returns:
            dict: Bitget API JSON response containing subaccount deposit address details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/broker/account/subaccount-address"
        body = {"subUid": subUid, "coin": coin}
        if chain:
            body["chain"] = chain
        return await self.client._send_request("POST", request_path, body=body)

    async def delete_subaccount_apikey(self, subUid, apiKey):
        """
        Delete ApiKey for the specified subaccount. Only applicable for ND broker main-account.

        Args:
            subUid (str): Sub account UID.
            apiKey (str): API Key.

        Returns:
            dict: Bitget API JSON response indicating success of deletion.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/broker/manage/delete-subaccount-apikey"
        body = {"subUid": subUid, "apiKey": apiKey}
        return await self.client._send_request("POST", request_path, body=body)

    async def get_broker_info(self):
        """
        Get account information of ND Brokers.

        Returns:
            dict: Bitget API JSON response containing broker information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/broker/account/info"
        return await self.client._send_request("GET", request_path, params={})

    async def get_broker_subaccounts(self, startTime=None, endTime=None, pageSize=None, pageNo=None):
        """
        Get Broker Subaccounts.

        Args:
            startTime (str, optional): Start timestamp, milliseconds. If both start and end time are empty, the default time is yesterday 00:00-23:59 (UTC+0). StartTime and endTime can only be filled in at the same time or not. If it exceeds 30 days, an error will be reported.
            endTime (str, optional): End timestamp, milliseconds. If both start and end time are empty, the default time is yesterday 00:00-23:59 (UTC+0). StartTime and endTime can only be filled in at the same time or not. If it exceeds 30 days, an error will be reported.
            pageSize (str, optional): Number of items per page, default is 100, maximum is 1000, if more than 1000 items are returned, 100 items will be returned by default.
            pageNo (str, optional): Pagination page number, default is 1.

        Returns:
            dict: Bitget API JSON response containing broker subaccounts.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/broker/v2/subaccounts"
        params = {}
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if pageSize:
            params["pageSize"] = pageSize
        if pageNo:
            params["pageNo"] = pageNo
        return await self.client._send_request("GET", request_path, params=params)

    async def get_broker_subaccounts_commissions(self, startTime=None, endTime=None, pageSize=None, pageNo=None, bizType=None, subBizType=None):
        """
        Get Broker Subaccounts Commissions.

        Args:
            startTime (str, optional): Start timestamp, milliseconds. If both start and end time are empty, the default time is yesterday 00:00-23:59 (UTC+0). StartTime and endTime can only be filled in at the same time or not. If it exceeds 30 days, an error will be reported.
            endTime (str, optional): End timestamp, milliseconds. If both start and end time are empty, the default time is yesterday 00:00-23:59 (UTC+0). StartTime and endTime can only be filled in at the same time or not. If it exceeds 30 days, an error will be reported.
            pageSize (str, optional): Number of items per page, default is 100, maximum is 1000, if more than 1000 items are returned, 100 items will be returned by default.
            pageNo (str, optional): Pagination page number, default is 1.
            bizType (str, optional): Optional, business type: `spot` or `futures`. If not filled, all types of commission information will be returned.
            subBizType (str, optional): Optional, business subtype: `spot_trade`, `spot_margin`, `usdt_futures`, `usdc_futures`, `coin_futures`. When `bizType=spot`, this parameter can be filled with `spot_trade` and `spot_margin`. When `bizType=future`, this parameter can be filled with `usdt_future`, `usdc_future` and `coin_future`.

        Returns:
            dict: Bitget API JSON response containing broker subaccounts commissions.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/broker/v2/commissions"
        params = {}
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if pageSize:
            params["pageSize"] = pageSize
        if pageNo:
            params["pageNo"] = pageNo
        if bizType:
            params["bizType"] = bizType
        if subBizType:
            params["subBizType"] = subBizType
        return await self.client._send_request("GET", request_path, params=params)

    async def get_broker_trade_volume(self, startTime=None, endTime=None, pageSize=None, pageNo=None):
        """
        Get Broker Trade Volume.

        Args:
            startTime (str, optional): Start timestamp, milliseconds. If both start and end time are empty, the default time is yesterday 00:00-23:59 (UTC+0). StartTime and endTime can only be filled in at the same time or not. If it exceeds 30 days, an error will be reported.
            endTime (str, optional): End timestamp, milliseconds. If both start and end time are empty, the default time is yesterday 00:00-23:59 (UTC+0). StartTime and endTime can only be filled in at the same time or not. If it exceeds 30 days, an error will be reported.
            pageSize (str, optional): Number of items per page, default is 100, maximum is 1000, if more than 1000 items are returned, 100 items will be returned by default.
            pageNo (str, optional): Pagination page number, default is 1.

        Returns:
            dict: Bitget API JSON response containing broker trade volume.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/broker/v2/trade-volume"
        params = {}
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if pageSize:
            params["pageSize"] = pageSize
        if pageNo:
            params["pageNo"] = pageNo
        return await self.client._send_request("GET", request_path, params=params)

    async def get_subaccounts_deposit_and_withdrawal_records(self, startTime=None, endTime=None, limit=None, idLessThan=None, type=None):
        """
        Get Sub-accounts Deposit and Withdrawal Records. Only applicable for ND broker main-account.

        Args:
            startTime (str, optional): Start timestamp. Milliseconds format of timestamp Unix, e.g. 1597026383085. If both start time and end time are empty, the default query time range will be yesterday from 00:00 to 23:59 (UTC+0). Start time and end time must either both be provided or both be empty. An error will be reported if the time range exceeds 7 days.
            endTime (str, optional): End timestamp. Milliseconds format of timestamp Unix, e.g. 1597026383085. If both start time and end time are empty, the default query time range will be yesterday from 00:00 to 23:59 (UTC+0). Start time and end time must either both be provided or both be empty. An error will be reported if the time range exceeds 7 days.
            limit (str, optional): Number of data. Default: 100, maximum: 100. 100 entries will be returned by default when limit is over 100.
            idLessThan (str, optional): Separate page content.
            type (str, optional): Records type: `all` (Both of deposit and withdrawal records, default), `deposit` (Deposit records), `withdrawl` (Withdrawal records).

        Returns:
            dict: Bitget API JSON response containing sub-accounts deposit and withdrawal records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/broker/all-sub-deposit-withdrawal"
        params = {}
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        if type:
            params["type"] = type
        return await self.client._send_request("GET", request_path, params=params)

    async def get_subaccount_apikey(self, subUid):
        """
        Get Subaccount ApiKey. Only applicable for ND broker main-account.

        Args:
            subUid (str): Sub account UID.

        Returns:
            dict: Bitget API JSON response containing subaccount API key details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/broker/manage/subaccount-apikey-list"
        params = {"subUid": subUid}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_subaccount_email(self, subUid):
        """
        Get subaccount email.

        Args:
            subUid (str): Subaccount user id.

        Returns:
            dict: Bitget API JSON response containing subaccount email details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/broker/account/subaccount-email"
        params = {"subUid": subUid}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_subaccount_future_assets(self, subUid, productType):
        """
        Fetch the future assets of the given subaccount. Only applicable for ND broker main-account.

        Args:
            subUid (str): Sub account UID.
            productType (str): Product type: `USDT-FUTURES` (USDT-M Futures), `COIN-FUTURES` (Coin-M Futures), `USDC-FUTURES` (USDC-M Futures).

        Returns:
            dict: Bitget API JSON response containing subaccount future assets.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/broker/account/subaccount-future-assets"
        params = {"subUid": subUid, "productType": productType}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_subaccount_list(self, limit=None, idLessThan=None, status=None, startTime=None, endTime=None):
        """
        Get subaccount list.

        Args:
            limit (str, optional): Number of results returned. Default:10 Max:100.
            idLessThan (str, optional): Requests the content on the page before this ID (older data), the value input should be the subUid of the corresponding interface.
            status (str, optional): Subaccount Status: normal, freeze, or del.
            startTime (str, optional): The start time of subaccount list. i.e., getting the subaccounts after that timestamp Unix millisecond timestamp, e.g. 1690196141868.
            endTime (str, optional): The end time of subaccount list. i.e., getting the subaccounts before that timestamp Unix millisecond timestamp, e.g. 1690196141868.

        Returns:
            dict: Bitget API JSON response containing subaccount list.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/broker/account/subaccount-list"
        params = {}
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        if status:
            params["status"] = status
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        return await self.client._send_request("GET", request_path, params=params)

    async def get_subaccount_spot_assets(self, subUid, coin=None, assetType=None):
        """
        Get subaccount spot assets.

        Args:
            subUid (str): Subaccount user id.
            coin (str, optional): Token name, e.g. USDT.
            assetType (str, optional): Asset type: `hold_only` (Position coin), `all` (All coins). This field is used for querying the positions of multiple coins. The default value is "hold_only". When only assetType is entered without coin, results of all eligible coins are returned. When both coin and assetType are entered, coin has higher priority.

        Returns:
            dict: Bitget API JSON response containing subaccount spot assets.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/broker/account/subaccount-spot-assets"
        params = {"subUid": subUid}
        if coin:
            params["coin"] = coin
        if assetType:
            params["assetType"] = assetType
        return await self.client._send_request("GET", request_path, params=params)

    async def modify_subaccount(self, subUid, permList, status, language=None):
        """
        Modify status and permissions of subaccounts.

        Args:
            subUid (str): Subaccount user id.
            permList (list[str]): Permissions: `withdraw`, `transfer`, `spot_trade`, `contract_trade`, `read`, `deposit`, `margin_trade` (spot margin).
            status (str): Subaccount Status: `normal` (normal status) or `freeze` (freeze status).
            language (str, optional): Subaccount language: `en_US`, `zh_CN`, `ja_JP`, `vi_VN`, `zh_TW`, `ru_RU`, `es_ES`, `tr_TR`, `fr_FR`, `de_DE`, `pt_PT`, `th_TH`.

        Returns:
            dict: Bitget API JSON response containing modified subaccount details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/broker/account/modify-subaccount"
        body = {"subUid": subUid, "permList": permList, "status": status}
        if language:
            body["language"] = language
        return await self.client._send_request("POST", request_path, body=body)

    async def modify_subaccount_apikey(self, subUid, apiKey, passphrase, label=None, ipList=None, permType=None, permList=None):
        """
        Modify ApiKey for the specified sub-account. Only applicable for ND broker main-account.

        Args:
            subUid (str): Sub account UID.
            apiKey (str): Sub account API Key.
            passphrase (str): Passphrase, please recreate if forgot.
            label (str, optional): Remark, length < 20.
            ipList (list[str], optional): IP whitelist, override, max 30 IP entries. Empty means no change.
            permType (str, optional): Permission type, override. Empty means no change: `read_and_write` or `readonly`.
            permList (list[str], optional): Permission list, override. Empty means not change: `contract_order`, `contract_position`, `spot_trade`, `margin_trade` (spot margin trade), `copytrading_trade`, `wallet_transfer` (available when `permType` is `read_and_write`).

        Returns:
            dict: Bitget API JSON response containing modified subaccount API key details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/broker/manage/modify-subaccount-apikey"
        body = {
            "subUid": subUid,
            "apiKey": apiKey,
            "passphrase": passphrase
        }
        if label:
            body["label"] = label
        if ipList:
            body["ipList"] = ipList
        if permType:
            body["permType"] = permType
        if permList:
            body["permList"] = permList
        return await self.client._send_request("POST", request_path, body=body)

    async def modify_subaccount_email(self, subUid, subaccountEmail):
        """
        Modify subaccount email.

        Args:
            subUid (str): Subaccount user id.
            subaccountEmail (str): Subaccount email.

        Returns:
            dict: Bitget API JSON response containing modified subaccount email details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/broker/account/modify-subaccount-email"
        body = {"subUid": subUid, "subaccountEmail": subaccountEmail}
        return await self.client._send_request("POST", request_path, body=body)

    async def sub_deposit_auto_transfer(self, subUid, coin, toAccountType):
        """
        After call, the fund recharge to the given subaccount will automatically transfer to the specified 'toAccountType'. Only applicable for ND broker main-account.

        Args:
            subUid (str): Sub account UID.
            coin (str): Coin.
            toAccountType (str): To account type: `spot` (default), `usdt-futures` (USDT professional futures, corresponding to mix_usdt), `coin-futures` (Mixed futures, corresponding to mix_usd), `usdc-futures` (USDC professional futures, corresponding to mix_usdc).

        Returns:
            dict: Bitget API JSON response indicating success or failure.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/broker/account/sub-deposit-auto-transfer"
        body = {"subUid": subUid, "coin": coin, "toAccountType": toAccountType}
        return await self.client._send_request("POST", request_path, body=body)

    async def sub_deposit_records(self, orderId=None, userId=None, startTime=None, endTime=None, limit=None, idLessThan=None):
        """
        Get ND sub-accounts deposit record. Only applicable for ND broker main-account.

        Args:
            orderId (str, optional): recordsId.
            userId (str, optional): Sub account UID.
            startTime (str, optional): Start timestamp. Milliseconds format of timestamp Unix, e.g. 1597026383085 (The maximum time span supported is three months. The default end time is three months if no value is set for the end time. ).
            endTime (str, optional): End timestamp. Milliseconds format of timestamp Unix, e.g. 1597026383085 (The maximum time span supported is three months. The default start time is three months ago if no value is set for the start time. ).
            limit (str, optional): Number of queries: Default: 20, maximum: 100.
            idLessThan (str, optional): Separate page content before this ID is requested (older data), and the value input should be the end ID of the last request.

        Returns:
            dict: Bitget API JSON response containing sub-account deposit records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/broker/subaccount-deposit"
        params = {}
        if orderId:
            params["orderId"] = orderId
        if userId:
            params["userId"] = userId
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def sub_withdrawal_records(self, orderId=None, userId=None, startTime=None, endTime=None, limit=None, idLessThan=None):
        """
        Get fund withdrawal records. Only applicable for ND broker main-account.

        Args:
            orderId (str, optional): withdrawal order ID.
            userId (str, optional): Sub account UID.
            startTime (str, optional): Start timestamp. Milliseconds format of timestamp Unix, e.g. 1597026383085 (The maximum time span supported is three months. The default end time is three months if no value is set for the end time. ).
            endTime (str, optional): End timestamp. Milliseconds format of timestamp Unix, e.g. 1597026383085 (The maximum time span supported is three months. The default start time is three months ago if no value is set for the start time. ).
            limit (str, optional): Number of queries: Default: 20, maximum: 100.
            idLessThan (str, optional): Separate page content before this ID is requested (older data), and the value input should be the end ID of the last request.

        Returns:
            dict: Bitget API JSON response containing sub-account withdrawal records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/broker/subaccount-withdrawal"
        params = {}
        if orderId:
            params["orderId"] = orderId
        if userId:
            params["userId"] = userId
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def subaccount_withdrawal(self, subUid, coin, dest, address, amount, chain=None, tag=None, clientOid=None):
        """
        ND broker initiates on chain withdraw or internal withdraw. Only applicable for ND broker main-account.

        Args:
            subUid (str): Sub account UID.
            coin (str): Coin, e.g. BTC. Only accept BTC/ETH/USDT/USDC/TRX/XRP/LTC/SOL/BNB/FTM/DOGE/ADA/SHIB/UNI/SEI/SUI/POL/FIL/LINK/TON/ARB/OP/DOT/AVAX.
            dest (str): Withdraw type: `on_chain` (on chain withdraw) or `internal_transfer` (internal withdraw).
            address (str): Address. When `dest`==`on_chain`, it should be the chain address. When `dest`==`internal_transfer`, it should be UID.
            amount (str): Withdraw amount.
            chain (str, optional): Chain name. It will use the main-chain of the 'coin' by default.
            tag (str, optional): Tag value for on chain withdraw, i.e. 'memo' of 'EOS', 'comment' of 'TON'.
            clientOid (str, optional): Client Order ID.

        Returns:
            dict: Bitget API JSON response containing order details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/broker/account/subaccount-withdrawal"
        body = {
            "subUid": subUid,
            "coin": coin,
            "dest": dest,
            "address": address,
            "amount": amount
        }
        if chain:
            body["chain"] = chain
        if tag:
            body["tag"] = tag
        if clientOid:
            body["clientOid"] = clientOid
        return await self.client._send_request("POST", request_path, body=body)