"""Unittests for documentation examples."""

import pytest

import varmeta as vm

TEMP = "temp"
FORCE = "force"
VELOCITY = "vel"
MASS = "mass"


@pytest.fixture
def temperature():
    return vm.Var(
        key=TEMP,
        name="Temperature",
        units="Celsius",
        desciption="Ambient temperature",
        components=None,
    )


@pytest.fixture
def force():
    return vm.Var(
        key=FORCE,
        name="Force",
        units="N",
        desciption="Force vector",
        components=("x", "y", "z"),
        component_axis=1,
    )


class TestDocExamples:
    def test_var_creation(self, temperature, force):
        data_dct = {TEMP: 25.0, FORCE: [10.0, 20.0, 30.0]}

        var_dct = vm.VarDict({TEMP: temperature, FORCE: force})
        print(var_dct)
        print(data_dct)

    def test_unpack_1(self, temperature, force):
        # Vector variable (e.g., 3D force)
        data_dct = {TEMP: 25.0, FORCE: [10.0, 20.0, 30.0]}

        var_dct = vm.VarDict({TEMP: temperature, FORCE: force})
        vars, vals = vm.unpack(var_dct, data_dct)
        print(vars)
        # Output:
        # {'temperature': Temperature [Celsius], 'force_x': Force - x [N], 'force_y': Force - y [N], 'force_z': Force - z [N]} # NoQA: E501
        print(vals)
        # {'temperature': 25.0, 'force_x': 10.0, 'force_y': 20.0, 'force_z': 30.0} # NoQA: E501

    def test_dict_to_df(self, temperature, force):
        # Vector variable (e.g., 3D force)
        data_dct = {TEMP: 25.0, FORCE: [10.0, 20.0, 30.0]}

        var_dct = vm.VarDict({TEMP: temperature, FORCE: force})
        data_dct = {FORCE: [[200, 250, -30], [300, 350, -100]], TEMP: [30, 40]}
        df = vm.dict_to_df(var_dct, data_dct)
        print(df)
        data_dct = {TEMP: [30, 40], FORCE: [[200, 250, -30], [300, 350, -100]]}
        df = vm.dict_to_df(var_dct, data_dct)
        print(df)

    def test_records_to_df(self, temperature, force):
        # Vector variable (e.g., 3D force)
        var_dct = vm.VarDict({TEMP: temperature, FORCE: force})
        data_dict_lst = [
            {FORCE: [200, 250, -30], TEMP: 30},
            {FORCE: [300, 350, -100], TEMP: 40},
        ]
        df = vm.records_to_df(var_dct, data_dict_lst)
        print(df)

    def test_serialisation(self, temperature, force):
        var_dct = vm.VarDict({TEMP: temperature, FORCE: force})
        var_data = vm.vars_to_dict(var_dct)
        print(var_data)
        # Output:
        # {
        #   'temp': {'key': 'temp', 'name': 'Temperature', 'units': 'Celsius', 'desciption': 'Ambient temperature', 'components': None, 'component_axis': 0}, # NoQA: E501
        #   'force': {'key': 'force', 'name': 'Force', 'units': 'N', 'desciption': 'Force vector', 'components': ('x', 'y', 'z'), 'component_axis': 1}  # NoQA: E501
        # }
        var_dct_recreated = vm.vars_from_dict(var_data)
        for k, v in var_dct_recreated.items():
            print(f"{k}: {'matches!' if v == var_dct[k] else 'differs!'}")
