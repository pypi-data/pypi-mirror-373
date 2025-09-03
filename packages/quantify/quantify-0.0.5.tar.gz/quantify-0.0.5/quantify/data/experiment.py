# Repository: https://gitlab.com/quantify-os/quantify
# Licensed according to the LICENSE file on the main branch
"""Utilities for managing experiment data."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Union

from quantify.data.handling import (
    DATASET_NAME,
    create_exp_folder,
    load_dataset,
    locate_experiment_container,
    write_dataset,
)
from quantify.data.handling import snapshot as create_snapshot
from quantify.data.types import TUID
from quantify.utilities.general import load_json, save_json

if TYPE_CHECKING:
    import xarray as xr

SNAPSHOT_FILENAME = "snapshot.json"
METADATA_FILENAME = "metadata.json"
JSONType = Union[dict[str, Any], list[Any], str, int, float, bool, None]


class QuantifyExperiment:
    """
    Class which represents all data related to an experiment. This allows the user to
    run experiments and store data without the
    `quantify.measurement.control.MeasurementControl`. The class serves as an
    initial interface for other data storage backends.
    """

    def __init__(self, tuid: str | None, dataset: xr.Dataset | None = None) -> None:
        """
        Creates an instance of the QuantifyExperiment.

        Parameters
        ----------
        tuid
            TUID to use
        dataset
            If the TUID is None, use the TUID from this dataset

        """
        if tuid is None:
            self.tuid = TUID(dataset.tuid)  # type: ignore
            self.dataset = dataset
        else:
            self.tuid = TUID(tuid)
            self.dataset = None
        self.tuid = TUID(self.tuid)

    def __repr__(self) -> str:  # noqa: D105
        classname = ".".join([self.__module__, self.__class__.__qualname__])
        idx = f"{id(self)}x"
        return f"<{classname} at %x{idx}>: TUID {self.tuid}"

    @property
    def experiment_directory(self) -> Path:
        """
        Returns a path to the experiment directory containing the TUID set within
        the class.

        Returns
        -------
        :

        """
        experiment_directory = locate_experiment_container(tuid=self.tuid)
        return Path(experiment_directory)

    @property
    def experiment_name(self) -> str:
        """The name of the experiment."""
        location = locate_experiment_container(tuid=self.tuid)
        name = location[location.find(self.tuid) + len(self.tuid) + 1 :]
        return name

    def _get_or_create_experiment_directory(self, name: str = "") -> Path:
        """
        Create the experiment directory containing the TUID set within the class,
        if it does not exist already.

        To be used by methods that write/save. The experiment directory will be
        created on the first write/save, not before. Methods that load should not
        create an experiment directory.

        name:
            Readable name given to the datafile

        Returns
        -------
        :
            The path to the experiment directory.

        """
        try:
            experiment_directory = self.experiment_directory
        except FileNotFoundError:
            experiment_directory = create_exp_folder(tuid=self.tuid, name=name)

        return Path(experiment_directory)

    def load_dataset(self) -> xr.Dataset:
        """
        Loads the quantify dataset associated with the TUID set within
        the class.

        Returns
        -------
        :

        Raises
        ------
        FileNotFoundError
            If no file with a dataset can be found

        """
        self.dataset = load_dataset(self.tuid)
        return self.dataset

    def write_dataset(self, dataset: xr.Dataset) -> None:
        """
        Writes the quantify dataset to the directory specified by
        `~.experiment_directory`.

        Parameters
        ----------
        dataset
            The dataset to be written to the directory

        """
        name = dataset.attrs.get("name", "")
        path = self._get_or_create_experiment_directory(name=name) / DATASET_NAME
        write_dataset(path, dataset)

    def load_snapshot(self) -> JSONType:
        """
        Loads the snapshot from the directory specified by
        `~.experiment_directory`.

        Returns
        -------
        :
            The loaded snapshot from disk

        Raises
        ------
        FileNotFoundError
            If no file with a snapshot can be found

        """
        return load_json(full_path=self.experiment_directory / SNAPSHOT_FILENAME)

    def save_snapshot(
        self,
        snapshot: dict[str, Any] | None = None,
        compression: str | None = None,
    ) -> None:
        """
        Writes the snapshot to disk as specified by
        `~.experiment_directory`.

        Parameters
        ----------
        snapshot
            The snapshot to be written to the directory
        compression
            The compression type to use. Can be one of 'gzip', 'bz2', 'lzma'.
            Defaults to None, which means no compression.

        """
        if snapshot is None:
            snapshot = create_snapshot()
        save_json(
            directory=self._get_or_create_experiment_directory(),
            filename=SNAPSHOT_FILENAME,
            data=snapshot,
            compression=compression,  # type: ignore
        )

    def load_metadata(self) -> dict[str, Any]:
        """
        Loads the metadata from the directory specified by
        `~.experiment_directory`.

        Returns
        -------
        :
            The loaded metadata from disk. None if no file is found.

        Raises
        ------
        FileNotFoundError
            If no file with metadata can be found

        """
        metadata = load_json(full_path=self.experiment_directory / METADATA_FILENAME)
        if not isinstance(metadata, dict):
            raise TypeError(
                f"Expected metadata to be a dict, got {type(metadata).__name__}"
            )
        return metadata

    def save_metadata(self, metadata: dict[str, Any] | None = None) -> None:
        """
        Writes the metadata to disk as specified by
        `~.experiment_directory`.

        Parameters
        ----------
        metadata
            The metadata to be written to the directory

        """
        save_json(
            directory=self._get_or_create_experiment_directory(),
            filename=METADATA_FILENAME,
            data=metadata,
        )

    def load_text(self, rel_path: str) -> str:
        """
        Loads a string from a text file from the path specified by
        `~.experiment_directory` / rel_path.

        Parameters
        ----------
        rel_path
            path relative to the base directory of the experiment,
            e.g. "data.json" or "my_folder/data.txt"

        Returns
        -------
        :
            The loaded text from disk

        Raises
        ------
        FileNotFoundError
            If no file can be found at `rel_path`

        """
        file_path = self.experiment_directory / rel_path
        text = file_path.read_text(encoding="utf-8")
        return text

    def save_text(self, text: str, rel_path: str) -> None:
        """
        Saves a string to a text file in the path specified by
        `~.experiment_directory` / rel_path.

        Parameters
        ----------
        text
            text to be saved
        rel_path
            path relative to the base directory of the experiment,
            e.g. "data.json" or "my_folder/data.txt"

        """
        directory = (self._get_or_create_experiment_directory() / rel_path).parent
        os.makedirs(directory, exist_ok=True)
        file_path = self.experiment_directory / rel_path
        file_path.write_text(text, encoding="utf-8")
