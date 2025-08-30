from .exceptions import BitgetAPIException

class Spot:
    def __init__(self, client):
        self.client = client

    async def get_server_time(self):
        """
        Get server time, Unix millisecond timestamp.

        Returns:
            dict: Bitget API JSON response containing the server time.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/public/time"
        return await self.client._send_request("GET", request_path)

    async def get_symbol_config(self, symbol=None):
        """
        Get trading pair configuration, supporting both individual and full queries.

        Args:
            symbol (str, optional): Trading pair name, e.g. BTCUSDT. If the field is left blank, all trading pair information will be returned by default.

        Returns:
            dict: Bitget API JSON response containing symbol configuration.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/public/symbols"
        params = {}
        if symbol:
            params["symbol"] = symbol
        return await self.client._send_request("GET", request_path, params=params)

    async def get_currency_information(self, coin=None):
        """
        Get spot coin information, supporting both individual and full queries.

        Args:
            coin (str, optional): Coin name. If the field is left blank, all coin information will be returned by default.

        Returns:
            dict: Bitget API JSON response containing currency information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/public/coins"
        params = {}
        if coin:
            params["coin"] = coin
        return await self.client._send_request("GET", request_path, params=params)

    async def get_deposit_address(self, coin, chain):
        """
        Get Deposit Address.

        Args:
            coin (str): Coin name, e.g. USDT.
            chain (str): Chain name, e.g. trc20.

        Returns:
            dict: Bitget API JSON response containing deposit address information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/wallet/deposit-address"
        params = {"coin": coin, "chain": chain}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_deposit_record(self, startTime, endTime, coin=None, orderId=None, idLessThan=None, limit=None):
        """
        Get Deposit Record.

        Args:
            startTime (str): The record start time for the query. Unix millisecond timestamp, e.g. 1690196141868.
            endTime (str): The end time of the record for the query. Unix millisecond timestamp, e.g. 1690196141868.
            coin (str, optional): Coin name, e.g. USDT.
            orderId (str, optional): The response orderId.
            idLessThan (str, optional): Requests the content on the page before this ID (older data), the value input should be the orderId of the corresponding interface.
            limit (str, optional): Number of entries per page. The default value is 20 and the maximum value is 100.

        Returns:
            dict: Bitget API JSON response containing deposit records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/wallet/deposit-records"
        params = {"startTime": startTime, "endTime": endTime}
        if coin:
            params["coin"] = coin
        if orderId:
            params["orderId"] = orderId
        if idLessThan:
            params["idLessThan"] = idLessThan
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_withdraw_record(self, startTime, endTime, coin=None, clientOid=None, idLessThan=None, orderId=None, limit=None):
        """
        Get Withdraw Record.

        Args:
            startTime (str): The record start time for the query. Unix millisecond timestamp, e.g. 1690196141868.
            endTime (str): The end time of the record for the query. Unix millisecond timestamp, e.g. 1690196141868.
            coin (str, optional): Coin name, e.g. USDT.
            clientOid (str, optional): Client customized ID.
            idLessThan (str, optional): Requests the content on the page before this ID (older data), the value input should be the orderId of the corresponding interface.
            orderId (str, optional): The response orderId.
            limit (str, optional): Number of entries per page. The default value is 20 and the maximum value is 100.

        Returns:
            dict: Bitget API JSON response containing withdrawal records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/wallet/withdrawal-records"
        params = {"startTime": startTime, "endTime": endTime}
        if coin:
            params["coin"] = coin
        if clientOid:
            params["clientOid"] = clientOid
        if idLessThan:
            params["idLessThan"] = idLessThan
        if orderId:
            params["orderId"] = orderId
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def withdraw(self, coin, transferType, address, size, chain=None, innerToType=None, areaCode=None, tag=None, remark=None, clientOid=None):
        """
        Coin withdrawals including on-chain withdrawals and internal transfers.

        Args:
            coin (str): Coin.
            transferType (str): Withdrawal of coins (`on_chain` or `internal_transfer`).
            address (str): Holder address.
            size (str): Amount.
            chain (str, optional): Ticin network e.g. erc20, trc20, etc. This field must be passed when the withdrawal type is on-chain.
            innerToType (str, optional): Type of address for internal withdrawals (`Email address`, `mobile`, `uid`). The default value is `uid`.
            areaCode (str, optional): This field is required when the value of the collection address type is mobile.
            tag (str, optional): Address tag.
            remark (str, optional): Note.
            clientOid (str, optional): Client Customized Id Unique.

        Returns:
            dict: Bitget API JSON response containing order ID and client customized ID.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/wallet/withdrawal"
        body = {
            "coin": coin,
            "transferType": transferType,
            "address": address,
            "size": size
        }
        if chain:
            body["chain"] = chain
        if innerToType:
            body["innerToType"] = innerToType
        if areaCode:
            body["areaCode"] = areaCode
        if tag:
            body["tag"] = tag
        if remark:
            body["remark"] = remark
        if clientOid:
            body["clientOid"] = clientOid
        return await self.client._send_request("POST", request_path, body=body)

    async def sub_transfer(self, fromType, toType, amount, coin, fromUserId, toUserId, symbol=None, clientOid=None):
        """
        Sub Transfer.
        The types of transfers supported by this interface include: Parent account to sub-account (only parent account APIKey has access), Sub-account to parent account (only parent account APIKey has access), Sub-account to sub-account (only the parent account APIKey has access and requires that the payee sub-accounts are the same parent account). The UIDs of the incoming and outgoing accounts in the request parameters must be mother-son/brother relationships, and only the mother account has access to all transfer operations.

        Args:
            fromType (str): Type of account to be transferred.
            toType (str): Recipient account type.
            amount (str): Amount to transfer.
            coin (str): Currency of transfer.
            fromUserId (str): Outgoing Account UID.
            toUserId (str): Incoming Account UID.
            symbol (str, optional): Required when transferring to or from an account type that is a leveraged position-by-position account.
            clientOid (str, optional): Custom order ID.

        Returns:
            dict: Bitget API JSON response containing transfer ID and client customized ID.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/wallet/subaccount-transfer"
        body = {
            "fromType": fromType,
            "toType": toType,
            "amount": amount,
            "coin": coin,
            "fromUserId": fromUserId,
            "toUserId": toUserId
        }
        if symbol:
            body["symbol"] = symbol
        if clientOid:
            body["clientOid"] = clientOid
        return await self.client._send_request("POST", request_path, body=body)

    async def transfer(self, fromType, toType, amount, coin, symbol, clientOid=None):
        """
        Transfer.
        The types of transfers supported by this interface include: Parent account to sub-account (only parent account APIKey has access), Sub-account to parent account (only parent account APIKey has access), Sub-account to sub-account (only the parent account APIKey has access and requires that the payee sub-accounts are the same parent account). The UIDs of the incoming and outgoing accounts in the request parameters must be mother-son/brother relationships, and only the mother account has access to all transfer operations.

        Args:
            fromType (str): Type of account to be transferred.
            toType (str): Recipient account type.
            amount (str): Amount to transfer.
            coin (str): Currency of transfer.
            symbol (str): Required when transferring to or from an account type that is a leveraged position-by-position account.
            clientOid (str, optional): Custom order ID.

        Returns:
            dict: Bitget API JSON response containing transfer ID and client customized ID.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/wallet/transfer"
        body = {
            "fromType": fromType,
            "toType": toType,
            "amount": amount,
            "coin": coin,
            "symbol": symbol
        }
        if clientOid:
            body["clientOid"] = clientOid
        return await self.client._send_request("POST", request_path, body=body)

    async def cancel_withdrawal(self, orderId):
        """
        Cancel Withdrawal.
        1. The user center can set the switch [Cancel Withdrawal], and there is a "regret period" of 1 minute to cancel the withdrawal.
        2. There is manual review in the preliminary review status, and the withdrawal can be cancelled. Once the initial review is passed or uploaded to the chain, the withdrawal cannot be revoked.
        3. Small-amount automatic currency withdrawals do not require manual review, and the withdrawal cannot be revoked.

        Args:
            orderId (str): Withdraw orderId.

        Returns:
            dict: Bitget API JSON response containing "success" or "fail".

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/wallet/cancel-withdrawal"
        body = {"orderId": orderId}
        return await self.client._send_request("POST", request_path, body=body)

    async def get_account_information(self):
        """
        Get account information.

        Returns:
            dict: Bitget API JSON response containing account information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/account/info"
        return await self.client._send_request("GET", request_path)

    async def get_account_assets(self, coin=None, assetType=None):
        """
        Get Account Assets.

        Args:
            coin (str, optional): Token name, e.g. USDT. This field is used for querying the positions of a single coin.
            assetType (str, optional): Asset type (`hold_only` or `all`). `hold_only`: Position coin. `all`: All coins. This field is used for querying the positions of multiple coins. The default value is `hold_only`. When only `assetType` is entered without coin, results of all eligible coins are returned. When both coin and `assetType` are entered, coin has higher priority.

        Returns:
            dict: Bitget API JSON response containing account assets.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/account/assets"
        params = {}
        if coin:
            params["coin"] = coin
        if assetType:
            params["assetType"] = assetType
        return await self.client._send_request("GET", request_path, params=params)

    async def get_sub_accounts_assets(self, idLessThan=None, limit=None):
        """
        Get Sub-accounts Assets (only return the sub-accounts which assets > 0).
        ND Brokers are not allowed to call this endpoint.

        Args:
            idLessThan (str, optional): Cursor ID. Pagination cursor. Do not pass it in the first request. For subsequent requests, pass the last ID returned previously.
            limit (str, optional): The number of sub-accounts returned per page. The default value is 10, and the maximum value is 50.

        Returns:
            dict: Bitget API JSON response containing sub-accounts assets.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/account/subaccount-assets"
        params = {}
        if idLessThan:
            params["idLessThan"] = idLessThan
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def modify_deposit_account(self, accountType, coin):
        """
        Modify the auto-transfer account type of deposit.

        Args:
            accountType (str): Account type (`spot`, `funding`, `coin-futures`, `usdt-futures`, `usdc-futures`).
            coin (str): Currency of transfer.

        Returns:
            dict: Bitget API JSON response containing "success" or "fail".

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/wallet/modify-deposit-account"
        body = {"accountType": accountType, "coin": coin}
        return await self.client._send_request("POST", request_path, body=body)

    async def get_account_bills(self, coin=None, groupType=None, businessType=None, startTime=None, endTime=None, limit=None, idLessThan=None):
        """
        Get Account Bills.

        Args:
            coin (str, optional): Token name, e.g. USDT.
            groupType (str, optional): Billing type (`deposit`, `withdraw`, `transaction`, `transfer`, `loan`, `financial`, `fait`, `convert`, `c2c`, `pre_c2c`, `on_chain`, `strategy`, `other`).
            businessType (str, optional): Business type (`DEPOSIT`, `WITHDRAW`, `BUY`, `SELL`, `DEDUCTION_HANDLING_FEE`, `TRANSFER_IN`, `TRANSFER_OUT`, `REBATE_REWARDS`, `AIRDROP_REWARDS`, `USDT_CONTRACT_REWARDS`, `MIX_CONTRACT_REWARDS`, `SYSTEM_LOCK`, `USER_LOCK`).
            startTime (str, optional): The start time of the billing history, i.e., getting the billing history after that timestamp Unix millisecond timestamp, e.g. 1690196141868.
            endTime (str, optional): The end time of the billing history, i.e., getting the billing history before that timestamp Unix millisecond timestamp, e.g. 1690196141868. The interval between startTime and endTime must not exceed 90 days.
            limit (str, optional): Number of results returned. Default: 100, maximum 500.
            idLessThan (str, optional): Requests the content on the page before this ID (older data), the value input should be the billId of the corresponding interface.

        Returns:
            dict: Bitget API JSON response containing account bills.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/account/bills"
        params = {}
        if coin:
            params["coin"] = coin
        if groupType:
            params["groupType"] = groupType
        if businessType:
            params["businessType"] = businessType
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_transferable_coin_list(self, fromType, toType):
        """
        Get transferable coin list.

        Args:
            fromType (str): Account type (`spot`, `p2p`, `coin_futures`, `usdt_futures`, `usdc_futures`, `crossed_margin`, `isolated_margin`).
            toType (str): Account type (`spot`, `p2p`, `coin_futures`, `usdt_futures`, `usdc_futures`, `crossed_margin`, `isolated_margin`).

        Returns:
            dict: Bitget API JSON response containing a list of transferable coins.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/wallet/transfer-coin-info"
        params = {"fromType": fromType, "toType": toType}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_main_sub_transfer_record(self, coin=None, role=None, subUid=None, startTime=None, endTime=None, clientOid=None, limit=None, idLessThan=None):
        """
        Get transfer record.

        Args:
            coin (str, optional): Token name.
            role (str, optional): Transfer out type (default: `initiator`). `initiator` or `receiver`.
            subUid (str, optional): Sub-account UID. If empty, it only queries the records that transfer from main account.
            startTime (str, optional): The start time of the billing history, i.e., getting the billing history after that timestamp Unix millisecond timestamp, e.g. 1690196141868.
            endTime (str, optional): The end time of the billing history, i.e., getting the billing history before that timestamp Unix millisecond timestamp, e.g. 1690196141868. The interval between startTime and endTime must not exceed 90 days.
            clientOid (str, optional): Order ID customized by user.
            limit (str, optional): Number of results returned: Default: 100, maximum 100.
            idLessThan (str, optional): Requests the content on the page before this ID (older data), the value input should be the transferId of the corresponding interface.

        Returns:
            dict: Bitget API JSON response containing main/sub transfer records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/account/sub-main-trans-record"
        params = {}
        if coin:
            params["coin"] = coin
        if role:
            params["role"] = role
        if subUid:
            params["subUid"] = subUid
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if clientOid:
            params["clientOid"] = clientOid
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_transfer_record(self, coin, fromType=None, startTime=None, endTime=None, clientOid=None, pageNum=None, limit=None, idLessThan=None):
        """
        Get transfer record.

        Args:
            coin (str): Token name.
            fromType (str, optional): Account type (`spot`, `p2p`, `coin_futures`, `usdt_futures`, `usdc_futures`, `crossed_margin`, `isolated_margin`).
            startTime (str, optional): The start time of the billing history, i.e., getting the billing history after that timestamp Unix millisecond timestamp, e.g. 1690196141868.
            endTime (str, optional): The end time of the billing history, i.e., getting the billing history before that timestamp Unix millisecond timestamp, e.g. 1690196141868. The interval between startTime and endTime must not exceed 90 days.
            clientOid (str, optional): Order ID customized by user.
            pageNum (str, optional): Requests the content on the page. Default: 1, max: 1000.
            limit (str, optional): Number of results returned: Default: 100, maximum 500.
            idLessThan (str, optional): (Deprecated) Requests the content on the page before this ID (older data), the value input should be the transferId of the corresponding interface.

        Returns:
            dict: Bitget API JSON response containing transfer records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/account/transferRecords"
        params = {"coin": coin}
        if fromType:
            params["fromType"] = fromType
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if clientOid:
            params["clientOid"] = clientOid
        if pageNum:
            params["pageNum"] = pageNum
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def switch_bgb_deduct(self, deduct):
        """
        Switch BGB Deduct.

        Args:
            deduct (str): `on` or `off`.

        Returns:
            dict: Bitget API JSON response.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/account/switch-deduct"
        body = {"deduct": deduct}
        return await self.client._send_request("POST", request_path, body=body)

    async def get_sub_account_deposit_address(self, subUid, coin, chain=None, size=None):
        """
        Get Sub-account Deposit Address (Please ensure that queried sub-account has deposit permission enabled).

        Args:
            subUid (str): Sub Account Uid. You can get the sub-account list via [Get Virtual Subaccounts](https://www.bitget.com/api-doc/common/vsubaccount/Get-Virtual-Subaccount-List) interface.
            coin (str): Coin name, e.g. USDT. All coin names can be returned from [Get Coin Info](https://www.bitget.com/api-doc/spot/market/Get-Coin-List) interface.
            chain (str, optional): Chain name, e.g. trc20. You can get the chain names via [Get Coin Info](https://www.bitget.com/api-doc/spot/market/Get-Coin-List) interface.
            size (str, optional): Bitcoin Lightning Network withdrawal amount, limit: 0.000001 - 0.01.

        Returns:
            dict: Bitget API JSON response containing sub-account deposit address information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/wallet/subaccount-deposit-address"
        params = {"subUid": subUid, "coin": coin}
        if chain:
            params["chain"] = chain
        if size:
            params["size"] = size
        return await self.client._send_request("GET", request_path, params=params)

    async def get_bgb_deduct_info(self):
        """
        Get BGB Deduct Info.

        Returns:
            dict: Bitget API JSON response containing BGB deduct information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/account/deduct-info"
        return await self.client._send_request("GET", request_path)

    async def get_sub_account_deposit_records(self, subUid, coin=None, startTime=None, endTime=None, idLessThan=None, limit=None):
        """
        Get SubAccount Deposit Records.

        Args:
            subUid (str): Sub Account Uid.
            coin (str, optional): Coin name, e.g. USDT.
            startTime (str, optional): The record start time for the query. Unix millisecond timestamp, e.g. 1690196141868.
            endTime (str, optional): The end time of the record for the query. Unix millisecond timestamp, e.g. 1690196141868.
            idLessThan (str, optional): Requests the content on the page before this ID (older data), the value input should be the orderId of the corresponding interface.
            limit (str, optional): Number of entries per page. The default value is 20 and the maximum value is 100.

        Returns:
            dict: Bitget API JSON response containing sub-account deposit records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/wallet/subaccount-deposit-records"
        params = {"subUid": subUid}
        if coin:
            params["coin"] = coin
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if idLessThan:
            params["idLessThan"] = idLessThan
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def upgrade_account(self, subUid=None):
        """
        Upgrade Account.
        1. No account type restrictions; both parent and sub-accounts are supported.
        2. This interface is only used for upgrading to the unified account mode.
        3. Please note that as the account upgrade process takes approximately 1 minute, the successful response you receive only indicates that the request has been received, and does not mean that the account has been successfully upgraded to a unified account.
        4. Please use the query upgrade status interface to confirm whether the account upgrade is successful.

        Args:
            subUid (str, optional): Sub-account User ID. This parameter is only valid when invoked by the parent account. It is ignored if invoked by a sub-account.

        Returns:
            dict: Bitget API JSON response.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/account/upgrade"
        body = {}
        if subUid:
            body["subUid"] = subUid
        return await self.client._send_request("POST", request_path, body=body)

    async def get_upgrade_status(self, subUid=None):
        """
        Get Upgrade Status.
        No account type restrictions; both parent and sub-accounts are supported.

        Args:
            subUid (str, optional): Sub-account User ID. This parameter is only valid when invoked by the parent account. It is ignored if invoked by a sub-account.

        Returns:
            dict: Bitget API JSON response containing upgrade status.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/account/upgrade-status"
        params = {}
        if subUid:
            params["subUid"] = subUid
        return await self.client._send_request("GET", request_path, params=params)

    async def get_ticker_information(self, symbol=None):
        """
        Get Ticker Information, Supports both single and batch queries.

        Args:
            symbol (str, optional): Trading pair name, e.g. BTCUSDT. If the field is left blank, all trading pair information will be returned by default.

        Returns:
            dict: Bitget API JSON response containing ticker information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/market/tickers"
        params = {}
        if symbol:
            params["symbol"] = symbol
        return await self.client._send_request("GET", request_path, params=params)

    async def get_merge_depth(self, symbol, precision=None, limit=None):
        """
        Get Merge Depth.

        Args:
            symbol (str): Trading pair.
            precision (str, optional): Price precision, return the cumulative depth according to the selected precision as the step size, enumeration value: `scale0`/`scale1`/`scale2`/`scale3`. `scale0` does not merge, the default value, generally speaking, `scale1` is the merged depth of the trading pair quotation accuracy *10, generally Under normal circumstances, `scale2` is the quotation accuracy* 100. Under normal circumstances, `scale3` is the quotation accuracy * 1000. Under normal circumstances, the accuracy corresponding to 0/1/2/3 is based on the actual return parameter "scale". Each trading pair The quotation accuracy is different. Some currency pairs do not have scale 2. Requests for scales that do not exist for the currency pair will be processed according to the maximum scale. Example: A certain trading pair only has scale 0/1, and when scale2 is requested, it is automatically reduced to scale1.
            limit (str, optional): Fixed gear enumeration value: `1`/`5`/`15`/`50`/`max`, default: `100`. When the actual depth does not meet the limit, return according to the actual gear, and pass in `max` to return the maximum gear of the trading pair.

        Returns:
            dict: Bitget API JSON response containing merged depth information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/market/merge-depth"
        params = {"symbol": symbol}
        if precision:
            params["precision"] = precision
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_orderbook_depth(self, symbol, type=None, limit=None):
        """
        Get OrderBook Depth.

        Args:
            symbol (str): Trading pair.
            type (str, optional): Default: `step0`. The value enums: `step0`, `step1`, `step2`, `step3`, `step4`, `step5`.
            limit (str, optional): Number of queries: Default: 150, maximum: 150.

        Returns:
            dict: Bitget API JSON response containing order book depth.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/market/orderbook"
        params = {"symbol": symbol}
        if type:
            params["type"] = type
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_candlestick_data(self, symbol, granularity, startTime=None, endTime=None, limit=None):
        """
        Get Candlestick Data.

        Args:
            symbol (str): Trading pair e.g.BTCUSDT.
            granularity (str): Time interval of charts. For the corresponding relationship between granularity and value, refer to the list below. minute: 1min,3min,5min,15min,30min hour: 1h,4h,6h,12h day: 1day,3day week: 1week month: 1M hour in UTC:6Hutc,12Hutc day in UTC:1Dutc,3Dutc week in UTC:1Wutc month in UTC: 1Mutc 1m, 3m, 5m can query for one month,15m can query for 52 days,30m can query for 62 days,1H can query for 83 days,2H can query for 120 days,4H can query for 240 days,6H can query for 360 days.
            startTime (str, optional): The time start point of the chart data, i.e., to get the chart data after this time stamp Unix millisecond timestamp, e.g. 1690196141868.
            endTime (str, optional): The time end point of the chart data, i.e., get the chart data before this time stamp Unix millisecond timestamp, e.g. 1690196141868.
            limit (str, optional): Number of queries: Default: 100, maximum: 1000.

        Returns:
            dict: Bitget API JSON response containing candlestick data.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/market/candles"
        params = {"symbol": symbol, "granularity": granularity}
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_call_auction_information(self, symbol):
        """
        Get Call Auction information.

        Args:
            symbol (str): Trading pair.

        Returns:
            dict: Bitget API JSON response containing call auction information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/market/auction"
        params = {"symbol": symbol}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_history_candlestick_data(self, symbol, granularity, endTime, limit=None):
        """
        Get History Candlestick Data.

        Args:
            symbol (str): Trading pair.
            granularity (str): Time interval of charts. For the corresponding relationship between granularity and value, refer to the list below. minute: 1min,3min,5min,15min,30min hour: 1h,4h,6h,12h day: 1day,3day week: 1week month: 1M hour in UTC:6Hutc,12Hutc day in UTC:1Dutc,3Dutc week in UTC:1Wutc month in UTC: 1Mutc.
            endTime (str): The time end point of the chart data, i.e., get the chart data before this time stamp Unix millisecond timestamp, e.g. 1690196141868.
            limit (str, optional): Number of queries: Default: 100, maximum: 200.

        Returns:
            dict: Bitget API JSON response containing historical candlestick data.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/market/history-candles"
        params = {"symbol": symbol, "granularity": granularity, "endTime": endTime}
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_recent_trades(self, symbol, limit=None):
        """
        Get Recent Trades.

        Args:
            symbol (str): Trading pair name, e.g. BTCUSDT.
            limit (str, optional): Default: 100, maximum: 500.

        Returns:
            dict: Bitget API JSON response containing recent trades.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/market/fills"
        params = {"symbol": symbol}
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_market_trades(self, symbol, limit=None, idLessThan=None, startTime=None, endTime=None):
        """
        Get Market Trades.
        * The time interval between startTime and endTime should not exceed 7 days.
        * It supports to get the data within 90days. You can download the older data on our [web](https://www.bitget.com/data-download)

        Args:
            symbol (str): Trading pair name, e.g. BTCUSDT.
            limit (str, optional): Number of data returned. Default: 500, maximum: 1000.
            idLessThan (str, optional): Order ID, returns records less than the specified 'tradeId'.
            startTime (str, optional): startTime, Unix millisecond timestamp e.g. 1690196141868. startTime and endTime should be within 7days.
            endTime (str, optional): endTime, Unix millisecond timestamp e.g. 1690196141868. startTime and endTime should be within 7days.

        Returns:
            dict: Bitget API JSON response containing market trades.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/market/fills-history"
        params = {"symbol": symbol}
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        return await self.client._send_request("GET", request_path, params=params)

    async def get_vip_fee_rate(self):
        """
        Get VIP Fee Rate.

        Returns:
            dict: Bitget API JSON response containing VIP fee rate information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/market/vip-fee-rate"
        return await self.client._send_request("GET", request_path)

    async def place_order(self, symbol, side, orderType, force, size, price=None, clientOid=None, triggerPrice=None, tpslType=None, requestTime=None, receiveWindow=None, stpMode=None, presetTakeProfitPrice=None, executeTakeProfitPrice=None, presetStopLossPrice=None, executeStopLossPrice=None):
        """
        Place Order.
        * For elite traders, please strictly adhere to the list of trading pairs specified in the [Available trading pairs and parameters for elite traders](https://www.bitget.com/zh-CN/support/articles/12560603808895) when placing orders using the Copy Trading API Key. Trading pairs outside the announced list are not available for copy trading.

        Args:
            symbol (str): Trading pair name, e.g. BTCUSDT. All symbols can be returned by [Get Symbol Info](https://www.bitget.com/api-doc/spot/market/Get-Symbols) interface.
            side (str): Order Direction (`buy` or `sell`).
            orderType (str): Order type (`limit` or `market`).
            force (str): Execution strategy(It is invalid when `orderType` is `market`). `gtc`: Normal limit order, good till cancelled. `post_only`: Post only. `fok`: Fill or kill. `ioc`: Immediate or cancel.
            size (str): Amount. For **Limit and Market-Sell** orders, it represents the number of **base coins**. For **Market-Buy** orders, it represents the number of **quote coins**. The decimal places of amount can be got trough [Get Symbol Info](https://www.bitget.com/api-doc/spot/market/Get-Symbols) interface.
            price (str, optional): Limit price. The decimal places of price and the price step can be returned by the [Get Symbol Info](https://www.bitget.com/api-doc/spot/market/Get-Symbols) interface.
            clientOid (str, optional): Customed order ID. It's invalid when `tpslType` is `tpsl`.
            triggerPrice (str, optional): SPOT TP/SL trigger price, only required in SPOT TP/SL order.
            tpslType (str, optional): Order type (`normal`: SPOT order(default) or `tpsl`: SPOT TP/SL order).
            requestTime (str, optional): Request Time, Unix millisecond timestamp.
            receiveWindow (str, optional): Valid time window, Unix millisecond timestamp. If it's set, the request is valid only when the time range between the timestamp in the request and the time that server received the request is within `receiveWindow`.
            stpMode (str, optional): STP Mode(Self Trade Prevention) (`none`: not setting STP(default), `cancel_taker`: cancel taker order, `cancel_maker`: cancel maker order, `cancel_both`: cancel both of taker and maker orders).
            presetTakeProfitPrice (str, optional): Take profit price. It's invalid when `tpslType` is `tpsl`. The decimal places of price and the price step can be returned by the [Get Symbol Info](https://www.bitget.com/api-doc/spot/market/Get-Symbols) interface.
            executeTakeProfitPrice (str, optional): Take profit execute price. It's invalid when `tpslType` is `tpsl`. The decimal places of price and the price step can be returned by the [Get Symbol Info](https://www.bitget.com/api-doc/spot/market/Get-Symbols) interface.
            presetStopLossPrice (str, optional): Stop loss price. It's invalid when `tpslType` is `tpsl`. The decimal places of price and the price step can be returned by the [Get Symbol Info](https://www.bitget.com/api-doc/spot/market/Get-Symbols) interface.
            executeStopLossPrice (str, optional): Stop loss execute price. It's invalid when `tpslType` is `tpsl`. The decimal places of price and the price step can be returned by the [Get Symbol Info](https://www.bitget.com/api-doc/spot/market/Get-Symbols) interface.

        Returns:
            dict: Bitget API JSON response containing order ID and custom order ID.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/trade/place-order"
        body = {
            "symbol": symbol,
            "side": side,
            "orderType": orderType,
            "force": force,
            "size": size
        }
        if price:
            body["price"] = price
        if clientOid:
            body["clientOid"] = clientOid
        if triggerPrice:
            body["triggerPrice"] = triggerPrice
        if tpslType:
            body["tpslType"] = tpslType
        if requestTime:
            body["requestTime"] = requestTime
        if receiveWindow:
            body["receiveWindow"] = receiveWindow
        if stpMode:
            body["stpMode"] = stpMode
        if presetTakeProfitPrice:
            body["presetTakeProfitPrice"] = presetTakeProfitPrice
        if executeTakeProfitPrice:
            body["executeTakeProfitPrice"] = executeTakeProfitPrice
        if presetStopLossPrice:
            body["presetStopLossPrice"] = presetStopLossPrice
        if executeStopLossPrice:
            body["executeStopLossPrice"] = executeStopLossPrice
        return await self.client._send_request("POST", request_path, body=body)

    async def cancel_replace_order(self, symbol, price, size, clientOid=None, orderId=None, newClientOid=None, presetTakeProfitPrice=None, executeTakeProfitPrice=None, presetStopLossPrice=None, executeStopLossPrice=None):
        """
        Cancel an Existing Order and Send a New Order.

        Args:
            symbol (str): Trading pair name, e.g. BTCUSDT. All symbols can be returned by [Get Symbol Info](https://www.bitget.com/api-doc/spot/market/Get-Symbols) interface.
            price (str): Limit price. The decimal places of price and the price step can be returned by the [Get Symbol Info](https://www.bitget.com/api-doc/spot/market/Get-Symbols) interface.
            size (str): Amount, it represents the number of **base coins**.
            clientOid (str, optional): Client Order ID. Either `orderId` or `clientOid` is required.
            orderId (str, optional): Order ID. Either `orderId` or `clientOid` is required.
            newClientOid (str, optional): New customed order ID. If `newClientOid` results in idempotency duplication, it may cause the old order to be successfully canceled but the new order placement to fail.
            presetTakeProfitPrice (str, optional): Take profit price. The decimal places of price and the price step can be returned by the [Get Symbol Info](https://www.bitget.com/api-doc/spot/market/Get-Symbols) interface.
            executeTakeProfitPrice (str, optional): Take profit execute price. The decimal places of price and the price step can be returned by the [Get Symbol Info](https://www.bitget.com/api-doc/spot/market/Get-Symbols) interface.
            presetStopLossPrice (str, optional): Stop loss price. The decimal places of price and the price step can be returned by the [Get Symbol Info](https://www.bitget.com/api-doc/spot/market/Get-Symbols) interface.
            executeStopLossPrice (str, optional): Stop loss execute price. The decimal places of price and the price step can be returned by the [Get Symbol Info](https://www.bitget.com/api-doc/spot/market/Get-Symbols) interface.

        Returns:
            dict: Bitget API JSON response containing order ID, client customized ID, success status, and message.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/trade/cancel-replace-order"
        body = {
            "symbol": symbol,
            "price": price,
            "size": size
        }
        if clientOid:
            body["clientOid"] = clientOid
        if orderId:
            body["orderId"] = orderId
        if newClientOid:
            body["newClientOid"] = newClientOid
        if presetTakeProfitPrice:
            body["presetTakeProfitPrice"] = presetTakeProfitPrice
        if executeTakeProfitPrice:
            body["executeTakeProfitPrice"] = executeTakeProfitPrice
        if presetStopLossPrice:
            body["presetStopLossPrice"] = presetStopLossPrice
        if executeStopLossPrice:
            body["executeStopLossPrice"] = executeStopLossPrice
        return await self.client._send_request("POST", request_path, body=body)

    async def batch_cancel_replace_order(self, orderList):
        """
        Batch Cancel Existing Order and Send New Orders.

        Args:
            orderList (list): Collection of placing orders, maximum length: 50. Each item in the list should be a dictionary with the following keys:
                symbol (str): Trading pair name, e.g. BTCUSDT. All symbols can be returned by [Get Symbol Info](https://www.bitget.com/api-doc/spot/market/Get-Symbols) interface.
                price (str): Limit price. The decimal places of price and the price step can be returned by the [Get Symbol Info](https://www.bitget.com/api-doc/spot/market/Get-Symbols) interface.
                size (str): Amount, it represents the number of **base coins**.
                clientOid (str, optional): Client Order ID. Either `orderId` or `clientOid` is required.
                orderId (str, optional): Order ID. Either `orderId` or `clientOid` is required.
                newClientOid (str, optional): New customed order ID. If `newClientOid` results in idempotency duplication, it may cause the old order to be successfully canceled but the new order placement to fail.
                presetTakeProfitPrice (str, optional): Take profit price. The decimal places of price and the price step can be returned by the [Get Symbol Info](https://www.bitget.com/api-doc/spot/market/Get-Symbols) interface.
                executeTakeProfitPrice (str, optional): Take profit execute price. The decimal places of price and the price step can be returned by the [Get Symbol Info](https://www.bitget.com/api-doc/spot/market/Get-Symbols) interface.
                presetStopLossPrice (str, optional): Stop loss price. The decimal places of price and the price step can be returned by the [Get Symbol Info](https://www.bitget.com/api-doc/spot/market/Get-Symbols) interface.
                executeStopLossPrice (str, optional): Stop loss execute price. The decimal places of price and the price step can be returned by the [Get Symbol Info](https://www.bitget.com/api-doc/spot/market/Get-Symbols) interface.

        Returns:
            dict: Bitget API JSON response containing lists of successful and failed operations.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/trade/batch-cancel-replace-order"
        body = {"orderList": orderList}
        return await self.client._send_request("POST", request_path, body=body)

    async def cancel_order(self, symbol, orderId=None, clientOid=None, tpslType=None):
        """
        Cancel Order.

        Args:
            symbol (str): Trading pair name, e.g. BTCUSDT. It is not required when `tpslType` is `tpsl`.
            tpslType (str, optional): Order type (`normal` or `tpsl`). Default: `normal`.
            orderId (str, optional): Order ID. Either `orderId` or `clientOid` is required. It's required when `tpslType` is `tpsl`.
            clientOid (str, optional): Client Order ID. Either `orderId` or `clientOid` is required.

        Returns:
            dict: Bitget API JSON response containing order ID and client customized ID.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/trade/cancel-order"
        body = {"symbol": symbol}
        if orderId:
            body["orderId"] = orderId
        if clientOid:
            body["clientOid"] = clientOid
        if tpslType:
            body["tpslType"] = tpslType
        return await self.client._send_request("POST", request_path, body=body)

    async def batch_cancel_orders(self, orderList, symbol=None, batchMode=None):
        """
        Batch Cancel Orders.

        Args:
            orderList (list): Order ID List, maximum length: 50. Each item in the list should be a dictionary containing either `orderId` (str, optional) or `clientOid` (str, optional).
            symbol (str, optional): Trading pair name, e.g. BTCUSDT.
            batchMode (str, optional): Batch order mode (`single` or `multiple`). `single`: single currency mode, default single currency mode. `multiple`: cross-currency mode. If single mode, the symbol in orderlist will be ignored. If multiple mode, the symbol in orderlist is not allowed to be null, and the symbol in orderlist is required. Symbol outside orderlist will be ignored.

        Returns:
            dict: Bitget API JSON response containing lists of successful and failed order cancellations.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/trade/batch-cancel-order"
        body = {"orderList": orderList}
        if symbol:
            body["symbol"] = symbol
        if batchMode:
            body["batchMode"] = batchMode
        return await self.client._send_request("POST", request_path, body=body)

    async def batch_place_orders(self, orderList, symbol=None, batchMode=None):
        """
        Batch Place Orders.

        Args:
            orderList (list): Collection of placing orders, maximum length: 50. Each item in the list should be a dictionary with the following keys:
                symbol (str, optional): Trading pair name, e.g. BTCUSDT.
                side (str): Order Direction (`buy` or `sell`).
                orderType (str): Order type (`limit` or `market`).
                force (str): Execution strategy (It will be invalid when `orderType` is `market`). `gtc`: Normal limit order, good till cancelled. `post_only`: Post only. `fok`: Fill or kill. `ioc`: Immediate or cancel.
                price (str, optional): Limit price. The decimal places of price and the price step can be returned by the [Get Symbol Info](https://www.bitget.com/api-doc/spot/market/Get-Symbols) interface.
                size (str): Amount. For **Limit and Market-Sell** orders, it represents the number of **base coins**. For **Market-Buy** orders, it represents the number of **quote coins**. The decimal places of amount can be got trough [Get Symbol Info](https://www.bitget.com/api-doc/spot/market/Get-Symbols) interface.
                clientOid (str, optional): Customed order ID.
                stpMode (str, optional): STP Mode (`none`, `cancel_taker`, `cancel_maker`, `cancel_both`).
                presetTakeProfitPrice (str, optional): Take profit price. The decimal places of price and the price step can be returned by the [Get Symbol Info](https://www.bitget.com/api-doc/spot/market/Get-Symbols) interface.
                executeTakeProfitPrice (str, optional): Take profit execute price. The decimal places of price and the price step can be returned by the [Get Symbol Info](https://www.bitget.com/api-doc/spot/market/Get-Symbols) interface.
                presetStopLossPrice (str, optional): Stop loss price. The decimal places of price and the price step can be returned by the [Get Symbol Info](https://www.bitget.com/api-doc/spot/market/Get-Symbols) interface.
                executeStopLossPrice (str, optional): Stop loss execute price. The decimal places of price and the price step can be returned by the [Get Symbol Info](https://www.bitget.com/api-doc/spot/market/Get-Symbols) interface.
            symbol (str, optional): Trading pair name, e.g. BTCUSDT.
            batchMode (str, optional): Batch order mode (`single` or `multiple`). `single`: single currency mode, default single currency mode. `multiple`: cross-currency mode. If single mode, the symbol in orderlist will be ignored. If multiple mode, the symbol in orderlist is not allowed to be null, and the symbol in orderlist is required. Symbol outside orderlist will be ignored.

        Returns:
            dict: Bitget API JSON response containing lists of successful and failed orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/trade/batch-orders"
        body = {"orderList": orderList}
        if symbol:
            body["symbol"] = symbol
        if batchMode:
            body["batchMode"] = batchMode
        return await self.client._send_request("POST", request_path, body=body)

    async def cancel_order_by_symbol(self, symbol):
        """
        Cancel order by symbol.

        Args:
            symbol (str): Trading pair name, e.g. BTCUSDT.

        Returns:
            dict: Bitget API JSON response containing the cancelled symbol. (This request is executed asynchronously. If you need to know the result, please query the Get History Orders endpoint.)

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/trade/cancel-symbol-order"
        body = {"symbol": symbol}
        return await self.client._send_request("POST", request_path, body=body)

    async def cancel_plan_order(self, orderId=None, clientOid=None):
        """
        Cancel Plan order.

        Args:
            orderId (str, optional): Either `orderId` or `clientOid` is required.
            clientOid (str, optional): Either `orderId` or `clientOid` is required.

        Returns:
            dict: Bitget API JSON response containing the result of the operation.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/trade/cancel-plan-order"
        body = {}
        if orderId:
            body["orderId"] = orderId
        if clientOid:
            body["clientOid"] = clientOid
        return await self.client._send_request("POST", request_path, body=body)

    async def get_order_info(self, orderId=None, clientOid=None, requestTime=None, receiveWindow=None):
        """
        Get Order Info.

        Args:
            orderId (str, optional): Either Order ID or `clientOids` is required.
            clientOid (str, optional): Either Client customized ID or `orderId` is required.
            requestTime (str, optional): Request Time, Unix millisecond timestamp.
            receiveWindow (str, optional): Valid window period Unix millisecond timestamp.

        Returns:
            dict: Bitget API JSON response containing order information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/trade/orderInfo"
        params = {}
        if orderId:
            params["orderId"] = orderId
        if clientOid:
            params["clientOid"] = clientOid
        if requestTime:
            params["requestTime"] = requestTime
        if receiveWindow:
            params["receiveWindow"] = receiveWindow
        return await self.client._send_request("GET", request_path, params=params)

    async def get_current_orders(self, symbol=None, startTime=None, endTime=None, idLessThan=None, limit=None, orderId=None, tpslType=None, requestTime=None, receiveWindow=None):
        """
        Get Unfilled Orders.

        Args:
            symbol (str, optional): Trading pair.
            startTime (str, optional): The record start time for the query. Unix millisecond timestamp, e.g. 1690196141868.
            endTime (str, optional): The end time of the record for the query. Unix millisecond timestamp, e.g. 1690196141868.
            idLessThan (str, optional): Requests the content on the page before this ID (older data), the value input should be the orderId of the corresponding interface.
            limit (str, optional): Limit number default 100 max 100.
            orderId (str, optional): OrderId.
            tpslType (str, optional): Order type (`normal` or `tpsl`). Default: `normal`.
            requestTime (str, optional): Request Time Unix millisecond timestamp.
            receiveWindow (str, optional): Valid window period Unix millisecond timestamp.

        Returns:
            dict: Bitget API JSON response containing current orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/trade/unfilled-orders"
        params = {}
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
        if orderId:
            params["orderId"] = orderId
        if tpslType:
            params["tpslType"] = tpslType
        if requestTime:
            params["requestTime"] = requestTime
        if receiveWindow:
            params["receiveWindow"] = receiveWindow
        return await self.client._send_request("GET", request_path, params=params)

    async def get_history_orders(self, symbol=None, startTime=None, endTime=None, idLessThan=None, limit=None, orderId=None, tpslType=None, requestTime=None, receiveWindow=None):
        """
        Get History Orders (It only supports to get the data within 90days. The older data can be downloaded from web).

        Args:
            symbol (str, optional): Trading pair.
            startTime (str, optional): The record start time for the query. Unix millisecond timestamp, e.g. 1690196141868. (For Managed Sub-Account, the StartTime cannot be earlier than the binding time).
            endTime (str, optional): The end time of the record for the query. Unix millisecond timestamp, e.g. 1690196141868.
            idLessThan (str, optional): Requests the content on the page before this ID (older data), the value input should be the orderId of the corresponding interface.
            limit (str, optional): Limit number default 100 max 100.
            orderId (str, optional): OrderId.
            tpslType (str, optional): Order type (`normal` or `tpsl`). Default: `normal`.
            requestTime (str, optional): Request Time Unix millisecond timestamp.
            receiveWindow (str, optional): Valid window period Unix millisecond timestamp.

        Returns:
            dict: Bitget API JSON response containing history orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/trade/history-orders"
        params = {}
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
        if orderId:
            params["orderId"] = orderId
        if tpslType:
            params["tpslType"] = tpslType
        if requestTime:
            params["requestTime"] = requestTime
        if receiveWindow:
            params["receiveWindow"] = receiveWindow
        return await self.client._send_request("GET", request_path, params=params)

    async def get_fills(self, symbol=None, orderId=None, startTime=None, endTime=None, limit=None, idLessThan=None):
        """
        Get Fills (It only supports to get the data within 90days. The older data can be downloaded from web).

        Args:
            symbol (str, optional): Trading pair name.
            orderId (str, optional): Order ID.
            startTime (str, optional): The start time of the orders, i.e. to get orders after that timestamp Unix millisecond timestamp, e.g. 1690196141868. (For Managed Sub-Account, the StartTime cannot be earlier than the binding time).
            endTime (str, optional): The end time of a fulfilled order, i.e., get orders prior to that timestamp Unix millisecond timestamp, e.g. 1690196141868. The interval between startTime and endTime must not exceed 90 days.
            limit (str, optional): Number of results returned: Default: 100, max 100.
            idLessThan (str, optional): Requests the content on the page before this ID (older data), the value input should be the tradeId of the corresponding interface.

        Returns:
            dict: Bitget API JSON response containing fills information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/trade/fills"
        params = {}
        if symbol:
            params["symbol"] = symbol
        if orderId:
            params["orderId"] = orderId
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def place_plan_order(self, symbol, side, triggerPrice, orderType, size, executePrice=None, planType=None, triggerType=None, clientOid=None, stpMode=None):
        """
        Place plan order.

        Args:
            symbol (str): Trading pair name, e.g. BTCUSDT.
            side (str): Direction (`buy` or `sell`).
            triggerPrice (str): Trigger price.
            orderType (str): Order type (`limit` or `market`).
            size (str): Quantity to buy. If `planType`=`amount`, it is the base coin. If `planType`=`total`, it is the quote coin.
            executePrice (str, optional): Execution price. It's required when `orderType`=`limit`.
            planType (str, optional): Order type (`amount` or `total`). `amount`: By amount of the order (base coin). `total`: By trading volume of the order (quote coin). The default value is `amount`.
            triggerType (str, optional): Trigger type (`fill_price` or `mark_price`).
            clientOid (str, optional): Client customized ID.
            stpMode (str, optional): STP Mode (`none`, `cancel_taker`, `cancel_maker`, `cancel_both`).

        Returns:
            dict: Bitget API JSON response containing order ID and client customized ID.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/trade/place-plan-order"
        body = {
            "symbol": symbol,
            "side": side,
            "triggerPrice": triggerPrice,
            "orderType": orderType,
            "size": size
        }
        if executePrice:
            body["executePrice"] = executePrice
        if planType:
            body["planType"] = planType
        if triggerType:
            body["triggerType"] = triggerType
        if clientOid:
            body["clientOid"] = clientOid
        if stpMode:
            body["stpMode"] = stpMode
        return await self.client._send_request("POST", request_path, body=body)

    async def modify_plan_order(self, triggerPrice, orderType, size, orderId=None, clientOid=None, executePrice=None):
        """
        Modify Plan Order.

        Args:
            triggerPrice (str): Trigger price.
            orderType (str): Order type (`limit` or `market`).
            size (str): Quantity to buy. If `planType`=`amount`, the quote currency is the base coin. If `planType`=`total`, the quote currency is the quote coin.
            orderId (str, optional): Either `orderId` or `clientOid` is required.
            clientOid (str, optional): Either `orderId` or `clientOid` is required.
            executePrice (str, optional): Execution price, cannot be null if `orderType`=`limit`.

        Returns:
            dict: Bitget API JSON response containing order ID and client customized ID.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/trade/modify-plan-order"
        body = {
            "triggerPrice": triggerPrice,
            "orderType": orderType,
            "size": size
        }
        if orderId:
            body["orderId"] = orderId
        if clientOid:
            body["clientOid"] = clientOid
        if executePrice:
            body["executePrice"] = executePrice
        return await self.client._send_request("POST", request_path, body=body)

    async def get_current_plan_orders(self, symbol=None, limit=None, idLessThan=None, startTime=None, endTime=None):
        """
        Get Current Plan Orders.

        Args:
            symbol (str, optional): Trading pair, e.g. BTCUSDT.
            limit (str, optional): Default is 20 Max is 100.
            idLessThan (str, optional): Requests the content on the page before this ID (older data), the value input should be the orderId of the corresponding interface.
            startTime (str, optional): The start time of the record for the query. Unix millisecond timestamp, e.g. 1690196141868. The `startTime` and `endTime` should be within 90 days.
            endTime (str, optional): The end time of the record for the query. Unix millisecond timestamp, e.g. 1690196141868. The `startTime` and `endTime` should be within 90 days.

        Returns:
            dict: Bitget API JSON response containing current plan orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/trade/current-plan-order"
        params = {}
        if symbol:
            params["symbol"] = symbol
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        return await self.client._send_request("GET", request_path, params=params)

    async def get_plan_sub_order(self, planOrderId):
        """
        Get Plan Sub Order.

        Args:
            planOrderId (str): Plan Order ID.

        Returns:
            dict: Bitget API JSON response containing plan sub order information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/trade/plan-sub-order"
        params = {"planOrderId": planOrderId}
        return await self.client._send_request("GET", request_path, params=params)

    def get_history_plan_orders(self, symbol, startTime, endTime, limit=None):
        """
        Get History Plan Orders.

        Args:
            symbol (str): Trading pair, e.g. BTCUSDT.
            startTime (str): The start time of the historical trigger orders, i.e. to get orders after that timestamp Unix millisecond timestamp, e.g. 1690196141868. The interval between `startTime` and `endTime` must not exceed 90 days.
            endTime (str): The end time of the historical trigger orders, i.e., getting orders prior to that timestamp Unix millisecond timestamp, e.g. 1690196141868. The interval between `startTime` and `endTime` must not exceed 90 days.
            limit (str, optional): Limit Default is 100, max is 100.

        Returns:
            dict: Bitget API JSON response containing historical plan orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/trade/history-plan-order"
        params = {"symbol": symbol, "startTime": startTime, "endTime": endTime}
        if limit:
            params["limit"] = limit
        return self.client._send_request("GET", request_path, params=params)

    def cancel_plan_orders_in_batch(self, symbolList=None):
        """
        Cancel Plan Orders in Batch.

        Args:
            symbolList (list, optional): Collection of trading pairs: ["BTCUSDT", "ETHUSDT"]. If no value is set, all spot trigger orders will be cancelled.

        Returns:
            dict: Bitget API JSON response containing lists of successful and unsuccessful cancelled orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v2/spot/trade/batch-cancel-plan-order"
        body = {}
        if symbolList:
            body["symbolList"] = symbolList
        return self.client._send_request("POST", request_path, body=body)
