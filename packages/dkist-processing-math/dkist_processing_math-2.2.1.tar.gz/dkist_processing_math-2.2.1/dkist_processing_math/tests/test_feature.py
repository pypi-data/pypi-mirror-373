import numpy as np
import pytest

from dkist_processing_math.feature import find_px_angles


def test_find_px_angles():
    """
    Given: a single numpy array
    When: finding the most significant angles in a hough transform
    Then: return the correct peak angle
    """

    theta = np.linspace(-np.pi / 4, np.pi / 4, 1500)

    def Gaussian(x, mu, sig):
        return np.exp(-np.power(x - mu, 2.0) / (2 * np.power(sig, 2.0)))

    mu = 0.1
    sigma = 0.2
    gaussian = Gaussian(theta, mu, sigma)

    H = np.zeros((20, 1500)) + gaussian[None, :]
    desired_peaktheta = np.array(mu)

    result_peaktheta = find_px_angles(H, theta)
    assert isinstance(result_peaktheta, np.ndarray)

    np.testing.assert_array_almost_equal(result_peaktheta, desired_peaktheta)


def always_fail_gaussian_fitter(*args):
    """This is how we force a failure to fit.

    Easier than trying to contrive a signal that fails to fit.
    """
    raise RuntimeError("Failing for a test")


def test_find_px_angles_interpolation_failure():
    """
    Given: A signal that will cause a fitting error in peakutils
    When: Trying to find the peak angle through interpolation
    Then: The non-interpolated peak angle is returned
    """
    theta = np.linspace(-np.pi / 4, np.pi / 4, 1500)
    signal = np.random.random(1500) * 10
    peak_idx = 400
    signal[peak_idx] = 100.0
    H = np.zeros((20, 1500)) + signal[None, :]

    desired_peaktheta = theta[peak_idx]
    result_peaktheta = find_px_angles(H, theta, peak_func=always_fail_gaussian_fitter)

    np.testing.assert_array_equal(desired_peaktheta, result_peaktheta)


def test_find_px_angles_interpolation_failure_raise_error():
    """
    Given: A signal that will cause a fitting error in peakutils
    When: Trying to find the peak angle through interpolation with the flag set to raise an error on interpolation failure
    Then: An error is raised
    """
    theta = np.linspace(-np.pi / 4, np.pi / 4, 1500)
    signal = np.random.random(1500) * 10
    peak_idx = 400
    signal[peak_idx] = 100.0
    H = np.zeros((20, 1500)) + signal[None, :]

    with pytest.raises(RuntimeError):
        find_px_angles(
            H,
            theta,
            peak_func=always_fail_gaussian_fitter,
            raise_error_on_failed_interpolation=True,
        )
