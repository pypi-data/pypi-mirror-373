import importlib

from qwak.inner.build_logic.interface.step_inteface import Step
from qwak import __version__ as qwak_core_version


class SetVersionStep(Step):
    STEP_DESCRIPTION = "Getting SDK Version"
    SDK_VERSION_NOT_AVAILABLE_MSG_FORMAT = (
        "Sdk version not available, using core version {qwak_core_version}"
    )
    SDK_VERSION_FOUND_MSG_FORMAT = "Found sdk version {qwak_sdk_version}"

    def description(self) -> str:
        return self.STEP_DESCRIPTION

    def execute(self) -> None:
        try:
            self.build_logger.debug("Getting sdk version")
            qwak_sdk_version = importlib.import_module("qwak_sdk").__version__
            self.context.qwak_sdk_version = qwak_sdk_version
            self.build_logger.debug(
                self.SDK_VERSION_FOUND_MSG_FORMAT.format(
                    qwak_sdk_version=qwak_sdk_version
                )
            )
        except ImportError:
            self.build_logger.debug(
                self.SDK_VERSION_NOT_AVAILABLE_MSG_FORMAT.format(
                    qwak_core_version=qwak_core_version
                )
            )
            self.context.qwak_sdk_version = qwak_core_version
