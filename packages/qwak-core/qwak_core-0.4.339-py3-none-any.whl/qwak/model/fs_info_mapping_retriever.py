from typing import Dict, List

from qwak.clients.administration.eco_system.eco_system_utils import EcosystemUtils
from qwak.clients.feature_store import FeatureRegistryClient
from qwak.feature_store._common.feature_set_utils import (
    FeatureSetInfo,
    get_env_to_featuresets_mapping,
    get_feature_set_info,
)
from qwak.model.schema_entities import BaseFeature, FeatureStoreInput
from qwak.model.utils.feature_utils import extract_env_name, extract_featureset_name


def retrieve_fs_mapping(
    features: List[BaseFeature],
) -> Dict[str, Dict[str, FeatureSetInfo]]:
    """
    Retrieve the feature set info mapping.
    If one of the features is a FeatureStoreInput and is in a different environment from the current one, populate it using a single API call.
    Otherwise, retrieve each feature set info individually.
    The reasoning behind this logic is that if all required features are in the same environment, it's more efficient to retrieve only the necessary feature set, rather than all feature sets.
    * Assuming the feature name is fully qualified with the environment name
    :param features:
    :return: dict of environment name to dict of feature set name to FeatureSetInfo
    """
    current_env_name = EcosystemUtils().get_current_environment_name()
    features_manager_client = FeatureRegistryClient()

    if any(
        [
            feature
            for feature in features
            if isinstance(feature, FeatureStoreInput)
            and extract_env_name(feature.name) != current_env_name
        ]
    ):
        return get_env_to_featuresets_mapping(features_manager_client)
    else:
        return _retrieve_fs_info_one_by_one(
            features_manager_client, current_env_name, features
        )


def _retrieve_fs_info_one_by_one(
    features_manager_client: FeatureRegistryClient,
    current_env_name: str,
    features: List[BaseFeature],
) -> Dict[str, Dict[str, FeatureSetInfo]]:
    fs_info_cache: Dict[str, FeatureSetInfo] = dict()

    for feature in features:
        if isinstance(feature, FeatureStoreInput):
            feature_set_name = extract_featureset_name(feature.name).lower()
            if feature_set_name not in fs_info_cache:
                fs_info_cache[feature_set_name] = get_feature_set_info(
                    features_manager_client, feature_set_name
                )
    return {current_env_name: fs_info_cache}
