import dataclasses
from typing import List, cast

from qwak.clients.administration.eco_system.eco_system_utils import EcosystemUtils
from qwak.exceptions import QwakException
from qwak.model.schema_entities import BaseFeature, FeatureStoreInput


def validate_and_sanitize_feature_name(feature_name: str, current_env_name: str) -> str:
    qualifiers = feature_name.split(".")
    if len(qualifiers) <= 1:
        raise QwakException(
            f"Feature name '{feature_name}' must adhere to the <featureset_name>.<feature_name> or <env_name>.<featureset_name>.<feature_name> convention"
        )
    elif len(qualifiers) == 2:  # env name is not included in the feature name
        feature_name = f"{current_env_name}.{feature_name}"
    return feature_name.lower()


def validate_and_sanitize_features_name(
    features: List[BaseFeature],
) -> List[BaseFeature]:
    """
    Verify that the features (from type FeatureStoreInput) names are valid and adhere to convention <featureset_name>.<feature_name> or <env_name>.<featureset_name>.<feature_name>
    Add the current env qualifier if env is missing and transform name to lowercase
    :param features:
    :return: sanitized features with lower case (to support case-insensitive) fully qualified feature names
    :exception QwakException: if the feature name does not adhere to the convention
    """
    ecosystem_utils = EcosystemUtils()
    current_env_name = ecosystem_utils.get_current_environment_name()
    return [
        (
            cast(
                FeatureStoreInput,
                dataclasses.replace(
                    feature,
                    name=validate_and_sanitize_feature_name(
                        feature.name, current_env_name
                    ),
                ),
            )
            if isinstance(feature, FeatureStoreInput)
            else feature
        )
        for feature in features
    ]


def extract_env_name(feature_name: str) -> str:
    """
    extracts env_name from featureset name
    assuming feature name is fully qualified (passed sanitization)
    :param feature_name:
    :return: env_name
    """
    qualifiers = feature_name.split(".")
    return ".".join(qualifiers[:-2])  # Everything except the last two parts


def extract_featureset_name(feature_name: str) -> str:
    qualifiers = feature_name.split(".")
    return qualifiers[-2]


def discard_env_from_name(
    feature_name: str,
) -> str:
    return ".".join(feature_name.split(".")[-2:])
