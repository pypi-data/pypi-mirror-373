# Repository: https://gitlab.com/quantify-os/quantify
# Licensed according to the LICENSE file on the main branch
"""Module containing schedules for common spectroscopy experiments."""

from __future__ import annotations

from typing import TYPE_CHECKING

import quantify.operations.pulse_library as pl
from quantify.enums import BinMode
from quantify.operations.acquisition_library import SSBIntegrationComplex
from quantify.resources import ClockResource
from quantify.schedules.schedule import Schedule

if TYPE_CHECKING:
    import numpy as np


def heterodyne_spec_sched(
    pulse_amp: float,
    pulse_duration: float,
    frequency: float,
    acquisition_delay: float,
    integration_time: float,
    port: str,
    clock: str,
    init_duration: float = 10e-6,
    repetitions: int = 1,
    port_out: str | None = None,
) -> Schedule:
    """
    Generate a schedule for performing heterodyne spectroscopy.

    Parameters
    ----------
    pulse_amp
        Amplitude of the spectroscopy pulse in Volt.
    pulse_duration
        Duration of the spectroscopy pulse in seconds.
    frequency
        Frequency of the spectroscopy pulse in Hertz.
    acquisition_delay
        Start of the data acquisition with respect to the start of the spectroscopy
        pulse in seconds.
    integration_time
        Integration time of the data acquisition in seconds.
    port
        Location on the device where the acquisition is performed.
    clock
        Reference clock used to track the spectroscopy frequency.
    init_duration
        The relaxation time or dead time.
    repetitions
        The amount of times the Schedule will be repeated.
    port_out
        Output port on the device where the pulse should be applied. If `None`, then use
        the same as `port`.

    """
    sched = Schedule("Heterodyne spectroscopy", repetitions)
    sched.add_resource(ClockResource(name=clock, freq=frequency))

    sched.add(pl.IdlePulse(duration=init_duration), label="buffer")

    if port_out is None:
        port_out = port

    pulse = sched.add(
        pl.SquarePulse(
            duration=pulse_duration,
            amp=pulse_amp,
            port=port_out,
            clock=clock,
        ),
        label="spec_pulse",
    )

    sched.add(
        SSBIntegrationComplex(
            duration=integration_time,
            port=port,
            clock=clock,
            acq_index=0,
            acq_channel=0,
        ),
        ref_op=pulse,
        ref_pt="start",
        rel_time=acquisition_delay,
        label="acquisition",
    )

    return sched


def heterodyne_spec_sched_nco(
    pulse_amp: float,
    pulse_duration: float,
    frequencies: np.ndarray,
    acquisition_delay: float,
    integration_time: float,
    port: str,
    clock: str,
    init_duration: float = 10e-6,
    repetitions: int = 1,
    port_out: str | None = None,
) -> Schedule:
    """
    Generate a batched schedule for performing fast heterodyne spectroscopy
    using the :class:`~quantify.operations.pulse_library.SetClockFrequency`
    operation for doing an NCO sweep.

    .. admonition:: Example use of the ``heterodyne_spec_sched_nco`` schedule
        :class: tip

        .. jupyter-execute::

            import numpy as np
            from qcodes.instrument.parameter import ManualParameter

            # from quantify.gettables import ScheduleGettable
            from quantify.device_under_test.quantum_device import QuantumDevice
            from quantify.device_under_test.transmon_element import BasicTransmonElement
            from quantify.schedules.spectroscopy_schedules import (
                heterodyne_spec_sched_nco
            )

            quantum_device = QuantumDevice(name="quantum_device")
            q0 = BasicTransmonElement("q0")
            quantum_device.add_element(q0)

            ...

            # Manual parameter for batched schedule
            ro_freq = ManualParameter("ro_freq", unit="Hz")
            ro_freq.batched = True
            ro_freqs = np.linspace(start=4.5e9, stop=5.5e9, num=11)
            quantum_device.cfg_sched_repetitions(5)

            # Configure the gettable
            device_element = quantum_device.get_element("q0")
            schedule_kwargs = {
                "pulse_amp": device_element.measure.pulse_amp(),
                "pulse_duration": device_element.measure.pulse_duration(),
                "frequencies": ro_freqs,
                "acquisition_delay": device_element.measure.acq_delay(),
                "integration_time": device_element.measure.integration_time(),
                "port": device_element.ports.readout(),
                "clock": device_element.name + ".ro",
                "init_duration": device_element.reset.duration(),
            }
            # spec_gettable = ScheduleGettable(
            #     quantum_device=quantum_device,
            #     schedule_function=heterodyne_spec_sched_nco,
            #     schedule_kwargs=schedule_kwargs,
            #     real_imag=False,
            #     batched=True,
            # )

            ...

            quantum_device.close()
            q0.close()


    Parameters
    ----------
    pulse_amp
        Amplitude of the spectroscopy pulse in Volt.
    pulse_duration
        Duration of the spectroscopy pulse in seconds.
    frequencies
        Sample frequencies for the spectroscopy pulse in Hertz.
    acquisition_delay
        Start of the data acquisition with respect to the start of the spectroscopy
        pulse in seconds.
    integration_time
        Integration time of the data acquisition in seconds.
    port
        Location on the device where the acquisition is performed.
    clock
        Reference clock used to track the spectroscopy frequency.
    init_duration
        The relaxation time or dead time.
    repetitions
        The amount of times the Schedule will be repeated.
    port_out
        Output port on the device where the pulse should be applied. If `None`, then use
        the same as `port`.

    """
    sched = Schedule("Fast heterodyne spectroscopy (NCO sweep)", repetitions)
    sched.add_resource(ClockResource(name=clock, freq=frequencies.flat[0]))

    if port_out is None:
        port_out = port

    for acq_idx, freq in enumerate(frequencies):
        sched.add(pl.IdlePulse(duration=init_duration), label=f"buffer {acq_idx}")

        sched.add(
            pl.SetClockFrequency(clock=clock, clock_freq_new=freq),
            label=f"set_freq {acq_idx} ({clock} {freq:e} Hz)",
        )

        spec_pulse = sched.add(
            pl.SquarePulse(
                duration=pulse_duration,
                amp=pulse_amp,
                port=port_out,
                clock=clock,
            ),
            label=f"spec_pulse {acq_idx})",
        )

        sched.add(
            SSBIntegrationComplex(
                duration=integration_time,
                port=port,
                clock=clock,
                acq_index=acq_idx,
                acq_channel=0,
                bin_mode=BinMode.AVERAGE,
            ),
            ref_op=spec_pulse,
            ref_pt="start",
            rel_time=acquisition_delay,
            label=f"acquisition {acq_idx})",
        )

    return sched


def two_tone_spec_sched(
    spec_pulse_amp: float,
    spec_pulse_duration: float,
    spec_pulse_port: str,
    spec_pulse_clock: str,
    spec_pulse_frequency: float,
    ro_pulse_amp: float,
    ro_pulse_duration: float,
    ro_pulse_delay: float,
    ro_pulse_port: str,
    ro_pulse_clock: str,
    ro_pulse_frequency: float,
    ro_acquisition_delay: float,
    ro_integration_time: float,
    init_duration: float = 10e-6,
    repetitions: int = 1,
) -> Schedule:
    """
    Generate a schedule for performing two-tone spectroscopy.

    Parameters
    ----------
    spec_pulse_amp
        Amplitude of the spectroscopy pulse in Volt.
    spec_pulse_duration
        Duration of the spectroscopy pulse in seconds.
    spec_pulse_port
        Location on the device where the spectroscopy pulse should be applied.
    spec_pulse_clock
        Reference clock used to track the spectroscopy frequency.
    spec_pulse_frequency
        Frequency of the spectroscopy pulse in Hertz.
    ro_pulse_amp
        Amplitude of the readout (spectroscopy) pulse in Volt.
    ro_pulse_duration
        Duration of the readout (spectroscopy) pulse in seconds.
    ro_pulse_delay
        Time between the end of the spectroscopy pulse and the start of the readout
        (spectroscopy) pulse.
    ro_pulse_port
        Location on the device where the readout (spectroscopy) pulse should be applied.
    ro_pulse_clock
        Reference clock used to track the readout (spectroscopy) frequency.
    ro_pulse_frequency
        Frequency of the readout (spectroscopy) pulse in Hertz.
    ro_acquisition_delay
        Start of the data acquisition with respect to the start of the readout pulse in
        seconds.
    ro_integration_time
        Integration time of the data acquisition in seconds.
    init_duration
        The relaxation time or dead time.
    repetitions
        The amount of times the Schedule will be repeated.

    """
    sched = Schedule("Two-tone spectroscopy", repetitions)
    sched.add_resource(ClockResource(name=spec_pulse_clock, freq=spec_pulse_frequency))
    sched.add_resource(ClockResource(name=ro_pulse_clock, freq=ro_pulse_frequency))

    sched.add(
        pl.IdlePulse(duration=init_duration),
        label="buffer",
    )

    sched.add(
        pl.SquarePulse(
            duration=spec_pulse_duration,
            amp=spec_pulse_amp,
            port=spec_pulse_port,
            clock=spec_pulse_clock,
        ),
        label="spec_pulse",
    )

    ro_pulse = sched.add(
        pl.SquarePulse(
            duration=ro_pulse_duration,
            amp=ro_pulse_amp,
            port=ro_pulse_port,
            clock=ro_pulse_clock,
        ),
        label="readout_pulse",
        rel_time=ro_pulse_delay,
    )

    sched.add(
        SSBIntegrationComplex(
            duration=ro_integration_time,
            port=ro_pulse_port,
            clock=ro_pulse_clock,
            acq_index=0,
            acq_channel=0,
        ),
        ref_op=ro_pulse,
        ref_pt="start",
        rel_time=ro_acquisition_delay,
        label="acquisition",
    )

    return sched


def two_tone_spec_sched_nco(
    spec_pulse_amp: float,
    spec_pulse_duration: float,
    spec_pulse_port: str,
    spec_pulse_clock: str,
    spec_pulse_frequencies: np.ndarray,
    ro_pulse_amp: float,
    ro_pulse_duration: float,
    ro_pulse_delay: float,
    ro_pulse_port: str,
    ro_pulse_clock: str,
    ro_pulse_frequency: float,
    ro_acquisition_delay: float,
    ro_integration_time: float,
    init_duration: float,
    repetitions: int = 1,
) -> Schedule:
    """
    Generate a batched schedule for performing fast two-tone spectroscopy using
    the :class:`~quantify.operations.pulse_library.SetClockFrequency`
    operation for doing an NCO sweep.

    For long-lived qubits, it is advisable to use a small number of repetitions and
    compensate by doing continuous spectroscopy (low amplitude, long duration pulse with
    simultaneous long readout).

    The "dead-time" between two data points needs to be sufficient to properly reset the
    qubit. That means that `init_duration` should be >> T1 (so typically >200us).

    .. admonition:: Example use of the ``two_tone_spec_sched_nco`` schedule
        :class: tip

        .. jupyter-execute::

            import numpy as np
            from qcodes.instrument.parameter import ManualParameter

            # from quantify.gettables import ScheduleGettable
            from quantify.device_under_test.quantum_device import QuantumDevice
            from quantify.device_under_test.transmon_element import BasicTransmonElement
            from quantify.schedules.spectroscopy_schedules import (
                two_tone_spec_sched_nco
            )

            quantum_device = QuantumDevice(name="quantum_device")
            q0 = BasicTransmonElement("q0")
            quantum_device.add_element(q0)

            ...

            # Manual parameter for batched schedule
            spec_freq = ManualParameter("spec_freq", unit="Hz")
            spec_freq.batched = True
            spec_freqs = np.linspace(start=4.5e9, stop=5.5e9, num=11)
            quantum_device.cfg_sched_repetitions(5)

            # Configure the gettable
            device_element = quantum_device.get_element("q0")
            schedule_kwargs = {
                "spec_pulse_amp": 0.5,
                "spec_pulse_duration": 8e-6,
                "spec_pulse_port": device_element.ports.microwave(),
                "spec_pulse_clock": device_element.name + ".01",
                "spec_pulse_frequencies": spec_freqs,
                "ro_pulse_amp": device_element.measure.pulse_amp(),
                "ro_pulse_duration": device_element.measure.pulse_duration(),
                "ro_pulse_delay": 300e-9,
                "ro_pulse_port": device_element.ports.readout(),
                "ro_pulse_clock": device_element.name + ".ro",
                "ro_pulse_frequency": 7.04e9,
                "ro_acquisition_delay": device_element.measure.acq_delay(),
                "ro_integration_time": device_element.measure.integration_time(),
                "init_duration": 300e-6,
            }
            # spec_gettable = ScheduleGettable(
            #     quantum_device=quantum_device,
            #     schedule_function=two_tone_spec_sched_nco,
            #     schedule_kwargs=schedule_kwargs,
            #     real_imag=False,
            #     batched=True,
            # )

            ...

            quantum_device.close()
            q0.close()


    Parameters
    ----------
    spec_pulse_amp
        Amplitude of the spectroscopy pulse in Volt.
    spec_pulse_duration
        Duration of the spectroscopy pulse in seconds.
    spec_pulse_port
        Location on the device where the spectroscopy pulse should be applied.
    spec_pulse_clock
        Reference clock used to track the spectroscopy frequency.
    spec_pulse_frequencies
        Sample frequencies for the spectroscopy pulse in Hertz.
    ro_pulse_amp
        Amplitude of the readout (spectroscopy) pulse in Volt.
    ro_pulse_duration
        Duration of the readout (spectroscopy) pulse in seconds.
    ro_pulse_delay
        Time between the end of the spectroscopy pulse and the start of the readout
        (spectroscopy) pulse.
    ro_pulse_port
        Location on the device where the readout (spectroscopy) pulse should be applied.
    ro_pulse_clock
        Reference clock used to track the readout (spectroscopy) frequency.
    ro_pulse_frequency
        Frequency of the readout (spectroscopy) pulse in Hertz.
    ro_acquisition_delay
        Start of the data acquisition with respect to the start of the readout pulse in
        seconds.
    ro_integration_time
        Integration time of the data acquisition in seconds.
    init_duration
        The relaxation time or dead time.
    repetitions
        The amount of times the Schedule will be repeated.

    """
    sched = Schedule("Fast two-tone spectroscopy (NCO sweep)", repetitions)
    sched.add_resources(
        [
            ClockResource(name=spec_pulse_clock, freq=spec_pulse_frequencies.flat[0]),
            ClockResource(name=ro_pulse_clock, freq=ro_pulse_frequency),
        ]
    )

    for acq_idx, spec_pulse_freq in enumerate(spec_pulse_frequencies):
        sched.add(pl.IdlePulse(duration=init_duration), label=f"buffer {acq_idx}")

        sched.add(
            pl.SetClockFrequency(
                clock=spec_pulse_clock, clock_freq_new=spec_pulse_freq
            ),
            label=f"set_freq {acq_idx} ({spec_pulse_clock} {spec_pulse_freq:e} Hz)",
        )

        spec_pulse = sched.add(
            pl.SquarePulse(
                duration=spec_pulse_duration,
                amp=spec_pulse_amp,
                port=spec_pulse_port,
                clock=spec_pulse_clock,
            ),
            label=f"spec_pulse {acq_idx}",
        )

        ro_pulse = sched.add(
            pl.SquarePulse(
                duration=ro_pulse_duration,
                amp=ro_pulse_amp,
                port=ro_pulse_port,
                clock=ro_pulse_clock,
            ),
            ref_op=spec_pulse,
            ref_pt="end",
            rel_time=ro_pulse_delay,
            label=f"readout_pulse {acq_idx}",
        )

        sched.add(
            SSBIntegrationComplex(
                duration=ro_integration_time,
                port=ro_pulse_port,
                clock=ro_pulse_clock,
                acq_index=acq_idx,
                acq_channel=0,
                bin_mode=BinMode.AVERAGE,
            ),
            ref_op=ro_pulse,
            ref_pt="start",
            rel_time=ro_acquisition_delay,
            label=f"acquisition {acq_idx}",
        )

    return sched
