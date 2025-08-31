"""Feature finding."""

from typing import Callable
from typing import Tuple

import numpy
import numpy as np
import peakutils as pku
from peakutils import gaussian_fit


def find_px_angles(
    hough_accumulator: numpy.ndarray,
    theta: numpy.ndarray,
    peak_func: Callable = gaussian_fit,
    px_width: int = 10,
    raise_error_on_failed_interpolation: bool = False,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Find the most significant angles in a Hough transform.

    Peaks in the Hough transform are first found with a simple max filter and then refined via interpolation of the
    surrounding peak.

    Parameters
    ----------
    hough_accumulator
        A 2D array representing a Hough accumulator

    theta
        A 1D array of the angle values corresponding to hough_accumulator

    peak_func
        Function that will be called to detect a unique peak in the x,y data. Must have args (x, y) and return x peak value.

    px_width
        The width, in pixels, around (+/-) the initial peak to apply peak_func for peak refinement

    raise_error_on_failed_interpolation
        If True, raise an error if the peak refinement minimization fails. Otherwise return the non-refined peak in this case.

    Returns
    -------
    peak_theta
        The most significant angles found

    """
    rss = np.sqrt(np.sum(hough_accumulator**2, axis=0))
    # This min distance limits us to only finding the single most prominent angle
    idx = pku.indexes(rss, min_dist=theta.size)
    peak_theta = pku.interpolate(theta, rss, ind=idx, width=px_width, func=peak_func)

    # If pku.interpolate fails to find a good fit it will return idx, which is not what we want.
    # In this case we either...
    if peak_theta == idx:
        if raise_error_on_failed_interpolation:
            # ...raise an Error
            raise RuntimeError("Interpolation of peak failed")

        # ...return the non-interpolated peak angle
        peak_theta = theta[peak_theta]

    return peak_theta
