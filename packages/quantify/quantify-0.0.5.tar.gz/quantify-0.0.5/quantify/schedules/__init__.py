# Repository: https://gitlab.com/quantify-os/quantify
# Licensed according to the LICENSE file on the main branch
"""
Standard library of schedules for common experiments.

The module contains the classes:
    - :class:`.ScheduleBase`,
    - :class:`.Schedule`,
    - :class:`.CompiledSchedule`.

.. tip::

    The source code of the schedule generating functions in this module can
    serve as examples when creating schedules for custom experiments.
"""

from quantify.schedules.schedule import CompiledSchedule, Schedulable, Schedule
from quantify.schedules.spectroscopy_schedules import (
    heterodyne_spec_sched,
    heterodyne_spec_sched_nco,
    two_tone_spec_sched,
    two_tone_spec_sched_nco,
)
from quantify.schedules.timedomain_schedules import (
    allxy_sched,
    echo_sched,
    rabi_pulse_sched,
    rabi_sched,
    ramsey_sched,
    readout_calibration_sched,
    t1_sched,
)
from quantify.schedules.trace_schedules import (
    trace_schedule,
    trace_schedule_circuit_layer,
    two_tone_trace_schedule,
)

__all__ = [
    "CompiledSchedule",
    "Schedulable",
    "Schedule",
    "heterodyne_spec_sched",
    "heterodyne_spec_sched_nco",
    "two_tone_spec_sched",
    "two_tone_spec_sched_nco",
    "allxy_sched",
    "echo_sched",
    "rabi_pulse_sched",
    "rabi_sched",
    "ramsey_sched",
    "readout_calibration_sched",
    "t1_sched",
    "trace_schedule",
    "trace_schedule_circuit_layer",
    "two_tone_trace_schedule",
]
