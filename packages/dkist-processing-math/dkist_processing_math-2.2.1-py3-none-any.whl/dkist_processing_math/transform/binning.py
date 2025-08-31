"""Binning transforms."""

from functools import partial
from typing import Iterable
from typing import Iterator
from typing import Literal
from typing import Tuple
from typing import Union

import numpy as np
from skimage import transform as skit


def bin_arrays(
    arrays: Union[Iterable[np.ndarray], np.ndarray], bin_factors: (int, int)
) -> Iterator[np.ndarray]:
    """
    Bin an iterable of arrays by summation over an integral number of pixels in each dimension.

    Parameters
    ----------
    arrays
        The arrays to be binned

    bin_factors
        The bin factors for each axis, which must be integral divisors of each array dimension

    Returns
    -------
    An Iterator yielding the binned arrays

    """
    arrays = [arrays] if isinstance(arrays, np.ndarray) else arrays
    partial_bin = partial(_bin_array, bin_factors=bin_factors)
    return map(partial_bin, arrays)


def _bin_array(array: np.ndarray, bin_factors: (int, int)) -> np.ndarray:
    """
    Bin an array by summation over an integral number of pixels in each dimension.

    Parameters
    ----------
    array
        The array to be binned

    bin_factors
        The bin factors for each axis, which must be integral divisors of each array dimension

    Returns
    -------
    The binned array

    """
    input_shape = array.shape
    if input_shape[0] % bin_factors[0] or input_shape[1] % bin_factors[1]:
        raise ValueError(
            "Array dimensions must be an integral multiple of the binning factor\n"
            f"Shape of array = {input_shape}, binning factors = {bin_factors}"
        )
    return skit.downscale_local_mean(array, bin_factors)


def resize_arrays(
    arrays: Union[Iterable[np.ndarray], np.ndarray],
    output_shape: Tuple[int, ...],
    order: Literal[0, 1, 2, 3, 4, 5] = 0,
    mode: Literal["constant", "edge", "symmetric", "reflect", "wrap"] = "edge",
) -> Iterator[np.ndarray]:
    """
    Resize an iterable of arrays using specified interpolation order.

    This function is more geared towards up-sampling arrays smoothly. For more accurate downsampling see
    `resize_arrays_local_mean`

    Parameters
    ----------
    arrays
        The arrays to be binned

    output_shape
        Shape to bin the input arrays to

    order
        The order of interpolation:

            0: Nearest-neighbor
            1: Bi-linear (default)
            2: Bi-quadratic
            3: Bi-cubic
            4: Bi-quartic
            5: Bi-quintic

    mode
        Points outside the boundaries of the input are filled according to the given mode. See `numpy.pad` for explanations.

    Returns
    -------
    An Iterator yielding the binned arrays

    """
    arrays = [arrays] if isinstance(arrays, np.ndarray) else arrays
    partial_bin = partial(_resize_array, output_shape=output_shape, order=order, mode=mode)
    return map(partial_bin, arrays)


def _resize_array(
    array: np.ndarray,
    output_shape: Tuple[int, ...],
    order: Literal[0, 1, 2, 3, 4, 5] = 0,
    mode: Literal["constant", "edge", "symmetric", "reflect", "wrap"] = "edge",
) -> np.ndarray:
    """
    Resize an array using the given interpolation order.

    Parameters
    ----------
    array
        The array to be binned

    output_shape
        Shape to bin the input arrays to

    order
        The order of interpolation:

            0: Nearest-neighbor
            1: Bi-linear (default)
            2: Bi-quadratic
            3: Bi-cubic
            4: Bi-quartic
            5: Bi-quintic

    mode
        Points outside the boundaries of the input are filled according to the given mode. See `numpy.pad` for explanations.

    Returns
    -------
    The binned array

    """
    return skit.resize(
        array, output_shape, preserve_range=True, anti_aliasing=False, order=order, mode=mode
    )


def resize_arrays_local_mean(
    arrays: Union[Iterable[np.ndarray], np.ndarray], output_shape: Tuple[int, ...]
) -> Iterator[np.ndarray]:
    """
    Bin an iterable of arrays by summation over an integral number of pixels in each dimension.

    This function is good for downsampling arrays, but acts like nearest-neighbor when upsampling.
    See `resize` for more flexible upsampling options.

    Note that when downsampling this method is sensitive to extreme outliers.

    Parameters
    ----------
    arrays
        The arrays to be binned

    output_shape
        Shape to bin the input arrays to

    Returns
    -------
    An Iterator yielding the binned arrays

    """
    arrays = [arrays] if isinstance(arrays, np.ndarray) else arrays
    partial_bin = partial(_resize_array_local_mean, output_shape=output_shape)
    return map(partial_bin, arrays)


def _resize_array_local_mean(array: np.ndarray, output_shape: Tuple[int, ...]) -> np.ndarray:
    """
    Bin an array by summation over an integral number of pixels in each dimension.

    Parameters
    ----------
    array
        The array to be binned

    output_shape
        Shape to bin the input arrays to

    Returns
    -------
    The binned array

    """
    return skit.resize_local_mean(array, output_shape, preserve_range=True)
