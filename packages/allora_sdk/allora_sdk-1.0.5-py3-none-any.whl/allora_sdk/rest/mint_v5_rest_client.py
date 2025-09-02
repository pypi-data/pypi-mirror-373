from typing import Protocol, runtime_checkable
import requests
import json
from allora_sdk.protos.mint.v5 import (
    QueryServiceEmissionInfoRequest as mint_v5_QueryServiceEmissionInfoRequest,
    QueryServiceEmissionInfoResponse as mint_v5_QueryServiceEmissionInfoResponse,
    QueryServiceInflationRequest as mint_v5_QueryServiceInflationRequest,
    QueryServiceInflationResponse as mint_v5_QueryServiceInflationResponse,
    QueryServiceParamsRequest as mint_v5_QueryServiceParamsRequest,
    QueryServiceParamsResponse as mint_v5_QueryServiceParamsResponse,
    RecalculateTargetEmissionRequest as mint_v5_RecalculateTargetEmissionRequest,
    RecalculateTargetEmissionResponse as mint_v5_RecalculateTargetEmissionResponse,
    UpdateParamsRequest as mint_v5_UpdateParamsRequest,
    UpdateParamsResponse as mint_v5_UpdateParamsResponse,
)

@runtime_checkable
class MintV5MsgServiceLike(Protocol):
    pass

class MintV5RestMsgServiceClient(MintV5MsgServiceLike):
    """Msgservice REST client."""

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
class MintV5QueryServiceLike(Protocol):
    def params(self, message: mint_v5_QueryServiceParamsRequest | None = None) -> mint_v5_QueryServiceParamsResponse: ...
    def inflation(self, message: mint_v5_QueryServiceInflationRequest | None = None) -> mint_v5_QueryServiceInflationResponse: ...
    def emission_info(self, message: mint_v5_QueryServiceEmissionInfoRequest | None = None) -> mint_v5_QueryServiceEmissionInfoResponse: ...

class MintV5RestQueryServiceClient(MintV5QueryServiceLike):
    """Queryservice REST client."""

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

    def params(self, message: mint_v5_QueryServiceParamsRequest | None = None) -> mint_v5_QueryServiceParamsResponse:
        params = {}
        url = self.base_url + f"/mint/v5/params"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return mint_v5_QueryServiceParamsResponse().from_json(response.text)

    def inflation(self, message: mint_v5_QueryServiceInflationRequest | None = None) -> mint_v5_QueryServiceInflationResponse:
        params = {}
        url = self.base_url + f"/mint/v5/inflation"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return mint_v5_QueryServiceInflationResponse().from_json(response.text)

    def emission_info(self, message: mint_v5_QueryServiceEmissionInfoRequest | None = None) -> mint_v5_QueryServiceEmissionInfoResponse:
        params = {}
        url = self.base_url + f"/mint/v5/emission_info"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return mint_v5_QueryServiceEmissionInfoResponse().from_json(response.text)
