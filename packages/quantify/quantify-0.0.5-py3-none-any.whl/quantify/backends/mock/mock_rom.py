# Repository: https://gitlab.com/quantify-os/quantify
# Licensed according to the LICENSE file on the main branch

# pyright: reportIncompatibleVariableOverride=false

"""Compiler backend for a mock readout module."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from quantify.structure.model import DataStructure
from quantify.structure.types import NDArray  # noqa: TCH001, pydantic

if TYPE_CHECKING:
    from quantify.enums import BinMode


class MockReadoutModule:
    """Mock readout module that just supports "TRACE" instruction."""

    def __init__(  # noqa: D107
        self,
        name: str,
        sampling_rate: float = 1e9,
        gain: float = 1.0,
    ) -> None:
        self.name = name
        self.data = []
        self.waveforms = {}
        self.instructions = []
        self.gain = gain
        self.sampling_rate = sampling_rate

    def upload_waveforms(self, waveforms: dict[str, NDArray]) -> None:
        """Upload a dictionary of waveforms defined on a 1 ns grid."""
        self.waveforms = waveforms

    def upload_instructions(self, instructions: list[str]) -> None:
        """Upload a sequence of instructions."""
        self.instructions = instructions

    def execute(self) -> None:
        """Execute the instruction sequence (only "TRACE" is supported)."""
        if self.instructions == []:
            raise RuntimeError(
                "No instructions available. Did you upload instructions?"
            )
        for instruction in self.instructions:
            if "TRACE" in instruction:
                self.data = []  # Clear data
                for wf in self.waveforms.values():
                    sampling_idx = np.arange(0, len(wf), int(self.sampling_rate / 1e9))
                    self.data.append(wf[sampling_idx] * self.gain)
            else:
                raise NotImplementedError(f"Instruction {instruction} not supported")

    def get_results(self) -> list[np.ndarray]:
        """Return the results of the execution."""
        if self.data == []:
            raise RuntimeError("No data available. Did you execute the sequence?")
        return self.data


class MockROMGettable:
    """Mock readout module gettable."""

    def __init__(
        self,
        mock_rom: MockReadoutModule,
        waveforms: dict[str, NDArray],
        instructions: list[str],
        sampling_rate: float = 1e9,
        gain: float = 1.0,
    ) -> None:
        """Initialize a mock rom gettable from a set of (compiled) settings."""
        self.mock_rom = mock_rom
        self.waveforms = waveforms
        self.instructions = instructions
        self.sampling_rate = sampling_rate
        self.gain = gain

    def get(self) -> list[np.ndarray]:
        """Execute the sequence and return the results."""
        # Set the sampling rate and gain
        self.mock_rom.sampling_rate = self.sampling_rate
        self.mock_rom.gain = self.gain
        # Upload waveforms and instructions
        self.mock_rom.upload_waveforms(self.waveforms)
        self.mock_rom.upload_instructions(self.instructions)
        # Execute and return results
        self.mock_rom.execute()
        return self.mock_rom.get_results()


class MockROMAcquisitionConfig(DataStructure):
    """
    Acquisition configuration for the mock readout module.

    This information is used in the instrument coordinator component to convert the
    acquired data to an xarray dataset.
    """

    n_acquisitions: int
    acq_protocols: dict[int, str]
    bin_mode: BinMode


class MockROMSettings(DataStructure):
    """Settings that can be uploaded to the mock readout module."""

    waveforms: dict[str, NDArray]
    instructions: list[str]
    sampling_rate: float = 1e9
    gain: float = 1.0
    acq_config: MockROMAcquisitionConfig
