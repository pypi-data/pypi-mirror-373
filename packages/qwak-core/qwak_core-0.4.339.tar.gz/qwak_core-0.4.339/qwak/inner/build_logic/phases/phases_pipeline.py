from typing import List, Optional

from qwak.inner.build_config.build_config_v1 import BuildConfigV1
from ..interface.build_phase import BuildPhase
from ..interface.context_interface import Context

from qwak.inner.build_logic.interface.step_inteface import Step


class PhasesPipeline:
    def __init__(
        self,
        config: Optional[BuildConfigV1],
        context: Context,
        build_phase: Optional[BuildPhase] = None,
    ) -> None:
        self._phases: List[PhasesPipeline] = []
        self._steps: List[Step] = []
        self.context = context
        self._config = config
        self.build_phase = build_phase

    @property
    def phases(self) -> List["PhasesPipeline"]:
        return self._phases

    @property
    def steps(self) -> List[Step]:
        return self._steps

    def add_phase(self, steps: List[Step], build_phase: BuildPhase):
        phase = PhasesPipeline(
            config=self._config,
            context=self.context,
            build_phase=build_phase,
        )

        for step in steps:
            step.context = self.context
            step.config = self._config
            step.build_phase = build_phase
            phase._steps.append(step)

        self._phases.append(phase)
