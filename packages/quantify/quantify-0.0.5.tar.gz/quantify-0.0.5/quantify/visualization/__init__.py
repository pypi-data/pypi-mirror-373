# Repository: https://gitlab.com/quantify-os/quantify
# Licensed according to the LICENSE file on the main branch
"""
The visualization module contains tools for real-time visualization as
well as utilities to help in plotting.

.. list-table::
    :header-rows: 1
    :widths: auto

    * - Import alias
      - Maps to
    * - :class:`!quantify.visualization.InstrumentMonitor`
      - :class:`.InstrumentMonitor`
    * - :class:`!quantify.visualization.PlotMonitor_pyqt`
      - :class:`.PlotMonitor_pyqt`
"""

from quantify.visualization.instrument_monitor import InstrumentMonitor
from quantify.visualization.pyqt_plotmon import PlotMonitor_pyqt

# Commented out because it messes up Sphinx and sphinx extensions
__all__ = ["PlotMonitor_pyqt", "InstrumentMonitor"]
