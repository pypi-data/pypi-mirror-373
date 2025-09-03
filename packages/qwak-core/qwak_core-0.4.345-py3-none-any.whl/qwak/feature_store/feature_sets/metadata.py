from dataclasses import dataclass

from _qwak_proto.qwak.feature_store.features.feature_set_pb2 import (
    FeatureSetUserMetadata as ProtoMetadata,
    FeaturesetVersionUserMetadata as ProtoFeaturesetVersionUserMetadata,
)

_METADATA_ATTRIBUTE = "_qwak_metadata"


def set_metadata_on_function(
    function,
    owner: str = "",
    description: str = "",
    display_name: str = "",
    version_comment="",
):
    setattr(
        function,
        _METADATA_ATTRIBUTE,
        Metadata(
            owner=owner,
            description=description,
            display_name=display_name,
            version_comment=version_comment,
        ),
    )


def get_metadata_from_function(
    function,
    owner: str = "",
    description: str = "",
    display_name: str = "",
    version_comment="",
):
    return getattr(
        function,
        _METADATA_ATTRIBUTE,
        Metadata(
            owner=owner,
            description=description,
            display_name=display_name,
            version_comment=version_comment,
        ),
    )


@dataclass
class Metadata:
    owner: str = ""
    description: str = ""
    display_name: str = ""
    version_comment: str = ""

    @staticmethod
    def from_proto(metadata: ProtoMetadata):
        return Metadata(
            owner=metadata.owner,
            description=metadata.description,
            display_name=metadata.display_name,
            version_comment=metadata.featureset_version_user_metadata.comment,
        )

    def to_proto(self):
        return ProtoMetadata(
            owner=self.owner,
            description=self.description,
            display_name=self.display_name,
            featureset_version_user_metadata=ProtoFeaturesetVersionUserMetadata(
                comment=self.version_comment
            ),
        )
