from copy import deepcopy

from _qwak_proto.qwak.builds.build_url_pb2 import BuildVersioningTagsType
from qwak.inner.build_logic.constants.upload_tag import (
    BUILD_CONFIG_TAG,
    QWAK_SDK_VERSION_TAG,
    MODEL_CODE_TAG,
)

from qwak.inner.build_logic.interface.step_inteface import Step


class StartRemoteBuildStep(Step):
    STEP_DESCRIPTION = "Start remote build"

    def description(self) -> str:
        return self.STEP_DESCRIPTION

    def execute(self) -> None:
        self.build_logger.info(f"Start remote build - {self.context.build_id}")
        config_copy = deepcopy(self.config)
        config_copy.build_properties.build_id = self.context.build_id
        config_copy.build_properties.build_name = self.context.build_name
        self.context.client_builds_orchestrator.build_model(
            build_conf=config_copy,
            build_v1_flag=False,
            build_config_url=self.get_download_url(BUILD_CONFIG_TAG),
            qwak_sdk_version_url=self.get_download_url(QWAK_SDK_VERSION_TAG),
            resolved_model_url=self.get_download_url(MODEL_CODE_TAG),
            git_commit_id=self.context.git_commit_id,
            sdk_version=self.context.qwak_sdk_version,
        )
        self.build_logger.info("Remote build started successfully")

    def get_download_url(self, tag: str) -> str:
        return (
            self.context.client_builds_orchestrator.get_build_versioning_download_url(
                model_id=self.config.build_properties.model_id,
                build_id=self.context.build_id,
                tag=tag,
                tag_type=BuildVersioningTagsType.FILE_TAG_TYPE,
            ).download_url
        )
