"""Unittests for vals module."""

import numpy as np
from numpy.testing import assert_array_equal

from varmeta.vars import Var


class TestVar:
    def test_numpy_unpack_axis_default(self):
        force = Var(
            key="F",
            name="force",
            units="N",
            desciption="A force",
            components=("x", "y", "z"),
        )
        data = np.array([[10, 11], [20, 21], [30, 31]])
        subvars, subvals = force.unpack(data)
        print(subvars, subvals)
        assert len(subvals) == 3
        assert_array_equal(subvals[0], np.array([10, 11]))
        assert subvars[0].name == "force - x"
        assert_array_equal(subvals[1], np.array([20, 21]))
        assert subvars[1].name == "force - y"
        assert_array_equal(subvals[2], np.array([30, 31]))
        assert subvars[2].name == "force - z"

    def test_numpy_unpack_axis_1(self):
        force = Var(
            key="F",
            name="force",
            units="N",
            desciption="A force",
            components=("x", "y"),
            component_axis=1,
        )
        data = np.array([[10, 11], [20, 21], [30, 31]])
        subvars, subvals = force.unpack(data)
        print(subvars, subvals)
        assert len(subvals) == 2
        assert_array_equal(subvals[0], np.array([10, 20, 30]))
        assert subvars[0].name == "force - x"
        assert_array_equal(subvals[1], np.array([11, 21, 31]))
        assert subvars[1].name == "force - y"
