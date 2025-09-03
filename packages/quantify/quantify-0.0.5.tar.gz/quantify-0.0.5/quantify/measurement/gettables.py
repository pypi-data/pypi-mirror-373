# Repository: https://gitlab.com/quantify-os/quantify
# Licensed according to the LICENSE file on the main branch
"""Module containing example gettables."""

import time


class StopWatchGettable:
    """Gettable used to track time elapsed per acquisition."""

    def __init__(self) -> None:
        """Creates timer."""
        self.name = "dt"
        self.label = r"$\Delta T$"
        self.unit = "s"

        # so that instance attr is defined in constructor
        self.t0 = time.time()

    def prepare(self) -> None:
        """Starts the timer for the stopwatch."""
        self.t0 = time.time()

    def get(self) -> float:
        """
        Returns the time elapsed since the last start of the stopwatch and restarts the
        timer.

        Returns
        -------
        :
            Elapsed time in seconds.

        """
        delta_time = time.time() - self.t0
        self.t0 = time.time()
        return delta_time
