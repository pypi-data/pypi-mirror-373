"""Linear algebra functions."""

import numpy as np


def nd_left_matrix_multiply(*, vector_stack: np.ndarray, matrix_stack: np.ndarray) -> np.ndarray:
    """
    Left-multiply an arbitrarily dimensioned stack of vectors by a similarly dimensioned stack of matrices.

    In math:

        result = M @ v

    where M is a matrix with dimensions ([n1, ...nn], D1, D2)
    and v is a vector with dimensions ([n1, ...nn], D2).

    The higher-order dimensions (n1, ...nn) can be anything (or nothing), but they must be the same for M and v.
    A special case where either the matrix or vector has NO higher-order dimensions is also allowed; the result will be
    the single matrix/vector broadcast over the higher-order dimensionality of the other element.

    Processing inputs with different numbers of higher-order dummy dimensions (i.e., dimension of length 1), while
    technically possible, is not supported because it would be unclear which input should set the output shape.

    Parameters
    ----------
    vector_stack : np.ndarray
        ([n1, ...nn], D2) ND stack of vectors with length D2

    matrix_stack : np.ndarray
        ([n1, ...nn], D1, D2) ND stack of matrices with shape (D1, D2)


    Returns
    -------
    np.ndarray
        ([n1, ...nn], D1) ND stack of vectors with length D1
    """
    _check_nd_dimensionality(matrix_stack=matrix_stack, vector_stack=vector_stack)

    matrix_shape = matrix_stack.shape[-2:]
    vector_size = vector_stack.shape[-1]
    if matrix_shape[-1] != vector_size:
        raise ValueError(
            f"Cannot perform left-multiplication with shapes {matrix_shape} @ {vector_size}."
        )

    result = np.sum(matrix_stack * vector_stack[..., None, :], axis=-1)
    return result


def nd_right_matrix_multiply(*, vector_stack: np.ndarray, matrix_stack: np.ndarray) -> np.ndarray:
    """
    Right-multiply an arbitrarily dimensioned stack of vectors by a similarly dimensioned stack of matrices.

    In math:

        result = v @ M

    where M is a matrix with dimensions ([n1, ...nn], D1, D2)
    and v is a vector with dimensions ([n1, ...nn], D1).

    The higher-order dimensions (n1, ...nn) can be anything (or nothing), but they must be the same for M and v.
    A special case where either the matrix or vector has NO higher-order dimensions is also allowed; the result will be
    the single matrix/vector broadcast over the higher-order dimensionality of the other element.

    Processing inputs with different numbers of higher-order dummy dimensions (i.e., dimension of length 1), while
    technically possible, is not supported because it would be unclear which input should set the output shape.

    Parameters
    ----------
    vector_stack : np.ndarray
        ([n1, ...nn], D2) ND stack of vectors with length D1

    matrix_stack : np.ndarray
        ([n1, ...nn], D1, D2) ND stack of matrices with shape (D1, D2)


    Returns
    -------
    np.ndarray
        ([n1, ...nn], D1) ND stack of vectors with length D2
    """
    _check_nd_dimensionality(matrix_stack=matrix_stack, vector_stack=vector_stack)

    matrix_shape = matrix_stack.shape[-2:]
    vector_size = vector_stack.shape[-1]
    if matrix_shape[-2] != vector_size:
        raise ValueError(
            f"Cannot perform left-multiplication with shapes {vector_size} @ {matrix_shape}."
        )

    result = np.sum(matrix_stack * vector_stack[..., :, None], axis=-2)
    return result


def _check_nd_dimensionality(matrix_stack, vector_stack):
    """
    Check that the matrix and vector stacks have higher-order dimensions that can be broadcast together.

    Enforces matrix stack shape[:-2] equals vector stack shape[:-1]. Raises a ValueError if the condition is not met.

    A special case of a matrix or vector with no higher-order dimensions is allowed.
    """
    matrix_ND_shape = matrix_stack.shape[:-2]
    vector_ND_shape = vector_stack.shape[:-1]
    if matrix_ND_shape and vector_ND_shape and matrix_ND_shape != vector_ND_shape:
        raise ValueError(
            f"Inputs must have the same shape for all but the last dimensions. "
            f"{matrix_ND_shape} != {vector_ND_shape}"
        )
