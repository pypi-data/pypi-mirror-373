from typing import Protocol, runtime_checkable
import requests
import json
from allora_sdk.protos.cosmos.base.tendermint.v1beta1 import (
    AbciQueryRequest as cosmos_base_tendermint_v1beta1_ABCIQueryRequest,
    AbciQueryResponse as cosmos_base_tendermint_v1beta1_ABCIQueryResponse,
    GetBlockByHeightRequest as cosmos_base_tendermint_v1beta1_GetBlockByHeightRequest,
    GetBlockByHeightResponse as cosmos_base_tendermint_v1beta1_GetBlockByHeightResponse,
    GetLatestBlockRequest as cosmos_base_tendermint_v1beta1_GetLatestBlockRequest,
    GetLatestBlockResponse as cosmos_base_tendermint_v1beta1_GetLatestBlockResponse,
    GetLatestValidatorSetRequest as cosmos_base_tendermint_v1beta1_GetLatestValidatorSetRequest,
    GetLatestValidatorSetResponse as cosmos_base_tendermint_v1beta1_GetLatestValidatorSetResponse,
    GetNodeInfoRequest as cosmos_base_tendermint_v1beta1_GetNodeInfoRequest,
    GetNodeInfoResponse as cosmos_base_tendermint_v1beta1_GetNodeInfoResponse,
    GetSyncingRequest as cosmos_base_tendermint_v1beta1_GetSyncingRequest,
    GetSyncingResponse as cosmos_base_tendermint_v1beta1_GetSyncingResponse,
    GetValidatorSetByHeightRequest as cosmos_base_tendermint_v1beta1_GetValidatorSetByHeightRequest,
    GetValidatorSetByHeightResponse as cosmos_base_tendermint_v1beta1_GetValidatorSetByHeightResponse,
)

@runtime_checkable
class CosmosBaseTendermintV1Beta1ServiceLike(Protocol):
    def get_node_info(self, message: cosmos_base_tendermint_v1beta1_GetNodeInfoRequest | None = None) -> cosmos_base_tendermint_v1beta1_GetNodeInfoResponse: ...
    def get_syncing(self, message: cosmos_base_tendermint_v1beta1_GetSyncingRequest | None = None) -> cosmos_base_tendermint_v1beta1_GetSyncingResponse: ...
    def get_latest_block(self, message: cosmos_base_tendermint_v1beta1_GetLatestBlockRequest | None = None) -> cosmos_base_tendermint_v1beta1_GetLatestBlockResponse: ...
    def get_block_by_height(self, message: cosmos_base_tendermint_v1beta1_GetBlockByHeightRequest) -> cosmos_base_tendermint_v1beta1_GetBlockByHeightResponse: ...
    def get_latest_validator_set(self, message: cosmos_base_tendermint_v1beta1_GetLatestValidatorSetRequest | None = None) -> cosmos_base_tendermint_v1beta1_GetLatestValidatorSetResponse: ...
    def get_validator_set_by_height(self, message: cosmos_base_tendermint_v1beta1_GetValidatorSetByHeightRequest) -> cosmos_base_tendermint_v1beta1_GetValidatorSetByHeightResponse: ...
    def abci_query(self, message: cosmos_base_tendermint_v1beta1_ABCIQueryRequest | None = None) -> cosmos_base_tendermint_v1beta1_ABCIQueryResponse: ...

class CosmosBaseTendermintV1Beta1RestServiceClient(CosmosBaseTendermintV1Beta1ServiceLike):
    """Service REST client."""

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

    def get_node_info(self, message: cosmos_base_tendermint_v1beta1_GetNodeInfoRequest | None = None) -> cosmos_base_tendermint_v1beta1_GetNodeInfoResponse:
        params = {}
        url = self.base_url + f"/cosmos/base/tendermint/v1beta1/node_info"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_base_tendermint_v1beta1_GetNodeInfoResponse().from_json(response.text)

    def get_syncing(self, message: cosmos_base_tendermint_v1beta1_GetSyncingRequest | None = None) -> cosmos_base_tendermint_v1beta1_GetSyncingResponse:
        params = {}
        url = self.base_url + f"/cosmos/base/tendermint/v1beta1/syncing"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_base_tendermint_v1beta1_GetSyncingResponse().from_json(response.text)

    def get_latest_block(self, message: cosmos_base_tendermint_v1beta1_GetLatestBlockRequest | None = None) -> cosmos_base_tendermint_v1beta1_GetLatestBlockResponse:
        params = {}
        url = self.base_url + f"/cosmos/base/tendermint/v1beta1/blocks/latest"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_base_tendermint_v1beta1_GetLatestBlockResponse().from_json(response.text)

    def get_block_by_height(self, message: cosmos_base_tendermint_v1beta1_GetBlockByHeightRequest) -> cosmos_base_tendermint_v1beta1_GetBlockByHeightResponse:
        params = {}
        url = self.base_url + f"/cosmos/base/tendermint/v1beta1/blocks/{message.height}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_base_tendermint_v1beta1_GetBlockByHeightResponse().from_json(response.text)

    def get_latest_validator_set(self, message: cosmos_base_tendermint_v1beta1_GetLatestValidatorSetRequest | None = None) -> cosmos_base_tendermint_v1beta1_GetLatestValidatorSetResponse:
        params = {
            "pagination": message.pagination if message else None,
        }
        url = self.base_url + f"/cosmos/base/tendermint/v1beta1/validatorsets/latest"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_base_tendermint_v1beta1_GetLatestValidatorSetResponse().from_json(response.text)

    def get_validator_set_by_height(self, message: cosmos_base_tendermint_v1beta1_GetValidatorSetByHeightRequest) -> cosmos_base_tendermint_v1beta1_GetValidatorSetByHeightResponse:
        params = {
            "pagination": message.pagination if message else None,
        }
        url = self.base_url + f"/cosmos/base/tendermint/v1beta1/validatorsets/{message.height}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_base_tendermint_v1beta1_GetValidatorSetByHeightResponse().from_json(response.text)

    def abci_query(self, message: cosmos_base_tendermint_v1beta1_ABCIQueryRequest | None = None) -> cosmos_base_tendermint_v1beta1_ABCIQueryResponse:
        params = {
            "path": message.path if message else None,
            "prove": message.prove if message else None,
            "height": message.height if message else None,
            "data": message.data if message else None,
        }
        url = self.base_url + f"/cosmos/base/tendermint/v1beta1/abci_query"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_base_tendermint_v1beta1_ABCIQueryResponse().from_json(response.text)
