from typing import Protocol, runtime_checkable
import requests
import json
from allora_sdk.protos.tendermint.abci import (
    RequestApplySnapshotChunk as tendermint_abci_RequestApplySnapshotChunk,
    RequestCheckTx as tendermint_abci_RequestCheckTx,
    RequestCommit as tendermint_abci_RequestCommit,
    RequestEcho as tendermint_abci_RequestEcho,
    RequestExtendVote as tendermint_abci_RequestExtendVote,
    RequestFinalizeBlock as tendermint_abci_RequestFinalizeBlock,
    RequestFlush as tendermint_abci_RequestFlush,
    RequestInfo as tendermint_abci_RequestInfo,
    RequestInitChain as tendermint_abci_RequestInitChain,
    RequestListSnapshots as tendermint_abci_RequestListSnapshots,
    RequestLoadSnapshotChunk as tendermint_abci_RequestLoadSnapshotChunk,
    RequestOfferSnapshot as tendermint_abci_RequestOfferSnapshot,
    RequestPrepareProposal as tendermint_abci_RequestPrepareProposal,
    RequestProcessProposal as tendermint_abci_RequestProcessProposal,
    RequestQuery as tendermint_abci_RequestQuery,
    RequestVerifyVoteExtension as tendermint_abci_RequestVerifyVoteExtension,
    ResponseApplySnapshotChunk as tendermint_abci_ResponseApplySnapshotChunk,
    ResponseCheckTx as tendermint_abci_ResponseCheckTx,
    ResponseCommit as tendermint_abci_ResponseCommit,
    ResponseEcho as tendermint_abci_ResponseEcho,
    ResponseExtendVote as tendermint_abci_ResponseExtendVote,
    ResponseFinalizeBlock as tendermint_abci_ResponseFinalizeBlock,
    ResponseFlush as tendermint_abci_ResponseFlush,
    ResponseInfo as tendermint_abci_ResponseInfo,
    ResponseInitChain as tendermint_abci_ResponseInitChain,
    ResponseListSnapshots as tendermint_abci_ResponseListSnapshots,
    ResponseLoadSnapshotChunk as tendermint_abci_ResponseLoadSnapshotChunk,
    ResponseOfferSnapshot as tendermint_abci_ResponseOfferSnapshot,
    ResponsePrepareProposal as tendermint_abci_ResponsePrepareProposal,
    ResponseProcessProposal as tendermint_abci_ResponseProcessProposal,
    ResponseQuery as tendermint_abci_ResponseQuery,
    ResponseVerifyVoteExtension as tendermint_abci_ResponseVerifyVoteExtension,
)

@runtime_checkable
class TendermintAbciABCILike(Protocol):
    pass

class TendermintAbciRestABCIClient(TendermintAbciABCILike):
    """Abci REST client."""

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
