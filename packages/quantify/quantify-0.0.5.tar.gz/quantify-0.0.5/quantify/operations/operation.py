# Repository: https://gitlab.com/quantify-os/quantify
# Licensed according to the LICENSE file on the main branch
"""Module containing the core concepts of the scheduler."""

from __future__ import annotations

import inspect
import logging
from collections import UserDict
from copy import deepcopy
from enum import Enum
from pydoc import locate

from quantify.helpers.collections import make_hash
from quantify.helpers.importers import export_python_object_to_path_string
from quantify.json_utils import JSONSchemaValMixin, lru_cache

cached_locate = lru_cache(locate)


class Operation(JSONSchemaValMixin, UserDict):
    """
    A representation of quantum circuit operations.

    The :class:`~Operation` class is a JSON-compatible data structure that contains
    information on how to represent the operation on the quantum-circuit and/or the
    quantum-device layer. It also contains information on where the operation should be
    applied: the :class:`~quantify.resources.Resource` s used.

    An operation always has the following attributes:

    - duration (float): duration of the operation in seconds (can be 0).
    - hash (str): an auto generated unique identifier.
    - name (str): a readable identifier, does not have to be unique.



    An Operation can contain information  on several levels of abstraction.
    This information is used when different representations are required. Note that when
    initializing an operation  not all of this information needs to be available
    as operations are typically modified during the compilation steps.

    .. tip::

        :mod:`quantify` comes with a
        :mod:`~quantify.operations.gate_library` and a
        :mod:`~quantify.operations.pulse_library` , both containing common
        operations.


    **JSON schema of a valid Operation**

    .. jsonschema:: https://gitlab.com/quantify-os/quantify-scheduler/-/raw/main/quantify/schemas/operation.json


    .. note::

        Two different Operations containing the same information generate the
        same hash and are considered identical.
    """

    schema_filename = "operation.json"
    _class_signature = None

    def __init__(self, name: str) -> None:  # noqa: D107
        super().__init__()

        # ensure keys exist
        self.data["name"] = name
        self.data["gate_info"] = {}
        self.data["pulse_info"] = []
        self.data["acquisition_info"] = []
        self.data["logic_info"] = {}
        self._duration: float = 0

    def __eq__(self, other) -> bool:  # noqa: ANN001
        """
        Returns the equality of two instances based on its hash.

        Parameters
        ----------
        other
            The other operation to compare to.

        Returns
        -------
        :

        """
        return hash(self) == hash(other)

    def __str__(self) -> str:
        """
        Returns a unique, evaluable string for unchanged data.

        Returns a concise string representation which can be evaluated into a new
        instance using :code:`eval(str(operation))` only when the data dictionary has
        not been modified.

        This representation is guaranteed to be unique.
        """
        return f"{self.__class__.__name__}(name='{self.name}')"

    def __getstate__(self):  # noqa: ANN204, D105
        return {
            "deserialization_type": export_python_object_to_path_string(self.__class__),
            "data": self.data,
        }

    def __setstate__(self, state):  # noqa: ANN001, ANN204, D105
        self.data = state["data"]
        data = state["data"]
        # This is to make sure we can be backwards compatible
        # when the "qubits" is used instead of "device_elements"
        # in the legacy serialized objects.
        if ((gate_info := data.get("gate_info")) is not None) and (
            (qubits := gate_info.get("qubits")) is not None
        ):
            new_gate_info = deepcopy(gate_info)
            if gate_info.get("device_elements") is not None:
                gate_info["device_elements"] = qubits
            new_gate_info.pop("qubits")
            data["gate_info"] = new_gate_info
        self.data = data
        self._update()

    def __hash__(self) -> int:  # noqa: D105
        return make_hash(self.data)

    def _update(self) -> None:
        """Update the Operation's internals."""

        def _get_operation_end(info) -> float:  # noqa: ANN001
            """Return the operation end in seconds."""
            return info["t0"] + info["duration"]

        # Iterate over the data and take longest duration
        self._duration = max(
            map(
                _get_operation_end,
                self.data["pulse_info"] + self.data["acquisition_info"],
            ),
            default=0,
        )

    @property
    def name(self) -> str:
        """Return the name of the operation."""
        return self.data["name"]

    @property
    def duration(self) -> float:
        """
        Determine operation duration from pulse_info.

        If the operation contains no pulse info, it is assumed to be ideal and
        have zero duration.
        """
        return self._duration

    @property
    def hash(self) -> str:
        """
        A hash based on the contents of the Operation.

        Needs to be a str for easy compatibility with json.
        """
        return str(hash(self))

    @classmethod
    def _get_signature(cls, parameters: dict) -> str:
        """
        Returns the constructor call signature of this instance for serialization.

        The string constructor representation can be used to recreate the object
        using eval(signature).

        Parameters
        ----------
        parameters : dict
            The current data dictionary.

        Returns
        -------
        :

        """
        if cls._class_signature is None:
            logging.info(f"Caching signature for class {cls.__name__}")
            cls._class_signature = inspect.signature(cls)
        signature = cls._class_signature

        def to_kwarg(key) -> str:  # noqa: ANN001
            """
            Returns a key-value pair in string format of a keyword argument.

            Parameters
            ----------
            key
                The parameter key

            Returns
            -------
            :

            """
            value = parameters[key]
            if isinstance(value, Enum):
                enum_value = value.value
                value = enum_value
            value = f"'{value}'" if isinstance(value, str) else value
            return f"{key}={value}"

        required_params = list(signature.parameters.keys())
        kwargs_list = map(to_kwarg, required_params)

        return f"{cls.__name__}({','.join(kwargs_list)})"

    def add_gate_info(self, gate_operation: Operation) -> None:
        """
        Updates self.data['gate_info'] with contents of gate_operation.

        Parameters
        ----------
        gate_operation
            an operation containing gate_info.

        """
        self.data["gate_info"].update(gate_operation.data["gate_info"])

    def add_device_representation(self, device_operation: Operation) -> None:
        """
        Adds device-level representation details to the current operation.

        Parameters
        ----------
        device_operation
            an operation containing the pulse_info and/or acquisition info describing
            how to represent the current operation at the quantum-device layer.

        """
        self.add_pulse(device_operation)
        self.add_acquisition(device_operation)

    def add_pulse(self, pulse_operation: Operation) -> None:
        """
        Adds pulse_info of pulse_operation Operation to this Operation.

        Parameters
        ----------
        pulse_operation
            an operation containing pulse_info.

        """
        self.data["pulse_info"] += pulse_operation.data["pulse_info"]
        self._update()

    def add_acquisition(self, acquisition_operation: Operation) -> None:
        """
        Adds acquisition_info of acquisition_operation Operation to this Operation.

        Parameters
        ----------
        acquisition_operation
            an operation containing acquisition_info.

        """
        self.data["acquisition_info"] += acquisition_operation.data["acquisition_info"]
        self._update()

    @classmethod
    def is_valid(cls, object_to_be_validated) -> bool:  # noqa: ANN001
        """
        Validates the object's contents against the schema.

        Additionally checks if the hash property of the object evaluates correctly.
        """
        valid_operation = super().is_valid(object_to_be_validated)
        if valid_operation:
            _ = object_to_be_validated.hash  # test that the hash property evaluates
            return True

        return False

    @property
    def valid_gate(self) -> bool:
        """An operation is a valid gate if it has gate-level representation details."""
        return len(self.data["gate_info"]) > 0

    @property
    def valid_pulse(self) -> bool:
        """
        An operation is a valid pulse if it has pulse-level
        representation details.
        """
        return len(self.data["pulse_info"]) > 0

    @property
    def valid_acquisition(self) -> bool:
        """
        An operation is a valid acquisition if it has pulse-level acquisition
        representation details.
        """
        return len(self.data["acquisition_info"]) > 0

    @property
    def is_conditional_acquisition(self) -> bool:
        """
        An operation is conditional if one of the following holds, ``self`` is an
        an acquisition with a ``feedback_trigger_label`` assigned to it.
        """
        if (acq_info := self.data.get("acquisition_info")) is not None:
            return len(acq_info) > 0 and (
                acq_info[0].get("feedback_trigger_label") is not None
            )

        return False

    @property
    def is_control_flow(self) -> bool:
        """
        Determine if operation is a control flow operation.

        Returns
        -------
        bool
            Whether the operation is a control flow operation.

        """
        return self.data.get("control_flow_info") is not None

    @property
    def has_voltage_offset(self) -> bool:
        """Checks if the operation contains information for a voltage offset."""
        return any(
            "offset_path_I" in pulse_info or "offset_path_Q" in pulse_info
            for pulse_info in self.data["pulse_info"]
        )
