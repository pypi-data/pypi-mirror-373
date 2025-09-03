# Repository: https://gitlab.com/quantify-os/quantify
# Licensed according to the LICENSE file on the main branch
"""Module containing the optimization analysis abstract base class."""

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from quantify.analysis import base_analysis as ba
from quantify.visualization import mpl_plotting as qpl
from quantify.visualization.SI_utilities import (
    adjust_axeslabels_SI,
    format_value_string,
)


class OptimizationAnalysis(ba.BaseAnalysis):
    """
    An analysis class which extracts the optimal quantities from an N-dimensional
    interpolating experiment.
    """

    # Override the run method so that we can add the new optional arguments
    # pylint: disable=attribute-defined-outside-init, arguments-differ
    def run(self, minimize: bool = True):  # noqa: ANN201
        """
        Parameters
        ----------
        minimize
            Boolean which determines whether to report the minimum or the maximum.
            True for minimize.
            False for maximize.

        Returns
        -------
        :class:`~quantify.analysis.optimization_analysis.OptimizationAnalysis`:
            The instance of this analysis.

        """  # NB the return type need to be specified manually to avoid circular import
        self.minimize = minimize
        return super().run()

    def process_data(self) -> None:
        """
        Finds the optimal (minimum or maximum) for y0 and saves the xi and y0
        values in the :code:`quantities_of_interest`.
        """
        if not isinstance(self.dataset, xr.Dataset):
            raise TypeError(
                f"self.dataset must be of type xr.Dataset but is {type(self.dataset)}"
            )
        text_msg = "Summary\n"

        arg_optimum_function = np.argmin if self.minimize else np.argmax
        optimum_function = np.min if self.minimize else np.max
        optimum_text = "minimum" if self.minimize else "maximum"

        # Go through every y variable and find the optimal point
        y_variable = "y0"

        text_msg += "\n"
        variable_name = self.dataset[y_variable].attrs["long_name"]
        text_msg += f"{variable_name} {optimum_text}:\n"

        # Find the optimum for each x coordinate
        for x_variable in self.dataset.coords:
            optimum = float(
                self.dataset[x_variable][
                    arg_optimum_function(self.dataset[y_variable].values)
                ].values
            )

            self.quantities_of_interest[self.dataset[x_variable].attrs["name"]] = (
                optimum
            )

            text_msg += format_value_string(
                self.dataset[x_variable].attrs["long_name"],
                optimum,
                end_char="\n",
                unit=self.dataset[x_variable].units,
            )

        # Find the corresponding optimal y value
        optimum = float(optimum_function(self.dataset[y_variable].values))

        self.quantities_of_interest[self.dataset[y_variable].attrs["name"]] = optimum

        text_msg += format_value_string(
            self.dataset[y_variable].attrs["long_name"],
            optimum,
            end_char="\n",
            unit=self.dataset[y_variable].units,
        )

        self.quantities_of_interest["plot_msg"] = text_msg

    def create_figures(self) -> None:
        """Plot each of the x variables against each of the y variables."""
        figs, axs = iteration_plots(self.dataset, self.quantities_of_interest)
        self.figs_mpl.update(figs)  # type: ignore
        self.axs_mpl.update(axs)  # type: ignore


def iteration_plots(dataset, quantities_of_interest):  # noqa: ANN001, ANN201
    """
    For every x and y variable, plot a graph of that variable vs
    the iteration index.
    """
    figs = {}
    axs = {}
    all_variables = list(dataset.coords.items()) + list(dataset.data_vars.items())
    for variable, values in all_variables:
        variable_name = dataset[variable].attrs["long_name"]

        fig, ax = plt.subplots()
        fig_id = f"Line plot {variable_name} vs iteration"

        ax.plot(values, marker=".", linewidth="0.5", markersize="4.5")
        adjust_axeslabels_SI(ax)

        qpl.set_ylabel(variable_name, dataset[variable].units, axis=ax)
        qpl.set_xlabel("iteration index", axis=ax)

        qpl.set_suptitle_from_dataset(
            fig, dataset, f"{variable_name} vs iteration number:"
        )

        qpl.plot_textbox(ax, quantities_of_interest["plot_msg"])

        # add the figure and axis to the dicts for saving
        figs[fig_id] = fig
        axs[fig_id] = ax

    return figs, axs
