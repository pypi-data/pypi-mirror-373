from typing import Protocol, runtime_checkable
import requests
import json
from allora_sdk.protos.cosmos.auth.v1beta1 import (
    AddressBytesToStringRequest as cosmos_auth_v1beta1_AddressBytesToStringRequest,
    AddressBytesToStringResponse as cosmos_auth_v1beta1_AddressBytesToStringResponse,
    AddressStringToBytesRequest as cosmos_auth_v1beta1_AddressStringToBytesRequest,
    AddressStringToBytesResponse as cosmos_auth_v1beta1_AddressStringToBytesResponse,
    Bech32PrefixRequest as cosmos_auth_v1beta1_Bech32PrefixRequest,
    Bech32PrefixResponse as cosmos_auth_v1beta1_Bech32PrefixResponse,
    MsgUpdateParams as cosmos_auth_v1beta1_MsgUpdateParams,
    MsgUpdateParamsResponse as cosmos_auth_v1beta1_MsgUpdateParamsResponse,
    QueryAccountAddressByIdRequest as cosmos_auth_v1beta1_QueryAccountAddressByIDRequest,
    QueryAccountAddressByIdResponse as cosmos_auth_v1beta1_QueryAccountAddressByIDResponse,
    QueryAccountInfoRequest as cosmos_auth_v1beta1_QueryAccountInfoRequest,
    QueryAccountInfoResponse as cosmos_auth_v1beta1_QueryAccountInfoResponse,
    QueryAccountRequest as cosmos_auth_v1beta1_QueryAccountRequest,
    QueryAccountResponse as cosmos_auth_v1beta1_QueryAccountResponse,
    QueryAccountsRequest as cosmos_auth_v1beta1_QueryAccountsRequest,
    QueryAccountsResponse as cosmos_auth_v1beta1_QueryAccountsResponse,
    QueryModuleAccountByNameRequest as cosmos_auth_v1beta1_QueryModuleAccountByNameRequest,
    QueryModuleAccountByNameResponse as cosmos_auth_v1beta1_QueryModuleAccountByNameResponse,
    QueryModuleAccountsRequest as cosmos_auth_v1beta1_QueryModuleAccountsRequest,
    QueryModuleAccountsResponse as cosmos_auth_v1beta1_QueryModuleAccountsResponse,
    QueryParamsRequest as cosmos_auth_v1beta1_QueryParamsRequest,
    QueryParamsResponse as cosmos_auth_v1beta1_QueryParamsResponse,
)

@runtime_checkable
class CosmosAuthV1Beta1MsgLike(Protocol):
    pass

class CosmosAuthV1Beta1RestMsgClient(CosmosAuthV1Beta1MsgLike):
    """Msg REST client."""

    def __init__(self, base_url: str):
        """
        Initialize REST client.

        :param base_url: Base URL for the REST API
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

    def __del__(self):
        """Clean up session on deletion."""
        if hasattr(self, 'session'):
            self.session.close()


@runtime_checkable
class CosmosAuthV1Beta1QueryLike(Protocol):
    def accounts(self, message: cosmos_auth_v1beta1_QueryAccountsRequest | None = None) -> cosmos_auth_v1beta1_QueryAccountsResponse: ...
    def account(self, message: cosmos_auth_v1beta1_QueryAccountRequest) -> cosmos_auth_v1beta1_QueryAccountResponse: ...
    def account_address_by_id(self, message: cosmos_auth_v1beta1_QueryAccountAddressByIDRequest) -> cosmos_auth_v1beta1_QueryAccountAddressByIDResponse: ...
    def params(self, message: cosmos_auth_v1beta1_QueryParamsRequest | None = None) -> cosmos_auth_v1beta1_QueryParamsResponse: ...
    def module_accounts(self, message: cosmos_auth_v1beta1_QueryModuleAccountsRequest | None = None) -> cosmos_auth_v1beta1_QueryModuleAccountsResponse: ...
    def module_account_by_name(self, message: cosmos_auth_v1beta1_QueryModuleAccountByNameRequest) -> cosmos_auth_v1beta1_QueryModuleAccountByNameResponse: ...
    def bech32_prefix(self, message: cosmos_auth_v1beta1_Bech32PrefixRequest | None = None) -> cosmos_auth_v1beta1_Bech32PrefixResponse: ...
    def address_bytes_to_string(self, message: cosmos_auth_v1beta1_AddressBytesToStringRequest) -> cosmos_auth_v1beta1_AddressBytesToStringResponse: ...
    def address_string_to_bytes(self, message: cosmos_auth_v1beta1_AddressStringToBytesRequest) -> cosmos_auth_v1beta1_AddressStringToBytesResponse: ...
    def account_info(self, message: cosmos_auth_v1beta1_QueryAccountInfoRequest) -> cosmos_auth_v1beta1_QueryAccountInfoResponse: ...

class CosmosAuthV1Beta1RestQueryClient(CosmosAuthV1Beta1QueryLike):
    """Query REST client."""

    def __init__(self, base_url: str):
        """
        Initialize REST client.

        :param base_url: Base URL for the REST API
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

    def __del__(self):
        """Clean up session on deletion."""
        if hasattr(self, 'session'):
            self.session.close()

    def accounts(self, message: cosmos_auth_v1beta1_QueryAccountsRequest | None = None) -> cosmos_auth_v1beta1_QueryAccountsResponse:
        params = {
            "pagination": message.pagination if message else None,
        }
        url = self.base_url + f"/cosmos/auth/v1beta1/accounts"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_auth_v1beta1_QueryAccountsResponse().from_json(response.text)

    def account(self, message: cosmos_auth_v1beta1_QueryAccountRequest) -> cosmos_auth_v1beta1_QueryAccountResponse:
        params = {}
        url = self.base_url + f"/cosmos/auth/v1beta1/accounts/{message.address}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_auth_v1beta1_QueryAccountResponse().from_json(response.text)

    def account_address_by_id(self, message: cosmos_auth_v1beta1_QueryAccountAddressByIDRequest) -> cosmos_auth_v1beta1_QueryAccountAddressByIDResponse:
        params = {
            "account_id": message.account_id if message else None,
        }
        url = self.base_url + f"/cosmos/auth/v1beta1/address_by_id/{message.id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_auth_v1beta1_QueryAccountAddressByIDResponse().from_json(response.text)

    def params(self, message: cosmos_auth_v1beta1_QueryParamsRequest | None = None) -> cosmos_auth_v1beta1_QueryParamsResponse:
        params = {}
        url = self.base_url + f"/cosmos/auth/v1beta1/params"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_auth_v1beta1_QueryParamsResponse().from_json(response.text)

    def module_accounts(self, message: cosmos_auth_v1beta1_QueryModuleAccountsRequest | None = None) -> cosmos_auth_v1beta1_QueryModuleAccountsResponse:
        params = {}
        url = self.base_url + f"/cosmos/auth/v1beta1/module_accounts"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_auth_v1beta1_QueryModuleAccountsResponse().from_json(response.text)

    def module_account_by_name(self, message: cosmos_auth_v1beta1_QueryModuleAccountByNameRequest) -> cosmos_auth_v1beta1_QueryModuleAccountByNameResponse:
        params = {}
        url = self.base_url + f"/cosmos/auth/v1beta1/module_accounts/{message.name}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_auth_v1beta1_QueryModuleAccountByNameResponse().from_json(response.text)

    def bech32_prefix(self, message: cosmos_auth_v1beta1_Bech32PrefixRequest | None = None) -> cosmos_auth_v1beta1_Bech32PrefixResponse:
        params = {}
        url = self.base_url + f"/cosmos/auth/v1beta1/bech32"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_auth_v1beta1_Bech32PrefixResponse().from_json(response.text)

    def address_bytes_to_string(self, message: cosmos_auth_v1beta1_AddressBytesToStringRequest) -> cosmos_auth_v1beta1_AddressBytesToStringResponse:
        params = {}
        url = self.base_url + f"/cosmos/auth/v1beta1/bech32/{message.address_bytes}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_auth_v1beta1_AddressBytesToStringResponse().from_json(response.text)

    def address_string_to_bytes(self, message: cosmos_auth_v1beta1_AddressStringToBytesRequest) -> cosmos_auth_v1beta1_AddressStringToBytesResponse:
        params = {}
        url = self.base_url + f"/cosmos/auth/v1beta1/bech32/{message.address_string}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_auth_v1beta1_AddressStringToBytesResponse().from_json(response.text)

    def account_info(self, message: cosmos_auth_v1beta1_QueryAccountInfoRequest) -> cosmos_auth_v1beta1_QueryAccountInfoResponse:
        params = {}
        url = self.base_url + f"/cosmos/auth/v1beta1/account_info/{message.address}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_auth_v1beta1_QueryAccountInfoResponse().from_json(response.text)
