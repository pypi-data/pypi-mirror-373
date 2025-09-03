from qwak.exceptions import QwakGeneralBuildException
from qwak.exceptions import QwakRemoteBuildFailedException
from qwak.inner.build_logic.interface.phase_run_handler import PhaseRunHandler
from qwak.inner.build_logic.interface.time_source import (
    SystemClockTimeSource,
    TimeSource,
    Stopwatch,
)
from qwak.inner.build_logic.phases.phases_pipeline import PhasesPipeline


def execute_build_pipeline(
    pipeline: PhasesPipeline,
    phase_run_handler: PhaseRunHandler,
):
    time_source = SystemClockTimeSource()
    for phase in pipeline.phases:
        with phase_run_handler.handle_current_phase(phase):
            phase_run(phase, phase_run_handler, time_source)


def phase_run(
    phase: PhasesPipeline,
    phase_run_handler: PhaseRunHandler,
    time_source: TimeSource,
):
    build_id = phase.context.build_id
    current_step_phase = None
    stop_watch = Stopwatch(time_source)
    try:
        for step in phase.steps:
            current_step_phase = step.build_phase
            step.set_logger(phase_run_handler.build_logger)
            phase_run_handler.handle_phase_in_progress(current_step_phase)

            step.execute()

        phase_duration = stop_watch.elapsed_time_in_seconds()
        phase_run_handler.handle_phase_finished_successfully(
            current_step_phase, phase_duration
        )
    except QwakGeneralBuildException as e:
        phase_duration = stop_watch.elapsed_time_in_seconds()
        phase_run_handler.handle_contact_support_error(
            build_id, current_step_phase, e, phase_duration
        )
    except QwakRemoteBuildFailedException as e:
        phase_duration = stop_watch.elapsed_time_in_seconds()
        phase_run_handler.handle_remote_build_error(
            build_id, current_step_phase, e, phase_duration
        )
    except KeyboardInterrupt:
        phase_duration = stop_watch.elapsed_time_in_seconds()
        phase_run_handler.handle_keyboard_interrupt(
            build_id, current_step_phase, phase_duration
        )
    except BaseException as e:
        phase_run_handler.build_logger.exception("Failed", e)
        phase_duration = stop_watch.elapsed_time_in_seconds()
        phase_run_handler.handle_pipeline_exception(
            build_id, current_step_phase, e, phase_duration
        )
