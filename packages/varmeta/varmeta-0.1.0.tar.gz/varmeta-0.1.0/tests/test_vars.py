"""Unittests for core module."""

from varmeta.vars import Var


class TestVar:
    def test_var_creation(self):
        var = Var(
            key="temp",
            name="temperature",
            units="Celsius",
            desciption="Ambient temperature",
            components=None,
        )
        assert var.name == "temperature"
        assert var.units == "Celsius"
        assert var.desciption == "Ambient temperature"
        assert var.components is None

    def test_var_str(self):
        var = Var(
            key="pressure",
            name="pressure",
            units="Pascal",
            desciption="Atmospheric pressure",
            components=None,
        )
        assert str(var) == "pressure [Pascal]"

    def test_var_ordering(self):
        var1 = Var(
            key="temp",
            name="temperature",
            units="Celsius",
            desciption="Ambient temperature",
            components=None,
        )
        var2 = Var(
            key="pressure",
            name="pressure",
            units="Pascal",
            desciption="Atmospheric pressure",
            components=None,
        )
        assert var1 > var2  # Based on name ordering

    def test_var_equality(self):
        var1 = Var(
            key="hum",
            name="humidity",
            units="Percent",
            desciption="Relative humidity",
            components=None,
        )
        var2 = Var(
            key="humidity",
            name="humidity",
            units="Percent",
            desciption="Relative humidity",
            components=None,
        )
        assert var1 == var2

    def test_var_inequality(self):
        var1 = Var(
            key="humidity",
            name="humidity",
            units="Percent",
            desciption="Relative humidity",
            components=None,
        )
        var2 = Var(
            key="temp",
            name="temperature",
            units="Celsius",
            desciption="Ambient temperature",
            components=None,
        )
        assert var1 != var2

    def test_hash_with_components(self):
        var = Var(
            key="vel",
            name="velocity",
            units="m/s",
            desciption="Speed of an object",
            components=("x", "y", "z"),
        )
        assert hash(var) != 0

    def test_unpack_axis_default(self):
        force = Var(
            key="F",
            name="force",
            units="N",
            desciption="A force",
            components=("x", "y", "z"),
        )
        data = [[10, 11], [20, 21], [30, 31]]
        subvars, subvals = force.unpack(data)
        print(subvars, subvals)
        assert len(subvals) == 3
        assert subvals[0] == [10, 11]
        assert subvars[0].name == "force - x"
        assert subvals[1] == [20, 21]
        assert subvars[1].name == "force - y"
        assert subvals[2] == [30, 31]
        assert subvars[2].name == "force - z"

    def test_unpack_axis_1(self):
        force = Var(
            key="F",
            name="force",
            units="N",
            desciption="A force",
            components=("x", "y"),
            component_axis=1,
        )
        data = [[10, 11], [20, 21], [30, 31]]
        subvars, subvals = force.unpack(data)
        print(subvars, subvals)
        assert len(subvals) == 2
        assert subvals[0] == [10, 20, 30]
        assert subvars[0].name == "force - x"
        assert subvals[1] == [11, 21, 31]
        assert subvars[1].name == "force - y"

    def test_round_trip_dict(self):
        force = Var(
            key="F",
            name="force",
            units="N",
            desciption="A force",
            components=("x", "y", "z"),
        )
        dct = force.to_dict()
        print(dct)
        new_var = Var(**dct)
        assert new_var == force
