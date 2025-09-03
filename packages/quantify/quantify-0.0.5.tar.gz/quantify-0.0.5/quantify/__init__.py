# Repository: https://gitlab.com/quantify-os/quantify
# Licensed according to the LICENSE file on the main branch
"""
Data acquisition framework focused on Quantum Computing and solid-state physics
experiments.

.. list-table::
    :header-rows: 1
    :widths: auto

    * - Import alias
      - Target
    * - :class:`.QuantumDevice`
      - :class:`!quantify.QuantumDevice`
    * - :class:`.Schedule`
      - :class:`!quantify.Schedule`
    * - :class:`.Resource`
      - :class:`!quantify.Resource`
    * - :class:`.ClockResource`
      - :class:`!quantify.ClockResource`
    * - :class:`.BasebandClockResource`
      - :class:`!quantify.BasebandClockResource`
    * - :class:`.DigitalClockResource`
      - :class:`!quantify.DigitalClockResource`
    * - :class:`.Operation`
      - :class:`!quantify.Operation`
    * - :obj:`.structure`
      - :obj:`!quantify.structure`
    * - :class:`.BasicTransmonElement`
      - :class:`!quantify.BasicTransmonElement`
    * - :class:`.CompositeSquareEdge`
      - :class:`!quantify.CompositeSquareEdge`
    * - :class:`.InstrumentCoordinator`
      - :class:`!quantify.InstrumentCoordinator`
    * - :class:`.GenericInstrumentCoordinatorComponent`
      - :class:`!quantify.GenericInstrumentCoordinatorComponent`
    * - :class:`.SerialCompiler`
      - :class:`!quantify.SerialCompiler`
    * - :class:`.MockLocalOscillator`
      - :class:`!quantify.MockLocalOscillator`
"""

from quantify import structure, waveforms
from quantify._version import __version__
from quantify.backends import SerialCompiler
from quantify.device_under_test import (
    BasicTransmonElement,
    QuantumDevice,
)
from quantify.instrument_coordinator.components.generic import (
    GenericInstrumentCoordinatorComponent,
)
from quantify.instrument_coordinator.instrument_coordinator import InstrumentCoordinator
from quantify.operations import Operation
from quantify.resources import (
    BasebandClockResource,
    ClockResource,
    DigitalClockResource,
    Resource,
)
from quantify.schedules import Schedule

__all__ = [
    "structure",
    "__version__",
    "SerialCompiler",
    "BasicTransmonElement",
    "QuantumDevice",
    "InstrumentCoordinator",
    "GenericInstrumentCoordinatorComponent",
    "Operation",
    "BasebandClockResource",
    "ClockResource",
    "DigitalClockResource",
    "Resource",
    "Schedule",
    "waveforms",
]
