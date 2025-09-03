# Repository: https://gitlab.com/quantify-os/quantify
# Licensed according to the LICENSE file on the main branch
"""Module containing the types for use with the analysis classes."""

from __future__ import annotations

from collections import UserDict

from jsonschema import validate

from quantify.utilities.general import load_json_schema


# pylint: disable=too-few-public-methods
# WARNING! Do not inherit from dict! if you do, `AnalysisSettings.update will skip the
# validation done in `__setitem__`.
class AnalysisSettings(UserDict):
    """
    Analysis settings with built-in schema validations.

    .. jsonschema:: schemas/AnalysisSettings.json#/configurations
    """

    schema = load_json_schema(__file__, "AnalysisSettings.json")["configurations"]
    schema_individual = dict(schema)
    schema_individual.pop("required")

    def __init__(self, settings: dict | None = None) -> None:
        """Initializes and validates the passed settings."""
        super().__init__()
        if settings:
            validate(settings, self.schema)
            for key, value in settings.items():
                super().__setitem__(key, value)

    def __setitem__(self, key, value) -> None:  # noqa: ANN001
        """Items are validated before assigning."""
        validate({key: value}, self.schema_individual)
        super().__setitem__(key, value)
