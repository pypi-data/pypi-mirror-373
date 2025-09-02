from typing import Protocol, runtime_checkable
import requests
import json
from allora_sdk.protos.cosmos.bank.v1beta1 import (
    MsgMultiSend as cosmos_bank_v1beta1_MsgMultiSend,
    MsgMultiSendResponse as cosmos_bank_v1beta1_MsgMultiSendResponse,
    MsgSend as cosmos_bank_v1beta1_MsgSend,
    MsgSendResponse as cosmos_bank_v1beta1_MsgSendResponse,
    MsgSetSendEnabled as cosmos_bank_v1beta1_MsgSetSendEnabled,
    MsgSetSendEnabledResponse as cosmos_bank_v1beta1_MsgSetSendEnabledResponse,
    MsgUpdateParams as cosmos_bank_v1beta1_MsgUpdateParams,
    MsgUpdateParamsResponse as cosmos_bank_v1beta1_MsgUpdateParamsResponse,
    QueryAllBalancesRequest as cosmos_bank_v1beta1_QueryAllBalancesRequest,
    QueryAllBalancesResponse as cosmos_bank_v1beta1_QueryAllBalancesResponse,
    QueryBalanceRequest as cosmos_bank_v1beta1_QueryBalanceRequest,
    QueryBalanceResponse as cosmos_bank_v1beta1_QueryBalanceResponse,
    QueryDenomMetadataByQueryStringRequest as cosmos_bank_v1beta1_QueryDenomMetadataByQueryStringRequest,
    QueryDenomMetadataByQueryStringResponse as cosmos_bank_v1beta1_QueryDenomMetadataByQueryStringResponse,
    QueryDenomMetadataRequest as cosmos_bank_v1beta1_QueryDenomMetadataRequest,
    QueryDenomMetadataResponse as cosmos_bank_v1beta1_QueryDenomMetadataResponse,
    QueryDenomOwnersByQueryRequest as cosmos_bank_v1beta1_QueryDenomOwnersByQueryRequest,
    QueryDenomOwnersByQueryResponse as cosmos_bank_v1beta1_QueryDenomOwnersByQueryResponse,
    QueryDenomOwnersRequest as cosmos_bank_v1beta1_QueryDenomOwnersRequest,
    QueryDenomOwnersResponse as cosmos_bank_v1beta1_QueryDenomOwnersResponse,
    QueryDenomsMetadataRequest as cosmos_bank_v1beta1_QueryDenomsMetadataRequest,
    QueryDenomsMetadataResponse as cosmos_bank_v1beta1_QueryDenomsMetadataResponse,
    QueryParamsRequest as cosmos_bank_v1beta1_QueryParamsRequest,
    QueryParamsResponse as cosmos_bank_v1beta1_QueryParamsResponse,
    QuerySendEnabledRequest as cosmos_bank_v1beta1_QuerySendEnabledRequest,
    QuerySendEnabledResponse as cosmos_bank_v1beta1_QuerySendEnabledResponse,
    QuerySpendableBalanceByDenomRequest as cosmos_bank_v1beta1_QuerySpendableBalanceByDenomRequest,
    QuerySpendableBalanceByDenomResponse as cosmos_bank_v1beta1_QuerySpendableBalanceByDenomResponse,
    QuerySpendableBalancesRequest as cosmos_bank_v1beta1_QuerySpendableBalancesRequest,
    QuerySpendableBalancesResponse as cosmos_bank_v1beta1_QuerySpendableBalancesResponse,
    QuerySupplyOfRequest as cosmos_bank_v1beta1_QuerySupplyOfRequest,
    QuerySupplyOfResponse as cosmos_bank_v1beta1_QuerySupplyOfResponse,
    QueryTotalSupplyRequest as cosmos_bank_v1beta1_QueryTotalSupplyRequest,
    QueryTotalSupplyResponse as cosmos_bank_v1beta1_QueryTotalSupplyResponse,
)

@runtime_checkable
class CosmosBankV1Beta1MsgLike(Protocol):
    pass

class CosmosBankV1Beta1RestMsgClient(CosmosBankV1Beta1MsgLike):
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
class CosmosBankV1Beta1QueryLike(Protocol):
    def balance(self, message: cosmos_bank_v1beta1_QueryBalanceRequest) -> cosmos_bank_v1beta1_QueryBalanceResponse: ...
    def all_balances(self, message: cosmos_bank_v1beta1_QueryAllBalancesRequest) -> cosmos_bank_v1beta1_QueryAllBalancesResponse: ...
    def spendable_balances(self, message: cosmos_bank_v1beta1_QuerySpendableBalancesRequest) -> cosmos_bank_v1beta1_QuerySpendableBalancesResponse: ...
    def spendable_balance_by_denom(self, message: cosmos_bank_v1beta1_QuerySpendableBalanceByDenomRequest) -> cosmos_bank_v1beta1_QuerySpendableBalanceByDenomResponse: ...
    def total_supply(self, message: cosmos_bank_v1beta1_QueryTotalSupplyRequest | None = None) -> cosmos_bank_v1beta1_QueryTotalSupplyResponse: ...
    def supply_of(self, message: cosmos_bank_v1beta1_QuerySupplyOfRequest | None = None) -> cosmos_bank_v1beta1_QuerySupplyOfResponse: ...
    def params(self, message: cosmos_bank_v1beta1_QueryParamsRequest | None = None) -> cosmos_bank_v1beta1_QueryParamsResponse: ...
    def denom_metadata(self, message: cosmos_bank_v1beta1_QueryDenomMetadataRequest) -> cosmos_bank_v1beta1_QueryDenomMetadataResponse: ...
    def denom_metadata_by_query_string(self, message: cosmos_bank_v1beta1_QueryDenomMetadataByQueryStringRequest | None = None) -> cosmos_bank_v1beta1_QueryDenomMetadataByQueryStringResponse: ...
    def denoms_metadata(self, message: cosmos_bank_v1beta1_QueryDenomsMetadataRequest | None = None) -> cosmos_bank_v1beta1_QueryDenomsMetadataResponse: ...
    def denom_owners(self, message: cosmos_bank_v1beta1_QueryDenomOwnersRequest) -> cosmos_bank_v1beta1_QueryDenomOwnersResponse: ...
    def denom_owners_by_query(self, message: cosmos_bank_v1beta1_QueryDenomOwnersByQueryRequest | None = None) -> cosmos_bank_v1beta1_QueryDenomOwnersByQueryResponse: ...
    def send_enabled(self, message: cosmos_bank_v1beta1_QuerySendEnabledRequest | None = None) -> cosmos_bank_v1beta1_QuerySendEnabledResponse: ...

class CosmosBankV1Beta1RestQueryClient(CosmosBankV1Beta1QueryLike):
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

    def balance(self, message: cosmos_bank_v1beta1_QueryBalanceRequest) -> cosmos_bank_v1beta1_QueryBalanceResponse:
        params = {
            "denom": message.denom if message else None,
        }
        url = self.base_url + f"/cosmos/bank/v1beta1/balances/{message.address}/by_denom"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_bank_v1beta1_QueryBalanceResponse().from_json(response.text)

    def all_balances(self, message: cosmos_bank_v1beta1_QueryAllBalancesRequest) -> cosmos_bank_v1beta1_QueryAllBalancesResponse:
        params = {
            "resolve_denom": message.resolve_denom if message else None,
            "pagination": message.pagination if message else None,
        }
        url = self.base_url + f"/cosmos/bank/v1beta1/balances/{message.address}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_bank_v1beta1_QueryAllBalancesResponse().from_json(response.text)

    def spendable_balances(self, message: cosmos_bank_v1beta1_QuerySpendableBalancesRequest) -> cosmos_bank_v1beta1_QuerySpendableBalancesResponse:
        params = {
            "pagination": message.pagination if message else None,
        }
        url = self.base_url + f"/cosmos/bank/v1beta1/spendable_balances/{message.address}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_bank_v1beta1_QuerySpendableBalancesResponse().from_json(response.text)

    def spendable_balance_by_denom(self, message: cosmos_bank_v1beta1_QuerySpendableBalanceByDenomRequest) -> cosmos_bank_v1beta1_QuerySpendableBalanceByDenomResponse:
        params = {
            "denom": message.denom if message else None,
        }
        url = self.base_url + f"/cosmos/bank/v1beta1/spendable_balances/{message.address}/by_denom"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_bank_v1beta1_QuerySpendableBalanceByDenomResponse().from_json(response.text)

    def total_supply(self, message: cosmos_bank_v1beta1_QueryTotalSupplyRequest | None = None) -> cosmos_bank_v1beta1_QueryTotalSupplyResponse:
        params = {
            "pagination": message.pagination if message else None,
        }
        url = self.base_url + f"/cosmos/bank/v1beta1/supply"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_bank_v1beta1_QueryTotalSupplyResponse().from_json(response.text)

    def supply_of(self, message: cosmos_bank_v1beta1_QuerySupplyOfRequest | None = None) -> cosmos_bank_v1beta1_QuerySupplyOfResponse:
        params = {
            "denom": message.denom if message else None,
        }
        url = self.base_url + f"/cosmos/bank/v1beta1/supply/by_denom"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_bank_v1beta1_QuerySupplyOfResponse().from_json(response.text)

    def params(self, message: cosmos_bank_v1beta1_QueryParamsRequest | None = None) -> cosmos_bank_v1beta1_QueryParamsResponse:
        params = {}
        url = self.base_url + f"/cosmos/bank/v1beta1/params"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_bank_v1beta1_QueryParamsResponse().from_json(response.text)

    def denom_metadata(self, message: cosmos_bank_v1beta1_QueryDenomMetadataRequest) -> cosmos_bank_v1beta1_QueryDenomMetadataResponse:
        params = {}
        url = self.base_url + f"/cosmos/bank/v1beta1/denoms_metadata/{message.denom}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_bank_v1beta1_QueryDenomMetadataResponse().from_json(response.text)

    def denom_metadata_by_query_string(self, message: cosmos_bank_v1beta1_QueryDenomMetadataByQueryStringRequest | None = None) -> cosmos_bank_v1beta1_QueryDenomMetadataByQueryStringResponse:
        params = {
            "denom": message.denom if message else None,
        }
        url = self.base_url + f"/cosmos/bank/v1beta1/denoms_metadata_by_query_string"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_bank_v1beta1_QueryDenomMetadataByQueryStringResponse().from_json(response.text)

    def denoms_metadata(self, message: cosmos_bank_v1beta1_QueryDenomsMetadataRequest | None = None) -> cosmos_bank_v1beta1_QueryDenomsMetadataResponse:
        params = {
            "pagination": message.pagination if message else None,
        }
        url = self.base_url + f"/cosmos/bank/v1beta1/denoms_metadata"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_bank_v1beta1_QueryDenomsMetadataResponse().from_json(response.text)

    def denom_owners(self, message: cosmos_bank_v1beta1_QueryDenomOwnersRequest) -> cosmos_bank_v1beta1_QueryDenomOwnersResponse:
        params = {
            "pagination": message.pagination if message else None,
        }
        url = self.base_url + f"/cosmos/bank/v1beta1/denom_owners/{message.denom}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_bank_v1beta1_QueryDenomOwnersResponse().from_json(response.text)

    def denom_owners_by_query(self, message: cosmos_bank_v1beta1_QueryDenomOwnersByQueryRequest | None = None) -> cosmos_bank_v1beta1_QueryDenomOwnersByQueryResponse:
        params = {
            "denom": message.denom if message else None,
            "pagination": message.pagination if message else None,
        }
        url = self.base_url + f"/cosmos/bank/v1beta1/denom_owners_by_query"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_bank_v1beta1_QueryDenomOwnersByQueryResponse().from_json(response.text)

    def send_enabled(self, message: cosmos_bank_v1beta1_QuerySendEnabledRequest | None = None) -> cosmos_bank_v1beta1_QuerySendEnabledResponse:
        params = {
            "denoms": message.denoms if message else None,
            "pagination": message.pagination if message else None,
        }
        url = self.base_url + f"/cosmos/bank/v1beta1/send_enabled"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_bank_v1beta1_QuerySendEnabledResponse().from_json(response.text)
