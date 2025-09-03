import os

from qwak.inner.build_logic.interface.step_inteface import Step
from qwak.inner.build_logic.tools.files import cleaning_up_after_build


class CleanupStep(Step):
    STEP_DESCRIPTION = "Clean build artifacts"

    def description(self) -> str:
        return self.STEP_DESCRIPTION

    def execute(self) -> None:
        self.build_logger.debug(
            "Cleanup environment - Deleting file and intermediate images"
        )
        if os.getenv("POD_NAME"):
            self.build_logger.debug("Skipping cleanup - Remote executor is temporary")
        else:
            cleaning_up_after_build(self)
