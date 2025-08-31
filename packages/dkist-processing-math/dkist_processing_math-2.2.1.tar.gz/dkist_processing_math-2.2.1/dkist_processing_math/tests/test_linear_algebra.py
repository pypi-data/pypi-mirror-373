import numpy as np
import pytest

from dkist_processing_math.linear_algebra import nd_left_matrix_multiply
from dkist_processing_math.linear_algebra import nd_right_matrix_multiply


@pytest.fixture
def D1() -> int:
    return 3


@pytest.fixture
def D2() -> int:
    return 4


@pytest.fixture
def extra_dims(num_dims) -> tuple[int]:
    dims = np.random.randint(low=1, high=5, size=num_dims)
    return tuple(dims)


@pytest.fixture
def matrix_stack(extra_dims: tuple[int, ...], single_matrix: bool, D1: int, D2: int) -> np.ndarray:
    full_shape = extra_dims + (D1, D2)
    if single_matrix:
        full_shape = (D1, D2)
    return np.random.random(full_shape)


@pytest.fixture
def left_vector_stack(extra_dims: tuple[int, ...], single_vector: bool, D2: int) -> np.ndarray:
    full_shape = extra_dims + (D2,)
    if single_vector:
        full_shape = (D2,)
    return np.random.random(full_shape)


@pytest.fixture
def right_vector_stack(extra_dims: tuple[int, ...], single_vector: bool, D1: int) -> np.ndarray:
    full_shape = extra_dims + (D1,)
    if single_vector:
        full_shape = (D1,)
    return np.random.random(full_shape)


# Stopping at 7 for no real reason. We need 0 and 2 for sure and then others to confirm generality.
# single_matrix = True tests the case where the matrix has no higher dimensions. Probably only need to test it once
# but we do it twice just because.
@pytest.mark.parametrize(
    "num_dims, single_matrix, single_vector",
    [
        (0, False, False),
        (1, False, False),
        (2, False, False),
        (2, True, False),
        (2, False, True),
        (3, False, False),
        (4, False, False),
        (4, False, True),
        (5, False, False),
        (5, True, False),
        (6, False, False),
        (7, False, False),
    ],
)
def test_nd_left_matrix_multiply(
    matrix_stack, left_vector_stack, extra_dims, single_matrix, single_vector, D1, D2, num_dims
):
    """
    Given: Matrix and vector stacks with arbitrary higher dimensions
    When: Left matrix multiplying them
    Then: The matrix multiplication is correctly broadcast across the higher dimensions
    """
    if num_dims == 0:
        expected = matrix_stack @ left_vector_stack
    else:
        flattened_size = np.prod(extra_dims)

        # If single_* is True then just tile it out to match the flattened size so the loop below works
        flat_matrix = (
            np.reshape(matrix_stack, (flattened_size, D1, D2))
            if not single_matrix
            else np.tile(matrix_stack[None, ...], (flattened_size, 1, 1))
        )
        flat_vector = (
            np.reshape(left_vector_stack, (flattened_size, D2))
            if not single_vector
            else np.tile(left_vector_stack[None, ...], (flattened_size, 1))
        )

        flat_expected = np.empty((flattened_size, D1))
        for i in range(flattened_size):
            flat_expected[i, :] = flat_matrix[i, :, :] @ flat_vector[i, :]

        expected = np.reshape(flat_expected, extra_dims + (D1,))

    value = nd_left_matrix_multiply(vector_stack=left_vector_stack, matrix_stack=matrix_stack)
    np.testing.assert_allclose(expected, value, rtol=1e-13)


def test_nd_left_matrix_multiply_errors():
    """
    Given: Matrix and vector stacks with mismatched shapes
    When: Trying to matrix multiply them
    Then: The correct error is raised
    """
    with pytest.raises(ValueError, match="Inputs must have the same shape"):
        nd_left_matrix_multiply(
            vector_stack=np.random.random((1, 3, 4)), matrix_stack=np.random.random((5, 2, 3, 4))
        )

    with pytest.raises(ValueError, match="Cannot perform left-multiplication"):
        nd_left_matrix_multiply(
            vector_stack=np.random.random((4)), matrix_stack=np.random.random((4, 6))
        )


# Stopping at 7 for no real reason. We need 0 and 2 for sure and then others to confirm generality.
# single_matrix = True tests the case where the matrix has no higher dimensions. Probably only need to test it once
# but we do it twice just because.
@pytest.mark.parametrize(
    "num_dims, single_matrix, single_vector",
    [
        (0, False, False),
        (1, False, False),
        (2, False, False),
        (2, True, False),
        (2, False, True),
        (3, False, False),
        (3, True, False),
        (4, False, False),
        (5, False, False),
        (5, False, True),
        (6, False, False),
        (7, False, False),
    ],
)
def test_nd_right_matrix_multiply(
    matrix_stack, right_vector_stack, extra_dims, single_matrix, single_vector, D1, D2, num_dims
):
    """
    Given: Matrix and vector stacks with arbitrary higher dimensions
    When: Right matrix multiplying them
    Then: The matrix multiplication is correctly broadcast across the higher dimensions
    """
    if num_dims == 0:
        expected = right_vector_stack @ matrix_stack
    else:
        flattened_size = np.prod(extra_dims)

        # If single_* is True then just tile it out to match the flattened size so the loop below works
        flat_matrix = (
            np.reshape(matrix_stack, (flattened_size, D1, D2))
            if not single_matrix
            else np.tile(matrix_stack[None, ...], (flattened_size, 1, 1))
        )

        flat_vector = (
            np.reshape(right_vector_stack, (flattened_size, D1))
            if not single_vector
            else np.tile(right_vector_stack[None, ...], (flattened_size, 1))
        )

        flat_expected = np.empty((flattened_size, D2))
        for i in range(flattened_size):
            flat_expected[i, :] = flat_vector[i, :] @ flat_matrix[i, :, :]

        expected = np.reshape(flat_expected, extra_dims + (D2,))

    value = nd_right_matrix_multiply(vector_stack=right_vector_stack, matrix_stack=matrix_stack)
    np.testing.assert_allclose(expected, value, rtol=1e-13)


def test_nd_right_matrix_multiply_errors():
    """
    Given: Matrix and vector stacks with mismatched shapes
    When: Trying to matrix multiply them
    Then: The correct error is raised
    """
    with pytest.raises(ValueError, match="Inputs must have the same shape"):
        nd_left_matrix_multiply(
            vector_stack=np.random.random((1, 3, 4)), matrix_stack=np.random.random((5, 2, 3, 4))
        )

    with pytest.raises(ValueError, match="Cannot perform left-multiplication"):
        nd_left_matrix_multiply(
            vector_stack=np.random.random((4)), matrix_stack=np.random.random((4, 6))
        )
