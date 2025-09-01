import uuid
from typing import Dict, Optional

import grpc
from _qwak_proto.qwak.feature_store.features.feature_set_pb2 import (
    DeployedModelInUseLink,
    FeatureSet,
    FeatureSetDefinition,
    FeaturesetInfo,
    FeatureSetList,
    FeatureSetMetadata,
    FeaturesetSchedulingState,
    FeatureSetSpec,
    FeatureStatus,
)
from _qwak_proto.qwak.feature_store.features.feature_set_service_pb2 import (
    DeleteFeatureSetResponse,
    DeleteFeaturesetVersionResponse,
    GetEnvToFeatureSetsMappingResponse,
    GetFeatureSetByNameResponse,
    GetFeaturesetSchedulingStateResponse,
    ListFeatureSetsResponse,
    ListFeaturesetVersionsByNameResponse,
    RegisterFeatureSetResponse,
    SetActiveFeaturesetVersionResponse,
    UpdateFeatureSetResponse,
)
from _qwak_proto.qwak.feature_store.features.feature_set_service_pb2_grpc import (
    FeatureSetServiceServicer,
)

CURRENT_ENV_NAME = "env_name"


class FeatureSetServiceMock(FeatureSetServiceServicer):
    def __init__(self):
        self._features_spec: Dict[str, FeatureSetSpec] = {}
        self._fs_next_versions: Dict[str, int] = {}
        self._fs_versions_by_name: Dict[str, Dict[int, FeatureSetDefinition]] = {}
        self._fs_definition_by_id: Dict[str, FeatureSetDefinition] = {}
        # this mapping is used to test the GetEnvToFeatureSetsMapping API. Note that the populated features sets may not be aligned with the self._features_spec featuresets
        self._env_to_features_spec = (
            {}
        )  # env_name -> {featureset_name -> featureset_definition}

    def reset_features(self):
        self._features_spec.clear()
        self._fs_next_versions.clear()
        self._fs_versions_by_name.clear()
        self._fs_definition_by_id.clear()
        self._env_to_features_spec.clear()

    def setup_empty_env(self, env_name):
        self._env_to_features_spec[env_name] = {}

    def register_featureset_to_env_to_features_map(
        self, env_name, featureset_spec: FeatureSetSpec
    ):
        fs_id = str(uuid.uuid4())
        self._env_to_features_spec[env_name] = self._env_to_features_spec.get(
            env_name, {}
        )
        feature_set_definition = FeatureSetDefinition(
            feature_set_id=fs_id,
            feature_set_spec=featureset_spec,
            status=FeatureStatus.VALID,
        )
        self._env_to_features_spec[env_name][
            featureset_spec.name
        ] = feature_set_definition

    def RegisterFeatureSet(self, request, context):
        fs_id = str(uuid.uuid4())
        curr_version = 1
        featureset_definition: FeatureSetDefinition = FeatureSetDefinition(
            feature_set_id=fs_id,
            feature_set_spec=request.feature_set_spec,
            featureset_version_number=curr_version,
            status=FeatureStatus.VALID,
        )
        self._features_spec[fs_id] = featureset_definition.feature_set_spec
        self._fs_definition_by_id[fs_id] = featureset_definition
        self._fs_versions_by_name[featureset_definition.feature_set_spec.name] = {
            curr_version: featureset_definition
        }
        self._fs_next_versions[featureset_definition.feature_set_spec.name] = (
            curr_version + 1
        )

        return RegisterFeatureSetResponse(
            feature_set=FeatureSet(feature_set_definition=featureset_definition)
        )

    def UpdateFeatureSet(self, request, context):
        fs_id: str = request.feature_set_id
        if fs_id in self._fs_definition_by_id:
            curr_version = self._fs_next_versions[request.feature_set_spec.name]
            featureset_definition: FeatureSetDefinition = FeatureSetDefinition(
                feature_set_id=fs_id,
                feature_set_spec=request.feature_set_spec,
                featureset_version_number=curr_version,
                status=FeatureStatus.VALID,
            )
            self._fs_definition_by_id[fs_id] = featureset_definition
            self._features_spec[fs_id] = featureset_definition.feature_set_spec
            self._fs_next_versions[featureset_definition.feature_set_spec.name] = (
                curr_version + 1
            )

            curr_versions = self._fs_versions_by_name[request.feature_set_spec.name]
            curr_versions[curr_version] = featureset_definition
            self._fs_versions_by_name[
                featureset_definition.feature_set_spec.name
            ] = curr_versions

            return UpdateFeatureSetResponse(
                feature_set=FeatureSet(feature_set_definition=featureset_definition)
            )

        context.set_details(f"Feature set ID {request.feature_set_id} doesn't exist'")
        context.set_code(grpc.StatusCode.NOT_FOUND)

    def DeleteFeatureSet(self, request, context):
        fs_definition: Optional[FeatureSetDefinition] = self._fs_definition_by_id.get(
            request.feature_set_id, None
        )
        if fs_definition:
            self._features_spec.pop(request.feature_set_id)
            self._fs_definition_by_id.pop(request.feature_set_id)
            self._fs_versions_by_name.pop(fs_definition.feature_set_spec.name)
            self._fs_next_versions.pop(fs_definition.feature_set_spec.name)
            return DeleteFeatureSetResponse()

        context.set_details(f"Feature set ID {request.feature_set_id} doesn't exist'")
        context.set_code(grpc.StatusCode.NOT_FOUND)

    def GetFeatureSetByName(self, request, context):
        feature_sets = [
            (fs_id, fs_definition)
            for (fs_id, fs_definition) in self._fs_definition_by_id.items()
            if fs_definition.feature_set_spec.name == request.feature_set_name
        ]
        if feature_sets:
            fs_id, fs_definition = feature_sets[0]
            return GetFeatureSetByNameResponse(
                feature_set=FeatureSet(
                    feature_set_definition=fs_definition,
                    metadata=FeatureSetMetadata(),
                    deployed_models_in_use_link=[DeployedModelInUseLink()],
                )
            )

        context.set_details(
            f"Feature set named {request.feature_set_name} doesn't exist'"
        )
        context.set_code(grpc.StatusCode.NOT_FOUND)

    def ListFeatureSets(self, request, context):
        return ListFeatureSetsResponse(
            feature_families=[
                FeatureSet(
                    feature_set_definition=fs_definition,
                    metadata=FeatureSetMetadata(),
                    deployed_models_in_use_link=[DeployedModelInUseLink()],
                )
                for fs_definition in self._fs_definition_by_id.values()
            ]
        )

    def GetFeaturesetSchedulingState(self, request, context):
        return GetFeaturesetSchedulingStateResponse(
            state=FeaturesetSchedulingState.SCHEDULING_STATE_ENABLED
        )

    def GetEnvToFeatureSetsMapping(self, request, context):
        env_to_featuresets_mapping = {}

        for env_name, featureset_df_dict in self._env_to_features_spec.items():
            env_to_featuresets_mapping[env_name] = FeatureSetList(
                feature_sets=[
                    FeatureSet(
                        feature_set_definition=fs_definition,
                        metadata=FeatureSetMetadata(),
                        deployed_models_in_use_link=[DeployedModelInUseLink()],
                    )
                    for fs_name, fs_definition in featureset_df_dict.items()
                ]
            )

        return GetEnvToFeatureSetsMappingResponse(
            env_to_feature_set_mapping=env_to_featuresets_mapping
        )

    def DeleteFeaturesetVersion(self, request, context):
        version_number = request.featureset_version_number
        version_definitions: Optional[
            Dict[int, FeatureSetDefinition]
        ] = self._fs_versions_by_name.get(request.featureset_name, None)
        if version_definitions:
            version_definition = version_definitions.get(version_number, None)
            if version_definition:
                if (
                    self._fs_definition_by_id[
                        version_definition.feature_set_id
                    ].featureset_version_number
                    != version_number
                ):
                    version_definitions.pop(version_number)
                    return DeleteFeaturesetVersionResponse()
                else:
                    context.set_details("Active version cant be deleted")
                    context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            else:
                context.set_details(
                    f"Version {version_number} not found for Feature set name {request.featureset_name}"
                )
                context.set_code(grpc.StatusCode.NOT_FOUND)
        else:
            context.set_details(
                f"Feature set name {request.featureset_name} doesn't exist'"
            )
            context.set_code(grpc.StatusCode.NOT_FOUND)

    def SetActiveFeaturesetVersion(self, request, context):
        version_definitions: Optional[
            Dict[int, FeatureSetDefinition]
        ] = self._fs_versions_by_name.get(request.featureset_name, None)
        if version_definitions:
            version_definition = version_definitions.get(
                request.featureset_version_number, None
            )
            if version_definition:
                self._fs_definition_by_id[
                    version_definition.feature_set_id
                ] = version_definition
                return SetActiveFeaturesetVersionResponse()
            else:
                context.set_details(
                    f"Version {request.featureset_version_number} not found for Feature set name {request.featureset_name}"
                )
                context.set_code(grpc.StatusCode.NOT_FOUND)
        else:
            context.set_details(
                f"Feature set name {request.featureset_name} doesn't exist'"
            )
            context.set_code(grpc.StatusCode.NOT_FOUND)

    def ListFeaturesetVersionsByName(self, request, context):
        versions: Optional[
            Dict[int, FeatureSetDefinition]
        ] = self._fs_versions_by_name.get(request.featureset_name, None)
        if versions:
            return ListFeaturesetVersionsByNameResponse(
                featuresets=[
                    FeaturesetInfo(
                        featureset_definition=feature_definition,
                        metadata=FeatureSetMetadata(),
                    )
                    for feature_definition in self._fs_versions_by_name[
                        request.featureset_name
                    ].values()
                ]
            )

        context.set_details(
            f"Feature set name {request.featureset_name} doesn't exist'"
        )
        context.set_code(grpc.StatusCode.NOT_FOUND)
