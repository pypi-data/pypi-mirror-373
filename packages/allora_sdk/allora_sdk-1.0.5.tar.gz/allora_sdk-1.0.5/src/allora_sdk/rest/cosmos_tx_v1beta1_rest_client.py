from typing import Protocol, runtime_checkable
import requests
import json
from allora_sdk.protos.cosmos.tx.v1beta1 import (
    BroadcastTxRequest as cosmos_tx_v1beta1_BroadcastTxRequest,
    BroadcastTxResponse as cosmos_tx_v1beta1_BroadcastTxResponse,
    GetBlockWithTxsRequest as cosmos_tx_v1beta1_GetBlockWithTxsRequest,
    GetBlockWithTxsResponse as cosmos_tx_v1beta1_GetBlockWithTxsResponse,
    GetTxRequest as cosmos_tx_v1beta1_GetTxRequest,
    GetTxResponse as cosmos_tx_v1beta1_GetTxResponse,
    GetTxsEventRequest as cosmos_tx_v1beta1_GetTxsEventRequest,
    GetTxsEventResponse as cosmos_tx_v1beta1_GetTxsEventResponse,
    SimulateRequest as cosmos_tx_v1beta1_SimulateRequest,
    SimulateResponse as cosmos_tx_v1beta1_SimulateResponse,
    TxDecodeAminoRequest as cosmos_tx_v1beta1_TxDecodeAminoRequest,
    TxDecodeAminoResponse as cosmos_tx_v1beta1_TxDecodeAminoResponse,
    TxDecodeRequest as cosmos_tx_v1beta1_TxDecodeRequest,
    TxDecodeResponse as cosmos_tx_v1beta1_TxDecodeResponse,
    TxEncodeAminoRequest as cosmos_tx_v1beta1_TxEncodeAminoRequest,
    TxEncodeAminoResponse as cosmos_tx_v1beta1_TxEncodeAminoResponse,
    TxEncodeRequest as cosmos_tx_v1beta1_TxEncodeRequest,
    TxEncodeResponse as cosmos_tx_v1beta1_TxEncodeResponse,
)

@runtime_checkable
class CosmosTxV1Beta1ServiceLike(Protocol):
    def simulate(self, message: cosmos_tx_v1beta1_SimulateRequest | None = None) -> cosmos_tx_v1beta1_SimulateResponse: ...
    def get_tx(self, message: cosmos_tx_v1beta1_GetTxRequest) -> cosmos_tx_v1beta1_GetTxResponse: ...
    def broadcast_tx(self, message: cosmos_tx_v1beta1_BroadcastTxRequest | None = None) -> cosmos_tx_v1beta1_BroadcastTxResponse: ...
    def get_txs_event(self, message: cosmos_tx_v1beta1_GetTxsEventRequest | None = None) -> cosmos_tx_v1beta1_GetTxsEventResponse: ...
    def get_block_with_txs(self, message: cosmos_tx_v1beta1_GetBlockWithTxsRequest) -> cosmos_tx_v1beta1_GetBlockWithTxsResponse: ...
    def tx_decode(self, message: cosmos_tx_v1beta1_TxDecodeRequest | None = None) -> cosmos_tx_v1beta1_TxDecodeResponse: ...
    def tx_encode(self, message: cosmos_tx_v1beta1_TxEncodeRequest | None = None) -> cosmos_tx_v1beta1_TxEncodeResponse: ...
    def tx_encode_amino(self, message: cosmos_tx_v1beta1_TxEncodeAminoRequest | None = None) -> cosmos_tx_v1beta1_TxEncodeAminoResponse: ...
    def tx_decode_amino(self, message: cosmos_tx_v1beta1_TxDecodeAminoRequest | None = None) -> cosmos_tx_v1beta1_TxDecodeAminoResponse: ...

class CosmosTxV1Beta1RestServiceClient(CosmosTxV1Beta1ServiceLike):
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

    def simulate(self, message: cosmos_tx_v1beta1_SimulateRequest | None = None) -> cosmos_tx_v1beta1_SimulateResponse:
        params = {
            "tx": message.tx if message else None,
            "tx_bytes": message.tx_bytes if message else None,
        }
        url = self.base_url + f"/cosmos/tx/v1beta1/simulate"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_tx_v1beta1_SimulateResponse().from_json(response.text)

    def get_tx(self, message: cosmos_tx_v1beta1_GetTxRequest) -> cosmos_tx_v1beta1_GetTxResponse:
        params = {}
        url = self.base_url + f"/cosmos/tx/v1beta1/txs/{message.hash}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_tx_v1beta1_GetTxResponse().from_json(response.text)

    def broadcast_tx(self, message: cosmos_tx_v1beta1_BroadcastTxRequest | None = None) -> cosmos_tx_v1beta1_BroadcastTxResponse:
        params = {
            "mode": message.mode if message else None,
            "tx_bytes": message.tx_bytes if message else None,
        }
        url = self.base_url + f"/cosmos/tx/v1beta1/txs"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_tx_v1beta1_BroadcastTxResponse().from_json(response.text)

    def get_txs_event(self, message: cosmos_tx_v1beta1_GetTxsEventRequest | None = None) -> cosmos_tx_v1beta1_GetTxsEventResponse:
        params = {
            "events": message.events if message else None,
            "order_by": message.order_by if message else None,
            "query": message.query if message else None,
            "page": message.page if message else None,
            "limit": message.limit if message else None,
            "pagination": message.pagination if message else None,
        }
        url = self.base_url + f"/cosmos/tx/v1beta1/txs"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_tx_v1beta1_GetTxsEventResponse().from_json(response.text)

    def get_block_with_txs(self, message: cosmos_tx_v1beta1_GetBlockWithTxsRequest) -> cosmos_tx_v1beta1_GetBlockWithTxsResponse:
        params = {
            "pagination": message.pagination if message else None,
        }
        url = self.base_url + f"/cosmos/tx/v1beta1/txs/block/{message.height}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_tx_v1beta1_GetBlockWithTxsResponse().from_json(response.text)

    def tx_decode(self, message: cosmos_tx_v1beta1_TxDecodeRequest | None = None) -> cosmos_tx_v1beta1_TxDecodeResponse:
        params = {
            "tx_bytes": message.tx_bytes if message else None,
        }
        url = self.base_url + f"/cosmos/tx/v1beta1/decode"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_tx_v1beta1_TxDecodeResponse().from_json(response.text)

    def tx_encode(self, message: cosmos_tx_v1beta1_TxEncodeRequest | None = None) -> cosmos_tx_v1beta1_TxEncodeResponse:
        params = {
            "tx": message.tx if message else None,
        }
        url = self.base_url + f"/cosmos/tx/v1beta1/encode"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_tx_v1beta1_TxEncodeResponse().from_json(response.text)

    def tx_encode_amino(self, message: cosmos_tx_v1beta1_TxEncodeAminoRequest | None = None) -> cosmos_tx_v1beta1_TxEncodeAminoResponse:
        params = {
            "amino_json": message.amino_json if message else None,
        }
        url = self.base_url + f"/cosmos/tx/v1beta1/encode/amino"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_tx_v1beta1_TxEncodeAminoResponse().from_json(response.text)

    def tx_decode_amino(self, message: cosmos_tx_v1beta1_TxDecodeAminoRequest | None = None) -> cosmos_tx_v1beta1_TxDecodeAminoResponse:
        params = {
            "amino_binary": message.amino_binary if message else None,
        }
        url = self.base_url + f"/cosmos/tx/v1beta1/decode/amino"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return cosmos_tx_v1beta1_TxDecodeAminoResponse().from_json(response.text)
