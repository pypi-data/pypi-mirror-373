# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)
# @author Jan-Lukas Wynen
from __future__ import annotations

from .._scipp import core as _cpp
from ..typing import VariableLikeType
from ._cpp_wrapper_util import call_func as _call_cpp_func


def logical_not(x: VariableLikeType) -> VariableLikeType:
    """Element-wise logical negation.

    Equivalent to::

        ~a

    Parameters
    ----------
    x:
        Input data.

    Returns
    -------
    :
        The logical inverse of ``x``.
    """
    return _call_cpp_func(_cpp.logical_not, x)  # type: ignore[return-value]


def logical_and(a: VariableLikeType, b: VariableLikeType) -> VariableLikeType:
    """Element-wise logical and.

    Equivalent to::

        a & b

    Parameters
    ----------
    a:
        First input.
    b:
        Second input.

    Returns
    -------
    :
        The logical and of the elements of ``a`` and ``b``.
    """
    return _call_cpp_func(_cpp.logical_and, a, b)  # type: ignore[return-value]


def logical_or(a: VariableLikeType, b: VariableLikeType) -> VariableLikeType:
    """Element-wise logical or.

    Equivalent to::

        a | b

    Parameters
    ----------
    a:
        First input.
    b:
        Second input.

    Returns
    -------
    :
        The logical or of the elements of ``a`` and ``b``.
    """
    return _call_cpp_func(_cpp.logical_or, a, b)  # type: ignore[return-value]


def logical_xor(a: VariableLikeType, b: VariableLikeType) -> VariableLikeType:
    """Element-wise logical exclusive-or.

    Equivalent to::

        a ^ b

    Parameters
    ----------
    a:
        First input.
    b:
        Second input.

    Returns
    -------
    :
        The logical exclusive-or of the elements of ``a`` and ``b``.
    """
    return _call_cpp_func(_cpp.logical_xor, a, b)  # type: ignore[return-value]
