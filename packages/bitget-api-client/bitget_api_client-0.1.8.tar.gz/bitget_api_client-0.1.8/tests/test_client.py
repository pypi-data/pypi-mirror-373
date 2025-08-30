import unittest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from bitget_api_client.client import BitgetApiClient, Affiliate, Broker, Common, Contract, CopyTrading, Earn, Instloan, Margin, Spot, Uta

class MockResponse:
    def __init__(self, status, json_data):
        self.status = status
        self._json_data = json_data
        self.json = AsyncMock(return_value=self._json_data)

    def raise_for_status(self):
        pass

class TestBitgetApiClient(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.api_key = "test_api_key"
        self.secret_key = "test_secret_key"
        self.passphrase = "test_passphrase"
        self.client = BitgetApiClient(self.api_key, self.secret_key, self.passphrase)

    async def asyncTearDown(self):
        await self.client.close()

    async def test_client_initialization(self):
        await self.asyncSetUp()
        self.assertEqual(self.client.api_key, self.api_key)
        self.assertEqual(self.client.secret_key, self.secret_key)
        self.assertEqual(self.client.passphrase, self.passphrase)
        self.assertEqual(self.client.base_url, "https://api.bitget.com")
        await self.asyncTearDown()

    @patch('aiohttp.ClientSession.get')
    async def test_send_request_get(self, mock_get):
        await self.asyncSetUp()
        mock_response = MockResponse(200, {"code": "00000", "msg": "success"})
        mock_get.return_value.__aenter__.return_value = mock_response

        response = await self.client._send_request("GET", "/test_path", params={"param1": "value1"})
        self.assertEqual(response, {"code": "00000", "msg": "success"})
        mock_get.assert_called_once()
        await self.asyncTearDown()

    @patch('aiohttp.ClientSession.post')
    async def test_send_request_post(self, mock_post):
        await self.asyncSetUp()
        mock_response = MockResponse(200, {"code": "00000", "msg": "success"})
        mock_post.return_value.__aenter__.return_value = mock_response

        response = await self.client._send_request("POST", "/test_path", body={"key": "value"})
        self.assertEqual(response, {"code": "00000", "msg": "success"})
        mock_post.assert_called_once()
        await self.asyncTearDown()

class TestAffiliate(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_client = AsyncMock()
        self.affiliate = Affiliate(self.mock_client)

    async def asyncTearDown(self):
        pass

    async def test_affiliate_initialization(self):
        await self.asyncSetUp()
        self.assertEqual(self.affiliate.client, self.mock_client)
        await self.asyncTearDown()

    async def test_get_agent_direct_commissions(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {"commissionList": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.affiliate.get_agent_direct_commissions(startTime="123", endTime="456", uid="789")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/broker/v1/agent/customer-commissions",
            params={'startTime': '123', 'endTime': '456', 'uid': '789'}
        )
        await self.asyncTearDown()

    async def test_get_agent_customer_trade_volume_list(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.affiliate.get_agent_customer_trade_volume_list(pageNo="1", pageSize="500", uid="123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/broker/v1/agent/customerTradeVolumnList",
            body={'pageNo': '1', 'pageSize': '500', 'uid': '123'}
        )
        await self.asyncTearDown()

    async def test_get_agent_customer_list(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.affiliate.get_agent_customer_list(pageNo="1", pageSize="500", uid="123", referralCode="abc")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/broker/v1/agent/customerList",
            body={'pageNo': '1', 'pageSize': '500', 'uid': '123', 'referralCode': 'abc'}
        )
        await self.asyncTearDown()

    async def test_get_agent_customer_kyc_result(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {"userList": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.affiliate.get_agent_customer_kyc_result(startTime="123", endTime="456", uid="789")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/broker/v1/agent/customer-kyc-result",
            params={'startTime': '123', 'endTime': '456', 'uid': '789'}
        )
        await self.asyncTearDown()

    async def test_get_agent_customer_deposit_list(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.affiliate.get_agent_customer_deposit_list(pageNo="1", pageSize="500", uid="123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/broker/v1/agent/customerDepositList",
            body={'pageNo': '1', 'pageSize': '500', 'uid': '123'}
        )
        await self.asyncTearDown()

    async def test_get_agent_customer_assets_list(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.affiliate.get_agent_customer_assets_list(pageNo="1", pageSize="500", uid="123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/broker/v1/agent/customerAccountAssetsList",
            body={'pageNo': '1', 'pageSize': '500', 'uid': '123'}
        )
        await self.asyncTearDown()

    async def test_get_agent_commission_detail(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {"commissionList": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.affiliate.get_agent_commission_detail(startTime="123", endTime="456", limit="10", idLessThan="789")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/broker/v1/agent/commission-distribution",
            params={'startTime': '123', 'endTime': '456', 'limit': '10', 'idLessThan': '789'}
        )
        await self.asyncTearDown()

class TestBroker(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_client = AsyncMock()
        self.broker = Broker(self.mock_client)

    async def asyncTearDown(self):
        pass

    async def test_broker_initialization(self):
        await self.asyncSetUp()
        self.assertEqual(self.broker.client, self.mock_client)
        await self.asyncTearDown()

    async def test_create_subaccount(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {"subUid": "123", "subaccountName": "test@example.com"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.broker.create_subaccount(subaccountName="test@example.com", label="test_label")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/broker/account/create-subaccount",
            body={'subaccountName': 'test@example.com', 'label': 'test_label'}
        )
        await self.asyncTearDown()

    async def test_create_subaccount_apikey(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {"subUid": "123", "apiKey": "abc", "secretKey": "xyz"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.broker.create_subaccount_apikey(
            subUid="123",
            passphrase="pass123",
            label="test_key",
            ipList=["1.1.1.1"],
            permType="read_and_write",
            permList=["spot_trade"]
        )
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/broker/manage/create-subaccount-apikey",
            body={
                'subUid': '123',
                'passphrase': 'pass123',
                'label': 'test_key',
                'ipList': ['1.1.1.1'],
                'permType': 'read_and_write',
                'permList': ['spot_trade']
            }
        )
        await self.asyncTearDown()

    async def test_create_subaccount_deposit_address(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {"address": "0x123", "coin": "ETH"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.broker.create_subaccount_deposit_address(subUid="123", coin="ETH", chain="ERC20")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/broker/account/subaccount-address",
            body={'subUid': '123', 'coin': 'ETH', 'chain': 'ERC20'}
        )
        await self.asyncTearDown()

    async def test_delete_subaccount_apikey(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": "success"}
        self.mock_client._send_request.return_value = expected_response

        response = await self.broker.delete_subaccount_apikey(subUid="123", apiKey="test_api_key")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/broker/manage/delete-subaccount-apikey",
            body={'subUid': '123', 'apiKey': 'test_api_key'}
        )
        await self.asyncTearDown()

    async def test_get_broker_info(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {"subAccountSize": "1", "maxSubAccountSize": "10"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.broker.get_broker_info()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/broker/account/info",
            params={}
        )
        await self.asyncTearDown()

    async def test_get_broker_subaccounts(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.broker.get_broker_subaccounts(startTime="123", endTime="456", pageNo="1", pageSize="10")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/broker/v2/subaccounts",
            params={'startTime': '123', 'endTime': '456', 'pageNo': '1', 'pageSize': '10'}
        )
        await self.asyncTearDown()

    async def test_get_broker_subaccounts_commissions(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.broker.get_broker_subaccounts_commissions(startTime="123", endTime="456", pageNo="1", pageSize="10", bizType="spot", subBizType="spot_trade")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/broker/v2/commissions",
            params={'startTime': '123', 'endTime': '456', 'pageNo': '1', 'pageSize': '10', 'bizType': 'spot', 'subBizType': 'spot_trade'}
        )
        await self.asyncTearDown()

    async def test_get_broker_trade_volume(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.broker.get_broker_trade_volume(startTime="123", endTime="456", pageNo="1", pageSize="10")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/broker/v2/trade-volume",
            params={'startTime': '123', 'endTime': '456', 'pageNo': '1', 'pageSize': '10'}
        )
        await self.asyncTearDown()

    async def test_get_subaccounts_deposit_and_withdrawal_records(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {"list": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.broker.get_subaccounts_deposit_and_withdrawal_records(startTime="123", endTime="456", limit="10", idLessThan="789", type="deposit")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/broker/all-sub-deposit-withdrawal",
            params={'startTime': '123', 'endTime': '456', 'limit': '10', 'idLessThan': '789', 'type': 'deposit'}
        )
        await self.asyncTearDown()

    async def test_get_subaccount_apikey(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.broker.get_subaccount_apikey(subUid="123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/broker/manage/subaccount-apikey-list",
            params={'subUid': '123'}
        )
        await self.asyncTearDown()

    async def test_get_subaccount_email(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {"subaccountEmail": "test@example.com"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.broker.get_subaccount_email(subUid="123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/broker/account/subaccount-email",
            params={'subUid': '123'}
        )
        await self.asyncTearDown()

    async def test_get_subaccount_future_assets(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {"assetsList": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.broker.get_subaccount_future_assets(subUid="123", productType="USDT-FUTURES")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/broker/account/subaccount-future-assets",
            params={'subUid': '123', 'productType': 'USDT-FUTURES'}
        )
        await self.asyncTearDown()

    async def test_get_subaccount_list(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {"subList": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.broker.get_subaccount_list(limit="10", idLessThan="123", status="normal", startTime="456", endTime="789")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/broker/account/subaccount-list",
            params={'limit': '10', 'idLessThan': '123', 'status': 'normal', 'startTime': '456', 'endTime': '789'}
        )
        await self.asyncTearDown()

    async def test_get_subaccount_spot_assets(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {"assetsList": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.broker.get_subaccount_spot_assets(subUid="123", coin="BTC", assetType="hold_only")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/broker/account/subaccount-spot-assets",
            params={'subUid': '123', 'coin': 'BTC', 'assetType': 'hold_only'}
        )
        await self.asyncTearDown()

    async def test_modify_subaccount(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {"subUid": "123"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.broker.modify_subaccount(subUid="123", permList=["transfer"], status="normal", language="en_US")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/broker/account/modify-subaccount",
            body={'subUid': '123', 'permList': ['transfer'], 'status': 'normal', 'language': 'en_US'}
        )
        await self.asyncTearDown()

    async def test_modify_subaccount_apikey(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.broker.modify_subaccount_apikey(
            subUid="123",
            apiKey="test_api_key",
            passphrase="test_passphrase",
            label="new_label",
            ipList=["192.168.1.1"],
            permType="read_and_write",
            permList=["spot_trade"]
        )
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/broker/manage/modify-subaccount-apikey",
            body={
                'subUid': '123',
                'apiKey': 'test_api_key',
                'passphrase': 'test_passphrase',
                'label': 'new_label',
                'ipList': ['192.168.1.1'],
                'permType': 'read_and_write',
                'permList': ['spot_trade']
            }
        )
        await self.asyncTearDown()

    async def test_modify_subaccount_email(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": "success"}
        self.mock_client._send_request.return_value = expected_response

        response = await self.broker.modify_subaccount_email(subUid="123", subaccountEmail="test@example.com")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/broker/account/modify-subaccount-email",
            body={'subUid': '123', 'subaccountEmail': 'test@example.com'}
        )
        await self.asyncTearDown()

    async def test_sub_deposit_auto_transfer(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": "success"}
        self.mock_client._send_request.return_value = expected_response

        response = await self.broker.sub_deposit_auto_transfer(subUid="123", coin="USDT", toAccountType="spot")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/broker/account/sub-deposit-auto-transfer",
            body={'subUid': '123', 'coin': 'USDT', 'toAccountType': 'spot'}
        )
        await self.asyncTearDown()

    async def test_sub_deposit_records(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.broker.sub_deposit_records(orderId="123", userId="456", startTime="789", endTime="1011", limit="10", idLessThan="1213")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/broker/subaccount-deposit",
            params={'orderId': '123', 'userId': '456', 'startTime': '789', 'endTime': '1011', 'limit': '10', 'idLessThan': '1213'}
        )
        await self.asyncTearDown()

    async def test_sub_withdrawal_records(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {"resultList": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.broker.sub_withdrawal_records(orderId="123", userId="456", startTime="789", endTime="1011", limit="10", idLessThan="1213")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/broker/subaccount-withdrawal",
            params={'orderId': '123', 'userId': '456', 'startTime': '789', 'endTime': '1011', 'limit': '10', 'idLessThan': '1213'}
        )
        await self.asyncTearDown()

    async def test_subaccount_withdrawal(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {"orderId": "123"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.broker.subaccount_withdrawal(subUid="123", coin="USDT", dest="on_chain", address="0xabc", amount="100", chain="ERC20", tag="tag1", clientOid="oid1")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/broker/account/subaccount-withdrawal",
            body={'subUid': '123', 'coin': 'USDT', 'dest': 'on_chain', 'address': '0xabc', 'amount': '100', 'chain': 'ERC20', 'tag': 'tag1', 'clientOid': 'oid1'}
        )
        await self.asyncTearDown()

class TestCommon(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_client = AsyncMock()
        self.common = Common(self.mock_client)

    async def asyncTearDown(self):
        pass

    async def test_common_initialization(self):
        await self.asyncSetUp()
        self.assertEqual(self.common.client, self.mock_client)
        await self.asyncTearDown()

    async def test_get_assets_overview(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.get_assets_overview()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/account/all-account-balance",
            params={}
        )
        await self.asyncTearDown()

    async def test_get_bot_account_assets(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.get_bot_account_assets(accountType="futures")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/account/bot-assets",
            params={'accountType': 'futures'}
        )
        await self.asyncTearDown()

    async def test_get_funding_assets(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.get_funding_assets(coin="USDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/account/funding-assets",
            params={'coin': 'USDT'}
        )
        await self.asyncTearDown()

    async def test_batch_create_virtual_subaccount_and_apikey(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        subaccounts_data = [{
            "subAccountName": "test_sub",
            "passphrase": "password123",
            "label": "test_label",
            "ipList": ["192.168.1.1"],
            "permList": ["spot_trade"]
        }]
        response = await self.common.batch_create_virtual_subaccount_and_apikey(subaccounts_data)
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/user/batch-create-subaccount-and-apikey",
            body=subaccounts_data
        )
        await self.asyncTearDown()

    async def test_get_bgb_convert_coins(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.get_bgb_convert_coins()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/market/bgb-convert-coins",
            params={}
        )
        await self.asyncTearDown()

    async def test_convert(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.convert(fromCoin="USDT", fromCoinSize="100", cnvtPrice="1.0", toCoin="BTC", toCoinSize="0.0001", traceId="123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/convert/trade",
            body={'fromCoin': 'USDT', 'fromCoinSize': '100', 'cnvtPrice': '1.0', 'toCoin': 'BTC', 'toCoinSize': '0.0001', 'traceId': '123'}
        )
        await self.asyncTearDown()

    async def test_convert_bgb(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.convert_bgb(coinList=["EOS", "GROK"])
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/convert/bgb-convert",
            body={'coinList': ['EOS', 'GROK']}
        )
        await self.asyncTearDown()

    async def test_create_virtual_subaccount(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.create_virtual_subaccount(subAccountList=["test1", "test2"])
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/user/create-virtual-subaccount",
            body={'subAccountList': ['test1', 'test2']}
        )
        await self.asyncTearDown()

    async def test_create_virtual_subaccount_apikey(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.create_virtual_subaccount_apikey(
            subAccountUid="123",
            passphrase="pass123",
            label="test_label",
            ipList=["192.168.1.1"],
            permType="read_and_write",
            permList=["spot_trade"]
        )
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/user/create-virtual-subaccount-apikey",
            body={
                'subAccountUid': '123',
                'passphrase': 'pass123',
                'label': 'test_label',
                'ipList': ['192.168.1.1'],
                'permType': 'read_and_write',
                'permList': ['spot_trade']
            }
        )
        await self.asyncTearDown()

    async def test_get_convert_history(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.get_convert_history(startTime="123", endTime="456", limit="10")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/convert/record",
            params={'startTime': '123', 'endTime': '456', 'limit': '10'}
        )
        await self.asyncTearDown()

    async def test_get_futures_transaction_records(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.get_futures_transaction_records(startTime="123", endTime="456", productType="USDT-FUTURES", marginCoin="USDT", limit="10", idLessThan="789")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/tax/future-record",
            params={'startTime': '123', 'endTime': '456', 'productType': 'USDT-FUTURES', 'marginCoin': 'USDT', 'limit': '10', 'idLessThan': '789'}
        )
        await self.asyncTearDown()

    async def test_get_margin_transaction_history(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.get_margin_transaction_history(startTime="123", endTime="456", marginType="crossed", coin="BTC", limit="10", idLessThan="789")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/tax/margin-record",
            params={'startTime': '123', 'endTime': '456', 'marginType': 'crossed', 'coin': 'BTC', 'limit': '10', 'idLessThan': '789'}
        )
        await self.asyncTearDown()

    async def test_get_p2p_transaction_records(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.get_p2p_transaction_records(startTime="123", endTime="456", coin="USDT", limit="10", idLessThan="789")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/tax/p2p-record",
            params={'startTime': '123', 'endTime': '456', 'coin': 'USDT', 'limit': '10', 'idLessThan': '789'}
        )
        await self.asyncTearDown()

    async def test_query_announcements(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.query_announcements(language="en_US", annType="latest_news", startTime="123", endTime="456", cursor="789", limit="10")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/public/annoucements",
            params={'language': 'en_US', 'annType': 'latest_news', 'startTime': '123', 'endTime': '456', 'cursor': '789', 'limit': '10'}
        )

    async def test_get_spot_transaction_records(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.get_spot_transaction_records(startTime="123", endTime="456", coin="USDT", limit="10", idLessThan="789")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/tax/spot-record",
            params={'startTime': '123', 'endTime': '456', 'coin': 'USDT', 'limit': '10', 'idLessThan': '789'}
        )

    async def test_get_business_line_all_symbol_trade_rate(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.get_business_line_all_symbol_trade_rate(symbol="BTCUSDT", businessType="mix")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/common/all-trade-rate",
            params={'symbol': 'BTCUSDT', 'businessType': 'mix'}
        )

    async def test_get_convert_coins(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.get_convert_coins()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/convert/currencies",
            params={}
        )

    async def test_get_futures_active_buy_sell_volume_data(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.get_futures_active_buy_sell_volume_data(symbol="BTCUSDT", period="5m")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/market/taker-buy-sell",
            params={'symbol': 'BTCUSDT', 'period': '5m'}
        )

    async def test_get_futures_active_long_short_account_data(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.get_futures_active_long_short_account_data(symbol="BTCUSDT", period="5m")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/market/account-long-short",
            params={'symbol': 'BTCUSDT', 'period': '5m'}
        )

    async def test_get_futures_active_long_short_position_data(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.get_futures_active_long_short_position_data(symbol="BTCUSDT", period="5m")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/market/position-long-short",
            params={'symbol': 'BTCUSDT', 'period': '5m'}
        )

    async def test_get_futures_long_and_short_ratio_data(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.get_futures_long_and_short_ratio_data(symbol="BTCUSDT", period="5m")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/market/long-short",
            params={'symbol': 'BTCUSDT', 'period': '5m'}
        )

    async def test_get_leveraged_long_short_ratio_data(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.get_leveraged_long_short_ratio_data(symbol="BTCUSDT", period="24h", coin="BTC")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/margin/market/long-short-ratio",
            params={'symbol': 'BTCUSDT', 'period': '24h', 'coin': 'BTC'}
        )

    async def test_get_isolated_margin_borrowing_ratio_data(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.get_isolated_margin_borrowing_ratio_data(symbol="BTCUSDT", period="24h")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/market/isolated-borrow-rate",
            params={'symbol': 'BTCUSDT', 'period': '24h'}
        )

    async def test_get_margin_loan_growth_rate_data(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.get_margin_loan_growth_rate_data(symbol="BTCUSDT", period="24h")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/market/margin-loan-ratio",
            params={'symbol': 'BTCUSDT', 'period': '24h'}
        )

    async def test_get_merchant_advertisement_list(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.get_merchant_advertisement_list(side="buy", coin="USDT", fiat="USD", limit="10")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/p2p/advList",
            params={'side': 'buy', 'coin': 'USDT', 'fiat': 'USD', 'limit': '10'}
        )

    async def test_get_merchant_information(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.get_merchant_information()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/p2p/merchantInfo",
            params={}
        )

    async def test_get_merchant_p2p_orders(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.get_merchant_p2p_orders(startTime="123", advNo="test_adv_no", endTime="456", limit="10", status="success", side="buy", coin="USDT", fiat="USD")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/p2p/orderList",
            params={'startTime': '123', 'advNo': 'test_adv_no', 'endTime': '456', 'limit': '10', 'status': 'success', 'side': 'buy', 'coin': 'USDT', 'fiat': 'USD'}
        )

    async def test_get_p2p_merchant_list(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.get_p2p_merchant_list(online="yes", idLessThan="123", limit="10")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/p2p/merchantList",
            params={'online': 'yes', 'idLessThan': '123', 'limit': '10'}
        )

    async def test_get_quoted_price(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.get_quoted_price(fromCoin="USDT", toCoin="ETH", fromCoinSize="100", toCoinSize="0.05")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/convert/quoted-price",
            params={'fromCoin': 'USDT', 'toCoin': 'ETH', 'fromCoinSize': '100', 'toCoinSize': '0.05'}
        )

    async def test_get_server_time(self):
        expected_response = {"code": "00000", "msg": "success", "data": "1234567890"}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.get_server_time()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/public/time",
            params={}
        )

    async def test_get_spot_fund_flow(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.get_spot_fund_flow(symbol="BTCUSDT", period="15m")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/market/fund-flow",
            params={'symbol': 'BTCUSDT', 'period': '15m'}
        )

    async def test_get_spot_whale_net_flow_data(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.get_spot_whale_net_flow_data(symbol="BTCUSDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/market/fund-net-flow",
            params={'symbol': 'BTCUSDT'}
        )

    async def test_get_trade_data_support_symbols(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.get_trade_data_support_symbols()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/market/support-symbols",
            params={}
        )





    

    async def test_get_virtual_subaccounts(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.get_virtual_subaccounts()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/user/virtual-subaccount-list",
            params={}
        )

    async def test_get_subaccount_apikey_list(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.get_subaccount_apikey_list(subAccountUid="123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/user/virtual-subaccount-apikey-list",
            params={'subAccountUid': '123'}
        )

    async def test_modify_virtual_subaccount(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.modify_virtual_subaccount(subAccountUid="123", status="normal", permList=["read"])
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/user/modify-virtual-subaccount",
            body={'subAccountUid': '123', 'status': 'normal', 'permList': ['read']}
        )

    async def test_modify_virtual_subaccount_apikey(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.common.modify_virtual_subaccount_apikey(
            subAccountUid="123",
            subAccountApiKey="test_api_key",
            passphrase="test_passphrase",
            label="new_label",
            ipList=["192.168.1.1"],
            permList=["spot_trade"]
        )
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/user/modify-virtual-subaccount-apikey",
            body={
                'subAccountUid': '123',
                'subAccountApiKey': 'test_api_key',
                'passphrase': 'test_passphrase',
                'label': 'new_label',
                'ipList': ['192.168.1.1'],
                'permList': ['spot_trade']
            }
        )

class TestContract(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_client = AsyncMock()
        self.contract = Contract(self.mock_client)

    async def asyncTearDown(self):
        pass

    async def test_contract_initialization(self):
        await self.asyncSetUp()
        self.assertEqual(self.contract.client, self.mock_client)
        await self.asyncTearDown()

    async def test_adjust_position_margin(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": ""}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.adjust_position_margin(symbol="BTCUSDT", productType="USDT-FUTURES", marginCoin="USDT", holdSide="long", amount="20")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/mix/account/set-margin",
            body={'symbol': 'BTCUSDT', 'productType': 'USDT-FUTURES', 'marginCoin': 'USDT', 'holdSide': 'long', 'amount': '20'}
        )
        await self.asyncTearDown()

    async def test_batch_cancel(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.batch_cancel(symbol="BTCUSDT", productType="USDT-FUTURES", orderIdList=[{"orderId": "123"}, {"orderId": "456"}, {"clientOid": "abc"}, {"clientOid": "def"}])
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/mix/order/batch-cancel-orders",
            body={'productType': 'USDT-FUTURES', 'orderIdList': [{'orderId': '123'}, {'orderId': '456'}, {'clientOid': 'abc'}, {'clientOid': 'def'}], 'symbol': 'BTCUSDT'}
        )
        await self.asyncTearDown()

    async def test_batch_order(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        order_list = [{
            "clientOid": "test1",
            "tradeMode": "cross",
            "price": "10000",
            "size": "1",
            "side": "buy",
            "orderType": "limit",
            "force": "gtc"
        }]
        response = await self.contract.batch_order(symbol="BTCUSDT", productType="USDT-FUTURES", marginCoin="USDT", marginMode="isolated", orderList=order_list)
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/mix/order/batch-place-order",
            body={'symbol': 'BTCUSDT', 'productType': 'USDT-FUTURES', 'marginCoin': 'USDT', 'marginMode': 'isolated', 'orderList': order_list}
        )
        await self.asyncTearDown()

    async def test_cancel_all_orders(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.cancel_all_orders(productType="USDT-FUTURES", marginCoin="USDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/mix/order/cancel-all-orders",
            body={'productType': 'USDT-FUTURES', 'marginCoin': 'USDT'}
        )
        await self.asyncTearDown()

    async def test_cancel_order(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.cancel_order(symbol="BTCUSDT", productType="USDT-FUTURES", orderId="123", clientOid="abc", marginCoin="USDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/mix/order/cancel-order",
            body={'symbol': 'BTCUSDT', 'productType': 'USDT-FUTURES', 'orderId': '123', 'clientOid': 'abc', 'marginCoin': 'USDT'}
        )
        await self.asyncTearDown()

    async def test_cancel_trigger_order(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.cancel_trigger_order(productType="USDT-FUTURES", orderIdList=[{"orderId": "123", "clientOid": ""}], symbol="BTCUSDT", marginCoin="USDT", planType="normal_plan")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/mix/order/cancel-plan-order",
            body={'productType': 'USDT-FUTURES', 'orderIdList': [{'orderId': '123', 'clientOid': ''}], 'symbol': 'BTCUSDT', 'marginCoin': 'USDT', 'planType': 'normal_plan'}
        )
        await self.asyncTearDown()

    async def test_change_leverage(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.change_leverage(symbol="BTCUSDT", productType="USDT-FUTURES", leverage="10", marginCoin="USDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/mix/account/set-leverage",
            body={'symbol': 'BTCUSDT', 'productType': 'USDT-FUTURES', 'leverage': '10', 'marginCoin': 'USDT'}
        )
        await self.asyncTearDown()

    async def test_change_margin_mode(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.change_margin_mode(symbol="BTCUSDT", productType="USDT-FUTURES", marginMode="crossed", marginCoin="USDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/mix/account/set-margin-mode",
            body={'symbol': 'BTCUSDT', 'productType': 'USDT-FUTURES', 'marginMode': 'crossed', 'marginCoin': 'USDT'}
        )
        await self.asyncTearDown()

    async def test_change_position_mode(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.change_position_mode(productType="USDT-FUTURES", posMode="one_way_mode")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/mix/account/set-position-mode",
            body={'productType': 'USDT-FUTURES', 'posMode': 'one_way_mode'}
        )

    async def test_change_the_product_line_leverage(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.change_the_product_line_leverage(productType="USDT-FUTURES", leverage="10")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/mix/account/set-all-leverage",
            body={'productType': 'USDT-FUTURES', 'leverage': '10'}
        )

    async def test_flash_close_position(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.flash_close_position(symbol="BTCUSDT", productType="USDT-FUTURES", holdSide="long")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/mix/order/close-positions",
            body={'productType': 'USDT-FUTURES', 'symbol': 'BTCUSDT', 'holdSide': 'long'}
        )

    async def test_get_account_bills(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_account_bills(productType="USDT-FUTURES", marginCoin="USDT", startTime="123", endTime="456", bizType="transfer", bizSubType="deposit", limit="10", idLessThan="789")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/account/account-bill",
            params={'productType': 'USDT-FUTURES', 'marginCoin': 'USDT', 'startTime': '123', 'endTime': '456', 'bizType': 'transfer', 'bizSubType': 'deposit', 'limit': '10', 'idLessThan': '789'}
        )

    async def test_get_account_list(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_account_list(productType="USDT-FUTURES")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/account/accounts",
            params={'productType': 'USDT-FUTURES'}
        )

    async def test_get_single_account(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_single_account(symbol="BTCUSDT", productType="USDT-FUTURES", marginCoin="USDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/account/account",
            params={'symbol': 'BTCUSDT', 'productType': 'USDT-FUTURES', 'marginCoin': 'USDT'}
        )

    async def test_get_subaccount_assets(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_subaccount_assets(productType="USDT-FUTURES")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/account/sub-account-assets",
            params={'productType': 'USDT-FUTURES'}
        )

    async def test_get_usdt_m_futures_interest_history(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_usdt_m_futures_interest_history(productType="USDT-FUTURES", coin="USDT", idLessThan="123", startTime="1678886400000", endTime="1678886400000", limit="100")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/account/interest-history",
            params={'productType': 'USDT-FUTURES', 'coin': 'USDT', 'idLessThan': '123', 'startTime': '1678886400000', 'endTime': '1678886400000', 'limit': '100'}
        )

    async def test_my_estimated_open_count(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.my_estimated_open_count(symbol="BTCUSDT", productType="USDT-FUTURES", marginCoin="USDT", openAmount="5000", openPrice="23189.5", leverage="20")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/account/open-count",
            params={'symbol': 'BTCUSDT', 'productType': 'USDT-FUTURES', 'marginCoin': 'USDT', 'openAmount': '5000', 'openPrice': '23189.5', 'leverage': '20'}
        )

    async def test_set_isolated_position_auto_margin(self):
        expected_response = {"code": "00000", "msg": "success", "data": "success"}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.set_isolated_position_auto_margin(symbol="BTCUSDT", autoMargin="on", marginCoin="USDT", holdSide="long")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/mix/account/set-auto-margin",
            body={'symbol': 'BTCUSDT', 'autoMargin': 'on', 'marginCoin': 'USDT', 'holdSide': 'long'}
        )

    async def test_set_usdt_m_futures_asset_mode(self):
        expected_response = {"code": "00000", "msg": "success", "data": "success"}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.set_usdt_m_futures_asset_mode(productType="USDT-FUTURES", assetMode="union")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/mix/account/set-asset-mode",
            body={'productType': 'USDT-FUTURES', 'assetMode': 'union'}
        )

    async def test_simultaneous_stop_profit_and_stop_loss_plan_orders(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.simultaneous_stop_profit_and_stop_loss_plan_orders(
            marginCoin="USDT",
            productType="USDT-FUTURES",
            symbol="BTCUSDT",
            holdSide="long",
            stopSurplusTriggerPrice="69000",
            stopSurplusTriggerType="mark_price",
            stopSurplusExecutePrice="69001",
            stopLossTriggerPrice="55001",
            stopLossTriggerType="mark_price",
            stopLossExecutePrice="55000"
        )
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/mix/order/place-pos-tpsl",
            body={
                'marginCoin': 'USDT',
                'productType': 'USDT-FUTURES',
                'symbol': 'BTCUSDT',
                'holdSide': 'long',
                'stopSurplusTriggerPrice': '69000',
                'stopSurplusTriggerType': 'mark_price',
                'stopSurplusExecutePrice': '69001',
                'stopLossTriggerPrice': '55001',
                'stopLossTriggerType': 'mark_price',
                'stopLossExecutePrice': '55000'
            }
        )

    async def test_stop_profit_and_stop_loss_plan_orders(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.stop_profit_and_stop_loss_plan_orders(
            marginCoin="USDT",
            productType="USDT-FUTURES",
            symbol="BTCUSDT",
            planType="profit_plan",
            triggerPrice="20000",
            holdSide="long",
            size="0.001",
            triggerType="mark_price",
            executePrice="0"
        )
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/mix/order/place-tpsl-order",
            body={
                'marginCoin': 'USDT',
                'productType': 'USDT-FUTURES',
                'symbol': 'BTCUSDT',
                'planType': 'profit_plan',
                'triggerPrice': '20000',
                'holdSide': 'long',
                'size': '0.001',
                'triggerType': 'mark_price',
                'executePrice': '0'
            }
        )

    async def test_trigger_sub_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.trigger_sub_order(planType="normal_plan", planOrderId="123", productType="USDT-FUTURES")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/order/plan-sub-order",
            params={'planType': 'normal_plan', 'planOrderId': '123', 'productType': 'USDT-FUTURES'}
        )

    async def test_vip_fee_rate(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.vip_fee_rate()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/market/vip-fee-rate",
            params={}
        )

    async def test_get_history_transactions(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_history_transactions(symbol="BTCUSDT", productType="usdt-futures", limit="100", idLessThan="123", startTime="1678886400000", endTime="1678886400000")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/market/fills-history",
            params={'symbol': 'BTCUSDT', 'productType': 'usdt-futures', 'limit': '100', 'idLessThan': '123', 'startTime': '1678886400000', 'endTime': '1678886400000'}
        )

    async def test_place_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.place_order(
            symbol="BTCUSDT",
            productType="USDT-FUTURES",
            marginMode="isolated",
            marginCoin="USDT",
            size="0.001",
            side="buy",
            orderType="limit",
            price="20000",
            tradeSide="open",
            force="gtc",
            clientOid="test_client_oid"
        )
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/mix/order/place-order",
            body={
                'symbol': 'BTCUSDT',
                'productType': 'USDT-FUTURES',
                'marginMode': 'isolated',
                'marginCoin': 'USDT',
                'size': '0.001',
                'side': 'buy',
                'orderType': 'limit',
                'price': '20000',
                'tradeSide': 'open',
                'force': 'gtc',
                'clientOid': 'test_client_oid'
            }
        )

    async def test_place_trigger_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.place_trigger_order(
            planType="normal_plan",
            symbol="BTCUSDT",
            productType="USDT-FUTURES",
            marginMode="isolated",
            marginCoin="USDT",
            size="0.001",
            triggerPrice="20000",
            triggerType="mark_price",
            side="buy",
            orderType="limit",
            price="19900",
            tradeSide="open",
            clientOid="test_client_oid_trigger"
        )
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/mix/order/place-plan-order",
            body={
                'planType': 'normal_plan',
                'symbol': 'BTCUSDT',
                'productType': 'USDT-FUTURES',
                'marginMode': 'isolated',
                'marginCoin': 'USDT',
                'size': '0.001',
                'triggerPrice': '20000',
                'triggerType': 'mark_price',
                'side': 'buy',
                'orderType': 'limit',
                'price': '19900',
                'tradeSide': 'open',
                'clientOid': 'test_client_oid_trigger'
            }
        )

    async def test_reversal(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.reversal(
            symbol="BTCUSDT",
            marginCoin="USDT",
            productType="USDT-FUTURES",
            side="buy",
            size="0.001",
            tradeSide="open",
            clientOid="test_client_oid_reversal"
        )
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/mix/order/click-backhand",
            body={
                'symbol': 'BTCUSDT',
                'marginCoin': 'USDT',
                'productType': 'USDT-FUTURES',
                'side': 'buy',
                'size': '0.001',
                'tradeSide': 'open',
                'clientOid': 'test_client_oid_reversal'
            }
        )

    async def test_get_ticker(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_ticker(symbol="BTCUSDT", productType="USDT-FUTURES")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/market/ticker",
            params={'symbol': 'BTCUSDT', 'productType': 'USDT-FUTURES'}
        )

    async def test_get_all_positions(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_all_positions(productType="USDT-FUTURES", marginCoin="USDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/position/all-position",
            params={'productType': 'USDT-FUTURES', 'marginCoin': 'USDT'}
        )

    async def test_get_all_tickers(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_all_tickers(productType="USDT-FUTURES")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/market/tickers",
            params={'productType': 'USDT-FUTURES'}
        )

    async def test_get_candlestick_data(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_candlestick_data(
            symbol="BTCUSDT",
            productType="USDT-FUTURES",
            granularity="5m",
            startTime="1678886400000",
            endTime="1678886400000",
            kLineType="MARKET",
            limit="100"
        )
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/market/candles",
            params={
                'symbol': 'BTCUSDT',
                'productType': 'USDT-FUTURES',
                'granularity': '5m',
                'startTime': '1678886400000',
                'endTime': '1678886400000',
                'kLineType': 'MARKET',
                'limit': '100'
            }
        )

    async def test_get_contract_oi_limit(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_contract_oi_limit(productType="USDT-FUTURES", symbol="BTCUSDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/market/oi-limit",
            params={'productType': 'USDT-FUTURES', 'symbol': 'BTCUSDT'}
        )

    async def test_get_contract_config(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_contract_config(productType="USDT-FUTURES", symbol="BTCUSDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/market/contracts",
            params={'productType': 'USDT-FUTURES', 'symbol': 'BTCUSDT'}
        )

    async def test_get_current_funding_rate(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_current_funding_rate(productType="USDT-FUTURES", symbol="BTCUSDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/market/current-fund-rate",
            params={'productType': 'USDT-FUTURES', 'symbol': 'BTCUSDT'}
        )

    async def test_get_discount_rate(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_discount_rate()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/market/discount-rate",
            params={}
        )

    

    

    async def test_get_historical_funding_rates(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_historical_funding_rates(
            symbol="BTCUSDT",
            productType="USDT-FUTURES",
            pageSize="20",
            pageNo="1"
        )
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/market/history-fund-rate",
            params={
                'symbol': 'BTCUSDT',
                'productType': 'USDT-FUTURES',
                'pageSize': '20',
                'pageNo': '1'
            }
        )

    async def test_get_historical_index_price_candlestick(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_historical_index_price_candlestick(
            symbol="BTCUSDT",
            productType="USDT-FUTURES",
            granularity="5m",
            startTime="1688824171000",
            endTime="1691329771000",
            limit="100"
        )
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/market/history-index-candles",
            params={
                'symbol': 'BTCUSDT',
                'productType': 'USDT-FUTURES',
                'granularity': '5m',
                'startTime': '1688824171000',
                'endTime': '1691329771000',
                'limit': '100'
            }
        )

    async def test_get_historical_mark_price_candlestick(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_historical_mark_price_candlestick(
            symbol="BTCUSDT",
            productType="USDT-FUTURES",
            granularity="5m",
            startTime="1688824171000",
            endTime="1691329771000",
            limit="100"
        )
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/market/history-mark-candles",
            params={
                'symbol': 'BTCUSDT',
                'productType': 'USDT-FUTURES',
                'granularity': '5m',
                'startTime': '1688824171000',
                'endTime': '1691329771000',
                'limit': '100'
            }
        )

    async def test_get_historical_transaction_details(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"fillList": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_historical_transaction_details(
            productType="USDT-FUTURES",
            orderId="123",
            symbol="BTCUSDT",
            startTime="1678886400000",
            endTime="1678886400000",
            idLessThan="789",
            limit="100"
        )
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/order/fill-history",
            params={
                'productType': 'USDT-FUTURES',
                'orderId': '123',
                'symbol': 'BTCUSDT',
                'startTime': '1678886400000',
                'endTime': '1678886400000',
                'idLessThan': '789',
                'limit': '100'
            }
        )

    async def test_get_interest_exchange_rate(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_interest_exchange_rate()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/market/exchange-rate",
            params={}
        )

    async def test_get_interest_rate_history(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_interest_rate_history(coin="USDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/market/union-interest-rate-history",
            params={'coin': 'USDT'}
        )

    async def test_get_mark_index_market_prices(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_mark_index_market_prices(symbol="BTCUSDT", productType="USDT-FUTURES")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/market/symbol-price",
            params={'symbol': 'BTCUSDT', 'productType': 'USDT-FUTURES'}
        )

    async def test_get_merge_market_depth(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_merge_market_depth(symbol="BTCUSDT", productType="USDT-FUTURES", precision="scale0", limit="1")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/market/merge-depth",
            params={'symbol': 'BTCUSDT', 'productType': 'USDT-FUTURES', 'precision': 'scale0', 'limit': '1'}
        )

    async def test_get_next_funding_time(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_next_funding_time(symbol="BTCUSDT", productType="USDT-FUTURES")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/market/funding-time",
            params={'symbol': 'BTCUSDT', 'productType': 'USDT-FUTURES'}
        )

    async def test_get_open_interest(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_open_interest(symbol="BTCUSDT", productType="USDT-FUTURES")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/market/open-interest",
            params={'symbol': 'BTCUSDT', 'productType': 'USDT-FUTURES'}
        )

    async def test_get_recent_transactions(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_recent_transactions(symbol="BTCUSDT", productType="USDT-FUTURES", limit="100")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/market/fills",
            params={'symbol': 'BTCUSDT', 'productType': 'USDT-FUTURES', 'limit': '100'}
        )

    async def test_get_history_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"entrustedList": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_history_order(
            productType="USDT-FUTURES",
            orderId="123",
            clientOid="abc",
            symbol="BTCUSDT",
            idLessThan="789",
            orderSource="normal",
            startTime="1678886400000",
            endTime="1678886400000",
            limit="100"
        )
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/order/orders-history",
            params={
                'productType': 'USDT-FUTURES',
                'orderId': '123',
                'clientOid': 'abc',
                'symbol': 'BTCUSDT',
                'idLessThan': '789',
                'orderSource': 'normal',
                'startTime': '1678886400000',
                'endTime': '1678886400000',
                'limit': '100'
            }
        )

    async def test_get_history_trigger_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"entrustedList": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_history_trigger_order(
            planType="normal_plan",
            productType="USDT-FUTURES",
            orderId="123",
            clientOid="abc",
            planStatus="executed",
            symbol="BTCUSDT",
            idLessThan="789",
            startTime="1678886400000",
            endTime="1678886400000",
            limit="100"
        )
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/order/orders-plan-history",
            params={
                'planType': 'normal_plan',
                'productType': 'USDT-FUTURES',
                'orderId': '123',
                'clientOid': 'abc',
                'planStatus': 'executed',
                'symbol': 'BTCUSDT',
                'idLessThan': '789',
                'startTime': '1678886400000',
                'endTime': '1678886400000',
                'limit': '100'
            }
        )

    async def test_modify_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.modify_order(
            symbol="BTCUSDT",
            productType="USDT-FUTURES",
            newClientOid="new_abc",
            orderId="123",
            newSize="0.001",
            newPrice="20000"
        )
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/mix/order/modify-order",
            body={
                'symbol': 'BTCUSDT',
                'productType': 'USDT-FUTURES',
                'newClientOid': 'new_abc',
                'orderId': '123',
                'newSize': '0.001',
                'newPrice': '20000'
            }
        )

    async def test_modify_the_stop_profit_and_stop_loss_plan_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.modify_the_stop_profit_and_stop_loss_plan_order(
            marginCoin="USDT",
            productType="USDT-FUTURES",
            symbol="BTCUSDT",
            triggerPrice="20000",
            size="0.001",
            orderId="123",
            triggerType="fill_price",
            executePrice="0",
            rangeRate=""
        )
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/mix/order/modify-tpsl-order",
            body={
                'marginCoin': 'USDT',
                'productType': 'USDT-FUTURES',
                'symbol': 'BTCUSDT',
                'triggerPrice': '20000',
                'size': '0.001',
                'orderId': '123',
                'triggerType': 'fill_price',
                'executePrice': '0',
                'rangeRate': ''
            }
        )

    async def test_modify_trigger_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.modify_trigger_order(
            productType="USDT-FUTURES",
            orderId="123",
            newSize="0.002",
            newPrice="21000",
            newTriggerPrice="20500",
            newTriggerType="mark_price"
        )
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/mix/order/modify-plan-order",
            body={
                'productType': 'USDT-FUTURES',
                'orderId': '123',
                'newSize': '0.002',
                'newPrice': '21000',
                'newTriggerPrice': '20500',
                'newTriggerType': 'mark_price'
            }
        )

    async def test_get_order_detail(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_order_detail(symbol="BTCUSDT", productType="USDT-FUTURES", orderId="123", clientOid="abc")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/order/detail",
            params={'symbol': 'BTCUSDT', 'productType': 'USDT-FUTURES', 'orderId': '123', 'clientOid': 'abc'}
        )

    async def test_get_order_fill_details(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_order_fill_details(productType="USDT-FUTURES", orderId="123", symbol="BTCUSDT", idLessThan="789", startTime="1678886400000", endTime="1678886400000", limit="100")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/order/fills",
            params={'productType': 'USDT-FUTURES', 'orderId': '123', 'symbol': 'BTCUSDT', 'idLessThan': '789', 'startTime': '1678886400000', 'endTime': '1678886400000', 'limit': '100'}
        )

    async def test_get_pending_orders(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_pending_orders(productType="USDT-FUTURES", orderId="123", clientOid="abc", symbol="BTCUSDT", status="live", idLessThan="789", startTime="1678886400000", endTime="1678886400000", limit="100")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/order/orders-pending",
            params={'productType': 'USDT-FUTURES', 'orderId': '123', 'clientOid': 'abc', 'symbol': 'BTCUSDT', 'status': 'live', 'idLessThan': '789', 'startTime': '1678886400000', 'endTime': '1678886400000', 'limit': '100'}
        )

    async def test_get_pending_trigger_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_pending_trigger_order(planType="normal_plan", productType="USDT-FUTURES", orderId="123", clientOid="abc", symbol="BTCUSDT", idLessThan="789", startTime="1678886400000", endTime="1678886400000", limit="100")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/order/orders-plan-pending",
            params={'planType': 'normal_plan', 'productType': 'USDT-FUTURES', 'orderId': '123', 'clientOid': 'abc', 'symbol': 'BTCUSDT', 'idLessThan': '789', 'startTime': '1678886400000', 'endTime': '1678886400000', 'limit': '100'}
        )

    async def test_get_position_adl_rank(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_position_adl_rank(productType="USDT-FUTURES")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/position/adlRank",
            params={'productType': 'USDT-FUTURES'}
        )

    async def test_get_position_tier(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_position_tier(productType="USDT-FUTURES", symbol="BTCUSDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/market/query-position-lever",
            params={'productType': 'USDT-FUTURES', 'symbol': 'BTCUSDT'}
        )

    async def test_get_single_position(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_single_position(productType="USDT-FUTURES", symbol="BTCUSDT", marginCoin="USDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/position/single-position",
            params={'productType': 'USDT-FUTURES', 'symbol': 'BTCUSDT', 'marginCoin': 'USDT'}
        )

    async def test_get_historical_position(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {"list": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.contract.get_historical_position(productType="USDT-FUTURES", symbol="BTCUSDT", idLessThan="123", startTime="1678886400000", endTime="1678886400000", limit="100")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/mix/position/history-position",
            params={'productType': 'USDT-FUTURES', 'symbol': 'BTCUSDT', 'idLessThan': '123', 'startTime': '1678886400000', 'endTime': '1678886400000', 'limit': '100'}
        )
        await self.asyncTearDown()

class TestCopyTrading(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_client = AsyncMock()
        self.copytrading = CopyTrading(self.mock_client)

    async def asyncTearDown(self):
        pass

    async def test_copytrading_initialization(self):
        await self.asyncSetUp()
        self.assertEqual(self.copytrading.client, self.mock_client)
        await self.asyncTearDown()

    async def test_add_or_modify_following_configurations(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        settings = {"copyType": "fixed", "copyAmount": "10", "copySymbol": "BTCUSDT"}
        response = await self.copytrading.add_or_modify_following_configurations(traderId="123", settings=settings, autoCopy="true", mode="normal")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/copy/spot-follower/settings",
            body={'traderId': '123', 'settings': settings, 'autoCopy': 'true', 'mode': 'normal'}
        )
        await self.asyncTearDown()

    async def test_set_mix_copy_trade_settings(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": "success"}
        self.mock_client._send_request.return_value = expected_response

        settings = [{
            "symbol": "BTCUSDT",
            "productType": "USDT-FUTURES",
            "marginType": "trader",
            "marginCoin": "USDT",
            "leverType": "trader",
            "traceType": "amount",
            "traceValue": "330",
            "maxHoldSize": "5000"
        }]
        response = await self.copytrading.set_mix_copy_trade_settings(traderId="123123123", settings=settings, autoCopy="on", mode="advanced")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/copy/mix-follower/settings",
            body={
                'traderId': '123123123',
                'settings': settings,
                'autoCopy': 'on',
                'mode': 'advanced'
            }
        )
        await self.asyncTearDown()

    async def test_cancel_follow(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.cancel_follow(traderId="123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/copy/spot-follower/cancel-trader",
            body={'traderId': '123'}
        )
        await self.asyncTearDown()

    async def test_unfollow_mix_trader(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": "success"}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.unfollow_mix_trader(traderId="123123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/copy/mix-follower/cancel-trader",
            body={'traderId': '123123'}
        )
        await self.asyncTearDown()

    async def test_change_copy_trade_symbol_setting(self):
        await self.asyncSetUp()
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        setting_list = [{
            "symbol": "BTCUSDT",
            "productType": "USDT-FUTURES",
            "marginMode": "isolated",
            "leverage": "10",
            "copyType": "fixed",
            "copyAmount": "10"
        }]
        response = await self.copytrading.change_copy_trade_symbol_setting(settingList=setting_list)
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/copy/mix-trader/config-setting-symbols",
            body={'settingList': setting_list}
        )
        await self.asyncTearDown()

    async def test_change_global_copy_trade_setting(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.change_global_copy_trade_setting(enable="true", showTotalEquity="true", showTpsl="true")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/copy/mix-trader/config-settings-base",
            body={'enable': 'true', 'showTotalEquity': 'true', 'showTpsl': 'true'}
        )

    async def test_set_spot_copytrade_symbols(self):
        expected_response = {"code": "00000", "msg": "success", "data": ""}
        self.mock_client._send_request.return_value = expected_response

        symbol_list = ["ethusdt", "btcusdt"]
        response = await self.copytrading.set_spot_copytrade_symbols(symbolList=symbol_list, settingType="add")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/copy/spot-trader/config-setting-symbols",
            body={'symbolList': symbol_list, 'settingType': 'add'}
        )

    async def test_close_tracking_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.close_tracking_order(productType="USDT-FUTURES", trackingNo="123", symbol="BTCUSDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/copy/mix-trader/order-close-positions",
            body={'productType': 'USDT-FUTURES', 'trackingNo': '123', 'symbol': 'BTCUSDT'}
        )

    async def test_close_positions(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"orderIdList": ["123", "321"]}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.close_positions(productType="USDT-FUTURES", trackingNo="1", symbol="BTCUSDT", marginCoin="USDT", marginMode="isolated", holdSide="long")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/copy/mix-follower/close-positions",
            body={'productType': 'USDT-FUTURES', 'trackingNo': '1', 'symbol': 'BTCUSDT', 'marginCoin': 'USDT', 'marginMode': 'isolated', 'holdSide': 'long'}
        )

    async def test_copy_settings(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.copy_settings(
            traderId="123",
            copyAmount="100",
            copyAllPostions="true",
            autoCopy="true",
            equityGuardian="true",
            equityGuardianMode="fixed",
            equity="1000",
            marginMode="isolated",
            leverage="10",
            multiple="1"
        )
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/copy/mix-follower/copy-settings",
            body={
                'traderId': '123',
                'copyAmount': '100',
                'copyAllPostions': 'true',
                'autoCopy': 'true',
                'equityGuardian': 'true',
                'equityGuardianMode': 'fixed',
                'equity': '1000',
                'marginMode': 'isolated',
                'leverage': '10',
                'multiple': '1'
            }
        )

    async def test_create_copy_apikey(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.create_copy_apikey(passphrase="test_passphrase")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/copy/mix-trader/create-copy-api",
            body={'passphrase': 'test_passphrase'}
        )

    async def test_modify_tracking_order_tpsl(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.modify_tracking_order_tpsl(trackingNo="123", productType="USDT-FUTURES", stopSurplusPrice="20000", stopLossPrice="19000")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/copy/mix-trader/order-modify-tpsl",
            body={'trackingNo': '123', 'productType': 'USDT-FUTURES', 'stopSurplusPrice': '20000', 'stopLossPrice': '19000'}
        )

    async def test_get_copy_trade_settings(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.get_copy_trade_settings(traderId="123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/copy/mix-follower/query-settings",
            params={'traderId': '123'}
        )

    async def test_get_copy_trade_symbol_settings(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.get_copy_trade_symbol_settings(productType="USDT-FUTURES")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/copy/mix-trader/config-query-symbols",
            params={'productType': 'USDT-FUTURES'}
        )

    async def test_get_copytrade_configuration(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.get_copytrade_configuration()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/copy/spot-trader/config-query-settings",
            params={}
        )

    async def test_get_current_copy_trade_orders(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.get_current_copy_trade_orders(symbol="BTCUSDT", traderId="123", idLessThan="789", idGreaterThan="456", startTime="1678886400000", endTime="1678886400000", limit="100")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/copy/spot-follower/query-current-orders",
            params={'symbol': 'BTCUSDT', 'traderId': '123', 'idLessThan': '789', 'idGreaterThan': '456', 'startTime': '1678886400000', 'endTime': '1678886400000', 'limit': '100'}
        )

    async def test_get_current_tracking_orders(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.get_current_tracking_orders(productType="USDT-FUTURES", idLessThan="789", idGreaterThan="456", startTime="1678886400000", endTime="1678886400000", limit="100", symbol="BTCUSDT", traderId="123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/copy/mix-follower/query-current-orders",
            params={'productType': 'USDT-FUTURES', 'idLessThan': '789', 'idGreaterThan': '456', 'startTime': '1678886400000', 'endTime': '1678886400000', 'limit': '100', 'symbol': 'BTCUSDT', 'traderId': '123'}
        )

    async def test_get_data_indicator_statistics(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.get_data_indicator_statistics()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/copy/spot-trader/order-total-detail",
            params={}
        )

    async def test_get_follow_configuration(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.get_follow_configuration(traderId="123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/copy/spot-follower/query-settings",
            params={'traderId': '123'}
        )

    async def test_get_follow_limit(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.get_follow_limit(productType="USDT-FUTURES", symbol="BTCUSDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/copy/mix-follower/query-quantity-limit",
            params={'productType': 'USDT-FUTURES', 'symbol': 'BTCUSDT'}
        )

    async def test_get_history_profit_share_detail(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.get_history_profit_share_detail(coin="USDT", idLessThan="789", idGreaterThan="456", startTime="1678886400000", endTime="1678886400000", limit="100")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/copy/mix-trader/profit-history-details",
            params={'coin': 'USDT', 'idLessThan': '789', 'idGreaterThan': '456', 'startTime': '1678886400000', 'endTime': '1678886400000', 'limit': '100'}
        )

    async def test_get_history_profit_sharing_details(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.get_history_profit_sharing_details(idLessThan="789", idGreaterThan="456", startTime="1678886400000", endTime="1678886400000", limit="100", coin="USDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/copy/spot-trader/profit-history-details",
            params={'idLessThan': '789', 'idGreaterThan': '456', 'startTime': '1678886400000', 'endTime': '1678886400000', 'limit': '100', 'coin': 'USDT'}
        )

    async def test_get_history_tracking_orders(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.get_history_tracking_orders(symbol="BTCUSDT", traderId="123", idLessThan="789", idGreaterThan="456", startTime="1678886400000", endTime="1678886400000", limit="100")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/copy/spot-follower/query-history-orders",
            params={'symbol': 'BTCUSDT', 'traderId': '123', 'idLessThan': '789', 'idGreaterThan': '456', 'startTime': '1678886400000', 'endTime': '1678886400000', 'limit': '100'}
        )

    async def test_get_my_followers(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.get_my_followers(pageNo="1", pageSize="10", startTime="123", endTime="456")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/copy/mix-trader/config-query-followers",
            params={'pageNo': '1', 'pageSize': '10', 'startTime': '123', 'endTime': '456'}
        )

    async def test_get_spot_my_followers(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.get_spot_my_followers(pageNo="1", pageSize="10", startTime="123", endTime="456")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/copy/spot-trader/config-query-followers",
            params={'pageNo': '1', 'pageSize': '10', 'startTime': '123', 'endTime': '456'}
        )

    async def test_get_my_traders(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.get_my_traders(startTime="123", endTime="456", pageNo="1", pageSize="10")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/copy/mix-follower/query-traders",
            params={'startTime': '123', 'endTime': '456', 'pageNo': '1', 'pageSize': '10'}
        )

    async def test_get_spot_my_traders(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.get_spot_my_traders(startTime="123", endTime="456", pageNo="1", pageSize="10")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/copy/spot-follower/query-traders",
            params={'startTime': '123', 'endTime': '456', 'pageNo': '1', 'pageSize': '10'}
        )

    async def test_get_profit_share_group_by_coin_date(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.get_profit_share_group_by_coin_date(pageSize="20", pageNo="1")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/copy/mix-trader/profits-group-coin-date",
            params={'pageSize': '20', 'pageNo': '1'}
        )

    async def test_get_profit_share_detail(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.get_profit_share_detail(coin="USDT", pageSize="20", pageNo="1")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/copy/mix-trader/profit-details",
            params={'coin': 'USDT', 'pageSize': '20', 'pageNo': '1'}
        )

    async def test_get_spot_trader_profit_summary(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.get_spot_trader_profit_summary()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/copy/spot-trader/profit-summarys",
            params={}
        )

    async def test_get_mix_trader_profit_history_summary(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.get_mix_trader_profit_history_summary()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/copy/mix-trader/profit-history-summarys",
            params={}
        )

    async def test_get_trader_current_trading_pair(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"currentTradingList": ["ETHUSDT", "BTCUSDT"]}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.get_trader_current_trading_pair(traderId="123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/copy/spot-follower/query-trader-symbols",
            params={'traderId': '123'}
        )

    async def test_get_tracking_order_summary(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.get_tracking_order_summary()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/copy/mix-trader/order-total-detail",
            params={}
        )

    async def test_get_unrealized_profit_sharing_details(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.get_unrealized_profit_sharing_details(coin="USDT", pageNo="1", pageSize="20")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/copy/spot-trader/profit-details",
            params={'coin': 'USDT', 'pageNo': '1', 'pageSize': '20'}
        )

    async def test_remove_follower(self):
        expected_response = {"code": "00000", "msg": "success", "data": "success"}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.remove_follower(followerUid="123123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/copy/mix-trader/config-remove-follower",
            body={'followerUid': '123123'}
        )

    async def test_remove_followers(self):
        expected_response = {"code": "00000", "msg": "success", "data": ""}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.remove_followers(followerUid="123123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/copy/spot-trader/config-remove-follower",
            body={'followerUid': '123123'}
        )

    async def test_sell_and_sell_in_batch(self):
        expected_response = {"code": "00000", "msg": "success", "data": ""}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.sell_and_sell_in_batch(trackingNoList=["12213123"], symbol="ethusdt")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/copy/spot-follower/order-close-tracking",
            body={'trackingNoList': ['12213123'], 'symbol': 'ethusdt'}
        )

    async def test_set_take_profit_and_stop_loss(self):
        expected_response = {"code": "00000", "msg": "success", "data": ""}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.set_take_profit_and_stop_loss(trackingNo="123", stopSurplusPrice="2000", stopLossPrice="1500")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/copy/spot-follower/setting-tpsl",
            body={'trackingNo': '123', 'stopSurplusPrice': '2000', 'stopLossPrice': '1500'}
        )

    async def test_set_tpsl(self):
        expected_response = {"code": "00000", "msg": "success", "data": "success"}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.set_tpsl(trackingNo="123", productType="mix", symbol="BTCUSDT", stopSurplusPrice="2000", stopLossPrice="1500")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/copy/mix-follower/setting-tpsl",
            body={'trackingNo': '123', 'productType': 'mix', 'symbol': 'BTCUSDT', 'stopSurplusPrice': '2000', 'stopLossPrice': '1500'}
        )

    async def test_stop_the_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": ""}
        self.mock_client._send_request.return_value = expected_response

        response = await self.copytrading.stop_the_order(trackingNoList=["123"])
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/copy/spot-follower/stop-order",
            body={'trackingNoList': ['123']}
        )

class TestEarn(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_client = AsyncMock()
        self.earn = Earn(self.mock_client)

    async def asyncTearDown(self):
        pass

    def test_earn_initialization(self):
        self.assertEqual(self.earn.client, self.mock_client)

    async def test_borrow(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"orderId": "1"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.earn.borrow(loanCoin="ETH", pledgeCoin="USDT", daily="SEVEN", loanAmount="0.01")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/earn/loan/borrow",
            body={'loanCoin': 'ETH', 'pledgeCoin': 'USDT', 'daily': 'SEVEN', 'loanAmount': '0.01'}
        )

        # Test with pledgeAmount
        self.mock_client.reset_mock() # Reset mock to check new call
        response = await self.earn.borrow(loanCoin="ETH", pledgeCoin="USDT", daily="SEVEN", pledgeAmount="100")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/earn/loan/borrow",
            body={'loanCoin': 'ETH', 'pledgeCoin': 'USDT', 'daily': 'SEVEN', 'pledgeAmount': '100'}
        )

        # Test with neither pledgeAmount nor loanAmount
        with self.assertRaises(ValueError):
            await self.earn.borrow(loanCoin="ETH", pledgeCoin="USDT", daily="SEVEN")

    async def test_get_earn_account_assets(self):
        expected_response = {"code": "00000", "msg": "success", "data": [{"coin": "BTC", "amount": "0.1"}, {"coin": "USDT", "amount": "400"}]}
        self.mock_client._send_request.return_value = expected_response

        response = await self.earn.get_earn_account_assets(coin="USDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/account/assets",
            params={'coin': 'USDT'}
        )

        self.mock_client.reset_mock()
        response = await self.earn.get_earn_account_assets()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/account/assets",
            params={}
        )

    async def test_get_currency_list(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"loanInfos": [], "pledgeInfos": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.earn.get_currency_list(coin="USDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/loan/public/coinInfos",
            params={'coin': 'USDT'}
        )

        self.mock_client.reset_mock()
        response = await self.earn.get_currency_list()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/loan/public/coinInfos",
            params={}
        )

    async def test_get_debts(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"pledgeInfos": [], "loanInfos": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.earn.get_debts()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/loan/debts",
            params={}
        )

    async def test_get_est_interest_and_borrowable(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"hourInterest": "0.00133436", "loanAmount": "216.2654"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.earn.get_est_interest_and_borrowable(loanCoin="USDT", pledgeCoin="ETH", daily="SEVEN", pledgeAmount="0.2")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/loan/public/hour-interest",
            params={'loanCoin': 'USDT', 'pledgeCoin': 'ETH', 'daily': 'SEVEN', 'pledgeAmount': '0.2'}
        )

    async def test_get_liquidation_records(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.earn.get_liquidation_records(startTime="1685957902000", endTime="1691228302423", orderId="1", loanCoin="TRX", pledgeCoin="USDT", status="COMPLETE", pageNo="1", pageSize="10")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/loan/reduces",
            params={'startTime': '1685957902000', 'endTime': '1691228302423', 'orderId': '1', 'loanCoin': 'TRX', 'pledgeCoin': 'USDT', 'status': 'COMPLETE', 'pageNo': '1', 'pageSize': '10'}
        )

        self.mock_client.reset_mock()
        response = await self.earn.get_liquidation_records(startTime="1685957902000", endTime="1691228302423")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/loan/reduces",
            params={'startTime': '1685957902000', 'endTime': '1691228302423'}
        )

    async def test_get_loan_history(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.earn.get_loan_history(startTime="1685957902000", endTime="1691228302423", orderId="1", loanCoin="TRX", pledgeCoin="USDT", status="REPAY", pageNo="1", pageSize="10")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/loan/borrow-history",
            params={'startTime': '1685957902000', 'endTime': '1691228302423', 'orderId': '1', 'loanCoin': 'TRX', 'pledgeCoin': 'USDT', 'status': 'REPAY', 'pageNo': '1', 'pageSize': '10'}
        )

        self.mock_client.reset_mock()
        response = await self.earn.get_loan_history(startTime="1685957902000", endTime="1691228302423")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/loan/borrow-history",
            params={'startTime': '1685957902000', 'endTime': '1691228302423'}
        )

    async def test_get_loan_orders(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.earn.get_loan_orders(orderId="1", loanCoin="ETH", pledgeCoin="USDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/loan/ongoing-orders",
            params={'orderId': '1', 'loanCoin': 'ETH', 'pledgeCoin': 'USDT'}
        )

        self.mock_client.reset_mock()
        response = await self.earn.get_loan_orders()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/loan/ongoing-orders",
            params={}
        )

    async def test_get_pledge_rate_history(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.earn.get_pledge_rate_history(startTime="1685957902000", endTime="1691228302423", orderId="1", reviseSide="down", pledgeCoin="USDT", pageNo="1", pageSize="10")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/loan/revise-history",
            params={'startTime': '1685957902000', 'endTime': '1691228302423', 'orderId': '1', 'reviseSide': 'down', 'pledgeCoin': 'USDT', 'pageNo': '1', 'pageSize': '10'}
        )

        self.mock_client.reset_mock()
        response = await self.earn.get_pledge_rate_history(startTime="1685957902000", endTime="1691228302423")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/loan/revise-history",
            params={'startTime': '1685957902000', 'endTime': '1691228302423'}
        )

    async def test_get_repay_history(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.earn.get_repay_history(startTime="1685957902000", endTime="1691228302423", orderId="1", loanCoin="TRX", pledgeCoin="USDT", pageNo="1", pageSize="10")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/loan/repay-history",
            params={'startTime': '1685957902000', 'endTime': '1691228302423', 'orderId': '1', 'loanCoin': 'TRX', 'pledgeCoin': 'USDT', 'pageNo': '1', 'pageSize': '10'}
        )

        self.mock_client.reset_mock()
        response = await self.earn.get_repay_history(startTime="1685957902000", endTime="1691228302423")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/loan/repay-history",
            params={'startTime': '1685957902000', 'endTime': '1691228302423'}
        )

    async def test_modify_pledge_rate(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"loanCoin": "TRX", "pledgeCoin": "USDT", "afterPledgeRate": "60.5"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.earn.modify_pledge_rate(orderId="1", amount="1", pledgeCoin="USDT", reviseType="OUT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/earn/loan/revise-pledge",
            body={'orderId': '1', 'amount': '1', 'pledgeCoin': 'USDT', 'reviseType': 'OUT'}
        )

    async def test_redeem_savings(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"orderId": "123123123", "status": "2000.000000"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.earn.redeem_savings(productId="23123123", periodType="flexible", amount="99999999", orderId="1")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/earn/savings/redeem",
            body={'productId': '23123123', 'periodType': 'flexible', 'amount': '99999999', 'orderId': '1'}
        )

        self.mock_client.reset_mock()
        response = await self.earn.redeem_savings(productId="23123123", periodType="flexible", amount="99999999")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/earn/savings/redeem",
            body={'productId': '23123123', 'periodType': 'flexible', 'amount': '99999999'}
        )

    async def test_repay(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"loanCoin": "TRX", "pledgeCoin": "USDT", "repayAmount": "1566.23820848", "payInterest": "0.1185634", "repayLoanAmount": "1566.22635214", "repayUnlockAmount": "195"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.earn.repay(orderId="ETH", repayAll="yes", repayUnlock="yes")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/earn/loan/repay",
            body={'orderId': 'ETH', 'repayAll': 'yes', 'repayUnlock': 'yes'}
        )

        self.mock_client.reset_mock()
        response = await self.earn.repay(orderId="ETH", repayAll="no", amount="100")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/earn/loan/repay",
            body={'orderId': 'ETH', 'repayAll': 'no', 'amount': '100'}
        )

    async def test_get_savings_account(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"btcAmount": "0.35821314", "usdtAmount": "9481.55500000", "btc24hEarning": "0.00000009", "usdt24hEarning": "0.00263912", "btcTotalEarning": "0.00000761", "usdtTotalEarning": "0.20145653"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.earn.get_savings_account()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/savings/account",
            params={}
        )

    async def test_get_savings_assets(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"resultList": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.earn.get_savings_assets(periodType="fixed", startTime="1659076670000", endTime="1659076670000", limit="10", idLessThan="123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/savings/assets",
            params={'periodType': 'fixed', 'startTime': '1659076670000', 'endTime': '1659076670000', 'limit': '10', 'idLessThan': '123'}
        )

        self.mock_client.reset_mock()
        response = await self.earn.get_savings_assets(periodType="flexible")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/savings/assets",
            params={'periodType': 'flexible'}
        )

    async def test_get_savings_product_list(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.earn.get_savings_product_list(coin="BTC", filter="available_and_held")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/savings/product",
            params={'coin': 'BTC', 'filter': 'available_and_held'}
        )

        self.mock_client.reset_mock()
        response = await self.earn.get_savings_product_list()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/savings/product",
            params={}
        )

    async def test_get_savings_records(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"resultList": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.earn.get_savings_records(periodType="flexible", coin="BGB", orderType="subscribe", startTime="1659076670000", endTime="1659076670000", limit="10", idLessThan="123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/savings/records",
            params={'periodType': 'flexible', 'coin': 'BGB', 'orderType': 'subscribe', 'startTime': '1659076670000', 'endTime': '1659076670000', 'limit': '10', 'idLessThan': '123'}
        )

        self.mock_client.reset_mock()
        response = await self.earn.get_savings_records(periodType="flexible")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/savings/records",
            params={'periodType': 'flexible'}
        )

    async def test_get_savings_subscription_detail(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"singleMinAmount": "10.000000", "singleMaxAmount": "2000.000000"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.earn.get_savings_subscription_detail(productId="123123", periodType="flexible")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/savings/subscribe-info",
            params={'productId': '123123', 'periodType': 'flexible'}
        )

    async def test_get_savings_subscription_result(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"result": "success", "msg": ""}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.earn.get_savings_subscription_result(productId="123123", periodType="flexible")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/savings/subscribe-result",
            params={'productId': '123123', 'periodType': 'flexible'}
        )

    async def test_get_sharkfin_account(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"btcSubscribeAmount": "0.00000000", "usdtSubscribeAmount": "0.00", "btcHistoricalAmount": "0.00000000", "usdtHistoricalAmount": "0.00000000", "btcTotalEarning": "0.00000000", "usdtTotalEarning": "0.00000000"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.earn.get_sharkfin_account()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/sharkfin/account",
            params={}
        )

    async def test_get_sharkfin_assets(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"resultList": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.earn.get_sharkfin_assets(status="subscribed", startTime="1659076670000", endTime="1659076670000", limit="10", idLessThan="123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/sharkfin/assets",
            params={'status': 'subscribed', 'startTime': '1659076670000', 'endTime': '1659076670000', 'limit': '10', 'idLessThan': '123'}
        )

        self.mock_client.reset_mock()
        response = await self.earn.get_sharkfin_assets(status="subscribed")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/sharkfin/assets",
            params={'status': 'subscribed'}
        )

    async def test_get_sharkfin_products(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"resultList": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.earn.get_sharkfin_products(coin="ETH", limit="10", idLessThan="1")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/sharkfin/product",
            params={'coin': 'ETH', 'limit': '10', 'idLessThan': '1'}
        )

        self.mock_client.reset_mock()
        response = await self.earn.get_sharkfin_products(coin="ETH")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/sharkfin/product",
            params={'coin': 'ETH'}
        )

    async def test_get_sharkfin_records(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"resultList": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.earn.get_sharkfin_records(type="subscription", coin="BGB", startTime="1659076670000", endTime="1659076670000", limit="10", idLessThan="123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/sharkfin/records",
            params={'type': 'subscription', 'coin': 'BGB', 'startTime': '1659076670000', 'endTime': '1659076670000', 'limit': '10', 'idLessThan': '123'}
        )

        self.mock_client.reset_mock()
        response = await self.earn.get_sharkfin_records(type="subscription")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/sharkfin/records",
            params={'type': 'subscription'}
        )

    async def test_get_sharkfin_subscription_result(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"result": "success", "msg": ""}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.earn.get_sharkfin_subscription_result(orderId="123123123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/sharkfin/subscribe-result",
            params={'orderId': '123123123'}
        )

    async def test_subscribe_savings(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"orderId": "1313060074239184896"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.earn.subscribe_savings(productId="23123123", periodType="flexible", amount="99999999")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/earn/savings/subscribe",
            body={'productId': '23123123', 'periodType': 'flexible', 'amount': '99999999'}
        )

    async def test_subscribe_sharkfin(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"orderId": "123123123", "status": "2000.000000"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.earn.subscribe_sharkfin(productId="23123123", amount="99999999")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/earn/sharkfin/subscribe",
            body={'productId': '23123123', 'amount': '99999999'}
        )

    async def test_get_sharkfin_subscription_detail(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"productCoin": "BTC", "subscribeCoin": "USDT"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.earn.get_sharkfin_subscription_detail(productId="1")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/sharkfin/subscribe-info",
            params={'productId': '1'}
        )

    async def test_get_savings_redemption_results(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"result": "success", "msg": ""}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.earn.get_savings_redemption_results(orderId="123123", periodType="flexible")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/earn/savings/redeem-result",
            params={'orderId': '123123', 'periodType': 'flexible'}
        )

class TestInstloan(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_client = AsyncMock()
        self.instloan = Instloan(self.mock_client)

    async def asyncTearDown(self):
        pass

    def test_instloan_initialization(self):
        self.assertEqual(self.instloan.client, self.mock_client)

    async def test_bind_unbind_sub_account_uid_to_risk_unit(self):
        expected_response = {"code": "00000", "msg": "success", "data": "success"}
        self.mock_client._send_request.return_value = expected_response

        response = await self.instloan.bind_unbind_sub_account_uid_to_risk_unit(uid="xxxxx", operate="bind", riskUnitId="123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/spot/ins-loan/bind-uid",
            body={'uid': 'xxxxx', 'operate': 'bind', 'riskUnitId': '123'}
        )

        self.mock_client.reset_mock()
        response = await self.instloan.bind_unbind_sub_account_uid_to_risk_unit(uid="xxxxx", operate="unbind")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/spot/ins-loan/bind-uid",
            body={'uid': 'xxxxx', 'operate': 'unbind'}
        )

    async def test_get_loan_orders(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.instloan.get_loan_orders(orderId="xxxxxxx", startTime="1713645576789", endTime="1713645576789")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/ins-loan/loan-order",
            params={'orderId': 'xxxxxxx', 'startTime': '1713645576789', 'endTime': '1713645576789'}
        )

        self.mock_client.reset_mock()
        response = await self.instloan.get_loan_orders()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/ins-loan/loan-order",
            params={}
        )

    async def test_get_ltv(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"ltv": "0.6667"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.instloan.get_ltv(riskUnitId="123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/ins-loan/ltv-convert",
            params={'riskUnitId': '123'}
        )

        self.mock_client.reset_mock()
        response = await self.instloan.get_ltv()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/ins-loan/ltv-convert",
            params={}
        )

    async def test_get_margin_coin_info(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"productId": "xxxxxxxx", "coinInfo": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.instloan.get_margin_coin_info(productId="xxx")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/ins-loan/ensure-coins-convert",
            params={'productId': 'xxx'}
        )

    async def test_get_product_info(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"productId": "xxxxxxxx", "leverage": "2"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.instloan.get_product_info(productId="xxx")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/ins-loan/product-infos",
            params={'productId': 'xxx'}
        )

    async def test_get_repayment_orders(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.instloan.get_repayment_orders(startTime="1659076670000", endTime="1659076670000", limit="10")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/ins-loan/repaid-history",
            params={'startTime': '1659076670000', 'endTime': '1659076670000', 'limit': '10'}
        )

        self.mock_client.reset_mock()
        response = await self.instloan.get_repayment_orders()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/ins-loan/repaid-history",
            params={}
        )

    async def test_get_risk_unit(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"riskUnitId": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.instloan.get_risk_unit()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/ins-loan/risk-unit",
            params={}
        )

    async def test_get_spot_symbols(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"productId": "xxxxxxxx", "spotSymbols": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.instloan.get_spot_symbols(productId="xxx")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/ins-loan/symbols",
            params={'productId': 'xxx'}
        )

        self.mock_client.reset_mock()
        response = await self.instloan.get_spot_symbols(productId="xxx")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/ins-loan/symbols",
            params={'productId': 'xxx'}
        )

    async def test_get_transferable_amount(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"coin": "USDT", "transfered": "1223", "userId": "xxxxxxxxxx"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.instloan.get_transferable_amount(coin="USDT", userId="123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/ins-loan/transfered",
            params={'coin': 'USDT', 'userId': '123'}
        )

        self.mock_client.reset_mock()
        response = await self.instloan.get_transferable_amount(coin="USDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/ins-loan/transfered",
            params={'coin': 'USDT'}
        )

class TestMargin(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_client = AsyncMock()
        self.margin = Margin(self.mock_client)

    async def asyncTearDown(self):
        pass

    def test_margin_initialization(self):
        self.assertEqual(self.margin.client, self.mock_client)

    async def test_cross_batch_cancel_orders(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"successList": [], "failureList": []}}
        self.mock_client._send_request.return_value = expected_response

        order_id_list = [{
            "orderId": "11232132134"
        }, {
            "clientOid": "mytestOid"
        }]
        response = await self.margin.cross_batch_cancel_orders(symbol="BTCUSDT", orderIdList=order_id_list)
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/margin/crossed/batch-cancel-order",
            body={'symbol': 'BTCUSDT', 'orderIdList': order_id_list}
        )

    async def test_cross_batch_orders(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"successList": [], "failureList": []}}
        self.mock_client._send_request.return_value = expected_response

        order_list = [{
            "side": "buy",
            "orderType": "market",
            "force": "gtc",
            "quoteSize": "10000",
            "loanType": "normal"
        }]
        response = await self.margin.cross_batch_orders(symbol="BTCUSDT", orderList=order_list)
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/margin/crossed/batch-place-order",
            body={'symbol': 'BTCUSDT', 'orderList': order_list}
        )

    async def test_cross_borrow(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"loanId": "2342332432", "coin": "USDT", "borrowAmount": "1.00000000"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.cross_borrow(coin="USDT", borrowAmount="1", clientOid="test_client_oid")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/margin/crossed/account/borrow",
            body={'coin': 'USDT', 'borrowAmount': '1', 'clientOid': 'test_client_oid'}
        )

    async def test_cross_cancel_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"orderId": "121211212122", "clientOid": "BITGET#121211212122"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.cross_cancel_order(symbol="BTCUSDT", orderId="12234234321432")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/margin/crossed/cancel-order",
            body={'symbol': 'BTCUSDT', 'orderId': '12234234321432'}
        )

    async def test_cross_flash_repay(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"repayId": "3423423", "coin": "ETH"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.cross_flash_repay(coin="BTC")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/margin/crossed/account/flash-repay",
            body={'coin': 'BTC'}
        )

    async def test_cross_place_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"orderId": "121211212122", "clientOid": "121211212122"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.cross_place_order(
            symbol="BTCUSDT",
            orderType="market",
            loanType="normal",
            force="gtc",
            side="buy",
            quoteSize="10000"
        )
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/margin/crossed/place-order",
            body={
                'symbol': 'BTCUSDT',
                'orderType': 'market',
                'loanType': 'normal',
                'force': 'gtc',
                'side': 'buy',
                'quoteSize': '10000'
            }
        )

    async def test_cross_repay(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"coin": "USDT", "repayId": "12313123213", "remainDebtAmount": "0.2", "repayAmount": "0.1"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.cross_repay(coin="BTC", repayAmount="0.1")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/margin/crossed/account/repay",
            body={'coin': 'BTC', 'repayAmount': '0.1'}
        )

    async def test_get_cross_tier_configuration(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.get_cross_tier_configuration(coin="ETH")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/margin/crossed/tier-data",
            params={'coin': 'ETH'}
        )

    async def test_get_cross_account_assets(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.get_cross_account_assets(coin="USDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/margin/crossed/account/assets",
            params={'coin': 'USDT'}
        )

    async def test_isolated_batch_cancel_orders(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"successList": [], "failureList": []}}
        self.mock_client._send_request.return_value = expected_response

        order_list = [
            {"orderId": "121211212122", "clientOid": "121211212122"}
        ]
        response = await self.margin.isolated_batch_cancel_orders(symbol="BTCUSDT", orderIdList=order_list)
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/margin/isolated/batch-cancel-order",
            body={
                'symbol': 'BTCUSDT',
                'orderIdList': order_list
            }
        )

    async def test_isolated_place_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"orderId": "121211212122", "clientOid": "121211212122"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.isolated_place_order(
            symbol="ETHUSDT",
            side="buy",
            price="1796.5",
            orderType="limit",
            force="gtc",
            baseSize="0.1",
            loanType="normal"
        )
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/margin/isolated/place-order",
            body={
                'symbol': 'ETHUSDT',
                'side': 'buy',
                'price': '1796.5',
                'orderType': 'limit',
                'force': 'gtc',
                'baseSize': '0.1',
                'loanType': 'normal'
            }
        )

    async def test_isolated_batch_orders(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"successList": [], "failureList": []}}
        self.mock_client._send_request.return_value = expected_response

        order_list = [{
            "side": "buy",
            "orderType": "market",
            "force": "gtc",
            "quoteSize": "110",
            "loanType": "normal"
        }]
        response = await self.margin.isolated_batch_orders(symbol="BTCUSDT", orderList=order_list)
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/margin/isolated/batch-place-order",
            body={'symbol': 'BTCUSDT', 'orderList': order_list}
        )

    async def test_isolated_cancel_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"orderId": "121211212122", "clientOid": "121211212122"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.isolated_cancel_order(symbol="ETHUSDT", orderId="121211212122")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/margin/isolated/cancel-order",
            body={'symbol': 'ETHUSDT', 'orderId': '121211212122'}
        )

    async def test_cancel_isolated_orders_in_batch(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"successList": [], "failureList": []}}
        self.mock_client._send_request.return_value = expected_response

        order_id_list = [{
            "orderId": "121211212122",
            "clientOid": "121211212122"
        }]
        response = await self.margin.isolated_batch_cancel_orders(symbol="BTCUSDT", orderIdList=order_id_list)
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/margin/isolated/batch-cancel-order",
            body={'symbol': 'BTCUSDT', 'orderIdList': order_id_list}
        )

    async def test_get_isolated_orders_history(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"orderList": [], "maxId": "1", "minId": "1"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.get_isolated_orders_history(symbol="ETHUSDT", startTime="1695336324000")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/margin/isolated/history-orders",
            params={'symbol': 'ETHUSDT', 'startTime': '1695336324000'}
        )

    async def test_get_isolated_order_fills(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"fills": [], "minId": "1", "maxId": "1"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.get_isolated_order_fills(symbol="ETHUSDT", startTime="1695336324000")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/margin/isolated/fills",
            params={'symbol': 'ETHUSDT', 'startTime': '1695336324000'}
        )

    async def test_isolated_borrow(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"loanId": "123412412452345", "symbol": "BTCUSDT", "coin": "USDT", "borrowAmount": "1.00000000"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.isolated_borrow(symbol="BTCUSDT", coin="USDT", borrowAmount="1")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/margin/isolated/account/borrow",
            body={'symbol': 'BTCUSDT', 'coin': 'USDT', 'borrowAmount': '1'}
        )

    async def test_isolated_repay(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"remainDebtAmount": "0", "symbol": "BTCUSDT", "repayId": "1234234234234", "coin": "USDT", "repayAmount": "1"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.isolated_repay(symbol="BTCUSDT", coin="USDT", repayAmount="1")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/margin/isolated/account/repay",
            body={'symbol': 'BTCUSDT', 'coin': 'USDT', 'repayAmount': '1'}
        )

    async def test_get_isolated_risk_rate(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.get_isolated_risk_rate(symbol="BTCUSDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/margin/isolated/account/risk-rate",
            params={'symbol': 'BTCUSDT'}
        )

    async def test_get_isolated_tier_configuration(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.get_isolated_tier_configuration(symbol="BTCUSDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/margin/isolated/tier-data",
            params={'symbol': 'BTCUSDT'}
        )

    async def test_isolated_flash_repay(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.isolated_flash_repay(symbolList=["ETHUSDT"])
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/margin/isolated/account/flash-repay",
            body={'symbolList': ['ETHUSDT']}
        )

    async def test_query_isolated_flash_repayment_result(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.query_isolated_flash_repayment_result(idList=["13423423"])
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/margin/isolated/account/query-flash-repay-status",
            body={'idList': ['13423423']}
        )

    async def test_get_isolated_repay_history(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"resultList": [], "maxId": "1", "minId": "1"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.get_isolated_repay_history(symbol="BTCUSDT", startTime="1695336324000", endTime="1695336324000", limit="20", idLessThan="123", repayId="456", coin="USDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/margin/isolated/repay-history",
            params={'symbol': 'BTCUSDT', 'startTime': '1695336324000', 'endTime': '1695336324000', 'limit': '20', 'idLessThan': '123', 'repayId': '456', 'coin': 'USDT'}
        )

    async def test_get_support_currencies(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.get_support_currencies()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/margin/currencies",
            params={}
        )

    async def test_get_the_leverage_interest_rate(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"coin": "BTC", "dailyInterestRate": "0.00003000", "annualInterestRate": "0.01095000", "updatedTime": "1746690900381"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.get_the_leverage_interest_rate(coin="BTC")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/margin/interest-rate-record",
            params={'coin': 'BTC'}
        )

    async def test_get_cross_interest_history(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"minId": "1", "maxId": "1", "resultList": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.get_cross_interest_history(startTime="1693205171000", coin="USDT", endTime="1694155571000", limit="20", idLessThan="123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/margin/crossed/interest-history",
            params={'startTime': '1693205171000', 'coin': 'USDT', 'endTime': '1694155571000', 'limit': '20', 'idLessThan': '123'}
        )

    async def test_get_cross_interest_rate_and_max_borrowable(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.get_cross_interest_rate_and_max_borrowable(coin="ETH")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/margin/crossed/interest-rate-and-limit",
            params={'coin': 'ETH'}
        )

    async def test_get_cross_liquidation_history(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"minId": "1", "maxId": "1", "resultList": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.get_cross_liquidation_history(startTime="1693205171000", endTime="1694155571000", limit="20", idLessThan="123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/margin/crossed/liquidation-history",
            params={'startTime': '1693205171000', 'endTime': '1694155571000', 'limit': '20', 'idLessThan': '123'}
        )

    async def test_get_cross_liquidation_orders(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"resultList": [], "idLessThan": "1131405566368010241"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.get_cross_liquidation_orders(startTime="1704100405000", endTime="1706174005091", limit="20")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/margin/crossed/liquidation-order",
            params={'startTime': '1704100405000', 'endTime': '1706174005091', 'limit': '20'}
        )

    async def test_get_cross_max_transferable(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"coin": "USDT", "maxTransferOutAmount": "11"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.get_cross_max_transferable(coin="USDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/margin/crossed/account/max-transfer-out-amount",
            params={'coin': 'USDT'}
        )

    async def test_get_cross_order_fills(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"fills": [], "maxId": "121211212122", "minId": "121211212122"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.get_cross_order_fills(symbol="BTCUSDT", startTime="1693205171000", endTime="1694155571000", limit="20", idLessThan="123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/margin/crossed/fills",
            params={'symbol': 'BTCUSDT', 'startTime': '1693205171000', 'endTime': '1694155571000', 'limit': '20', 'idLessThan': '123'}
        )

    async def test_get_cross_repay_history(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"resultList": [], "maxId": "1", "minId": "1"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.get_cross_repay_history(startTime="1693205171000", endTime="1694155571000", limit="20", idLessThan="123", repayId="456", coin="USDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/margin/crossed/repay-history",
            params={'startTime': '1693205171000', 'endTime': '1694155571000', 'limit': '20', 'idLessThan': '123', 'repayId': '456', 'coin': 'USDT'}
        )

    async def test_get_cross_risk_rate(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"riskRateRatio": "0"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.get_cross_risk_rate()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/margin/crossed/account/risk-rate",
            params={}
        )

    async def test_get_isolated_account_asset(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.get_isolated_account_asset(symbol="BTCUSDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/margin/isolated/account/assets",
            params={'symbol': 'BTCUSDT'}
        )

    async def test_get_isolated_borrow_history(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"resultList": [], "maxId": "1", "minId": "1"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.get_isolated_borrow_history(symbol="BTCUSDT", startTime="1695336324000", endTime="1695336324000", limit="20", idLessThan="123", loanId="456", coin="USDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/margin/isolated/borrow-history",
            params={'symbol': 'BTCUSDT', 'startTime': '1695336324000', 'endTime': '1695336324000', 'limit': '20', 'idLessThan': '123', 'loanId': '456', 'coin': 'USDT'}
        )

    async def test_get_isolated_current_orders(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"orderList": [], "maxId": "121211212122", "minId": "121211212122"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.get_isolated_current_orders(symbol="ETHUSDT", startTime="1695336324000")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/margin/isolated/open-orders",
            params={'symbol': 'ETHUSDT', 'startTime': '1695336324000'}
        )

    async def test_get_isolated_financial_history(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"resultList": [], "maxId": "1", "minId": "1"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.get_isolated_financial_history(symbol="BTCUSDT", startTime="1692690126000", endTime="1695625219083", limit="20", idLessThan="123", marginType="transfer_in", coin="USDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/margin/isolated/financial-records",
            params={'symbol': 'BTCUSDT', 'startTime': '1692690126000', 'endTime': '1695625219083', 'limit': '20', 'idLessThan': '123', 'marginType': 'transfer_in', 'coin': 'USDT'}
        )

    async def test_get_isolated_interest_history(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"resultList": [], "maxId": "1", "minId": "1"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.get_isolated_interest_history(symbol="BTCUSDT", startTime="1695336324000", endTime="1695336324000", limit="20", idLessThan="123", coin="USDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/margin/isolated/interest-history",
            params={'symbol': 'BTCUSDT', 'startTime': '1695336324000', 'endTime': '1695336324000', 'limit': '20', 'idLessThan': '123', 'coin': 'USDT'}
        )

    async def test_get_isolated_interest_rate_and_max_borrowable(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.get_isolated_interest_rate_and_max_borrowable(symbol="BTCUSDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/margin/isolated/interest-rate-and-limit",
            params={'symbol': 'BTCUSDT'}
        )

    async def test_get_isolated_liquidation_history(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"resultList": [], "maxId": "1", "minId": "1"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.get_isolated_liquidation_history(symbol="BTCUSDT", startTime="1692690126000", endTime="1695624945382", limit="20", idLessThan="123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/margin/isolated/liquidation-history",
            params={'symbol': 'BTCUSDT', 'startTime': '1692690126000', 'endTime': '1695624945382', 'limit': '20', 'idLessThan': '123'}
        )

    async def test_get_isolated_liquidation_orders(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"resultList": [], "idLessThan": "123456789"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.get_isolated_liquidation_orders(startTime="1704100405000", endTime="1706174005091", limit="20", type="place_order", symbol="BTCUSDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/margin/isolated/liquidation-order",
            params={'startTime': '1704100405000', 'endTime': '1706174005091', 'limit': '20', 'type': 'place_order', 'symbol': 'BTCUSDT'}
        )

    async def test_get_isolated_max_borrowable(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"symbol": "ETHUSDT", "baseCoin": "ETH", "baseCoinMaxBorrowAmount": "10.1401916", "quoteCoin": "USDT", "quoteCoinMaxBorrowAmount": "3976070.21616"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.get_isolated_max_borrowable(symbol="BTCUSDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/margin/isolated/account/max-borrowable-amount",
            params={'symbol': 'BTCUSDT'}
        )

    async def test_get_isolated_max_transferable(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"baseCoin": "BTC", "symbol": "BTCUSDT", "baseCoinMaxTransferOutAmount": "199999", "quoteCoin": "USDT", "quoteCoinMaxTransferOutAmount": "1000000"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.margin.get_isolated_max_transferable(symbol="BTCUSDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/margin/isolated/account/max-transfer-out-amount",
            params={'symbol': 'BTCUSDT'}
        )

class TestSpot(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_client = AsyncMock()
        self.spot = Spot(self.mock_client)

    async def asyncTearDown(self):
        pass

    def test_spot_initialization(self):
        self.assertEqual(self.spot.client, self.mock_client)

    async def test_get_server_time(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"serverTime": "1688008631614"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_server_time()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/public/time"
        )

    async def test_get_symbol_config(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_symbol_config(symbol="BTCUSDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/public/symbols",
            params={'symbol': 'BTCUSDT'}
        )

    async def test_get_currency_information(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_currency_information(coin="BTC")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/public/coins",
            params={'coin': 'BTC'}
        )

    async def test_get_deposit_address(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_deposit_address(coin="USDT", chain="trc20")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/wallet/deposit-address",
            params={'coin': 'USDT', 'chain': 'trc20'}
        )

    async def test_get_deposit_record(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_deposit_record(startTime="1659036670000", endTime="1659076670000", coin="USDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/wallet/deposit-records",
            params={'startTime': '1659036670000', 'endTime': '1659076670000', 'coin': 'USDT'}
        )

    async def test_get_withdraw_record(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_withdraw_record(startTime="1659036670000", endTime="1659076670000", coin="USDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/wallet/withdrawal-records",
            params={'startTime': '1659036670000', 'endTime': '1659076670000', 'coin': 'USDT'}
        )

    async def test_withdraw(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"orderId": "888291686266343424", "clientOid": "123"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.withdraw(coin="USDT", transferType="on_chain", address="TBQ2LGFysnqkscvKqLBxnVVVw7ohiDvbdZ", size="10", chain="trc20")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/spot/wallet/withdrawal",
            body={'coin': 'USDT', 'transferType': 'on_chain', 'address': 'TBQ2LGFysnqkscvKqLBxnVVVw7ohiDvbdZ', 'size': '10', 'chain': 'trc20'}
        )

    async def test_sub_transfer(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"transferId": "123456", "clientOid": "x123"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.sub_transfer(fromType="spot", toType="usdt_futures", amount="100", coin="USDT", fromUserId="123", toUserId="456")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/spot/wallet/subaccount-transfer",
            body={'fromType': 'spot', 'toType': 'usdt_futures', 'amount': '100', 'coin': 'USDT', 'fromUserId': '123', 'toUserId': '456'}
        )

    async def test_transfer(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"transferId": "123456", "clientOid": "x123"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.transfer(fromType="spot", toType="isolated_margin", amount="300", coin="USDT", symbol="BTCUSDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/spot/wallet/transfer",
            body={'fromType': 'spot', 'toType': 'isolated_margin', 'amount': '300', 'coin': 'USDT', 'symbol': 'BTCUSDT'}
        )

    async def test_cancel_withdrawal(self):
        expected_response = {"code": "00000", "msg": "success", "data": "success"}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.cancel_withdrawal(orderId="1231231312312")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/spot/wallet/cancel-withdrawal",
            body={'orderId': '1231231312312'}
        )

    async def test_get_account_information(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_account_information()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/account/info"
        )

    async def test_get_account_assets(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_account_assets(coin="USDT", assetType="hold_only")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/account/assets",
            params={'coin': 'USDT', 'assetType': 'hold_only'}
        )

    async def test_get_sub_accounts_assets(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_sub_accounts_assets(idLessThan="123", limit="10")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/account/subaccount-assets",
            params={'idLessThan': '123', 'limit': '10'}
        )

    async def test_modify_deposit_account(self):
        expected_response = {"code": "00000", "msg": "success", "data": "success"}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.modify_deposit_account(accountType="usdt-futures", coin="USDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/spot/wallet/modify-deposit-account",
            body={'accountType': 'usdt-futures', 'coin': 'USDT'}
        )

    async def test_get_account_bills(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_account_bills(coin="USDT", startTime="1690196141868", endTime="1690196141868")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/account/bills",
            params={'coin': 'USDT', 'startTime': '1690196141868', 'endTime': '1690196141868'}
        )

    async def test_get_transferable_coin_list(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_transferable_coin_list(fromType="isolated_margin", toType="spot")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/wallet/transfer-coin-info",
            params={'fromType': 'isolated_margin', 'toType': 'spot'}
        )

    async def test_get_main_sub_transfer_record(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_main_sub_transfer_record(coin="USDT", startTime="1699510219000", endTime="1699684880000")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/account/sub-main-trans-record",
            params={'coin': 'USDT', 'startTime': '1699510219000', 'endTime': '1699684880000'}
        )

    async def test_get_transfer_record(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_transfer_record(coin="USDT", fromType="exchange", startTime="1659076670", endTime="1659076670")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/account/transferRecords",
            params={'coin': 'USDT', 'fromType': 'exchange', 'startTime': '1659076670', 'endTime': '1659076670'}
        )

    async def test_switch_bgb_deduct(self):
        expected_response = {"code": "00000", "msg": "success", "data": True}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.switch_bgb_deduct(deduct="on")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/spot/account/switch-deduct",
            body={'deduct': 'on'}
        )

    async def test_get_sub_account_deposit_address(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_sub_account_deposit_address(subUid="123", coin="USDT", chain="ERC20")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/wallet/subaccount-deposit-address",
            params={'subUid': '123', 'coin': 'USDT', 'chain': 'ERC20'}
        )

    async def test_get_bgb_deduct_info(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"deduct": "on"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_bgb_deduct_info()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/account/deduct-info"
        )

    async def test_get_sub_account_deposit_records(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_sub_account_deposit_records(subUid="12121212", coin="USDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/wallet/subaccount-deposit-records",
            params={'subUid': '12121212', 'coin': 'USDT'}
        )

    async def test_upgrade_account(self):
        expected_response = {"code": "00000", "msg": "success", "data": None}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.upgrade_account(subUid="123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/spot/account/upgrade",
            body={'subUid': '123'}
        )

    async def test_get_upgrade_status(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"status": "success"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_upgrade_status(subUid="123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/account/upgrade-status",
            params={'subUid': '123'}
        )

    async def test_get_ticker_information(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_ticker_information(symbol="BTCUSDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/market/tickers",
            params={'symbol': 'BTCUSDT'}
        )

    async def test_get_merge_depth(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_merge_depth(symbol="BTCUSDT", precision="scale0", limit="100")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/market/merge-depth",
            params={'symbol': 'BTCUSDT', 'precision': 'scale0', 'limit': '100'}
        )

    async def test_get_orderbook_depth(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_orderbook_depth(symbol="BTCUSDT", type="step0", limit="100")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/market/orderbook",
            params={'symbol': 'BTCUSDT', 'type': 'step0', 'limit': '100'}
        )

    async def test_get_candlestick_data(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_candlestick_data(symbol="BTCUSDT", granularity="1min", startTime="1659076670000", endTime="1659080270000", limit="100")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/market/candles",
            params={'symbol': 'BTCUSDT', 'granularity': '1min', 'startTime': '1659076670000', 'endTime': '1659080270000', 'limit': '100'}
        )

    async def test_get_call_auction_information(self):
        expected_response = {"code": "00000", "msg": "success", "data": {}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_call_auction_information(symbol="BTCUSDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/market/auction",
            params={'symbol': 'BTCUSDT'}
        )

    async def test_get_history_candlestick_data(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_history_candlestick_data(symbol="BTCUSDT", granularity="1min", endTime="1659080270000", limit="100")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/market/history-candles",
            params={'symbol': 'BTCUSDT', 'granularity': '1min', 'endTime': '1659080270000', 'limit': '100'}
        )

    async def test_get_recent_trades(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_recent_trades(symbol="BTCUSDT", limit="100")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/market/fills",
            params={'symbol': 'BTCUSDT', 'limit': '100'}
        )

    async def test_get_market_trades(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_market_trades(symbol="BTCUSDT", limit="20", startTime="1678965010861", endTime="1678965910861")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/market/fills-history",
            params={'symbol': 'BTCUSDT', 'limit': '20', 'startTime': '1678965010861', 'endTime': '1678965910861'}
        )

    async def test_get_vip_fee_rate(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_vip_fee_rate()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/market/vip-fee-rate"
        )

    async def test_place_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"orderId": "1001", "clientOid": "121211212122"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.place_order(symbol="BTCUSDT", side="buy", orderType="limit", force="gtc", price="23222.5", size="1", clientOid="121211212122")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/spot/trade/place-order",
            body={'symbol': 'BTCUSDT', 'side': 'buy', 'orderType': 'limit', 'force': 'gtc', 'price': '23222.5', 'size': '1', 'clientOid': '121211212122'}
        )

    async def test_batch_cancel_replace_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        order_list = [{
            "orderId": "xxxxxxxxxxxxxxxxx",
            "clientOid": "",
            "symbol": "BTCUSDT",
            "price": "3.17",
            "size": "5"
        }]
        response = await self.spot.batch_cancel_replace_order(orderList=order_list)
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/spot/trade/batch-cancel-replace-order",
            body={'orderList': order_list}
        )

        self.mock_client.reset_mock()
        response = await self.spot.cancel_order(symbol="BTCUSDT", tpslType="tpsl", clientOid="xx001")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/spot/trade/cancel-order",
            body={'symbol': 'BTCUSDT', 'tpslType': 'tpsl', 'clientOid': 'xx001'}
        )

    async def test_cancel_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"orderId": "121211212122", "clientOid": "xx001"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.cancel_order(symbol="BTCUSDT", orderId="121211212122")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/spot/trade/cancel-order",
            body={'symbol': 'BTCUSDT', 'orderId': '121211212122'}
        )

    async def test_batch_cancel_orders(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"successList": [], "failureList": []}}
        self.mock_client._send_request.return_value = expected_response

        order_list = [{
            "orderId": "121211212122",
            "symbol": "BTCUSDT",
            "clientOid": "121211212122"
        }]
        response = await self.spot.batch_cancel_orders(orderList=order_list, symbol="BTCUSDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/spot/trade/batch-cancel-order",
            body={'orderList': order_list, 'symbol': 'BTCUSDT'}
        )

    async def test_batch_place_orders(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"successList": [], "failureList": []}}
        self.mock_client._send_request.return_value = expected_response

        order_list = [{
            "side": "buy",
            "orderType": "limit",
            "force": "gtc",
            "price": "23222.5",
            "size": "1",
            "clientOid": "121211212122"
        }]
        response = await self.spot.batch_place_orders(symbol="BTCUSDT", orderList=order_list, batchMode="single")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/spot/trade/batch-orders",
            body={'symbol': 'BTCUSDT', 'orderList': order_list, 'batchMode': 'single'}
        )

        self.mock_client.reset_mock()
        order_list_multiple = [{
            "symbol": "BTCUSDT",
            "side": "buy",
            "orderType": "limit",
            "force": "gtc",
            "price": "23222.5",
            "size": "1",
            "clientOid": "121211212122"
        }]
        response = await self.spot.batch_place_orders(orderList=order_list_multiple, batchMode="multiple")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/spot/trade/batch-orders",
            body={'orderList': order_list_multiple, 'batchMode': 'multiple'}
        )

    async def test_cancel_replace_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"orderId": "xxxxxxxxxxxxxxx", "clientOid": None, "success": "success", "msg": None}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.cancel_replace_order(symbol="BTCUSDT", price="3.24", size="4", orderId="xxxxxxxxxxxxxxx")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/spot/trade/cancel-replace-order",
            body={'symbol': 'BTCUSDT', 'price': '3.24', 'size': '4', 'orderId': 'xxxxxxxxxxxxxxx'}
        )

    async def test_cancel_order_by_symbol(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"symbol": "BGBUSDT"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.cancel_order_by_symbol(symbol="BTCUSDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/spot/trade/cancel-symbol-order",
            body={'symbol': 'BTCUSDT'}
        )

    async def test_cancel_plan_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"result": "success"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.cancel_plan_order(orderId="121211212122")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/spot/trade/cancel-plan-order",
            body={'orderId': '121211212122'}
        )

        self.mock_client.reset_mock()
        response = await self.spot.cancel_plan_order(clientOid="test_client_oid")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/spot/trade/cancel-plan-order",
            body={'clientOid': 'test_client_oid'}
        )

    async def test_get_order_info(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_order_info(orderId="1234567890")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/trade/orderInfo",
            params={'orderId': '1234567890'}
        )

    async def test_get_current_orders(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_current_orders(symbol="BTCUSDT", startTime="1659036670000", endTime="1659076670000", limit="20")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/trade/unfilled-orders",
            params={'symbol': 'BTCUSDT', 'startTime': '1659036670000', 'endTime': '1659076670000', 'limit': '20'}
        )

    async def test_get_history_orders(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_history_orders(symbol="BTCUSDT", startTime="1659036670000", endTime="1659076670000", limit="20")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/trade/history-orders",
            params={'symbol': 'BTCUSDT', 'startTime': '1659036670000', 'endTime': '1659076670000', 'limit': '20'}
        )

    async def test_get_fills(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_fills(symbol="BTCUSDT", startTime="1659036670000", endTime="1659076670000", limit="20")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/trade/fills",
            params={'symbol': 'BTCUSDT', 'startTime': '1659036670000', 'endTime': '1659076670000', 'limit': '20'}
        )

    async def test_place_plan_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"orderId": "121211212122", "clientOid": "121211212122"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.place_plan_order(symbol="TRXUSDT", side="buy", triggerPrice="0.041572", executePrice="0.041572", size="151", triggerType="market_price", orderType="limit", clientOid="12345")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/spot/trade/place-plan-order",
            body={'symbol': 'TRXUSDT', 'side': 'buy', 'triggerPrice': '0.041572', 'executePrice': '0.041572', 'size': '151', 'triggerType': 'market_price', 'orderType': 'limit', 'clientOid': '12345'}
        )

    async def test_modify_plan_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"orderId": "121211212122", "clientOid": "121211212122"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.modify_plan_order(orderId="121211212122", triggerPrice="0.041222", executePrice="0.041272", size="156", orderType="limit")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/spot/trade/modify-plan-order",
            body={'orderId': '121211212122', 'triggerPrice': '0.041222', 'executePrice': '0.041272', 'size': '156', 'orderType': 'limit'}
        )

    async def test_get_current_plan_orders(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"nextFlag": False, "idLessThan": "1", "orderList": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_current_plan_orders(symbol="BTCUSDT", limit="10")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/trade/current-plan-order",
            params={'symbol': 'BTCUSDT', 'limit': '10'}
        )

    async def test_get_plan_sub_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_plan_sub_order(planOrderId="xxxxxxxxxxxxxxxxxx")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/trade/plan-sub-order",
            params={'planOrderId': 'xxxxxxxxxxxxxxxxxx'}
        )

    async def test_get_history_plan_orders(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"nextFlag": False, "idLessThan": "1", "orderList": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.get_history_plan_orders(symbol="BTCUSDT", startTime="1659036670000", endTime="1659076670000", limit="20")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v2/spot/trade/history-plan-order",
            params={'symbol': 'BTCUSDT', 'startTime': '1659036670000', 'endTime': '1659076670000', 'limit': '20'}
        )

    async def test_cancel_plan_orders_in_batch(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"successList": [], "failureList": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.spot.cancel_plan_orders_in_batch(symbolList=["BTCUSDT", "ETHUSDT"])
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v2/spot/trade/batch-cancel-plan-order",
            body={'symbolList': ['BTCUSDT', 'ETHUSDT']}
        )

class TestUta(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_client = AsyncMock()
        self.uta = Uta(self.mock_client)
        self.mock_client._send_websocket_request.return_value = {"status": "message sent"}

    def tearDown(self):
        pass

    def test_uta_initialization(self):
        self.assertEqual(self.uta.client, self.mock_client)

    async def test_get_account_info(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"uid": "1111111111", "accountMode": "hybrid"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_account_info()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/account/settings",
            params={}
        )

    async def test_get_account_assets(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"accountEquity": "11.13919278"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_account_assets()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/account/assets",
            params={}
        )

    async def test_get_account_funding_assets(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_account_funding_assets(coin="USDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/account/funding-assets",
            params={'coin': 'USDT'}
        )

    async def test_get_account_fee_rate(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"makerFeeRate": "0.0008", "takerFeeRate": "0.0008"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_account_fee_rate(symbol="BTCUSDT", category="SPOT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/account/fee-rate",
            params={'symbol': 'BTCUSDT', 'category': 'SPOT'}
        )

    async def test_get_convert_records(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"list": [], "cursor": "123"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_convert_records(fromCoin="BTC", toCoin="USDT", startTime="123", endTime="456", limit="10", cursor="789")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/account/convert-records",
            params={'fromCoin': 'BTC', 'toCoin': 'USDT', 'startTime': '123', 'endTime': '456', 'limit': '10', 'cursor': '789'}
        )

    async def test_get_historical_candlestick_uta(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_kline_candlestick_history(
            category="USDT-FUTURES",
            symbol="BTCUSDT",
            interval="1m",
            startTime="1678886400000",
            endTime="1678886400000",
            type="MARKET",
            limit="100"
        )
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/market/history-candles",
            params={
                'category': 'USDT-FUTURES',
                'symbol': 'BTCUSDT',
                'interval': '1m',
                'startTime': '1678886400000',
                'endTime': '1678886400000',
                'type': 'MARKET',
                'limit': '100'
            }
        )

    async def test_get_kline_candlestick(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_kline_candlestick(
            category="USDT-FUTURES",
            symbol="BTCUSDT",
            interval="1m",
            startTime="1678886400000",
            endTime="1678886400000",
            type="MARKET",
            limit="100"
        )
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/market/candles",
            params={
                'category': 'USDT-FUTURES',
                'symbol': 'BTCUSDT',
                'interval': '1m',
                'startTime': '1678886400000',
                'endTime': '1678886400000',
                'type': 'MARKET',
                'limit': '100'
            }
        )

    async def test_get_deduct_info(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"deduct": "on"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_deduct_info()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/account/deduct-info",
            params={}
        )

    async def test_subscribe_account_channel(self):
        response = await self.uta.subscribe_account_channel()
        self.mock_client._send_websocket_request.assert_called_once_with({
            "op": "subscribe",
            "args": [
                {
                    "instType": "UTA",
                    "topic": "account"
                }
            ]
        })
        self.assertEqual(response, {"status": "message sent"})

    async def test_get_margin_coin_info(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"productId": "xxxxxxxx", "coinInfo": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_margin_coin_info(productId="xxx")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/ins-loan/ensure-coins-convert",
            params={'productId': 'xxx'}
        )

    async def test_get_margin_loan(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"dailyInterest": "0.1", "annualInterest": "0.00416667", "limit": "3000"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_margin_loan(coin="BTC")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/market/margin-loans",
            params={'coin': 'BTC'}
        )

    async def test_get_loan_orders(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_loan_orders(orderId="test_order_id", startTime="123", endTime="456")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/ins-loan/loan-order",
            params={'orderId': 'test_order_id', 'startTime': '123', 'endTime': '456'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.get_loan_orders()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/ins-loan/loan-order",
            params={}
        )

    async def test_get_ltv(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"ltv": "0.6667"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_ltv(riskUnitId="test_risk_unit_id")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/ins-loan/ltv-convert",
            params={'riskUnitId': 'test_risk_unit_id'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.get_ltv()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/ins-loan/ltv-convert",
            params={}
        )

    async def test_get_open_interest_limit(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_open_interest_limit(category="USDT-FUTURES", symbol="BTCUSDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/market/oi-limit",
            params={'category': 'USDT-FUTURES', 'symbol': 'BTCUSDT'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.get_open_interest_limit(category="USDT-FUTURES")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/market/oi-limit",
            params={'category': 'USDT-FUTURES'}
        )

    async def test_get_open_interest(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"list": [{"symbol": "BTCUSDT", "openInterest": "2243.019"}], "ts": "1730969652411"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_open_interest(category="USDT-FUTURES", symbol="BTCUSDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/market/open-interest",
            params={'category': 'USDT-FUTURES', 'symbol': 'BTCUSDT'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.get_open_interest(category="USDT-FUTURES")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/market/open-interest",
            params={'category': 'USDT-FUTURES'}
        )

    async def test_get_open_orders(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"list": [], "cursor": "1235058132196622336"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_open_orders(category="USDT-FUTURES", symbol="BTCUSDT", startTime="1659076670000", endTime="1659076670000", limit="100", cursor="123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/trade/unfilled-orders",
            params={'category': 'USDT-FUTURES', 'symbol': 'BTCUSDT', 'startTime': '1659076670000', 'endTime': '1659076670000', 'limit': '100', 'cursor': '123'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.get_open_orders(category="SPOT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/trade/unfilled-orders",
            params={'category': 'SPOT'}
        )

    async def test_get_order_details(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"orderId": "111111111111111111"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_order_details(orderId="111111111111111111")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/trade/order-info",
            params={'orderId': '111111111111111111'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.get_order_details(clientOid="121211212122")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/trade/order-info",
            params={'clientOid': '121211212122'}
        )

    async def test_get_order_history(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"list": [], "cursor": "1233319323918499840"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_order_history(category="USDT-FUTURES", symbol="BTCUSDT", startTime="1659076670000", endTime="1659076670000", limit="100", cursor="123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/trade/history-orders",
            params={'category': 'USDT-FUTURES', 'symbol': 'BTCUSDT', 'startTime': '1659076670000', 'endTime': '1659076670000', 'limit': '100', 'cursor': '123'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.get_order_history(category="SPOT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/trade/history-orders",
            params={'category': 'SPOT'}
        )

    async def test_get_orderbook(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"a": [], "b": [], "ts": "1730969017964"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_orderbook(category="USDT-FUTURES", symbol="BTCUSDT", limit="5")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/market/orderbook",
            params={'category': 'USDT-FUTURES', 'symbol': 'BTCUSDT', 'limit': '5'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.get_orderbook(category="SPOT", symbol="ETHUSDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/market/orderbook",
            params={'category': 'SPOT', 'symbol': 'ETHUSDT'}
        )

    async def test_get_position_adl_rank(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_position_adl_rank()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/position/adlRank",
            params={}
        )

    async def test_get_position_info(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"list": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_position_info(category="USDT-FUTURES", symbol="BTCUSDT", posSide="long")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/position/current-position",
            params={'category': 'USDT-FUTURES', 'symbol': 'BTCUSDT', 'posSide': 'long'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.get_position_info(category="SPOT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/position/current-position",
            params={'category': 'SPOT'}
        )

    async def test_get_position_tier(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_position_tier(category="USDT-FUTURES", symbol="BTCUSDT", coin="USDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/market/position-tier",
            params={'category': 'USDT-FUTURES', 'symbol': 'BTCUSDT', 'coin': 'USDT'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.get_position_tier(category="MARGIN")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/market/position-tier",
            params={'category': 'MARGIN'}
        )

    async def test_get_positions_history(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"list": [], "cursor": "1111111111111111111"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_positions_history(category="USDT-FUTURES", symbol="BTCUSDT", startTime="1659076670000", endTime="1659076670000", limit="100", cursor="123")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/position/history-position",
            params={'category': 'USDT-FUTURES', 'symbol': 'BTCUSDT', 'startTime': '1659076670000', 'endTime': '1659076670000', 'limit': '100', 'cursor': '123'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.get_positions_history(category="SPOT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/position/history-position",
            params={'category': 'SPOT'}
        )

    async def test_get_product_info(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"productId": "xxxxxxxx", "leverage": "2"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_product_info(productId="test_product_id")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/ins-loan/product-infos",
            params={'productId': 'test_product_id'}
        )

    async def test_get_proof_of_reserves(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"merkleRootHash": "e0dff99bbe2c2dcb"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_proof_of_reserves()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/market/proof-of-reserves",
            params={}
        )

    async def test_get_repayable_coins(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"repayableCoinList": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_repayable_coins()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/account/repayable-coins",
            params={}
        )

    async def test_get_repayment_orders(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_repayment_orders(startTime="1659076670000", endTime="1659076670000", limit="100")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/ins-loan/repaid-history",
            params={'startTime': '1659076670000', 'endTime': '1659076670000', 'limit': '100'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.get_repayment_orders()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/ins-loan/repaid-history",
            params={}
        )

    async def test_get_risk_reserve(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"totalBalance": "", "coin": "USDT"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_risk_reserve(category="USDT-FUTURES", symbol="BTCUSDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/market/risk-reserve",
            params={'category': 'USDT-FUTURES', 'symbol': 'BTCUSDT'}
        )

    async def test_get_risk_unit(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"riskUnitId": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_risk_unit()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/ins-loan/risk-unit",
            params={}
        )

    async def test_get_sub_account_api_keys(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"items": [], "hasNext": False, "cursor": "18484"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_sub_account_api_keys(subUid="test_sub_uid", limit="100", cursor="test_cursor")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/user/sub-api-list",
            params={'subUid': 'test_sub_uid', 'limit': '100', 'cursor': 'test_cursor'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.get_sub_account_api_keys(subUid="test_sub_uid")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/user/sub-api-list",
            params={'subUid': 'test_sub_uid'}
        )

    async def test_get_sub_account_list(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"list": [], "hasNext": False, "cursor": "18484"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_sub_account_list(limit="100", cursor="test_cursor")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/user/sub-list",
            params={'limit': '100', 'cursor': 'test_cursor'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.get_sub_account_list()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/user/sub-list",
            params={}
        )

    async def test_get_subaccount_unified_assets(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_subaccount_unified_assets(subUid="test_sub_uid", cursor="test_cursor", limit="10")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/account/sub-unified-assets",
            params={'subUid': 'test_sub_uid', 'cursor': 'test_cursor', 'limit': '10'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.get_subaccount_unified_assets()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/account/sub-unified-assets",
            params={}
        )

    async def test_get_switch_status(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"status": "success"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_switch_status()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/account/switch-status",
            params={}
        )

    async def test_get_main_sub_transfer_records(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"list": [], "cursor": "2"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_main_sub_transfer_records(subUid="test_sub_uid", role="initiator", coin="USDT", startTime="1659076670000", endTime="1659076670000", clientOid="test_client_oid", limit="100", cursor="test_cursor")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/account/sub-transfer-record",
            params={'subUid': 'test_sub_uid', 'role': 'initiator', 'coin': 'USDT', 'startTime': '1659076670000', 'endTime': '1659076670000', 'clientOid': 'test_client_oid', 'limit': '100', 'cursor': 'test_cursor'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.get_main_sub_transfer_records()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/account/sub-transfer-record",
            params={}
        )

    async def test_get_tickers(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_tickers(category="SPOT", symbol="BTCUSDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/market/tickers",
            params={'category': 'SPOT', 'symbol': 'BTCUSDT'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.get_tickers(category="USDT-FUTURES")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/market/tickers",
            params={'category': 'USDT-FUTURES'}
        )

    async def test_get_trade_symbols(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"productId": "xxxxxxxx", "spotSymbols": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_trade_symbols(productId="test_product_id")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/ins-loan/symbols",
            params={'productId': 'test_product_id'}
        )

    async def test_get_transferable_coins(self):
        expected_response = {"code": "00000", "msg": "success", "data": ["USDT"]}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_transferable_coins(fromType="uta", toType="spot")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/account/transferable-coins",
            params={'fromType': 'uta', 'toType': 'spot'}
        )

    async def test_get_transferred_quantity(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"coin": "USDT", "transfered": "1223", "userId": "xxxxxxxxxx"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_transferred_quantity(coin="USDT", userId="test_user_id")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/ins-loan/transfered",
            params={'coin': 'USDT', 'userId': 'test_user_id'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.get_transferred_quantity(coin="BTC")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/ins-loan/transfered",
            params={'coin': 'BTC'}
        )

    async def test_get_withdrawal_records(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_withdrawal_records(startTime="1700561435000", endTime="1703153435933", coin="USDT", orderId="test_order_id", clientOid="test_client_oid", limit="100", cursor="test_cursor")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/account/withdrawal-records",
            params={'startTime': '1700561435000', 'endTime': '1703153435933', 'coin': 'USDT', 'orderId': 'test_order_id', 'clientOid': 'test_client_oid', 'limit': '100', 'cursor': 'test_cursor'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.get_withdrawal_records(startTime="1700561435000", endTime="1703153435933")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/account/withdrawal-records",
            params={'startTime': '1700561435000', 'endTime': '1703153435933'}
        )

    async def test_main_sub_account_transfer(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"transferId": "172947298237423", "clientOid": "test_001"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.main_sub_account_transfer(fromType="spot", toType="uta", amount="1000", coin="USDT", fromUserId="1991021336", toUserId="4746345901", clientOid="test_client_oid")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/account/sub-transfer",
            body={'fromType': 'spot', 'toType': 'uta', 'amount': '1000', 'coin': 'USDT', 'fromUserId': '1991021336', 'toUserId': '4746345901', 'clientOid': 'test_client_oid'}
        )

    async def test_transfer(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"transferId":"111111111111"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.transfer(fromType="spot", toType="p2p", amount="0.1", coin="BTC", symbol="BTCUSDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/account/transfer",
            body={'fromType': 'spot', 'toType': 'p2p', 'amount': '0.1', 'coin': 'BTC', 'symbol': 'BTCUSDT'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.transfer(fromType="spot", toType="p2p", amount="0.1", coin="BTC")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/account/transfer",
            body={'fromType': 'spot', 'toType': 'p2p', 'amount': '0.1', 'coin': 'BTC'}
        )

    async def test_modify_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"orderId": "121212121212", "clientOid": "BITGET#1627293504612"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.modify_order(orderId="1", qty="123", price="123", autoCancel="no")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/trade/modify-order",
            body={'orderId': '1', 'qty': '123', 'price': '123', 'autoCancel': 'no'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.modify_order(clientOid="test_client_oid", qty="10")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/trade/modify-order",
            body={'clientOid': 'test_client_oid', 'qty': '10'}
        )

    async def test_history_strategy_orders(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"list": []}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.history_strategy_orders(category="USDT-FUTURES", type="tpsl", startTime="1597026383085", endTime="1597026383085", limit="100", cursor="test_cursor")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/trade/history-strategy-orders",
            params={'category': 'USDT-FUTURES', 'type': 'tpsl', 'startTime': '1597026383085', 'endTime': '1597026383085', 'limit': '100', 'cursor': 'test_cursor'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.history_strategy_orders(category="SPOT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/trade/history-strategy-orders",
            params={'category': 'SPOT'}
        )

    async def test_modify_sub_account_api_key(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"apiKey": "***********************************"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.modify_sub_account_api_key(apikey="test_api_key", passphrase="test_passphrase", type="read_write", permissions=["uta_trade"], ips=["127.0.0.1"])
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/user/update-sub-api",
            body={'apiKey': 'test_api_key', 'passphrase': 'test_passphrase', 'type': 'read_write', 'permissions': ['uta_trade'], 'ips': ['127.0.0.1']}
        )

        self.mock_client.reset_mock()
        response = await self.uta.modify_sub_account_api_key(apikey="test_api_key", passphrase="test_passphrase")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/user/update-sub-api",
            body={'apiKey': 'test_api_key', 'passphrase': 'test_passphrase'}
        )

    async def test_place_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"clientOid": "121211212122", "orderId": "121212121212"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.place_order(category="SPOT", symbol="BGBUSDT", qty="123", side="buy", orderType="limit", price="1.11", timeInForce="gtc", posSide="long", clientOid="test_client_oid", reduceOnly="no", stpMode="none", tpTriggerBy="market", slTriggerBy="market", takeProfit="100", stopLoss="50", tpOrderType="market", slOrderType="market", tpLimitPrice="90", slLimitPrice="60")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/trade/place-order",
            body={'category': 'SPOT', 'symbol': 'BGBUSDT', 'qty': '123', 'side': 'buy', 'orderType': 'limit', 'price': '1.11', 'timeInForce': 'gtc', 'posSide': 'long', 'clientOid': 'test_client_oid', 'reduceOnly': 'no', 'stpMode': 'none', 'tpTriggerBy': 'market', 'slTriggerBy': 'market', 'takeProfit': '100', 'stopLoss': '50', 'tpOrderType': 'market', 'slOrderType': 'market', 'tpLimitPrice': '90', 'slLimitPrice': '60'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.place_order(category="USDT-FUTURES", symbol="BTCUSDT", qty="0.001", side="buy", orderType="market")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/trade/place-order",
            body={'category': 'USDT-FUTURES', 'symbol': 'BTCUSDT', 'qty': '0.001', 'side': 'buy', 'orderType': 'market'}
        )

    async def test_place_strategy_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"clientOid": "121211212122", "orderId": "121212121212"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.place_strategy_order(category="USDT-FUTURES", symbol="BTCUSDT", posSide="long", clientOid="test_client_oid", type="tpsl", tpslMode="full", qty="0.001", tpTriggerBy="market", slTriggerBy="market", takeProfit="100", stopLoss="50", tpOrderType="market", slOrderType="market", tpLimitPrice="90", slLimitPrice="60")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/trade/place-strategy-order",
            body={'category': 'USDT-FUTURES', 'symbol': 'BTCUSDT', 'posSide': 'long', 'clientOid': 'test_client_oid', 'type': 'tpsl', 'tpslMode': 'full', 'qty': '0.001', 'tpTrigger': 'market', 'slTriggerBy': 'market', 'takeProfit': '100', 'stopLoss': '50', 'tpOrderType': 'market', 'slOrderType': 'market', 'tpLimitPrice': '90', 'slLimitPrice': '60'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.place_strategy_order(category="SPOT", symbol="ETHUSDT", posSide="long")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/trade/place-strategy-order",
            body={'category': 'SPOT', 'symbol': 'ETHUSDT', 'posSide': 'long'}
        )

    async def test_subscribe_position_channel(self):
        response = await self.uta.subscribe_position_channel()
        self.mock_client._send_websocket_request.assert_called_once_with({
            "op": "subscribe",
            "args": [
                {
                    "instType": "UTA",
                    "topic": "position"
                }
            ]
        })
        self.assertEqual(response, {"status": "message sent"})

    async def test_subscribe_order_channel(self):
        response = await self.uta.subscribe_order_channel()
        self.mock_client._send_websocket_request.assert_called_once_with({
            "op": "subscribe",
            "args": [
                {
                    "instType": "UTA",
                    "topic": "order"
                }
            ]
        })
        self.assertEqual(response, {"status": "message sent"})

    async def test_subscribe_public_trades_channel(self):
        response = await self.uta.subscribe_public_trades_channel(instType="usdt-futures", symbol="BTCUSDT")
        self.mock_client._send_websocket_request.assert_called_once_with({
            "op": "subscribe",
            "args": [
                {
                    "instType": "usdt-futures",
                    "topic": "publicTrade",
                    "symbol": "BTCUSDT"
                }
            ]
        })
        self.assertEqual(response, {"status": "message sent"})

    async def test_subscribe_tickers_channel(self):
        response = await self.uta.subscribe_tickers_channel(instType="spot", symbol="BTCUSDT")
        self.mock_client._send_websocket_request.assert_called_once_with({
            "op": "subscribe",
            "args": [
                {
                    "instType": "spot",
                    "topic": "ticker",
                    "symbol": "BTCUSDT"
                }
            ]
        })
        self.assertEqual(response, {"status": "message sent"})

    async def test_repay(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"result": "YES", "repayAmount":"4345"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.repay(repayableCoinList=["USDT"], paymentCoinList=["ETH"])
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/account/repay",
            body={'repayableCoinList': ['USDT'], 'paymentCoinList': ['ETH']}
        )

    async def test_set_holding_mode(self):
        expected_response = {"code": "00000", "msg": "success", "data": "success"}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.set_holding_mode(holdMode="one_way_mode")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/account/set-hold-mode",
            body={'holdMode': 'one_way_mode'}
        )

    async def test_set_leverage(self):
        expected_response = {"code": "00000", "msg": "success", "data": "success"}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.set_leverage(category="USDT-FUTURES", leverage="10", symbol="BTCUSDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/account/set-leverage",
            body={'category': 'USDT-FUTURES', 'leverage': '10', 'symbol': 'BTCUSDT'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.set_leverage(category="MARGIN", leverage="5", coin="USDT", posSide="long")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/account/set-leverage",
            body={'category': 'MARGIN', 'leverage': '5', 'coin': 'USDT', 'posSide': 'long'}
        )

    async def test_set_up_deposit_account(self):
        expected_response = {"code": "00000", "msg": "success", "data": "success"}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.set_up_deposit_account(coin="BTC", accountType="funding")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/account/deposit-account",
            body={'coin': 'BTC', 'accountType': 'funding'}
        )

    async def test_switch_account(self):
        expected_response = {"code": "00000", "msg": "success", "data": None}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.switch_account()
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/account/switch",
            body={}
        )

    async def test_switch_deduct(self):
        expected_response = {"code": "00000", "msg": "success", "data": "success"}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.switch_deduct(deduct="on")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/account/switch-deduct",
            body={'deduct': 'on'}
        )

    async def test_withdrawal(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"orderId": "111111111111", "clientOid": "111111111111"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.withdrawal(coin="usdt", transferType="internal_transfer", address="234234242", size="100", chain="erc20", innerToType="uid", areaCode="123", tag="test_tag", remark="test_remark", clientOid="test_client_oid", memberCode="bithumb", identityType="user", companyName="test_company", firstName="test_first", lastName="test_last")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/account/withdrawal",
            body={'coin': 'usdt', 'transferType': 'internal_transfer', 'address': '234234242', 'size': '100', 'chain': 'erc20', 'innerToType': 'uid', 'areaCode': '123', 'tag': 'test_tag', 'remark': 'test_remark', 'clientOid': 'test_client_oid', 'memberCode': 'bithumb', 'identityType': 'user', 'companyName': 'test_company', 'firstName': 'test_first', 'lastName': 'test_last'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.withdrawal(coin="usdt", transferType="on_chain", address="test_address", size="10", chain="erc20")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/account/withdrawal",
            body={'coin': 'usdt', 'transferType': 'on_chain', 'address': 'test_address', 'size': '10', 'chain': 'erc20'}
        )

    async def test_modify_strategy_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"clientOid": "121211212122", "orderId": "121212121212"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.modify_strategy_order(orderId="121211212122", qty="1", tpTriggerBy="market", takeProfit="106000", tpOrderType="market")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/trade/modify-strategy-order",
            body={'orderId': '121211212122', 'qty': '1', 'tpTriggerBy': 'market', 'takeProfit': '106000', 'tpOrderType': 'market'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.modify_strategy_order(orderId="test_client_oid", qty="10", stopLoss="90000", slOrderType="limit", slLimitPrice="89000")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/trade/modify-strategy-order",
            body={'orderId': 'test_client_oid', 'qty': '10', 'stopLoss': '90000', 'slOrderType': 'limit', 'slLimitPrice': '89000'}
        )

    async def test_get_recent_public_fills(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_recent_public_fills(category="USDT-FUTURES", symbol="BTCUSDT", limit="100")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/market/fills",
            params={'category': 'USDT-FUTURES', 'symbol': 'BTCUSDT', 'limit': '100'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.get_recent_public_fills(category="SPOT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "GET",
            "/api/v3/market/fills",
            params={'category': 'SPOT'}
        )

    async def test_batch_cancel(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        orders_to_cancel = [
            {"orderId": "112233", "category": "spot", "symbol": "BTCUSDT"},
            {"clientOid": "123456", "category": "spot", "symbol": "BTCUSDT"}
        ]
        response = await self.uta.batch_cancel(orders_to_cancel)
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/trade/cancel-batch",
            body=orders_to_cancel
        )

    async def test_batch_modify_orders(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        order_list = [
            {"orderId": "1", "qty": "123", "price": "123", "autoCancel": "no"},
            {"orderId": "2", "qty": "123", "price": "123", "autoCancel": "no"}
        ]
        response = await self.uta.batch_modify_orders(order_list)
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/trade/batch-modify-order",
            body=order_list
        )

    async def test_batch_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        order_list = [
            {"category": "SPOT", "symbol": "BGBUSDT", "orderType": "limit", "qty": "123", "price": "1.11", "side": "buy", "posSide": "long", "timeInForce": "gtc", "reduceOnly": "no"}
        ]
        response = await self.uta.batch_order(order_list)
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/trade/place-batch",
            body=order_list
        )

    #    async def test_bind_unbind_uid_to_risk_unit(self):
#        expected_response = {"code": "00000", "msg": "success", "data": {"riskUnitId": "12345678", "uid": "12345678", "operate": "bind"}}
#        self.mock_client._send_request.return_value = expected_response
#
#        response = await self.uta.bind_unbind_uid_to_risk_unit(uid="12345678", operate="bind", riskUnitId="12345678")
#        self.assertEqual(response, expected_response)
#        self.mock_client._send_request.assert_called_once_with(
#            "POST",
#            "/api/v3/ins-loan/bind-uid",
#            body={'uid': '12345678', 'operate': 'bind', 'riskUnitId': '12345678'}
#        )
#
#        self.mock_client.reset_mock()
#        response = await self.uta.bind_unbind_uid_to_risk_unit(uid="12345678", operate="unbind")
#        self.assertEqual(response, expected_response)
#        self.mock_client._send_request.assert_called_once_with(
#            "POST",
#            "/api/v3/ins-loan/bind-uid",
#            body={'uid': '12345678', 'operate': 'unbind'}
#        )

    @patch('time.time', Mock(return_value=1750035029.506))
    async def test_batch_place_order_channel(self):
        category = "spot"
        orders = [
            {
                "clientOid": "xxxxxxxx1",
                "orderType": "limit",
                "price": "100",
                "qty": "0.1",
                "side": "buy",
                "symbol": "BTCUSDT",
                "timeInForce": "gtc"
            },
            {
                "clientOid": "xxxxxxxx2",
                "orderType": "limit",
                "price": "100",
                "qty": "0.15",
                "side": "buy",
                "symbol": "BTCUSDT",
                "timeInForce": "gtc"
            }
        ]
        response = await self.uta.batch_place_order_channel("1750035029506", category, orders)
        expected_message = {
            "op": "trade",
            "id": "1750035029506",
            "category": category,
            "topic": "batch-place",
            "args": orders
        }
        self.mock_client._send_websocket_request.assert_called_once_with(expected_message)
        self.assertEqual(response, {"status": "message sent"})

    async def test_cancel_all_orders(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.cancel_all_orders(category="SPOT", symbol="BTCUSDT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/trade/cancel-symbol-order",
            body={'category': 'SPOT', 'symbol': 'BTCUSDT'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.cancel_all_orders(category="SPOT")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/trade/cancel-symbol-order",
            body={'category': 'SPOT'}
        )

    async def test_cancel_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"orderId": "111111111111111111", "clientOid": "121211212122"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.cancel_order(orderId="111111111111111111")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/trade/cancel-order",
            body={'orderId': '111111111111111111'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.cancel_order(clientOid="121211212122")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/trade/cancel-order",
            body={'clientOid': '121211212122'}
        )

    async def test_cancel_strategy_order(self):
        expected_response = {"code": "00000", "msg": "success", "data": None}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.cancel_strategy_order(orderId="111111111111111111")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/trade/cancel-strategy-order",
            body={'orderId': '111111111111111111'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.cancel_strategy_order(clientOid="121211212122")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/trade/cancel-strategy-order",
            body={'clientOid': '121211212122'}
        )

    async def test_close_all_positions(self):
        expected_response = {"code": "00000", "msg": "success", "data": []}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.close_all_positions(category="USDT-FUTURES", symbol="BTCUSDT", posSide="long")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/trade/close-positions",
            body={'category': 'USDT-FUTURES', 'symbol': 'BTCUSDT', 'posSide': 'long'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.close_all_positions(category="USDT-FUTURES")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/trade/close-positions",
            body={'category': 'USDT-FUTURES'}
        )

    async def test_countdown_cancel_all(self):
        expected_response = {"code": "00000", "msg": "success", "data": "success"}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.countdown_cancel_all(countdown="40")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/trade/countdown-cancel-all",
            body={'countdown': '40'}
        )

    async def test_create_sub_account(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"username": "xxxx@virtual-bitget.com", "subUid": "xxxx", "status": "normal", "note": "xxxx", "createdTime": "1740211445041", "updatedTime": "1740211445041"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.create_sub_account(username="testuser", accountMode="unified", note="testnote")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/user/create-sub",
            body={'username': 'testuser', 'accountMode': 'unified', 'note': 'testnote'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.create_sub_account(username="anotheruser")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/user/create-sub",
            body={'username': 'anotheruser'}
        )

    async def test_get_max_open_available(self):
        expected_response = {"code": "00000", "msg": "success", "data": {"available": "52.008255"}}
        self.mock_client._send_request.return_value = expected_response

        response = await self.uta.get_max_open_available(category="SPOT", symbol="BTCUSDT", orderType="market", side="sell", price="10000", size="1")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/account/max-open-available",
            body={'category': 'SPOT', 'symbol': 'BTCUSDT', 'orderType': 'market', 'side': 'sell', 'price': '10000', 'size': '1'}
        )

        self.mock_client.reset_mock()
        response = await self.uta.get_max_open_available(category="SPOT", symbol="BTCUSDT", orderType="market", side="sell")
        self.assertEqual(response, expected_response)
        self.mock_client._send_request.assert_called_once_with(
            "POST",
            "/api/v3/account/max-open-available",
            body={'category': 'SPOT', 'symbol': 'BTCUSDT', 'orderType': 'market', 'side': 'sell'}
        )


