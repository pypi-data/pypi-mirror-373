from __future__ import annotations

import collections.abc
import typing

import PySide6.QtGui

__all__: list[str] = ["Matrix4x4"]

class Matrix4x4:
    """
    A 4x4 transformation matrix.
    """

    @staticmethod
    def identity_matrix() -> Matrix4x4:
        """
        Construct a new identity matrix.
        """

    @staticmethod
    def rotation_x_matrix(rx: typing.SupportsFloat) -> Matrix4x4:
        """
        Construct a new rotation matrix in the x axis.
        """

    @staticmethod
    def rotation_y_matrix(ry: typing.SupportsFloat) -> Matrix4x4:
        """
        Construct a new rotation matrix in the y axis.
        """

    @staticmethod
    def rotation_z_matrix(rz: typing.SupportsFloat) -> Matrix4x4:
        """
        Construct a new rotation matrix in the z axis.
        """

    @staticmethod
    def scale_matrix(
        sx: typing.SupportsFloat, sy: typing.SupportsFloat, sz: typing.SupportsFloat
    ) -> Matrix4x4:
        """
        Construct a new scale matrix.
        """

    @staticmethod
    def transformation_matrix(
        sx: typing.SupportsFloat,
        sy: typing.SupportsFloat,
        sz: typing.SupportsFloat,
        rx: typing.SupportsFloat,
        ry: typing.SupportsFloat,
        rz: typing.SupportsFloat,
        dx: typing.SupportsFloat,
        dy: typing.SupportsFloat,
        dz: typing.SupportsFloat,
    ) -> Matrix4x4:
        """
        Construct a new transformation matrix made from scale, rotation and translation.
        """

    @staticmethod
    def translation_matrix(
        dx: typing.SupportsFloat, dy: typing.SupportsFloat, dz: typing.SupportsFloat
    ) -> Matrix4x4:
        """
        Construct a new translation matrix.
        """

    @typing.overload
    def __init__(self) -> None:
        """
        Construct with uninitialised memory.
        """

    @typing.overload
    def __init__(
        self,
        arg0: tuple[
            tuple[
                typing.SupportsFloat,
                typing.SupportsFloat,
                typing.SupportsFloat,
                typing.SupportsFloat,
            ],
            tuple[
                typing.SupportsFloat,
                typing.SupportsFloat,
                typing.SupportsFloat,
                typing.SupportsFloat,
            ],
            tuple[
                typing.SupportsFloat,
                typing.SupportsFloat,
                typing.SupportsFloat,
                typing.SupportsFloat,
            ],
            tuple[
                typing.SupportsFloat,
                typing.SupportsFloat,
                typing.SupportsFloat,
                typing.SupportsFloat,
            ],
        ],
    ) -> None:
        """
        Construct from tuples.
        """

    @typing.overload
    def __init__(self, other: Matrix4x4) -> None:
        """
        Copy from another matrix.
        """

    @typing.overload
    def __init__(self, arg0: collections.abc.Buffer) -> None: ...
    @typing.overload
    def __init__(self, arg0: PySide6.QtGui.QMatrix4x4) -> None: ...
    @typing.overload
    def __mul__(self, other: Matrix4x4) -> Matrix4x4:
        """
        Multiply this matrix with another matrix.
        """

    @typing.overload
    def __mul__(
        self,
        other: list[
            tuple[typing.SupportsFloat, typing.SupportsFloat, typing.SupportsFloat]
        ],
    ) -> list[tuple[float, float, float]]:
        """
        Multiply this matrix with a sequence of vectors.
        """

    def __repr__(self) -> str: ...
    def almost_equal(self, other: Matrix4x4, err: typing.SupportsFloat = 1e-06) -> bool:
        """
        Check if this matrix is almost equal to another matrix.
        """

    def decompose(
        self,
    ) -> tuple[
        tuple[float, float, float],
        tuple[float, float, float],
        tuple[float, float, float],
    ]:
        """
        Decompose the matrix into scale, rotation and displacement tuples.
        Note that these values may be incorrect if the matrix is more complex
        Recompose the matrix and compare with the original to check
        """

    def get_element(self, i: typing.SupportsInt, j: typing.SupportsInt) -> float:
        """
        Get an element in the matrix.
        """

    def inverse(self) -> Matrix4x4:
        """
        Compute the inverse of this matrix.
        Raises RuntimeError if the matrix cannot be inverted.
        """

    def rotate_x(self, rx: typing.SupportsFloat) -> Matrix4x4:
        """
        Rotate this matrix by the specified amount in the x axis.
        """

    def rotate_y(self, ry: typing.SupportsFloat) -> Matrix4x4:
        """
        Rotate this matrix by the specified amount in the y axis.
        """

    def rotate_z(self, rz: typing.SupportsFloat) -> Matrix4x4:
        """
        Rotate this matrix by the specified amount in the z axis.
        """

    def scale(
        self,
        sx: typing.SupportsFloat,
        sy: typing.SupportsFloat,
        sz: typing.SupportsFloat,
    ) -> Matrix4x4:
        """
        Scale this matrix by the specified amount.
        """

    def set_element(
        self, i: typing.SupportsInt, j: typing.SupportsInt, value: typing.SupportsFloat
    ) -> None:
        """
        Set an element in the matrix.
        """

    def to_qt(self) -> PySide6.QtGui.QMatrix4x4: ...
    def translate(
        self,
        dx: typing.SupportsFloat,
        dy: typing.SupportsFloat,
        dz: typing.SupportsFloat,
    ) -> Matrix4x4:
        """
        Translate this matrix by the specified amount.
        """
