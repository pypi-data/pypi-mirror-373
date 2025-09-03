# Repository: https://gitlab.com/quantify-os/quantify
# Licensed according to the LICENSE file on the main branch
"""
Module containing an education example of an analysis subclass.

See :ref:`analysis-framework-tutorial` that guides you through the process of building
this analysis.
"""

import matplotlib.pyplot as plt
import xarray as xr

import quantify.analysis.base_analysis as ba
from quantify.analysis.fitting_models import CosineModel
from quantify.visualization import mpl_plotting as qpl
from quantify.visualization.SI_utilities import (
    adjust_axeslabels_SI,
    format_value_string,
)


class CosineAnalysis(ba.BaseAnalysis):
    """Exemplary analysis subclass that fits a cosine to a dataset."""

    def process_data(self) -> None:
        """
        In some cases, you might need to process the data, e.g., reshape, filter etc.,
        before starting the analysis. This is the method where it should be done.

        See :meth:`~quantify.analysis.spectroscopy_analysis.ResonatorSpectroscopyAnalysis.process_data`
        for an implementation example.
        """  # noqa: E501

    def run_fitting(self) -> None:
        """Fits a :class:`~quantify.analysis.fitting_models.CosineModel` to the data."""
        # create a fitting model based on a cosine function
        model = CosineModel()
        if not isinstance(self.dataset, xr.Dataset):
            raise TypeError(
                f"self.dataset must be of type xr.Dataset but is {type(self.dataset)}"
            )
        guess = model.guess(self.dataset.y0.values, x=self.dataset.x0.values)
        result = model.fit(
            self.dataset.y0.values, x=self.dataset.x0.values, params=guess
        )
        self.fit_results.update({"cosine": result})

    def create_figures(self) -> None:
        """Creates a figure with the data and the fit."""
        fig, ax = plt.subplots()
        fig_id = "cos_fit"
        self.figs_mpl.update({fig_id: fig})  # type: ignore
        self.axs_mpl.update({fig_id: ax})  # type: ignore

        if not isinstance(self.dataset, xr.Dataset):
            raise TypeError(
                f"self.dataset must be of type xr.Dataset but is {type(self.dataset)}"
            )
        self.dataset.y0.plot(ax=ax, x="x0", marker="o", linestyle="")
        qpl.plot_fit(ax, self.fit_results["cosine"])
        qpl.plot_textbox(ax, ba.wrap_text(self.quantities_of_interest["fit_msg"]))

        adjust_axeslabels_SI(ax)
        qpl.set_suptitle_from_dataset(fig, self.dataset, "x0-y0")
        ax.legend()

    def analyze_fit_results(self) -> None:
        """Checks fit success and populates :code:`quantities_of_interest`."""
        fit_result = self.fit_results["cosine"]
        fit_warning = ba.check_lmfit(fit_result)
        if not isinstance(self.dataset, xr.Dataset):
            raise TypeError(
                f"self.dataset must be of type xr.Dataset but is {type(self.dataset)}"
            )

        # If there is a problem with the fit, display an error message in the text box.
        # Otherwise, display the parameters as normal.
        if fit_warning is None:
            self.quantities_of_interest["fit_success"] = True
            unit = self.dataset.y0.units
            text_msg = "Summary\n"
            text_msg += format_value_string(
                r"$f$", fit_result.params["frequency"], end_char="\n", unit="Hz"
            )
            text_msg += format_value_string(
                r"$A$", fit_result.params["amplitude"], unit=unit
            )
        else:
            text_msg = fit_warning
            self.quantities_of_interest["fit_success"] = False

        # save values and fit uncertainty
        for parameter_name in ["frequency", "amplitude"]:
            self.quantities_of_interest[parameter_name] = ba.lmfit_par_to_ufloat(
                fit_result.params[parameter_name]
            )
        self.quantities_of_interest["fit_msg"] = text_msg
