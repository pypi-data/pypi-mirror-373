from __future__ import annotations

import re
from pathlib import Path
from typing import Any, List, Tuple, Union, Optional

import joblib
import requests
from retrying import retry

from _qwak_proto.qwak.builds.build_url_pb2 import BuildVersioningTagsType
from _qwak_proto.qwak.builds.builds_orchestrator_service_pb2 import (
    GetBuildVersioningUploadURLResponse,
)
from qwak.exceptions import QwakException
from qwak.exceptions import QwakGeneralBuildException
from qwak.inner.build_logic.constants.temp_dir import TEMP_LOCAL_MODEL_DIR
from qwak.inner.build_logic.constants.upload_tag import (
    MODEL_CODE_TAG,
    SKINNY_MODEL_CODE_TAG,
    QWAK_SDK_VERSION_TAG,
    BUILD_CONFIG_TAG,
    QWAK_RUNTIME_WHEEL_TAG,
    QWAK_CORE_WHEEL_TAG,
    QWAK_BUILT_MODEL_TAG,
)
from qwak.inner.build_logic.interface.step_inteface import Step
from qwak.inner.build_logic.tools.files import (
    QWAK_IGNORE_FILE_NAME,
    IGNORED_PATTERNS_FOR_UPLOAD,
    zip_model,
    UploadInChunks,
)
from qwak.inner.build_logic.tools.ignore_files import load_patterns_from_ignore_file

_MAX_FILE_SIZE_BYTES = 10000000


def should_retry(qwak_exception: QwakException):
    # when Got 403 from Jfrog it means that the reposity doesn't exist. It may happen when in the first build in the project
    return str(qwak_exception.message).__contains__("403")


class UploadStep(Step):
    STEP_DESCRIPTION = "Saving Qwak Model"

    def description(self) -> str:
        return self.STEP_DESCRIPTION

    def execute(self) -> None:
        files_tag_iterator = self.create_files_to_upload()
        files_total_size = sum(
            file.stat().st_size for (file, tag) in files_tag_iterator
        )
        upload_so_far = 0
        for file, tag in files_tag_iterator:
            if file.exists():
                pre_signed_url = self.upload_file(
                    file=file,
                    tag=tag,
                    all_files_size_to_upload=files_total_size,
                    read_so_far=upload_so_far,
                )
                upload_so_far += file.stat().st_size

                if tag == MODEL_CODE_TAG:
                    self.context.model_code_remote_url = str(pre_signed_url).split("?")[
                        0
                    ]

    def create_files_to_upload(self) -> Union[List[Tuple[Any, Any], Tuple[Path, Any]]]:
        ignored_patterns = (
            load_patterns_from_ignore_file(
                build_logger=self.build_logger,
                ignore_file_path=self.context.host_temp_local_build_dir
                / TEMP_LOCAL_MODEL_DIR
                / self.config.build_properties.model_uri.main_dir
                / QWAK_IGNORE_FILE_NAME,
            )
            + IGNORED_PATTERNS_FOR_UPLOAD
        )

        # copy 'main' and 'tests' directories
        dirs_to_include = [self.config.build_properties.model_uri.main_dir, "tests"]
        deps_folders = []
        for (
            folder
        ) in self.config.build_properties.model_uri.dependency_required_folders:
            destination_folder = folder
            while destination_folder.startswith(".."):
                destination_folder = re.sub(r"^\.\./", "", destination_folder)
            deps_folders.append(destination_folder)
        if deps_folders:
            self.build_logger.debug(
                f"Adding dependency folders to model code: {deps_folders}"
            )
            dirs_to_include += deps_folders

        self.build_logger.debug("Zipping skinny model code")
        skinny_size_zip_file = zip_model(
            build_dir=self.context.host_temp_local_build_dir,
            dependency_file=self.context.model_relative_dependency_file,
            deps_lock_file=self.context.model_relative_dependency_lock_file,
            dirs_to_include=dirs_to_include,
            zip_name="skinny_size_model_code",
            ignored_patterns=ignored_patterns,
            max_bytes=_MAX_FILE_SIZE_BYTES,
        )

        # Full size model
        self.build_logger.debug("Zipping full model code")
        full_size_zip_file = zip_model(
            build_dir=self.context.host_temp_local_build_dir,
            dependency_file=self.context.model_relative_dependency_file,
            deps_lock_file=self.context.model_relative_dependency_lock_file,
            dirs_to_include=dirs_to_include,
            zip_name="full_size_model_code",
            ignored_patterns=ignored_patterns,
        )

        # Dump config file for upload
        config_file_temp = self.context.host_temp_local_build_dir / "build.conf"
        config_file_temp.write_text(self.config.to_yaml())

        # Dump qwak-sdk version for upload
        qwak_sdk_version_temp = self.context.host_temp_local_build_dir / "VERSION"
        qwak_sdk_version_temp.write_text(self.context.qwak_sdk_version)

        files_tag_iterator = [
            (full_size_zip_file, MODEL_CODE_TAG),
            (skinny_size_zip_file, SKINNY_MODEL_CODE_TAG),
            (qwak_sdk_version_temp, QWAK_SDK_VERSION_TAG),
            (config_file_temp, BUILD_CONFIG_TAG),
        ]

        if self.context.custom_runtime_wheel:
            files_tag_iterator.append(
                (self.context.custom_runtime_wheel, QWAK_RUNTIME_WHEEL_TAG)
            )

        if self.context.custom_core_wheel:
            files_tag_iterator.append(
                (self.context.custom_core_wheel, QWAK_CORE_WHEEL_TAG)
            )

        if self.config.pre_built_model:
            temp_model_file = (
                self.context.host_temp_local_build_dir / QWAK_BUILT_MODEL_TAG
            )
            joblib.dump(self.config.pre_built_model, temp_model_file, compress=3)
            files_tag_iterator.append((temp_model_file, QWAK_BUILT_MODEL_TAG))

        return files_tag_iterator

    def upload_file(
        self, file: Path, tag: str, all_files_size_to_upload: int, read_so_far: int
    ):
        self.build_logger.debug(f"Upload file {file}")

        pre_signed_url_response: GetBuildVersioningUploadURLResponse = (
            self.get_pre_signed_upload_url(
                tag=tag, tag_type=BuildVersioningTagsType.FILE_TAG_TYPE
            )
        )
        self.upload_file_to_remote_storge(
            upload_url=pre_signed_url_response.upload_url,
            file=file,
            all_files_size_to_upload=all_files_size_to_upload,
            read_so_far=read_so_far,
            headers=pre_signed_url_response.headers,
        )

        self.build_logger.debug(f"Upload file {file} completed")

        return pre_signed_url_response.upload_url

    def get_pre_signed_upload_url(
        self, tag: str, tag_type: Optional[BuildVersioningTagsType]
    ) -> GetBuildVersioningUploadURLResponse:
        try:
            self.build_logger.debug(f"Getting pre-signed url for upload - tag {tag}")

            pre_signed_url_response: GetBuildVersioningUploadURLResponse = (
                self.context.client_builds_orchestrator.get_build_versioning_upload_url(
                    build_id=self.context.build_id,
                    model_id=self.context.model_id,
                    tag=tag,
                    tag_type=tag_type,
                )
            )

            self.build_logger.debug("Pre-signed url generated successfully")

            return pre_signed_url_response
        except QwakException as e:
            raise QwakGeneralBuildException(
                message="Unable to get pre-signed url for uploading model",
                src_exception=e,
            )

    def upload_file_to_remote_storge(
        self,
        upload_url: str,
        file: Path,
        all_files_size_to_upload: int,
        read_so_far: int,
        headers: Optional[dict] = None,
    ):
        if not headers:
            headers = {}

        try:
            self.build_logger.debug(f"Upload file {file} to Qwak storage")

            self.send_request(
                upload_url, file, all_files_size_to_upload, read_so_far, headers
            )
            self.build_logger.debug(
                f"File {file} uploaded to Qwak storage successfully"
            )
        except Exception as e:
            raise QwakGeneralBuildException(
                message="Fail uploading model to remote storage.",
                src_exception=e,
            )

    @retry(retry_on_exception=should_retry, wait_fixed=15000, stop_max_delay=60000)
    def send_request(
        self,
        upload_url: str,
        file: Path,
        all_files_size_to_upload: int,
        read_so_far: int,
        headers: Optional[dict],
    ):
        if not headers:
            headers = {}

        # Adding to the current headers the content-type
        headers["content-type"] = "text/plain"

        http_response = requests.put(  # nosec B113
            url=upload_url,
            data=UploadInChunks(
                file=file,
                build_logger=self.build_logger,
                chunk_size_bytes=10,
                all_files_size_to_upload=all_files_size_to_upload,
                read_so_far=read_so_far,
            ),
            headers=headers,
        )

        if http_response.status_code not in [200, 201]:
            raise QwakException(
                f"Status: [{http_response.status_code}], "
                f"reason: [{http_response.reason}]"
            )
