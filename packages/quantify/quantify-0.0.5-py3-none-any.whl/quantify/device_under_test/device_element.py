# Repository: https://gitlab.com/quantify-os/quantify
# Licensed according to the LICENSE file on the main branch
"""The module contains definitions for device elements."""

from __future__ import annotations

from typing import Any

from deepmerge import always_merger
from qcodes.instrument.base import Instrument

from quantify.backends.graph_compilation import OperationCompilationConfig
from quantify.helpers.importers import export_python_object_to_path_string
from quantify.json_utils import JSONSerializableMixin


class DeviceElement(JSONSerializableMixin, Instrument):
    """
    Create a device element for managing parameters.

    The :class:`~DeviceElement` is responsible for compiling operations applied to that
    specific device element from the quantum-circuit to the quantum-device
    layer.
    """

    _ELEMENT_TEMPLATE: dict[str, Any] = {}

    def __init__(self, name: str, **kwargs) -> None:  # noqa: ANN003, D107
        if "-" in name or "_" in name:
            raise ValueError(
                f"Invalid DeviceElement name '{name}'. Hyphens and "
                f"underscores are not allowed due to naming conventions"
            )
        super().__init__(name, **kwargs)

    def __getstate__(self) -> dict:  # type: ignore
        """
        Serialize :class:`~DeviceElement` and derived classes.

        Serialization is performed by converting submodules into a dict containing
        the name of the device element and a dict for each submodule containing its
        parameter names and corresponding values.
        """
        snapshot = self.snapshot()

        element_data: dict[str, Any] = {"name": self.name}
        for submodule_name, submodule_data in snapshot["submodules"].items():
            element_data[submodule_name] = {
                name: data["value"]
                for name, data in submodule_data["parameters"].items()
            }

        state = {
            "deserialization_type": export_python_object_to_path_string(self.__class__),
            "mode": "__init__",
            "data": element_data,
        }
        return state

    @classmethod
    def get_element_template(cls) -> dict[str, Any]:
        """
        Return the merged element template for this device element.

        Subclasses should override or extend the `_ELEMENT_TEMPLATE` class attribute to
        define or customize supported operations for the device element. This enables
        flexible and composable device element definitions.

        Example:
            class MyElement(DeviceElement):
                _ELEMENT_TEMPLATE = {
                    "my_op": {"factory": ..., "kwargs": {...}},
                }

            class MyChildElement(MyElement):
                _ELEMENT_TEMPLATE = {
                    "my_op": {"factory": ..., "kwargs": {...}},  # override
                    "other_op": {"factory": ..., "kwargs": {...}},  # add
                }

            # Merged template will contain both "my_op" (overridden) and "other_op".

        """
        result: dict[str, Any] = {}
        for base in reversed(cls.__mro__):
            tpl = getattr(base, "_ELEMENT_TEMPLATE", None)
            if tpl:
                result = always_merger.merge(result.copy(), tpl)
        return result

    @property
    def pre_computed_calls(self) -> dict[str, Any]:
        """
        Return a dictionary of runtime values for this device element.

        This property is intended as an extension point for subclasses. Subclasses
        should override this property to provide runtime-computed values (such as
        calibration results or device-specific parameters) that are needed for operation
        compilation or configuration.

        To extend or override values from a parent class, use the following pattern:

            calls = super().pre_computed_calls.copy()
            calls.update({
                "my_param": self.compute_my_param(),
                # ... add or override more keys ...
            })
            return calls

        This ensures that all runtime values from parent and child classes are
        available, and that child classes can override parent keys as needed.

        Example:
            class MyElement(DeviceElement):
                @property
                def pre_computed_calls(self):
                    return {"foo": 1}

            class MyChildElement(MyElement):
                @property
                def pre_computed_calls(self):
                    calls = super().pre_computed_calls.copy()
                    calls.update({"bar": 2, "foo": 42})  # add and override
                    return calls

            # MyChildElement().pre_computed_calls will contain both "foo" (overridden)
            # and "bar".

        """
        return {}

    def _generate_config(self) -> dict[str, dict[str, OperationCompilationConfig]]:
        """
        Generate part of the device configuration specific to this element.

        This method is intended as a base implementation for subclasses. It uses the
        element template and pre-computed calls to construct operation compilation
        configurations for this device element. Subclasses may override this method to
        customize how the configuration is generated for their specific needs,
        but should generally call this base implementation to ensure standard behavior.

        Returns:
            dict[str, dict[str, OperationCompilationConfig]]: The device configuration
                for this element.

        """
        qubit_ops: dict[str, OperationCompilationConfig] = {
            op_name: OperationCompilationConfig(
                factory_func=meta["factory"],
                factory_kwargs={
                    k: getter(self.pre_computed_calls) if callable(getter) else getter
                    for k, getter in meta["kwargs"].items()
                },
                gate_info_factory_kwargs=meta.get("gate_keys"),
            )
            for op_name, meta in self.get_element_template().items()
        }
        return {self.name: qubit_ops}
