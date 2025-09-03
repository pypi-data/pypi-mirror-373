import contextlib
import os
import shutil
import uuid
from pathlib import Path

from qwak.inner.build_config.build_config_v1 import BuildConfigV1
from qwak.inner.build_logic.constants.host_resource import HOST_QWAK_HIDDEN_FOLDER
from qwak.inner.build_logic.execute_build_pipeline import execute_build_pipeline
from qwak.inner.build_logic.run_handlers.programmatic_phase_run_handler import (
    ProgrammaticPhaseRunHandler,
)
from qwak.inner.build_logic.trigger_build_context import TriggerBuildContext
from qwak.qwak_client.build_api_helpers.build_api_steps import (
    get_trigger_build_api_steps,
)
from qwak.qwak_client.build_api_helpers.messages import SUCCESS_MSG_API
from qwak.tools.logger import setup_qwak_logger, get_qwak_logger

BUILDS_LOGS = HOST_QWAK_HIDDEN_FOLDER / "logs" / "build"
BUILD_LOG_NAME = "build.log"
MAX_LOGS_NUMBER = 15
DEBUG_LEVEL = 2


@contextlib.contextmanager
def get_build_logger(config: BuildConfigV1, build_id: str):
    log_path = BUILDS_LOGS / config.build_properties.model_id / build_id
    log_path.mkdir(parents=True, exist_ok=True)
    try:
        (log_path / "build_config.yml").write_text(config.to_yaml())
        setup_qwak_logger(logs_folder=log_path, log_file_name=BUILD_LOG_NAME)
        yield get_qwak_logger()
    finally:
        # Cleanup - Save only x last zips
        logs_zip_sorted_by_data = sorted(
            BUILDS_LOGS.rglob("**/*"), key=os.path.getmtime
        )[:-MAX_LOGS_NUMBER]
        path: Path
        for path in logs_zip_sorted_by_data:
            if path.is_file():
                os.remove(path)
            elif path.is_dir():
                shutil.rmtree(path, ignore_errors=True)


def trigger_build_api(config: BuildConfigV1):
    build_id = str(uuid.uuid4())
    with get_build_logger(config=config, build_id=build_id) as logger:
        context = TriggerBuildContext()
        context.build_id = build_id
        pipeline = get_trigger_build_api_steps(config, context)
        build_runner = ProgrammaticPhaseRunHandler(
            logger, config.verbose, json_logs=False
        )
        execute_build_pipeline(pipeline, build_runner)
        logger.info(
            SUCCESS_MSG_API.format(
                build_id=build_id,
                model_id=context.model_id,
                project_uuid=context.project_uuid,
            )
        )

    return build_id
