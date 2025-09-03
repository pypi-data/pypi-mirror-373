from dataclasses import dataclass, field
from typing import List

from _qwak_proto.qwak.models.models_pb2 import ModelMetadata as ModelMetadataProto

from qwak.qwak_client.builds.build import Build
from qwak.qwak_client.deployments.deployment import Deployment, EnvironmentAudienceRoute
from qwak.qwak_client.models.model import Model


@dataclass
class ModelMetadata:
    model: Model = field(default=None)
    deployments: List[Deployment] = field(default_factory=list)
    audience_routes: List[EnvironmentAudienceRoute] = field(default_factory=list)
    deployed_builds: List[Build] = field(default_factory=list)

    @staticmethod
    def from_proto(proto: ModelMetadataProto):
        return ModelMetadata(
            model=Model.from_proto(proto.model),
            deployments=[Deployment.from_proto(d) for d in proto.deployment_details],
            audience_routes=[
                EnvironmentAudienceRoute.from_proto(env_id, route)
                for env_id, env in proto.audience_routes_grouped_by_environment.items()
                for route in env.audience_routes
            ],
            deployed_builds=[Build.from_builds_management(b) for b in proto.build],
        )
