"""Statistics."""

from typing import Iterable
from typing import Union

import numpy as np


def average_numpy_arrays(arrays: Union[Iterable[np.ndarray], np.ndarray]) -> np.ndarray:
    """
    Given an iterable of numpy arrays, calculate the pixel-wise average and return it in a numpy array.

    This will work for a single array as well, just in case...

    Parameters
    ----------
    arrays
        The arrays to be averaged

    Returns
    -------
    The average of the input arrays

    """
    arrays = [arrays] if isinstance(arrays, np.ndarray) else arrays
    count = 0  # This statement is here only to suppress an uninitialized variable warning
    output = None
    for count, array in enumerate(arrays):
        if output is None:
            output = np.array(array).astype(float)
        else:
            if array.shape != output.shape:
                raise ValueError(
                    f"All arrays must be the same shape. "
                    f"Shape of initial array = {output.shape} "
                    f"Shape of current array = {array.shape}"
                )
            output += array
    if output is not None:
        return output / (count + 1)
    raise ValueError("data_arrays is empty")


def stddev_numpy_arrays(arrays: Iterable[np.ndarray]) -> np.ndarray:
    r"""
    Given an iterable of numpy arrays, calculate the pixel-wise standard deviation and return it in a numpy array.

    This function uses Welford's single-pass algorithm. The standard deviation for the :math:`n^{th}` array is

    .. math::
        \sigma_n = \sqrt{\frac{M_{2,n}}{n}}

    where

    .. math::
        M_{2,n} = M_{2,n-1} + (x_n - \bar{x}_{n-1})(x_n - \bar{x}_n)

    and

    .. math::
        \bar{x}_n = \bar{x}_{n-1} + \frac{x_n - \bar{x}_{n-1}}{n}

    Note that in computing :math:`\sigma` we divide by :math:`n` instead of :math:`(n-1)`. This is to match the default
    behavior of `numpy.std`.

    Parameters
    ----------
    arrays
        The arrays to be to compute the standard deviation of. Must be an Iterator of at least two arrays.

    Returns
    -------
    The standard deviation of the input arrays
    """
    if isinstance(arrays, np.ndarray):
        raise ValueError(
            "Need an Iterator with at least two arrays, but a single array was provided."
        )

    running_mean = 0.0
    running_M2 = 0.0
    count = 0
    for array in arrays:
        count += 1
        try:
            diff_from_prev_mean = array - running_mean
        except ValueError:
            raise ValueError(
                f"All arrays must be the same shape. "
                f"Shape of initial array = {running_mean.shape} "
                f"Shape of current array = {array.shape}"
            )
        running_mean += diff_from_prev_mean / count
        diff_from_current_mean = array - running_mean
        running_M2 += diff_from_prev_mean * diff_from_current_mean

    match count:
        case 0:
            raise ValueError("arrays is empty")
        case 1:
            raise ValueError(f"Need at least two arrays. Provided Iterator only has {count}")
        case _:
            return np.sqrt(running_M2 / count)
