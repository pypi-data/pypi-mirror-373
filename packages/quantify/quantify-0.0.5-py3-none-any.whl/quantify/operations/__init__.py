# Repository: https://gitlab.com/quantify-os/quantify
# Licensed according to the LICENSE file on the main branch
"""
Standard library of commonly used operations.

This module contains the following class:
    - :class:`.Operation`.

.. tip::

    Quantify scheduler can trivially be extended by creating custom operations. Take a
    look at e.g., the pulse library for examples on how to implement custom pulses.

"""

from quantify.operations.acquisition_library import (
    Acquisition,
    NumericalSeparatedWeightedIntegration,
    NumericalWeightedIntegration,
    SSBIntegrationComplex,
    ThresholdedAcquisition,
    Timetag,
    TimetagTrace,
    Trace,
    TriggerCount,
    WeightedIntegratedSeparated,
)
from quantify.operations.control_flow_library import (
    ConditionalOperation,
    ControlFlowOperation,
    ControlFlowSpec,
    LoopOperation,
)
from quantify.operations.gate_library import (
    CNOT,
    CZ,
    X90,
    Y90,
    Z90,
    H,
    Measure,
    Reset,
    Rxy,
    Rz,
    X,
    Y,
    Z,
)
from quantify.operations.operation import Operation
from quantify.operations.pulse_compensation_library import (
    PulseCompensation,
)
from quantify.operations.pulse_factories import (
    composite_square_pulse,
    nv_spec_pulse_mw,
    phase_shift,
    rxy_drag_pulse,
    rxy_gauss_pulse,
    rxy_hermite_pulse,
    rxy_pulse,
)
from quantify.operations.pulse_library import (
    ChirpPulse,
    DRAGPulse,
    GaussPulse,
    IdlePulse,
    MarkerPulse,
    NumericalPulse,
    RampPulse,
    ReferenceMagnitude,
    ResetClockPhase,
    SetClockFrequency,
    ShiftClockPhase,
    SkewedHermitePulse,
    SoftSquarePulse,
    SquarePulse,
    StaircasePulse,
    SuddenNetZeroPulse,
    Timestamp,
    VoltageOffset,
    WindowOperation,
)

__all__ = [
    "Acquisition",
    "NumericalSeparatedWeightedIntegration",
    "NumericalWeightedIntegration",
    "SSBIntegrationComplex",
    "ThresholdedAcquisition",
    "Timetag",
    "TimetagTrace",
    "Trace",
    "TriggerCount",
    "WeightedIntegratedSeparated",
    "CNOT",
    "CZ",
    "X90",
    "Y90",
    "Z90",
    "H",
    "Measure",
    "Reset",
    "Rxy",
    "Rz",
    "X",
    "Y",
    "Z",
    "Operation",
    "phase_shift",
    "rxy_drag_pulse",
    "rxy_gauss_pulse",
    "rxy_hermite_pulse",
    "ChirpPulse",
    "DRAGPulse",
    "GaussPulse",
    "IdlePulse",
    "MarkerPulse",
    "NumericalPulse",
    "RampPulse",
    "ReferenceMagnitude",
    "ResetClockPhase",
    "SetClockFrequency",
    "ShiftClockPhase",
    "SkewedHermitePulse",
    "SoftSquarePulse",
    "SquarePulse",
    "StaircasePulse",
    "SuddenNetZeroPulse",
    "Timestamp",
    "VoltageOffset",
    "WindowOperation",
    "ConditionalOperation",
    "ControlFlowOperation",
    "ControlFlowSpec",
    "LoopOperation",
    "PulseCompensation",
    "composite_square_pulse",
    "nv_spec_pulse_mw",
    "rxy_pulse",
]
