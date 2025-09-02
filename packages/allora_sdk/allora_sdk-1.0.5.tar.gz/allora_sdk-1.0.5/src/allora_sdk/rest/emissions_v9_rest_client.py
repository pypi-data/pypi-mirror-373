from typing import Protocol, runtime_checkable
import requests
import json
from allora_sdk.protos.emissions.v9 import (
    AddStakeRequest as emissions_v9_AddStakeRequest,
    AddStakeResponse as emissions_v9_AddStakeResponse,
    AddToGlobalAdminWhitelistRequest as emissions_v9_AddToGlobalAdminWhitelistRequest,
    AddToGlobalAdminWhitelistResponse as emissions_v9_AddToGlobalAdminWhitelistResponse,
    AddToGlobalReputerWhitelistRequest as emissions_v9_AddToGlobalReputerWhitelistRequest,
    AddToGlobalReputerWhitelistResponse as emissions_v9_AddToGlobalReputerWhitelistResponse,
    AddToGlobalWhitelistRequest as emissions_v9_AddToGlobalWhitelistRequest,
    AddToGlobalWhitelistResponse as emissions_v9_AddToGlobalWhitelistResponse,
    AddToGlobalWorkerWhitelistRequest as emissions_v9_AddToGlobalWorkerWhitelistRequest,
    AddToGlobalWorkerWhitelistResponse as emissions_v9_AddToGlobalWorkerWhitelistResponse,
    AddToTopicCreatorWhitelistRequest as emissions_v9_AddToTopicCreatorWhitelistRequest,
    AddToTopicCreatorWhitelistResponse as emissions_v9_AddToTopicCreatorWhitelistResponse,
    AddToTopicReputerWhitelistRequest as emissions_v9_AddToTopicReputerWhitelistRequest,
    AddToTopicReputerWhitelistResponse as emissions_v9_AddToTopicReputerWhitelistResponse,
    AddToTopicWorkerWhitelistRequest as emissions_v9_AddToTopicWorkerWhitelistRequest,
    AddToTopicWorkerWhitelistResponse as emissions_v9_AddToTopicWorkerWhitelistResponse,
    AddToWhitelistAdminRequest as emissions_v9_AddToWhitelistAdminRequest,
    AddToWhitelistAdminResponse as emissions_v9_AddToWhitelistAdminResponse,
    BulkAddToGlobalReputerWhitelistRequest as emissions_v9_BulkAddToGlobalReputerWhitelistRequest,
    BulkAddToGlobalReputerWhitelistResponse as emissions_v9_BulkAddToGlobalReputerWhitelistResponse,
    BulkAddToGlobalWorkerWhitelistRequest as emissions_v9_BulkAddToGlobalWorkerWhitelistRequest,
    BulkAddToGlobalWorkerWhitelistResponse as emissions_v9_BulkAddToGlobalWorkerWhitelistResponse,
    BulkAddToTopicReputerWhitelistRequest as emissions_v9_BulkAddToTopicReputerWhitelistRequest,
    BulkAddToTopicReputerWhitelistResponse as emissions_v9_BulkAddToTopicReputerWhitelistResponse,
    BulkAddToTopicWorkerWhitelistRequest as emissions_v9_BulkAddToTopicWorkerWhitelistRequest,
    BulkAddToTopicWorkerWhitelistResponse as emissions_v9_BulkAddToTopicWorkerWhitelistResponse,
    BulkRemoveFromGlobalReputerWhitelistRequest as emissions_v9_BulkRemoveFromGlobalReputerWhitelistRequest,
    BulkRemoveFromGlobalReputerWhitelistResponse as emissions_v9_BulkRemoveFromGlobalReputerWhitelistResponse,
    BulkRemoveFromGlobalWorkerWhitelistRequest as emissions_v9_BulkRemoveFromGlobalWorkerWhitelistRequest,
    BulkRemoveFromGlobalWorkerWhitelistResponse as emissions_v9_BulkRemoveFromGlobalWorkerWhitelistResponse,
    BulkRemoveFromTopicReputerWhitelistRequest as emissions_v9_BulkRemoveFromTopicReputerWhitelistRequest,
    BulkRemoveFromTopicReputerWhitelistResponse as emissions_v9_BulkRemoveFromTopicReputerWhitelistResponse,
    BulkRemoveFromTopicWorkerWhitelistRequest as emissions_v9_BulkRemoveFromTopicWorkerWhitelistRequest,
    BulkRemoveFromTopicWorkerWhitelistResponse as emissions_v9_BulkRemoveFromTopicWorkerWhitelistResponse,
    CanCreateTopicRequest as emissions_v9_CanCreateTopicRequest,
    CanCreateTopicResponse as emissions_v9_CanCreateTopicResponse,
    CanSubmitReputerPayloadRequest as emissions_v9_CanSubmitReputerPayloadRequest,
    CanSubmitReputerPayloadResponse as emissions_v9_CanSubmitReputerPayloadResponse,
    CanSubmitWorkerPayloadRequest as emissions_v9_CanSubmitWorkerPayloadRequest,
    CanSubmitWorkerPayloadResponse as emissions_v9_CanSubmitWorkerPayloadResponse,
    CanUpdateAllGlobalWhitelistsRequest as emissions_v9_CanUpdateAllGlobalWhitelistsRequest,
    CanUpdateAllGlobalWhitelistsResponse as emissions_v9_CanUpdateAllGlobalWhitelistsResponse,
    CanUpdateGlobalReputerWhitelistRequest as emissions_v9_CanUpdateGlobalReputerWhitelistRequest,
    CanUpdateGlobalReputerWhitelistResponse as emissions_v9_CanUpdateGlobalReputerWhitelistResponse,
    CanUpdateGlobalWorkerWhitelistRequest as emissions_v9_CanUpdateGlobalWorkerWhitelistRequest,
    CanUpdateGlobalWorkerWhitelistResponse as emissions_v9_CanUpdateGlobalWorkerWhitelistResponse,
    CanUpdateParamsRequest as emissions_v9_CanUpdateParamsRequest,
    CanUpdateParamsResponse as emissions_v9_CanUpdateParamsResponse,
    CanUpdateTopicWhitelistRequest as emissions_v9_CanUpdateTopicWhitelistRequest,
    CanUpdateTopicWhitelistResponse as emissions_v9_CanUpdateTopicWhitelistResponse,
    CancelRemoveDelegateStakeRequest as emissions_v9_CancelRemoveDelegateStakeRequest,
    CancelRemoveDelegateStakeResponse as emissions_v9_CancelRemoveDelegateStakeResponse,
    CancelRemoveStakeRequest as emissions_v9_CancelRemoveStakeRequest,
    CancelRemoveStakeResponse as emissions_v9_CancelRemoveStakeResponse,
    CreateNewTopicRequest as emissions_v9_CreateNewTopicRequest,
    CreateNewTopicResponse as emissions_v9_CreateNewTopicResponse,
    DelegateStakeRequest as emissions_v9_DelegateStakeRequest,
    DelegateStakeResponse as emissions_v9_DelegateStakeResponse,
    DisableTopicReputerWhitelistRequest as emissions_v9_DisableTopicReputerWhitelistRequest,
    DisableTopicReputerWhitelistResponse as emissions_v9_DisableTopicReputerWhitelistResponse,
    DisableTopicWorkerWhitelistRequest as emissions_v9_DisableTopicWorkerWhitelistRequest,
    DisableTopicWorkerWhitelistResponse as emissions_v9_DisableTopicWorkerWhitelistResponse,
    EnableTopicReputerWhitelistRequest as emissions_v9_EnableTopicReputerWhitelistRequest,
    EnableTopicReputerWhitelistResponse as emissions_v9_EnableTopicReputerWhitelistResponse,
    EnableTopicWorkerWhitelistRequest as emissions_v9_EnableTopicWorkerWhitelistRequest,
    EnableTopicWorkerWhitelistResponse as emissions_v9_EnableTopicWorkerWhitelistResponse,
    FundTopicRequest as emissions_v9_FundTopicRequest,
    FundTopicResponse as emissions_v9_FundTopicResponse,
    GetActiveForecastersForTopicRequest as emissions_v9_GetActiveForecastersForTopicRequest,
    GetActiveForecastersForTopicResponse as emissions_v9_GetActiveForecastersForTopicResponse,
    GetActiveInferersForTopicRequest as emissions_v9_GetActiveInferersForTopicRequest,
    GetActiveInferersForTopicResponse as emissions_v9_GetActiveInferersForTopicResponse,
    GetActiveReputersForTopicRequest as emissions_v9_GetActiveReputersForTopicRequest,
    GetActiveReputersForTopicResponse as emissions_v9_GetActiveReputersForTopicResponse,
    GetActiveTopicsAtBlockRequest as emissions_v9_GetActiveTopicsAtBlockRequest,
    GetActiveTopicsAtBlockResponse as emissions_v9_GetActiveTopicsAtBlockResponse,
    GetCountForecasterInclusionsInTopicRequest as emissions_v9_GetCountForecasterInclusionsInTopicRequest,
    GetCountForecasterInclusionsInTopicResponse as emissions_v9_GetCountForecasterInclusionsInTopicResponse,
    GetCountInfererInclusionsInTopicRequest as emissions_v9_GetCountInfererInclusionsInTopicRequest,
    GetCountInfererInclusionsInTopicResponse as emissions_v9_GetCountInfererInclusionsInTopicResponse,
    GetCurrentLowestForecasterScoreRequest as emissions_v9_GetCurrentLowestForecasterScoreRequest,
    GetCurrentLowestForecasterScoreResponse as emissions_v9_GetCurrentLowestForecasterScoreResponse,
    GetCurrentLowestInfererScoreRequest as emissions_v9_GetCurrentLowestInfererScoreRequest,
    GetCurrentLowestInfererScoreResponse as emissions_v9_GetCurrentLowestInfererScoreResponse,
    GetCurrentLowestReputerScoreRequest as emissions_v9_GetCurrentLowestReputerScoreRequest,
    GetCurrentLowestReputerScoreResponse as emissions_v9_GetCurrentLowestReputerScoreResponse,
    GetDelegateRewardPerShareRequest as emissions_v9_GetDelegateRewardPerShareRequest,
    GetDelegateRewardPerShareResponse as emissions_v9_GetDelegateRewardPerShareResponse,
    GetDelegateStakeInTopicInReputerRequest as emissions_v9_GetDelegateStakeInTopicInReputerRequest,
    GetDelegateStakeInTopicInReputerResponse as emissions_v9_GetDelegateStakeInTopicInReputerResponse,
    GetDelegateStakePlacementRequest as emissions_v9_GetDelegateStakePlacementRequest,
    GetDelegateStakePlacementResponse as emissions_v9_GetDelegateStakePlacementResponse,
    GetDelegateStakeRemovalInfoRequest as emissions_v9_GetDelegateStakeRemovalInfoRequest,
    GetDelegateStakeRemovalInfoResponse as emissions_v9_GetDelegateStakeRemovalInfoResponse,
    GetDelegateStakeRemovalRequest as emissions_v9_GetDelegateStakeRemovalRequest,
    GetDelegateStakeRemovalResponse as emissions_v9_GetDelegateStakeRemovalResponse,
    GetDelegateStakeRemovalsUpUntilBlockRequest as emissions_v9_GetDelegateStakeRemovalsUpUntilBlockRequest,
    GetDelegateStakeRemovalsUpUntilBlockResponse as emissions_v9_GetDelegateStakeRemovalsUpUntilBlockResponse,
    GetDelegateStakeUponReputerRequest as emissions_v9_GetDelegateStakeUponReputerRequest,
    GetDelegateStakeUponReputerResponse as emissions_v9_GetDelegateStakeUponReputerResponse,
    GetForecastScoresUntilBlockRequest as emissions_v9_GetForecastScoresUntilBlockRequest,
    GetForecastScoresUntilBlockResponse as emissions_v9_GetForecastScoresUntilBlockResponse,
    GetForecasterNetworkRegretRequest as emissions_v9_GetForecasterNetworkRegretRequest,
    GetForecasterNetworkRegretResponse as emissions_v9_GetForecasterNetworkRegretResponse,
    GetForecasterScoreEmaRequest as emissions_v9_GetForecasterScoreEmaRequest,
    GetForecasterScoreEmaResponse as emissions_v9_GetForecasterScoreEmaResponse,
    GetForecastsAtBlockRequest as emissions_v9_GetForecastsAtBlockRequest,
    GetForecastsAtBlockResponse as emissions_v9_GetForecastsAtBlockResponse,
    GetInferenceScoresUntilBlockRequest as emissions_v9_GetInferenceScoresUntilBlockRequest,
    GetInferenceScoresUntilBlockResponse as emissions_v9_GetInferenceScoresUntilBlockResponse,
    GetInferencesAtBlockRequest as emissions_v9_GetInferencesAtBlockRequest,
    GetInferencesAtBlockResponse as emissions_v9_GetInferencesAtBlockResponse,
    GetInfererNetworkRegretRequest as emissions_v9_GetInfererNetworkRegretRequest,
    GetInfererNetworkRegretResponse as emissions_v9_GetInfererNetworkRegretResponse,
    GetInfererScoreEmaRequest as emissions_v9_GetInfererScoreEmaRequest,
    GetInfererScoreEmaResponse as emissions_v9_GetInfererScoreEmaResponse,
    GetLatestForecasterWeightRequest as emissions_v9_GetLatestForecasterWeightRequest,
    GetLatestForecasterWeightResponse as emissions_v9_GetLatestForecasterWeightResponse,
    GetLatestInfererWeightRequest as emissions_v9_GetLatestInfererWeightRequest,
    GetLatestInfererWeightResponse as emissions_v9_GetLatestInfererWeightResponse,
    GetLatestNetworkInferencesOutlierResistantRequest as emissions_v9_GetLatestNetworkInferencesOutlierResistantRequest,
    GetLatestNetworkInferencesOutlierResistantResponse as emissions_v9_GetLatestNetworkInferencesOutlierResistantResponse,
    GetLatestNetworkInferencesRequest as emissions_v9_GetLatestNetworkInferencesRequest,
    GetLatestNetworkInferencesResponse as emissions_v9_GetLatestNetworkInferencesResponse,
    GetLatestRegretStdNormRequest as emissions_v9_GetLatestRegretStdNormRequest,
    GetLatestRegretStdNormResponse as emissions_v9_GetLatestRegretStdNormResponse,
    GetLatestTopicInferencesRequest as emissions_v9_GetLatestTopicInferencesRequest,
    GetLatestTopicInferencesResponse as emissions_v9_GetLatestTopicInferencesResponse,
    GetListeningCoefficientRequest as emissions_v9_GetListeningCoefficientRequest,
    GetListeningCoefficientResponse as emissions_v9_GetListeningCoefficientResponse,
    GetMultiReputerStakeInTopicRequest as emissions_v9_GetMultiReputerStakeInTopicRequest,
    GetMultiReputerStakeInTopicResponse as emissions_v9_GetMultiReputerStakeInTopicResponse,
    GetNaiveInfererNetworkRegretRequest as emissions_v9_GetNaiveInfererNetworkRegretRequest,
    GetNaiveInfererNetworkRegretResponse as emissions_v9_GetNaiveInfererNetworkRegretResponse,
    GetNetworkInferencesAtBlockOutlierResistantRequest as emissions_v9_GetNetworkInferencesAtBlockOutlierResistantRequest,
    GetNetworkInferencesAtBlockOutlierResistantResponse as emissions_v9_GetNetworkInferencesAtBlockOutlierResistantResponse,
    GetNetworkInferencesAtBlockRequest as emissions_v9_GetNetworkInferencesAtBlockRequest,
    GetNetworkInferencesAtBlockResponse as emissions_v9_GetNetworkInferencesAtBlockResponse,
    GetNetworkLossBundleAtBlockRequest as emissions_v9_GetNetworkLossBundleAtBlockRequest,
    GetNetworkLossBundleAtBlockResponse as emissions_v9_GetNetworkLossBundleAtBlockResponse,
    GetNextChurningBlockByTopicIdRequest as emissions_v9_GetNextChurningBlockByTopicIdRequest,
    GetNextChurningBlockByTopicIdResponse as emissions_v9_GetNextChurningBlockByTopicIdResponse,
    GetNextTopicIdRequest as emissions_v9_GetNextTopicIdRequest,
    GetNextTopicIdResponse as emissions_v9_GetNextTopicIdResponse,
    GetOneInForecasterNetworkRegretRequest as emissions_v9_GetOneInForecasterNetworkRegretRequest,
    GetOneInForecasterNetworkRegretResponse as emissions_v9_GetOneInForecasterNetworkRegretResponse,
    GetOneOutForecasterForecasterNetworkRegretRequest as emissions_v9_GetOneOutForecasterForecasterNetworkRegretRequest,
    GetOneOutForecasterForecasterNetworkRegretResponse as emissions_v9_GetOneOutForecasterForecasterNetworkRegretResponse,
    GetOneOutForecasterInfererNetworkRegretRequest as emissions_v9_GetOneOutForecasterInfererNetworkRegretRequest,
    GetOneOutForecasterInfererNetworkRegretResponse as emissions_v9_GetOneOutForecasterInfererNetworkRegretResponse,
    GetOneOutInfererForecasterNetworkRegretRequest as emissions_v9_GetOneOutInfererForecasterNetworkRegretRequest,
    GetOneOutInfererForecasterNetworkRegretResponse as emissions_v9_GetOneOutInfererForecasterNetworkRegretResponse,
    GetOneOutInfererInfererNetworkRegretRequest as emissions_v9_GetOneOutInfererInfererNetworkRegretRequest,
    GetOneOutInfererInfererNetworkRegretResponse as emissions_v9_GetOneOutInfererInfererNetworkRegretResponse,
    GetParamsRequest as emissions_v9_GetParamsRequest,
    GetParamsResponse as emissions_v9_GetParamsResponse,
    GetPreviousForecastRewardFractionRequest as emissions_v9_GetPreviousForecastRewardFractionRequest,
    GetPreviousForecastRewardFractionResponse as emissions_v9_GetPreviousForecastRewardFractionResponse,
    GetPreviousInferenceRewardFractionRequest as emissions_v9_GetPreviousInferenceRewardFractionRequest,
    GetPreviousInferenceRewardFractionResponse as emissions_v9_GetPreviousInferenceRewardFractionResponse,
    GetPreviousPercentageRewardToStakedReputersRequest as emissions_v9_GetPreviousPercentageRewardToStakedReputersRequest,
    GetPreviousPercentageRewardToStakedReputersResponse as emissions_v9_GetPreviousPercentageRewardToStakedReputersResponse,
    GetPreviousReputerRewardFractionRequest as emissions_v9_GetPreviousReputerRewardFractionRequest,
    GetPreviousReputerRewardFractionResponse as emissions_v9_GetPreviousReputerRewardFractionResponse,
    GetPreviousTopicQuantileForecasterScoreEmaRequest as emissions_v9_GetPreviousTopicQuantileForecasterScoreEmaRequest,
    GetPreviousTopicQuantileForecasterScoreEmaResponse as emissions_v9_GetPreviousTopicQuantileForecasterScoreEmaResponse,
    GetPreviousTopicQuantileInfererScoreEmaRequest as emissions_v9_GetPreviousTopicQuantileInfererScoreEmaRequest,
    GetPreviousTopicQuantileInfererScoreEmaResponse as emissions_v9_GetPreviousTopicQuantileInfererScoreEmaResponse,
    GetPreviousTopicQuantileReputerScoreEmaRequest as emissions_v9_GetPreviousTopicQuantileReputerScoreEmaRequest,
    GetPreviousTopicQuantileReputerScoreEmaResponse as emissions_v9_GetPreviousTopicQuantileReputerScoreEmaResponse,
    GetPreviousTopicWeightRequest as emissions_v9_GetPreviousTopicWeightRequest,
    GetPreviousTopicWeightResponse as emissions_v9_GetPreviousTopicWeightResponse,
    GetReputerLossBundlesAtBlockRequest as emissions_v9_GetReputerLossBundlesAtBlockRequest,
    GetReputerLossBundlesAtBlockResponse as emissions_v9_GetReputerLossBundlesAtBlockResponse,
    GetReputerNodeInfoRequest as emissions_v9_GetReputerNodeInfoRequest,
    GetReputerNodeInfoResponse as emissions_v9_GetReputerNodeInfoResponse,
    GetReputerScoreEmaRequest as emissions_v9_GetReputerScoreEmaRequest,
    GetReputerScoreEmaResponse as emissions_v9_GetReputerScoreEmaResponse,
    GetReputerStakeInTopicRequest as emissions_v9_GetReputerStakeInTopicRequest,
    GetReputerStakeInTopicResponse as emissions_v9_GetReputerStakeInTopicResponse,
    GetReputersScoresAtBlockRequest as emissions_v9_GetReputersScoresAtBlockRequest,
    GetReputersScoresAtBlockResponse as emissions_v9_GetReputersScoresAtBlockResponse,
    GetStakeFromDelegatorInTopicInReputerRequest as emissions_v9_GetStakeFromDelegatorInTopicInReputerRequest,
    GetStakeFromDelegatorInTopicInReputerResponse as emissions_v9_GetStakeFromDelegatorInTopicInReputerResponse,
    GetStakeFromDelegatorInTopicRequest as emissions_v9_GetStakeFromDelegatorInTopicRequest,
    GetStakeFromDelegatorInTopicResponse as emissions_v9_GetStakeFromDelegatorInTopicResponse,
    GetStakeFromReputerInTopicInSelfRequest as emissions_v9_GetStakeFromReputerInTopicInSelfRequest,
    GetStakeFromReputerInTopicInSelfResponse as emissions_v9_GetStakeFromReputerInTopicInSelfResponse,
    GetStakeRemovalForReputerAndTopicIdRequest as emissions_v9_GetStakeRemovalForReputerAndTopicIdRequest,
    GetStakeRemovalForReputerAndTopicIdResponse as emissions_v9_GetStakeRemovalForReputerAndTopicIdResponse,
    GetStakeRemovalInfoRequest as emissions_v9_GetStakeRemovalInfoRequest,
    GetStakeRemovalInfoResponse as emissions_v9_GetStakeRemovalInfoResponse,
    GetStakeRemovalsUpUntilBlockRequest as emissions_v9_GetStakeRemovalsUpUntilBlockRequest,
    GetStakeRemovalsUpUntilBlockResponse as emissions_v9_GetStakeRemovalsUpUntilBlockResponse,
    GetStakeReputerAuthorityRequest as emissions_v9_GetStakeReputerAuthorityRequest,
    GetStakeReputerAuthorityResponse as emissions_v9_GetStakeReputerAuthorityResponse,
    GetTopicFeeRevenueRequest as emissions_v9_GetTopicFeeRevenueRequest,
    GetTopicFeeRevenueResponse as emissions_v9_GetTopicFeeRevenueResponse,
    GetTopicInitialForecasterEmaScoreRequest as emissions_v9_GetTopicInitialForecasterEmaScoreRequest,
    GetTopicInitialForecasterEmaScoreResponse as emissions_v9_GetTopicInitialForecasterEmaScoreResponse,
    GetTopicInitialInfererEmaScoreRequest as emissions_v9_GetTopicInitialInfererEmaScoreRequest,
    GetTopicInitialInfererEmaScoreResponse as emissions_v9_GetTopicInitialInfererEmaScoreResponse,
    GetTopicInitialReputerEmaScoreRequest as emissions_v9_GetTopicInitialReputerEmaScoreRequest,
    GetTopicInitialReputerEmaScoreResponse as emissions_v9_GetTopicInitialReputerEmaScoreResponse,
    GetTopicLastReputerCommitInfoRequest as emissions_v9_GetTopicLastReputerCommitInfoRequest,
    GetTopicLastReputerCommitInfoResponse as emissions_v9_GetTopicLastReputerCommitInfoResponse,
    GetTopicLastWorkerCommitInfoRequest as emissions_v9_GetTopicLastWorkerCommitInfoRequest,
    GetTopicLastWorkerCommitInfoResponse as emissions_v9_GetTopicLastWorkerCommitInfoResponse,
    GetTopicRequest as emissions_v9_GetTopicRequest,
    GetTopicResponse as emissions_v9_GetTopicResponse,
    GetTopicRewardNonceRequest as emissions_v9_GetTopicRewardNonceRequest,
    GetTopicRewardNonceResponse as emissions_v9_GetTopicRewardNonceResponse,
    GetTopicStakeRequest as emissions_v9_GetTopicStakeRequest,
    GetTopicStakeResponse as emissions_v9_GetTopicStakeResponse,
    GetTotalRewardToDistributeRequest as emissions_v9_GetTotalRewardToDistributeRequest,
    GetTotalRewardToDistributeResponse as emissions_v9_GetTotalRewardToDistributeResponse,
    GetTotalStakeRequest as emissions_v9_GetTotalStakeRequest,
    GetTotalStakeResponse as emissions_v9_GetTotalStakeResponse,
    GetTotalSumPreviousTopicWeightsRequest as emissions_v9_GetTotalSumPreviousTopicWeightsRequest,
    GetTotalSumPreviousTopicWeightsResponse as emissions_v9_GetTotalSumPreviousTopicWeightsResponse,
    GetUnfulfilledReputerNoncesRequest as emissions_v9_GetUnfulfilledReputerNoncesRequest,
    GetUnfulfilledReputerNoncesResponse as emissions_v9_GetUnfulfilledReputerNoncesResponse,
    GetUnfulfilledWorkerNoncesRequest as emissions_v9_GetUnfulfilledWorkerNoncesRequest,
    GetUnfulfilledWorkerNoncesResponse as emissions_v9_GetUnfulfilledWorkerNoncesResponse,
    GetWorkerForecastScoresAtBlockRequest as emissions_v9_GetWorkerForecastScoresAtBlockRequest,
    GetWorkerForecastScoresAtBlockResponse as emissions_v9_GetWorkerForecastScoresAtBlockResponse,
    GetWorkerInferenceScoresAtBlockRequest as emissions_v9_GetWorkerInferenceScoresAtBlockRequest,
    GetWorkerInferenceScoresAtBlockResponse as emissions_v9_GetWorkerInferenceScoresAtBlockResponse,
    GetWorkerLatestInferenceByTopicIdRequest as emissions_v9_GetWorkerLatestInferenceByTopicIdRequest,
    GetWorkerLatestInferenceByTopicIdResponse as emissions_v9_GetWorkerLatestInferenceByTopicIdResponse,
    GetWorkerNodeInfoRequest as emissions_v9_GetWorkerNodeInfoRequest,
    GetWorkerNodeInfoResponse as emissions_v9_GetWorkerNodeInfoResponse,
    InsertReputerPayloadRequest as emissions_v9_InsertReputerPayloadRequest,
    InsertReputerPayloadResponse as emissions_v9_InsertReputerPayloadResponse,
    InsertWorkerPayloadRequest as emissions_v9_InsertWorkerPayloadRequest,
    InsertWorkerPayloadResponse as emissions_v9_InsertWorkerPayloadResponse,
    IsReputerNonceUnfulfilledRequest as emissions_v9_IsReputerNonceUnfulfilledRequest,
    IsReputerNonceUnfulfilledResponse as emissions_v9_IsReputerNonceUnfulfilledResponse,
    IsReputerRegisteredInTopicIdRequest as emissions_v9_IsReputerRegisteredInTopicIdRequest,
    IsReputerRegisteredInTopicIdResponse as emissions_v9_IsReputerRegisteredInTopicIdResponse,
    IsTopicActiveRequest as emissions_v9_IsTopicActiveRequest,
    IsTopicActiveResponse as emissions_v9_IsTopicActiveResponse,
    IsTopicReputerWhitelistEnabledRequest as emissions_v9_IsTopicReputerWhitelistEnabledRequest,
    IsTopicReputerWhitelistEnabledResponse as emissions_v9_IsTopicReputerWhitelistEnabledResponse,
    IsTopicWorkerWhitelistEnabledRequest as emissions_v9_IsTopicWorkerWhitelistEnabledRequest,
    IsTopicWorkerWhitelistEnabledResponse as emissions_v9_IsTopicWorkerWhitelistEnabledResponse,
    IsWhitelistAdminRequest as emissions_v9_IsWhitelistAdminRequest,
    IsWhitelistAdminResponse as emissions_v9_IsWhitelistAdminResponse,
    IsWhitelistedGlobalActorRequest as emissions_v9_IsWhitelistedGlobalActorRequest,
    IsWhitelistedGlobalActorResponse as emissions_v9_IsWhitelistedGlobalActorResponse,
    IsWhitelistedGlobalAdminRequest as emissions_v9_IsWhitelistedGlobalAdminRequest,
    IsWhitelistedGlobalAdminResponse as emissions_v9_IsWhitelistedGlobalAdminResponse,
    IsWhitelistedGlobalReputerRequest as emissions_v9_IsWhitelistedGlobalReputerRequest,
    IsWhitelistedGlobalReputerResponse as emissions_v9_IsWhitelistedGlobalReputerResponse,
    IsWhitelistedGlobalWorkerRequest as emissions_v9_IsWhitelistedGlobalWorkerRequest,
    IsWhitelistedGlobalWorkerResponse as emissions_v9_IsWhitelistedGlobalWorkerResponse,
    IsWhitelistedTopicCreatorRequest as emissions_v9_IsWhitelistedTopicCreatorRequest,
    IsWhitelistedTopicCreatorResponse as emissions_v9_IsWhitelistedTopicCreatorResponse,
    IsWhitelistedTopicReputerRequest as emissions_v9_IsWhitelistedTopicReputerRequest,
    IsWhitelistedTopicReputerResponse as emissions_v9_IsWhitelistedTopicReputerResponse,
    IsWhitelistedTopicWorkerRequest as emissions_v9_IsWhitelistedTopicWorkerRequest,
    IsWhitelistedTopicWorkerResponse as emissions_v9_IsWhitelistedTopicWorkerResponse,
    IsWorkerNonceUnfulfilledRequest as emissions_v9_IsWorkerNonceUnfulfilledRequest,
    IsWorkerNonceUnfulfilledResponse as emissions_v9_IsWorkerNonceUnfulfilledResponse,
    IsWorkerRegisteredInTopicIdRequest as emissions_v9_IsWorkerRegisteredInTopicIdRequest,
    IsWorkerRegisteredInTopicIdResponse as emissions_v9_IsWorkerRegisteredInTopicIdResponse,
    RegisterRequest as emissions_v9_RegisterRequest,
    RegisterResponse as emissions_v9_RegisterResponse,
    RemoveDelegateStakeRequest as emissions_v9_RemoveDelegateStakeRequest,
    RemoveDelegateStakeResponse as emissions_v9_RemoveDelegateStakeResponse,
    RemoveFromGlobalAdminWhitelistRequest as emissions_v9_RemoveFromGlobalAdminWhitelistRequest,
    RemoveFromGlobalAdminWhitelistResponse as emissions_v9_RemoveFromGlobalAdminWhitelistResponse,
    RemoveFromGlobalReputerWhitelistRequest as emissions_v9_RemoveFromGlobalReputerWhitelistRequest,
    RemoveFromGlobalReputerWhitelistResponse as emissions_v9_RemoveFromGlobalReputerWhitelistResponse,
    RemoveFromGlobalWhitelistRequest as emissions_v9_RemoveFromGlobalWhitelistRequest,
    RemoveFromGlobalWhitelistResponse as emissions_v9_RemoveFromGlobalWhitelistResponse,
    RemoveFromGlobalWorkerWhitelistRequest as emissions_v9_RemoveFromGlobalWorkerWhitelistRequest,
    RemoveFromGlobalWorkerWhitelistResponse as emissions_v9_RemoveFromGlobalWorkerWhitelistResponse,
    RemoveFromTopicCreatorWhitelistRequest as emissions_v9_RemoveFromTopicCreatorWhitelistRequest,
    RemoveFromTopicCreatorWhitelistResponse as emissions_v9_RemoveFromTopicCreatorWhitelistResponse,
    RemoveFromTopicReputerWhitelistRequest as emissions_v9_RemoveFromTopicReputerWhitelistRequest,
    RemoveFromTopicReputerWhitelistResponse as emissions_v9_RemoveFromTopicReputerWhitelistResponse,
    RemoveFromTopicWorkerWhitelistRequest as emissions_v9_RemoveFromTopicWorkerWhitelistRequest,
    RemoveFromTopicWorkerWhitelistResponse as emissions_v9_RemoveFromTopicWorkerWhitelistResponse,
    RemoveFromWhitelistAdminRequest as emissions_v9_RemoveFromWhitelistAdminRequest,
    RemoveFromWhitelistAdminResponse as emissions_v9_RemoveFromWhitelistAdminResponse,
    RemoveRegistrationRequest as emissions_v9_RemoveRegistrationRequest,
    RemoveRegistrationResponse as emissions_v9_RemoveRegistrationResponse,
    RemoveStakeRequest as emissions_v9_RemoveStakeRequest,
    RemoveStakeResponse as emissions_v9_RemoveStakeResponse,
    RewardDelegateStakeRequest as emissions_v9_RewardDelegateStakeRequest,
    RewardDelegateStakeResponse as emissions_v9_RewardDelegateStakeResponse,
    TopicExistsRequest as emissions_v9_TopicExistsRequest,
    TopicExistsResponse as emissions_v9_TopicExistsResponse,
    UpdateParamsRequest as emissions_v9_UpdateParamsRequest,
    UpdateParamsResponse as emissions_v9_UpdateParamsResponse,
)

@runtime_checkable
class EmissionsV9MsgServiceLike(Protocol):
    pass

class EmissionsV9RestMsgServiceClient(EmissionsV9MsgServiceLike):
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
class EmissionsV9QueryServiceLike(Protocol):
    def get_params(self, message: emissions_v9_GetParamsRequest | None = None) -> emissions_v9_GetParamsResponse: ...
    def get_next_topic_id(self, message: emissions_v9_GetNextTopicIdRequest | None = None) -> emissions_v9_GetNextTopicIdResponse: ...
    def get_topic(self, message: emissions_v9_GetTopicRequest) -> emissions_v9_GetTopicResponse: ...
    def get_worker_latest_inference_by_topic_id(self, message: emissions_v9_GetWorkerLatestInferenceByTopicIdRequest) -> emissions_v9_GetWorkerLatestInferenceByTopicIdResponse: ...
    def get_inferences_at_block(self, message: emissions_v9_GetInferencesAtBlockRequest) -> emissions_v9_GetInferencesAtBlockResponse: ...
    def get_latest_topic_inferences(self, message: emissions_v9_GetLatestTopicInferencesRequest) -> emissions_v9_GetLatestTopicInferencesResponse: ...
    def get_forecasts_at_block(self, message: emissions_v9_GetForecastsAtBlockRequest) -> emissions_v9_GetForecastsAtBlockResponse: ...
    def get_network_loss_bundle_at_block(self, message: emissions_v9_GetNetworkLossBundleAtBlockRequest) -> emissions_v9_GetNetworkLossBundleAtBlockResponse: ...
    def get_total_stake(self, message: emissions_v9_GetTotalStakeRequest | None = None) -> emissions_v9_GetTotalStakeResponse: ...
    def get_reputer_stake_in_topic(self, message: emissions_v9_GetReputerStakeInTopicRequest) -> emissions_v9_GetReputerStakeInTopicResponse: ...
    def get_multi_reputer_stake_in_topic(self, message: emissions_v9_GetMultiReputerStakeInTopicRequest) -> emissions_v9_GetMultiReputerStakeInTopicResponse: ...
    def get_stake_from_reputer_in_topic_in_self(self, message: emissions_v9_GetStakeFromReputerInTopicInSelfRequest) -> emissions_v9_GetStakeFromReputerInTopicInSelfResponse: ...
    def get_delegate_stake_in_topic_in_reputer(self, message: emissions_v9_GetDelegateStakeInTopicInReputerRequest) -> emissions_v9_GetDelegateStakeInTopicInReputerResponse: ...
    def get_stake_from_delegator_in_topic_in_reputer(self, message: emissions_v9_GetStakeFromDelegatorInTopicInReputerRequest) -> emissions_v9_GetStakeFromDelegatorInTopicInReputerResponse: ...
    def get_stake_from_delegator_in_topic(self, message: emissions_v9_GetStakeFromDelegatorInTopicRequest) -> emissions_v9_GetStakeFromDelegatorInTopicResponse: ...
    def get_topic_stake(self, message: emissions_v9_GetTopicStakeRequest) -> emissions_v9_GetTopicStakeResponse: ...
    def get_stake_removals_up_until_block(self, message: emissions_v9_GetStakeRemovalsUpUntilBlockRequest) -> emissions_v9_GetStakeRemovalsUpUntilBlockResponse: ...
    def get_delegate_stake_removals_up_until_block(self, message: emissions_v9_GetDelegateStakeRemovalsUpUntilBlockRequest) -> emissions_v9_GetDelegateStakeRemovalsUpUntilBlockResponse: ...
    def get_stake_removal_info(self, message: emissions_v9_GetStakeRemovalInfoRequest) -> emissions_v9_GetStakeRemovalInfoResponse: ...
    def get_delegate_stake_removal_info(self, message: emissions_v9_GetDelegateStakeRemovalInfoRequest) -> emissions_v9_GetDelegateStakeRemovalInfoResponse: ...
    def get_worker_node_info(self, message: emissions_v9_GetWorkerNodeInfoRequest) -> emissions_v9_GetWorkerNodeInfoResponse: ...
    def get_reputer_node_info(self, message: emissions_v9_GetReputerNodeInfoRequest) -> emissions_v9_GetReputerNodeInfoResponse: ...
    def is_worker_registered_in_topic_id(self, message: emissions_v9_IsWorkerRegisteredInTopicIdRequest) -> emissions_v9_IsWorkerRegisteredInTopicIdResponse: ...
    def is_reputer_registered_in_topic_id(self, message: emissions_v9_IsReputerRegisteredInTopicIdRequest) -> emissions_v9_IsReputerRegisteredInTopicIdResponse: ...
    def get_network_inferences_at_block(self, message: emissions_v9_GetNetworkInferencesAtBlockRequest) -> emissions_v9_GetNetworkInferencesAtBlockResponse: ...
    def get_network_inferences_at_block_outlier_resistant(self, message: emissions_v9_GetNetworkInferencesAtBlockOutlierResistantRequest) -> emissions_v9_GetNetworkInferencesAtBlockOutlierResistantResponse: ...
    def get_latest_network_inferences(self, message: emissions_v9_GetLatestNetworkInferencesRequest) -> emissions_v9_GetLatestNetworkInferencesResponse: ...
    def get_latest_network_inferences_outlier_resistant(self, message: emissions_v9_GetLatestNetworkInferencesOutlierResistantRequest) -> emissions_v9_GetLatestNetworkInferencesOutlierResistantResponse: ...
    def is_worker_nonce_unfulfilled(self, message: emissions_v9_IsWorkerNonceUnfulfilledRequest) -> emissions_v9_IsWorkerNonceUnfulfilledResponse: ...
    def is_reputer_nonce_unfulfilled(self, message: emissions_v9_IsReputerNonceUnfulfilledRequest) -> emissions_v9_IsReputerNonceUnfulfilledResponse: ...
    def get_unfulfilled_worker_nonces(self, message: emissions_v9_GetUnfulfilledWorkerNoncesRequest) -> emissions_v9_GetUnfulfilledWorkerNoncesResponse: ...
    def get_unfulfilled_reputer_nonces(self, message: emissions_v9_GetUnfulfilledReputerNoncesRequest) -> emissions_v9_GetUnfulfilledReputerNoncesResponse: ...
    def get_inferer_network_regret(self, message: emissions_v9_GetInfererNetworkRegretRequest) -> emissions_v9_GetInfererNetworkRegretResponse: ...
    def get_forecaster_network_regret(self, message: emissions_v9_GetForecasterNetworkRegretRequest) -> emissions_v9_GetForecasterNetworkRegretResponse: ...
    def get_one_in_forecaster_network_regret(self, message: emissions_v9_GetOneInForecasterNetworkRegretRequest) -> emissions_v9_GetOneInForecasterNetworkRegretResponse: ...
    def is_whitelist_admin(self, message: emissions_v9_IsWhitelistAdminRequest) -> emissions_v9_IsWhitelistAdminResponse: ...
    def get_topic_last_worker_commit_info(self, message: emissions_v9_GetTopicLastWorkerCommitInfoRequest) -> emissions_v9_GetTopicLastWorkerCommitInfoResponse: ...
    def get_topic_last_reputer_commit_info(self, message: emissions_v9_GetTopicLastReputerCommitInfoRequest) -> emissions_v9_GetTopicLastReputerCommitInfoResponse: ...
    def get_topic_reward_nonce(self, message: emissions_v9_GetTopicRewardNonceRequest) -> emissions_v9_GetTopicRewardNonceResponse: ...
    def get_reputer_loss_bundles_at_block(self, message: emissions_v9_GetReputerLossBundlesAtBlockRequest) -> emissions_v9_GetReputerLossBundlesAtBlockResponse: ...
    def get_stake_reputer_authority(self, message: emissions_v9_GetStakeReputerAuthorityRequest) -> emissions_v9_GetStakeReputerAuthorityResponse: ...
    def get_delegate_stake_placement(self, message: emissions_v9_GetDelegateStakePlacementRequest) -> emissions_v9_GetDelegateStakePlacementResponse: ...
    def get_delegate_stake_upon_reputer(self, message: emissions_v9_GetDelegateStakeUponReputerRequest) -> emissions_v9_GetDelegateStakeUponReputerResponse: ...
    def get_delegate_reward_per_share(self, message: emissions_v9_GetDelegateRewardPerShareRequest) -> emissions_v9_GetDelegateRewardPerShareResponse: ...
    def get_stake_removal_for_reputer_and_topic_id(self, message: emissions_v9_GetStakeRemovalForReputerAndTopicIdRequest) -> emissions_v9_GetStakeRemovalForReputerAndTopicIdResponse: ...
    def get_delegate_stake_removal(self, message: emissions_v9_GetDelegateStakeRemovalRequest) -> emissions_v9_GetDelegateStakeRemovalResponse: ...
    def get_previous_topic_weight(self, message: emissions_v9_GetPreviousTopicWeightRequest) -> emissions_v9_GetPreviousTopicWeightResponse: ...
    def get_total_sum_previous_topic_weights(self, message: emissions_v9_GetTotalSumPreviousTopicWeightsRequest | None = None) -> emissions_v9_GetTotalSumPreviousTopicWeightsResponse: ...
    def topic_exists(self, message: emissions_v9_TopicExistsRequest) -> emissions_v9_TopicExistsResponse: ...
    def is_topic_active(self, message: emissions_v9_IsTopicActiveRequest) -> emissions_v9_IsTopicActiveResponse: ...
    def get_topic_fee_revenue(self, message: emissions_v9_GetTopicFeeRevenueRequest) -> emissions_v9_GetTopicFeeRevenueResponse: ...
    def get_inferer_score_ema(self, message: emissions_v9_GetInfererScoreEmaRequest) -> emissions_v9_GetInfererScoreEmaResponse: ...
    def get_forecaster_score_ema(self, message: emissions_v9_GetForecasterScoreEmaRequest) -> emissions_v9_GetForecasterScoreEmaResponse: ...
    def get_reputer_score_ema(self, message: emissions_v9_GetReputerScoreEmaRequest) -> emissions_v9_GetReputerScoreEmaResponse: ...
    def get_inference_scores_until_block(self, message: emissions_v9_GetInferenceScoresUntilBlockRequest) -> emissions_v9_GetInferenceScoresUntilBlockResponse: ...
    def get_previous_topic_quantile_forecaster_score_ema(self, message: emissions_v9_GetPreviousTopicQuantileForecasterScoreEmaRequest) -> emissions_v9_GetPreviousTopicQuantileForecasterScoreEmaResponse: ...
    def get_previous_topic_quantile_inferer_score_ema(self, message: emissions_v9_GetPreviousTopicQuantileInfererScoreEmaRequest) -> emissions_v9_GetPreviousTopicQuantileInfererScoreEmaResponse: ...
    def get_previous_topic_quantile_reputer_score_ema(self, message: emissions_v9_GetPreviousTopicQuantileReputerScoreEmaRequest) -> emissions_v9_GetPreviousTopicQuantileReputerScoreEmaResponse: ...
    def get_worker_inference_scores_at_block(self, message: emissions_v9_GetWorkerInferenceScoresAtBlockRequest) -> emissions_v9_GetWorkerInferenceScoresAtBlockResponse: ...
    def get_current_lowest_inferer_score(self, message: emissions_v9_GetCurrentLowestInfererScoreRequest) -> emissions_v9_GetCurrentLowestInfererScoreResponse: ...
    def get_forecast_scores_until_block(self, message: emissions_v9_GetForecastScoresUntilBlockRequest) -> emissions_v9_GetForecastScoresUntilBlockResponse: ...
    def get_worker_forecast_scores_at_block(self, message: emissions_v9_GetWorkerForecastScoresAtBlockRequest) -> emissions_v9_GetWorkerForecastScoresAtBlockResponse: ...
    def get_current_lowest_forecaster_score(self, message: emissions_v9_GetCurrentLowestForecasterScoreRequest) -> emissions_v9_GetCurrentLowestForecasterScoreResponse: ...
    def get_reputers_scores_at_block(self, message: emissions_v9_GetReputersScoresAtBlockRequest) -> emissions_v9_GetReputersScoresAtBlockResponse: ...
    def get_current_lowest_reputer_score(self, message: emissions_v9_GetCurrentLowestReputerScoreRequest) -> emissions_v9_GetCurrentLowestReputerScoreResponse: ...
    def get_listening_coefficient(self, message: emissions_v9_GetListeningCoefficientRequest) -> emissions_v9_GetListeningCoefficientResponse: ...
    def get_previous_reputer_reward_fraction(self, message: emissions_v9_GetPreviousReputerRewardFractionRequest) -> emissions_v9_GetPreviousReputerRewardFractionResponse: ...
    def get_previous_inference_reward_fraction(self, message: emissions_v9_GetPreviousInferenceRewardFractionRequest) -> emissions_v9_GetPreviousInferenceRewardFractionResponse: ...
    def get_previous_forecast_reward_fraction(self, message: emissions_v9_GetPreviousForecastRewardFractionRequest) -> emissions_v9_GetPreviousForecastRewardFractionResponse: ...
    def get_previous_percentage_reward_to_staked_reputers(self, message: emissions_v9_GetPreviousPercentageRewardToStakedReputersRequest | None = None) -> emissions_v9_GetPreviousPercentageRewardToStakedReputersResponse: ...
    def get_total_reward_to_distribute(self, message: emissions_v9_GetTotalRewardToDistributeRequest | None = None) -> emissions_v9_GetTotalRewardToDistributeResponse: ...
    def get_naive_inferer_network_regret(self, message: emissions_v9_GetNaiveInfererNetworkRegretRequest | None = None) -> emissions_v9_GetNaiveInfererNetworkRegretResponse: ...
    def get_one_out_inferer_inferer_network_regret(self, message: emissions_v9_GetOneOutInfererInfererNetworkRegretRequest | None = None) -> emissions_v9_GetOneOutInfererInfererNetworkRegretResponse: ...
    def get_one_out_inferer_forecaster_network_regret(self, message: emissions_v9_GetOneOutInfererForecasterNetworkRegretRequest | None = None) -> emissions_v9_GetOneOutInfererForecasterNetworkRegretResponse: ...
    def get_one_out_forecaster_inferer_network_regret(self, message: emissions_v9_GetOneOutForecasterInfererNetworkRegretRequest | None = None) -> emissions_v9_GetOneOutForecasterInfererNetworkRegretResponse: ...
    def get_one_out_forecaster_forecaster_network_regret(self, message: emissions_v9_GetOneOutForecasterForecasterNetworkRegretRequest | None = None) -> emissions_v9_GetOneOutForecasterForecasterNetworkRegretResponse: ...
    def get_active_topics_at_block(self, message: emissions_v9_GetActiveTopicsAtBlockRequest) -> emissions_v9_GetActiveTopicsAtBlockResponse: ...
    def get_next_churning_block_by_topic_id(self, message: emissions_v9_GetNextChurningBlockByTopicIdRequest) -> emissions_v9_GetNextChurningBlockByTopicIdResponse: ...
    def get_count_inferer_inclusions_in_topic(self, message: emissions_v9_GetCountInfererInclusionsInTopicRequest) -> emissions_v9_GetCountInfererInclusionsInTopicResponse: ...
    def get_count_forecaster_inclusions_in_topic(self, message: emissions_v9_GetCountForecasterInclusionsInTopicRequest) -> emissions_v9_GetCountForecasterInclusionsInTopicResponse: ...
    def get_active_reputers_for_topic(self, message: emissions_v9_GetActiveReputersForTopicRequest) -> emissions_v9_GetActiveReputersForTopicResponse: ...
    def get_active_forecasters_for_topic(self, message: emissions_v9_GetActiveForecastersForTopicRequest) -> emissions_v9_GetActiveForecastersForTopicResponse: ...
    def get_active_inferers_for_topic(self, message: emissions_v9_GetActiveInferersForTopicRequest) -> emissions_v9_GetActiveInferersForTopicResponse: ...
    def is_whitelisted_global_worker(self, message: emissions_v9_IsWhitelistedGlobalWorkerRequest) -> emissions_v9_IsWhitelistedGlobalWorkerResponse: ...
    def is_whitelisted_global_reputer(self, message: emissions_v9_IsWhitelistedGlobalReputerRequest) -> emissions_v9_IsWhitelistedGlobalReputerResponse: ...
    def is_whitelisted_global_admin(self, message: emissions_v9_IsWhitelistedGlobalAdminRequest) -> emissions_v9_IsWhitelistedGlobalAdminResponse: ...
    def is_topic_worker_whitelist_enabled(self, message: emissions_v9_IsTopicWorkerWhitelistEnabledRequest) -> emissions_v9_IsTopicWorkerWhitelistEnabledResponse: ...
    def is_topic_reputer_whitelist_enabled(self, message: emissions_v9_IsTopicReputerWhitelistEnabledRequest) -> emissions_v9_IsTopicReputerWhitelistEnabledResponse: ...
    def is_whitelisted_topic_creator(self, message: emissions_v9_IsWhitelistedTopicCreatorRequest) -> emissions_v9_IsWhitelistedTopicCreatorResponse: ...
    def is_whitelisted_global_actor(self, message: emissions_v9_IsWhitelistedGlobalActorRequest) -> emissions_v9_IsWhitelistedGlobalActorResponse: ...
    def is_whitelisted_topic_worker(self, message: emissions_v9_IsWhitelistedTopicWorkerRequest) -> emissions_v9_IsWhitelistedTopicWorkerResponse: ...
    def is_whitelisted_topic_reputer(self, message: emissions_v9_IsWhitelistedTopicReputerRequest) -> emissions_v9_IsWhitelistedTopicReputerResponse: ...
    def can_update_all_global_whitelists(self, message: emissions_v9_CanUpdateAllGlobalWhitelistsRequest) -> emissions_v9_CanUpdateAllGlobalWhitelistsResponse: ...
    def can_update_global_worker_whitelist(self, message: emissions_v9_CanUpdateGlobalWorkerWhitelistRequest) -> emissions_v9_CanUpdateGlobalWorkerWhitelistResponse: ...
    def can_update_global_reputer_whitelist(self, message: emissions_v9_CanUpdateGlobalReputerWhitelistRequest) -> emissions_v9_CanUpdateGlobalReputerWhitelistResponse: ...
    def can_update_params(self, message: emissions_v9_CanUpdateParamsRequest) -> emissions_v9_CanUpdateParamsResponse: ...
    def can_update_topic_whitelist(self, message: emissions_v9_CanUpdateTopicWhitelistRequest) -> emissions_v9_CanUpdateTopicWhitelistResponse: ...
    def can_create_topic(self, message: emissions_v9_CanCreateTopicRequest) -> emissions_v9_CanCreateTopicResponse: ...
    def can_submit_worker_payload(self, message: emissions_v9_CanSubmitWorkerPayloadRequest) -> emissions_v9_CanSubmitWorkerPayloadResponse: ...
    def can_submit_reputer_payload(self, message: emissions_v9_CanSubmitReputerPayloadRequest) -> emissions_v9_CanSubmitReputerPayloadResponse: ...
    def get_topic_initial_inferer_ema_score(self, message: emissions_v9_GetTopicInitialInfererEmaScoreRequest) -> emissions_v9_GetTopicInitialInfererEmaScoreResponse: ...
    def get_topic_initial_forecaster_ema_score(self, message: emissions_v9_GetTopicInitialForecasterEmaScoreRequest) -> emissions_v9_GetTopicInitialForecasterEmaScoreResponse: ...
    def get_topic_initial_reputer_ema_score(self, message: emissions_v9_GetTopicInitialReputerEmaScoreRequest) -> emissions_v9_GetTopicInitialReputerEmaScoreResponse: ...
    def get_latest_regret_std_norm(self, message: emissions_v9_GetLatestRegretStdNormRequest) -> emissions_v9_GetLatestRegretStdNormResponse: ...
    def get_latest_inferer_weight(self, message: emissions_v9_GetLatestInfererWeightRequest) -> emissions_v9_GetLatestInfererWeightResponse: ...
    def get_latest_forecaster_weight(self, message: emissions_v9_GetLatestForecasterWeightRequest) -> emissions_v9_GetLatestForecasterWeightResponse: ...

class EmissionsV9RestQueryServiceClient(EmissionsV9QueryServiceLike):
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

    def get_params(self, message: emissions_v9_GetParamsRequest | None = None) -> emissions_v9_GetParamsResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/params"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetParamsResponse().from_json(response.text)

    def get_next_topic_id(self, message: emissions_v9_GetNextTopicIdRequest | None = None) -> emissions_v9_GetNextTopicIdResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/next_topic_id"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetNextTopicIdResponse().from_json(response.text)

    def get_topic(self, message: emissions_v9_GetTopicRequest) -> emissions_v9_GetTopicResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/topics/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetTopicResponse().from_json(response.text)

    def get_worker_latest_inference_by_topic_id(self, message: emissions_v9_GetWorkerLatestInferenceByTopicIdRequest) -> emissions_v9_GetWorkerLatestInferenceByTopicIdResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/topics/{message.topic_id}/workers/{message.worker_address}/latest_inference"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetWorkerLatestInferenceByTopicIdResponse().from_json(response.text)

    def get_inferences_at_block(self, message: emissions_v9_GetInferencesAtBlockRequest) -> emissions_v9_GetInferencesAtBlockResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/inferences/{message.topic_id}/{message.block_height}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetInferencesAtBlockResponse().from_json(response.text)

    def get_latest_topic_inferences(self, message: emissions_v9_GetLatestTopicInferencesRequest) -> emissions_v9_GetLatestTopicInferencesResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/latest_inferences/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetLatestTopicInferencesResponse().from_json(response.text)

    def get_forecasts_at_block(self, message: emissions_v9_GetForecastsAtBlockRequest) -> emissions_v9_GetForecastsAtBlockResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/forecasts/{message.topic_id}/{message.block_height}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetForecastsAtBlockResponse().from_json(response.text)

    def get_network_loss_bundle_at_block(self, message: emissions_v9_GetNetworkLossBundleAtBlockRequest) -> emissions_v9_GetNetworkLossBundleAtBlockResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/network_loss/{message.topic_id}/{message.block_height}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetNetworkLossBundleAtBlockResponse().from_json(response.text)

    def get_total_stake(self, message: emissions_v9_GetTotalStakeRequest | None = None) -> emissions_v9_GetTotalStakeResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/total_stake"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetTotalStakeResponse().from_json(response.text)

    def get_reputer_stake_in_topic(self, message: emissions_v9_GetReputerStakeInTopicRequest) -> emissions_v9_GetReputerStakeInTopicResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/reputer_stake/{message.address}/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetReputerStakeInTopicResponse().from_json(response.text)

    def get_multi_reputer_stake_in_topic(self, message: emissions_v9_GetMultiReputerStakeInTopicRequest) -> emissions_v9_GetMultiReputerStakeInTopicResponse:
        params = {
            "addresses": message.addresses if message else None,
        }
        url = self.base_url + f"/emissions/v9/reputers_stakes/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetMultiReputerStakeInTopicResponse().from_json(response.text)

    def get_stake_from_reputer_in_topic_in_self(self, message: emissions_v9_GetStakeFromReputerInTopicInSelfRequest) -> emissions_v9_GetStakeFromReputerInTopicInSelfResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/reputer_stake_self/{message.reputer_address}/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetStakeFromReputerInTopicInSelfResponse().from_json(response.text)

    def get_delegate_stake_in_topic_in_reputer(self, message: emissions_v9_GetDelegateStakeInTopicInReputerRequest) -> emissions_v9_GetDelegateStakeInTopicInReputerResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/reputer_delegate_stake/{message.reputer_address}/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetDelegateStakeInTopicInReputerResponse().from_json(response.text)

    def get_stake_from_delegator_in_topic_in_reputer(self, message: emissions_v9_GetStakeFromDelegatorInTopicInReputerRequest) -> emissions_v9_GetStakeFromDelegatorInTopicInReputerResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/delegate_stake/{message.delegator_address}/{message.reputer_address}/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetStakeFromDelegatorInTopicInReputerResponse().from_json(response.text)

    def get_stake_from_delegator_in_topic(self, message: emissions_v9_GetStakeFromDelegatorInTopicRequest) -> emissions_v9_GetStakeFromDelegatorInTopicResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/delegate_stake/{message.delegator_address}/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetStakeFromDelegatorInTopicResponse().from_json(response.text)

    def get_topic_stake(self, message: emissions_v9_GetTopicStakeRequest) -> emissions_v9_GetTopicStakeResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/stake/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetTopicStakeResponse().from_json(response.text)

    def get_stake_removals_up_until_block(self, message: emissions_v9_GetStakeRemovalsUpUntilBlockRequest) -> emissions_v9_GetStakeRemovalsUpUntilBlockResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/stake_removals/{message.block_height}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetStakeRemovalsUpUntilBlockResponse().from_json(response.text)

    def get_delegate_stake_removals_up_until_block(self, message: emissions_v9_GetDelegateStakeRemovalsUpUntilBlockRequest) -> emissions_v9_GetDelegateStakeRemovalsUpUntilBlockResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/delegate_stake_removals/{message.block_height}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetDelegateStakeRemovalsUpUntilBlockResponse().from_json(response.text)

    def get_stake_removal_info(self, message: emissions_v9_GetStakeRemovalInfoRequest) -> emissions_v9_GetStakeRemovalInfoResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/stake_removal/{message.topic_id}/{message.reputer}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetStakeRemovalInfoResponse().from_json(response.text)

    def get_delegate_stake_removal_info(self, message: emissions_v9_GetDelegateStakeRemovalInfoRequest) -> emissions_v9_GetDelegateStakeRemovalInfoResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/delegate_stake_removal/{message.topic_id}/{message.delegator}/{message.reputer}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetDelegateStakeRemovalInfoResponse().from_json(response.text)

    def get_worker_node_info(self, message: emissions_v9_GetWorkerNodeInfoRequest) -> emissions_v9_GetWorkerNodeInfoResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/worker/{message.address}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetWorkerNodeInfoResponse().from_json(response.text)

    def get_reputer_node_info(self, message: emissions_v9_GetReputerNodeInfoRequest) -> emissions_v9_GetReputerNodeInfoResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/reputer/{message.address}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetReputerNodeInfoResponse().from_json(response.text)

    def is_worker_registered_in_topic_id(self, message: emissions_v9_IsWorkerRegisteredInTopicIdRequest) -> emissions_v9_IsWorkerRegisteredInTopicIdResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/worker_registered/{message.topic_id}/{message.address}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_IsWorkerRegisteredInTopicIdResponse().from_json(response.text)

    def is_reputer_registered_in_topic_id(self, message: emissions_v9_IsReputerRegisteredInTopicIdRequest) -> emissions_v9_IsReputerRegisteredInTopicIdResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/reputer_registered/{message.topic_id}/{message.address}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_IsReputerRegisteredInTopicIdResponse().from_json(response.text)

    def get_network_inferences_at_block(self, message: emissions_v9_GetNetworkInferencesAtBlockRequest) -> emissions_v9_GetNetworkInferencesAtBlockResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/network_inferences/{message.topic_id}/last_inference/{message.block_height_last_inference}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetNetworkInferencesAtBlockResponse().from_json(response.text)

    def get_network_inferences_at_block_outlier_resistant(self, message: emissions_v9_GetNetworkInferencesAtBlockOutlierResistantRequest) -> emissions_v9_GetNetworkInferencesAtBlockOutlierResistantResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/network_inferences_outlier_resistant/{message.topic_id}/last_inference/{message.block_height_last_inference}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetNetworkInferencesAtBlockOutlierResistantResponse().from_json(response.text)

    def get_latest_network_inferences(self, message: emissions_v9_GetLatestNetworkInferencesRequest) -> emissions_v9_GetLatestNetworkInferencesResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/latest_network_inferences/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetLatestNetworkInferencesResponse().from_json(response.text)

    def get_latest_network_inferences_outlier_resistant(self, message: emissions_v9_GetLatestNetworkInferencesOutlierResistantRequest) -> emissions_v9_GetLatestNetworkInferencesOutlierResistantResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/latest_network_inferences_outlier_resistant/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetLatestNetworkInferencesOutlierResistantResponse().from_json(response.text)

    def is_worker_nonce_unfulfilled(self, message: emissions_v9_IsWorkerNonceUnfulfilledRequest) -> emissions_v9_IsWorkerNonceUnfulfilledResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/is_worker_nonce_unfulfilled/{message.topic_id}/{message.block_height}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_IsWorkerNonceUnfulfilledResponse().from_json(response.text)

    def is_reputer_nonce_unfulfilled(self, message: emissions_v9_IsReputerNonceUnfulfilledRequest) -> emissions_v9_IsReputerNonceUnfulfilledResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/is_reputer_nonce_unfulfilled/{message.topic_id}/{message.block_height}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_IsReputerNonceUnfulfilledResponse().from_json(response.text)

    def get_unfulfilled_worker_nonces(self, message: emissions_v9_GetUnfulfilledWorkerNoncesRequest) -> emissions_v9_GetUnfulfilledWorkerNoncesResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/unfulfilled_worker_nonces/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetUnfulfilledWorkerNoncesResponse().from_json(response.text)

    def get_unfulfilled_reputer_nonces(self, message: emissions_v9_GetUnfulfilledReputerNoncesRequest) -> emissions_v9_GetUnfulfilledReputerNoncesResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/unfulfilled_reputer_nonces/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetUnfulfilledReputerNoncesResponse().from_json(response.text)

    def get_inferer_network_regret(self, message: emissions_v9_GetInfererNetworkRegretRequest) -> emissions_v9_GetInfererNetworkRegretResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/inferer_network_regret/{message.topic_id}/{message.actor_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetInfererNetworkRegretResponse().from_json(response.text)

    def get_forecaster_network_regret(self, message: emissions_v9_GetForecasterNetworkRegretRequest) -> emissions_v9_GetForecasterNetworkRegretResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/forecaster_network_regret/{message.topic_id}/{message.worker}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetForecasterNetworkRegretResponse().from_json(response.text)

    def get_one_in_forecaster_network_regret(self, message: emissions_v9_GetOneInForecasterNetworkRegretRequest) -> emissions_v9_GetOneInForecasterNetworkRegretResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/one_in_forecaster_network_regret/{message.topic_id}/{message.forecaster}/{message.inferer}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetOneInForecasterNetworkRegretResponse().from_json(response.text)

    def is_whitelist_admin(self, message: emissions_v9_IsWhitelistAdminRequest) -> emissions_v9_IsWhitelistAdminResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/whitelist_admin/{message.address}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_IsWhitelistAdminResponse().from_json(response.text)

    def get_topic_last_worker_commit_info(self, message: emissions_v9_GetTopicLastWorkerCommitInfoRequest) -> emissions_v9_GetTopicLastWorkerCommitInfoResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/topic_last_worker_commit_info/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetTopicLastWorkerCommitInfoResponse().from_json(response.text)

    def get_topic_last_reputer_commit_info(self, message: emissions_v9_GetTopicLastReputerCommitInfoRequest) -> emissions_v9_GetTopicLastReputerCommitInfoResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/topic_last_reputer_commit_info/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetTopicLastReputerCommitInfoResponse().from_json(response.text)

    def get_topic_reward_nonce(self, message: emissions_v9_GetTopicRewardNonceRequest) -> emissions_v9_GetTopicRewardNonceResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/topic_reward_nonce/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetTopicRewardNonceResponse().from_json(response.text)

    def get_reputer_loss_bundles_at_block(self, message: emissions_v9_GetReputerLossBundlesAtBlockRequest) -> emissions_v9_GetReputerLossBundlesAtBlockResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/reputer_loss_bundles/{message.topic_id}/{message.block_height}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetReputerLossBundlesAtBlockResponse().from_json(response.text)

    def get_stake_reputer_authority(self, message: emissions_v9_GetStakeReputerAuthorityRequest) -> emissions_v9_GetStakeReputerAuthorityResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/stake_reputer_authority/{message.topic_id}/{message.reputer}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetStakeReputerAuthorityResponse().from_json(response.text)

    def get_delegate_stake_placement(self, message: emissions_v9_GetDelegateStakePlacementRequest) -> emissions_v9_GetDelegateStakePlacementResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/delegate_stake_placement/{message.topic_id}/{message.delegator}/{message.target}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetDelegateStakePlacementResponse().from_json(response.text)

    def get_delegate_stake_upon_reputer(self, message: emissions_v9_GetDelegateStakeUponReputerRequest) -> emissions_v9_GetDelegateStakeUponReputerResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/delegate_stake_upon_reputer/{message.topic_id}/{message.target}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetDelegateStakeUponReputerResponse().from_json(response.text)

    def get_delegate_reward_per_share(self, message: emissions_v9_GetDelegateRewardPerShareRequest) -> emissions_v9_GetDelegateRewardPerShareResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/delegate_reward_per_share/{message.topic_id}/{message.reputer}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetDelegateRewardPerShareResponse().from_json(response.text)

    def get_stake_removal_for_reputer_and_topic_id(self, message: emissions_v9_GetStakeRemovalForReputerAndTopicIdRequest) -> emissions_v9_GetStakeRemovalForReputerAndTopicIdResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/stake_removal/{message.reputer}/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetStakeRemovalForReputerAndTopicIdResponse().from_json(response.text)

    def get_delegate_stake_removal(self, message: emissions_v9_GetDelegateStakeRemovalRequest) -> emissions_v9_GetDelegateStakeRemovalResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/delegate_stake_removal/{message.block_height}/{message.topic_id}/{message.delegator}/{message.reputer}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetDelegateStakeRemovalResponse().from_json(response.text)

    def get_previous_topic_weight(self, message: emissions_v9_GetPreviousTopicWeightRequest) -> emissions_v9_GetPreviousTopicWeightResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/previous_topic_weight/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetPreviousTopicWeightResponse().from_json(response.text)

    def get_total_sum_previous_topic_weights(self, message: emissions_v9_GetTotalSumPreviousTopicWeightsRequest | None = None) -> emissions_v9_GetTotalSumPreviousTopicWeightsResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/sum_previous_total_topic_weight"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetTotalSumPreviousTopicWeightsResponse().from_json(response.text)

    def topic_exists(self, message: emissions_v9_TopicExistsRequest) -> emissions_v9_TopicExistsResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/topic_exists/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_TopicExistsResponse().from_json(response.text)

    def is_topic_active(self, message: emissions_v9_IsTopicActiveRequest) -> emissions_v9_IsTopicActiveResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/is_topic_active/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_IsTopicActiveResponse().from_json(response.text)

    def get_topic_fee_revenue(self, message: emissions_v9_GetTopicFeeRevenueRequest) -> emissions_v9_GetTopicFeeRevenueResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/topic_fee_revenue/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetTopicFeeRevenueResponse().from_json(response.text)

    def get_inferer_score_ema(self, message: emissions_v9_GetInfererScoreEmaRequest) -> emissions_v9_GetInfererScoreEmaResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/inferer_score_ema/{message.topic_id}/{message.inferer}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetInfererScoreEmaResponse().from_json(response.text)

    def get_forecaster_score_ema(self, message: emissions_v9_GetForecasterScoreEmaRequest) -> emissions_v9_GetForecasterScoreEmaResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/forecaster_score_ema/{message.topic_id}/{message.forecaster}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetForecasterScoreEmaResponse().from_json(response.text)

    def get_reputer_score_ema(self, message: emissions_v9_GetReputerScoreEmaRequest) -> emissions_v9_GetReputerScoreEmaResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/reputer_score_ema/{message.topic_id}/{message.reputer}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetReputerScoreEmaResponse().from_json(response.text)

    def get_inference_scores_until_block(self, message: emissions_v9_GetInferenceScoresUntilBlockRequest) -> emissions_v9_GetInferenceScoresUntilBlockResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/inference_scores_until_block/{message.topic_id}/{message.block_height}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetInferenceScoresUntilBlockResponse().from_json(response.text)

    def get_previous_topic_quantile_forecaster_score_ema(self, message: emissions_v9_GetPreviousTopicQuantileForecasterScoreEmaRequest) -> emissions_v9_GetPreviousTopicQuantileForecasterScoreEmaResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/topic_quantile_forecaster_score_ema/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetPreviousTopicQuantileForecasterScoreEmaResponse().from_json(response.text)

    def get_previous_topic_quantile_inferer_score_ema(self, message: emissions_v9_GetPreviousTopicQuantileInfererScoreEmaRequest) -> emissions_v9_GetPreviousTopicQuantileInfererScoreEmaResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/topic_quantile_inferer_score_ema/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetPreviousTopicQuantileInfererScoreEmaResponse().from_json(response.text)

    def get_previous_topic_quantile_reputer_score_ema(self, message: emissions_v9_GetPreviousTopicQuantileReputerScoreEmaRequest) -> emissions_v9_GetPreviousTopicQuantileReputerScoreEmaResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/topic_quantile_reputer_score_ema/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetPreviousTopicQuantileReputerScoreEmaResponse().from_json(response.text)

    def get_worker_inference_scores_at_block(self, message: emissions_v9_GetWorkerInferenceScoresAtBlockRequest) -> emissions_v9_GetWorkerInferenceScoresAtBlockResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/worker_inference_scores_at_block/{message.topic_id}/{message.block_height}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetWorkerInferenceScoresAtBlockResponse().from_json(response.text)

    def get_current_lowest_inferer_score(self, message: emissions_v9_GetCurrentLowestInfererScoreRequest) -> emissions_v9_GetCurrentLowestInfererScoreResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/current_lowest_inferer_score/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetCurrentLowestInfererScoreResponse().from_json(response.text)

    def get_forecast_scores_until_block(self, message: emissions_v9_GetForecastScoresUntilBlockRequest) -> emissions_v9_GetForecastScoresUntilBlockResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/forecast_scores_until_block/{message.topic_id}/{message.block_height}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetForecastScoresUntilBlockResponse().from_json(response.text)

    def get_worker_forecast_scores_at_block(self, message: emissions_v9_GetWorkerForecastScoresAtBlockRequest) -> emissions_v9_GetWorkerForecastScoresAtBlockResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/worker_forecast_scores_at_block/{message.topic_id}/{message.block_height}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetWorkerForecastScoresAtBlockResponse().from_json(response.text)

    def get_current_lowest_forecaster_score(self, message: emissions_v9_GetCurrentLowestForecasterScoreRequest) -> emissions_v9_GetCurrentLowestForecasterScoreResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/current_lowest_forecaster_score/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetCurrentLowestForecasterScoreResponse().from_json(response.text)

    def get_reputers_scores_at_block(self, message: emissions_v9_GetReputersScoresAtBlockRequest) -> emissions_v9_GetReputersScoresAtBlockResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/reputers_scores_at_block/{message.topic_id}/{message.block_height}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetReputersScoresAtBlockResponse().from_json(response.text)

    def get_current_lowest_reputer_score(self, message: emissions_v9_GetCurrentLowestReputerScoreRequest) -> emissions_v9_GetCurrentLowestReputerScoreResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/current_lowest_reputer_score/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetCurrentLowestReputerScoreResponse().from_json(response.text)

    def get_listening_coefficient(self, message: emissions_v9_GetListeningCoefficientRequest) -> emissions_v9_GetListeningCoefficientResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/listening_coefficient/{message.topic_id}/{message.reputer}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetListeningCoefficientResponse().from_json(response.text)

    def get_previous_reputer_reward_fraction(self, message: emissions_v9_GetPreviousReputerRewardFractionRequest) -> emissions_v9_GetPreviousReputerRewardFractionResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/previous_reputer_reward_fraction/{message.topic_id}/{message.reputer}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetPreviousReputerRewardFractionResponse().from_json(response.text)

    def get_previous_inference_reward_fraction(self, message: emissions_v9_GetPreviousInferenceRewardFractionRequest) -> emissions_v9_GetPreviousInferenceRewardFractionResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/previous_inference_reward_fraction/{message.topic_id}/{message.worker}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetPreviousInferenceRewardFractionResponse().from_json(response.text)

    def get_previous_forecast_reward_fraction(self, message: emissions_v9_GetPreviousForecastRewardFractionRequest) -> emissions_v9_GetPreviousForecastRewardFractionResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/previous_forecast_reward_fraction/{message.topic_id}/{message.worker}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetPreviousForecastRewardFractionResponse().from_json(response.text)

    def get_previous_percentage_reward_to_staked_reputers(self, message: emissions_v9_GetPreviousPercentageRewardToStakedReputersRequest | None = None) -> emissions_v9_GetPreviousPercentageRewardToStakedReputersResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/previous_percentage_reward_to_staked_reputers"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetPreviousPercentageRewardToStakedReputersResponse().from_json(response.text)

    def get_total_reward_to_distribute(self, message: emissions_v9_GetTotalRewardToDistributeRequest | None = None) -> emissions_v9_GetTotalRewardToDistributeResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/total_reward_to_distribute"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetTotalRewardToDistributeResponse().from_json(response.text)

    def get_naive_inferer_network_regret(self, message: emissions_v9_GetNaiveInfererNetworkRegretRequest | None = None) -> emissions_v9_GetNaiveInfererNetworkRegretResponse:
        params = {
            "topic_id": message.topic_id if message else None,
            "inferer": message.inferer if message else None,
        }
        url = self.base_url + f"/emissions/v9/native_inferer_network_regret"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetNaiveInfererNetworkRegretResponse().from_json(response.text)

    def get_one_out_inferer_inferer_network_regret(self, message: emissions_v9_GetOneOutInfererInfererNetworkRegretRequest | None = None) -> emissions_v9_GetOneOutInfererInfererNetworkRegretResponse:
        params = {
            "topic_id": message.topic_id if message else None,
            "one_out_inferer": message.one_out_inferer if message else None,
            "inferer": message.inferer if message else None,
        }
        url = self.base_url + f"/emissions/v9/one_out_inferer_inferer_network_regret"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetOneOutInfererInfererNetworkRegretResponse().from_json(response.text)

    def get_one_out_inferer_forecaster_network_regret(self, message: emissions_v9_GetOneOutInfererForecasterNetworkRegretRequest | None = None) -> emissions_v9_GetOneOutInfererForecasterNetworkRegretResponse:
        params = {
            "topic_id": message.topic_id if message else None,
            "forecaster": message.forecaster if message else None,
            "one_out_inferer": message.one_out_inferer if message else None,
        }
        url = self.base_url + f"/emissions/v9/one_out_inferer_forecaster_network_regret"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetOneOutInfererForecasterNetworkRegretResponse().from_json(response.text)

    def get_one_out_forecaster_inferer_network_regret(self, message: emissions_v9_GetOneOutForecasterInfererNetworkRegretRequest | None = None) -> emissions_v9_GetOneOutForecasterInfererNetworkRegretResponse:
        params = {
            "topic_id": message.topic_id if message else None,
            "inferer": message.inferer if message else None,
            "one_out_forecaster": message.one_out_forecaster if message else None,
        }
        url = self.base_url + f"/emissions/v9/one_out_forecaster_inferer_network_regret"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetOneOutForecasterInfererNetworkRegretResponse().from_json(response.text)

    def get_one_out_forecaster_forecaster_network_regret(self, message: emissions_v9_GetOneOutForecasterForecasterNetworkRegretRequest | None = None) -> emissions_v9_GetOneOutForecasterForecasterNetworkRegretResponse:
        params = {
            "topic_id": message.topic_id if message else None,
            "forecaster": message.forecaster if message else None,
            "one_out_forecaster": message.one_out_forecaster if message else None,
        }
        url = self.base_url + f"/emissions/v9/one_out_forecaster_forecaster_network_regret"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetOneOutForecasterForecasterNetworkRegretResponse().from_json(response.text)

    def get_active_topics_at_block(self, message: emissions_v9_GetActiveTopicsAtBlockRequest) -> emissions_v9_GetActiveTopicsAtBlockResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/active_topics_at_block/{message.block_height}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetActiveTopicsAtBlockResponse().from_json(response.text)

    def get_next_churning_block_by_topic_id(self, message: emissions_v9_GetNextChurningBlockByTopicIdRequest) -> emissions_v9_GetNextChurningBlockByTopicIdResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/next_churning_block_by_topic_id/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetNextChurningBlockByTopicIdResponse().from_json(response.text)

    def get_count_inferer_inclusions_in_topic(self, message: emissions_v9_GetCountInfererInclusionsInTopicRequest) -> emissions_v9_GetCountInfererInclusionsInTopicResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/count_inferer_inclusions_in_topic/{message.topic_id}/{message.inferer}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetCountInfererInclusionsInTopicResponse().from_json(response.text)

    def get_count_forecaster_inclusions_in_topic(self, message: emissions_v9_GetCountForecasterInclusionsInTopicRequest) -> emissions_v9_GetCountForecasterInclusionsInTopicResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/count_forecaster_inclusions_in_topic/{message.topic_id}/{message.forecaster}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetCountForecasterInclusionsInTopicResponse().from_json(response.text)

    def get_active_reputers_for_topic(self, message: emissions_v9_GetActiveReputersForTopicRequest) -> emissions_v9_GetActiveReputersForTopicResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/active_reputers/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetActiveReputersForTopicResponse().from_json(response.text)

    def get_active_forecasters_for_topic(self, message: emissions_v9_GetActiveForecastersForTopicRequest) -> emissions_v9_GetActiveForecastersForTopicResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/active_forecasters/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetActiveForecastersForTopicResponse().from_json(response.text)

    def get_active_inferers_for_topic(self, message: emissions_v9_GetActiveInferersForTopicRequest) -> emissions_v9_GetActiveInferersForTopicResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/active_inferers/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetActiveInferersForTopicResponse().from_json(response.text)

    def is_whitelisted_global_worker(self, message: emissions_v9_IsWhitelistedGlobalWorkerRequest) -> emissions_v9_IsWhitelistedGlobalWorkerResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/is_whitelisted_global_worker/{message.address}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_IsWhitelistedGlobalWorkerResponse().from_json(response.text)

    def is_whitelisted_global_reputer(self, message: emissions_v9_IsWhitelistedGlobalReputerRequest) -> emissions_v9_IsWhitelistedGlobalReputerResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/is_whitelisted_global_reputer/{message.address}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_IsWhitelistedGlobalReputerResponse().from_json(response.text)

    def is_whitelisted_global_admin(self, message: emissions_v9_IsWhitelistedGlobalAdminRequest) -> emissions_v9_IsWhitelistedGlobalAdminResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/is_whitelisted_global_admin/{message.address}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_IsWhitelistedGlobalAdminResponse().from_json(response.text)

    def is_topic_worker_whitelist_enabled(self, message: emissions_v9_IsTopicWorkerWhitelistEnabledRequest) -> emissions_v9_IsTopicWorkerWhitelistEnabledResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/is_topic_worker_whitelist_enabled/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_IsTopicWorkerWhitelistEnabledResponse().from_json(response.text)

    def is_topic_reputer_whitelist_enabled(self, message: emissions_v9_IsTopicReputerWhitelistEnabledRequest) -> emissions_v9_IsTopicReputerWhitelistEnabledResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/is_topic_reputer_whitelist_enabled/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_IsTopicReputerWhitelistEnabledResponse().from_json(response.text)

    def is_whitelisted_topic_creator(self, message: emissions_v9_IsWhitelistedTopicCreatorRequest) -> emissions_v9_IsWhitelistedTopicCreatorResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/is_whitelisted_topic_creator/{message.address}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_IsWhitelistedTopicCreatorResponse().from_json(response.text)

    def is_whitelisted_global_actor(self, message: emissions_v9_IsWhitelistedGlobalActorRequest) -> emissions_v9_IsWhitelistedGlobalActorResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/is_whitelisted_global_actor/{message.address}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_IsWhitelistedGlobalActorResponse().from_json(response.text)

    def is_whitelisted_topic_worker(self, message: emissions_v9_IsWhitelistedTopicWorkerRequest) -> emissions_v9_IsWhitelistedTopicWorkerResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/is_whitelisted_topic_worker/{message.topic_id}/{message.address}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_IsWhitelistedTopicWorkerResponse().from_json(response.text)

    def is_whitelisted_topic_reputer(self, message: emissions_v9_IsWhitelistedTopicReputerRequest) -> emissions_v9_IsWhitelistedTopicReputerResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/is_whitelisted_topic_reputer/{message.topic_id}/{message.address}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_IsWhitelistedTopicReputerResponse().from_json(response.text)

    def can_update_all_global_whitelists(self, message: emissions_v9_CanUpdateAllGlobalWhitelistsRequest) -> emissions_v9_CanUpdateAllGlobalWhitelistsResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/can_update_all_global_whitelists/{message.address}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_CanUpdateAllGlobalWhitelistsResponse().from_json(response.text)

    def can_update_global_worker_whitelist(self, message: emissions_v9_CanUpdateGlobalWorkerWhitelistRequest) -> emissions_v9_CanUpdateGlobalWorkerWhitelistResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/can_update_global_worker_whitelist/{message.address}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_CanUpdateGlobalWorkerWhitelistResponse().from_json(response.text)

    def can_update_global_reputer_whitelist(self, message: emissions_v9_CanUpdateGlobalReputerWhitelistRequest) -> emissions_v9_CanUpdateGlobalReputerWhitelistResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/can_update_global_reputer_whitelist/{message.address}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_CanUpdateGlobalReputerWhitelistResponse().from_json(response.text)

    def can_update_params(self, message: emissions_v9_CanUpdateParamsRequest) -> emissions_v9_CanUpdateParamsResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/can_update_params/{message.address}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_CanUpdateParamsResponse().from_json(response.text)

    def can_update_topic_whitelist(self, message: emissions_v9_CanUpdateTopicWhitelistRequest) -> emissions_v9_CanUpdateTopicWhitelistResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/can_update_topic_whitelist/{message.topic_id}/{message.address}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_CanUpdateTopicWhitelistResponse().from_json(response.text)

    def can_create_topic(self, message: emissions_v9_CanCreateTopicRequest) -> emissions_v9_CanCreateTopicResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/can_create_topic/{message.address}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_CanCreateTopicResponse().from_json(response.text)

    def can_submit_worker_payload(self, message: emissions_v9_CanSubmitWorkerPayloadRequest) -> emissions_v9_CanSubmitWorkerPayloadResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/can_submit_worker_payload/{message.topic_id}/{message.address}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_CanSubmitWorkerPayloadResponse().from_json(response.text)

    def can_submit_reputer_payload(self, message: emissions_v9_CanSubmitReputerPayloadRequest) -> emissions_v9_CanSubmitReputerPayloadResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/can_submit_reputer_payload/{message.topic_id}/{message.address}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_CanSubmitReputerPayloadResponse().from_json(response.text)

    def get_topic_initial_inferer_ema_score(self, message: emissions_v9_GetTopicInitialInfererEmaScoreRequest) -> emissions_v9_GetTopicInitialInfererEmaScoreResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/initial_inferer_ema_score/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetTopicInitialInfererEmaScoreResponse().from_json(response.text)

    def get_topic_initial_forecaster_ema_score(self, message: emissions_v9_GetTopicInitialForecasterEmaScoreRequest) -> emissions_v9_GetTopicInitialForecasterEmaScoreResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/initial_forecaster_ema_score/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetTopicInitialForecasterEmaScoreResponse().from_json(response.text)

    def get_topic_initial_reputer_ema_score(self, message: emissions_v9_GetTopicInitialReputerEmaScoreRequest) -> emissions_v9_GetTopicInitialReputerEmaScoreResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/initial_reputer_ema_score/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetTopicInitialReputerEmaScoreResponse().from_json(response.text)

    def get_latest_regret_std_norm(self, message: emissions_v9_GetLatestRegretStdNormRequest) -> emissions_v9_GetLatestRegretStdNormResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/latest_regret_stdnorm/{message.topic_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetLatestRegretStdNormResponse().from_json(response.text)

    def get_latest_inferer_weight(self, message: emissions_v9_GetLatestInfererWeightRequest) -> emissions_v9_GetLatestInfererWeightResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/latest_inferer_weight/{message.topic_id}/{message.actor_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetLatestInfererWeightResponse().from_json(response.text)

    def get_latest_forecaster_weight(self, message: emissions_v9_GetLatestForecasterWeightRequest) -> emissions_v9_GetLatestForecasterWeightResponse:
        params = {}
        url = self.base_url + f"/emissions/v9/latest_forecaster_weight/{message.topic_id}/{message.actor_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return emissions_v9_GetLatestForecasterWeightResponse().from_json(response.text)
