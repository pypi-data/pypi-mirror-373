# Copyright 2021 IRT Saint Exupéry, https://www.irt-saintexupery.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
from __future__ import annotations

import pickle
import re

import pytest
from gemseo import configure
from gemseo.algos.design_space import DesignSpace
from gemseo.scenarios.doe_scenario import DOEScenario
from numpy import array
from numpy import compress

from gemseo_matlab.engine import get_matlab_engine
from gemseo_matlab.matlab_data_processor import load_matlab_file
from gemseo_matlab.matlab_discipline import MatlabDiscipline

from .matlab_files import MATLAB_FILES_DIR_PATH

MATLAB_SIMPLE_FUNC = MATLAB_FILES_DIR_PATH / "dummy_test.m"
MATLAB_PARALLEL_FUNC = MATLAB_FILES_DIR_PATH / "dummy_test_parallel.m"
MATLAB_COMPLEX_FUNC = MATLAB_FILES_DIR_PATH / "dummy_complex_fct.m"
MATLAB_SIMPLE_FUNC_MULTIDIM = MATLAB_FILES_DIR_PATH / "dummy_test_multidim.m"
MATLAB_SIMPLE_FUNC_MULTIDIM_JAC = MATLAB_FILES_DIR_PATH / "dummy_test_multidim_jac.m"
FCT_MULTIDIM_DATASET = MATLAB_FILES_DIR_PATH / "dummy_file_multidim_fct.mat"


def test_engine_property():
    """Check the engine property."""
    mat = MatlabDiscipline(MATLAB_SIMPLE_FUNC)
    assert not mat.engine.is_closed


def test_inputs_from_matlab():
    """Test input variables read from matlab file."""
    mat2 = MatlabDiscipline(MATLAB_COMPLEX_FUNC)
    assert mat2._MatlabDiscipline__inputs == ["a", "b", "c", "d", "e", "f"]


def test_inputs_from_param():
    """Test input variables given as input param."""
    mat = MatlabDiscipline(
        MATLAB_COMPLEX_FUNC, input_names=["v1", "v2", "v3", "v4", "v5", "v6"]
    )
    assert mat._MatlabDiscipline__inputs == ["v1", "v2", "v3", "v4", "v5", "v6"]


def test_outputs():
    """Test output variables."""
    mat2 = MatlabDiscipline(MATLAB_COMPLEX_FUNC)
    assert mat2._MatlabDiscipline__outputs == ["x", "y", "z"]


def test_inputs_and_outputs_size_unknown():
    """Test that size of input and output variables are unknown when initializing
    without matlab data."""
    mat1 = MatlabDiscipline(MATLAB_SIMPLE_FUNC)

    assert mat1._MatlabDiscipline__inputs_size["x"] == -1
    assert mat1._MatlabDiscipline__outputs_size["y"] == -1
    assert mat1._MatlabDiscipline__is_size_known is False


def test_inputs_and_outputs_size_known_eval():
    """Test that size of input and output variables are known after evaluating matlab
    function."""
    mat2 = MatlabDiscipline(MATLAB_SIMPLE_FUNC_MULTIDIM)
    mat2.execute({"x": array([1, 1]), "y": array([1])})

    assert mat2._MatlabDiscipline__inputs_size["x"] == 2
    assert mat2._MatlabDiscipline__inputs_size["y"] == 1
    assert mat2._MatlabDiscipline__outputs_size["z1"] == 2
    assert mat2._MatlabDiscipline__outputs_size["z2"] == 1
    assert mat2._MatlabDiscipline__is_size_known is True


def test_inputs_and_outputs_size_known_init():
    """Test the size of input and output variables are known when initializing with
    matlab data."""
    mat2 = MatlabDiscipline(
        MATLAB_SIMPLE_FUNC_MULTIDIM, matlab_data_path=FCT_MULTIDIM_DATASET
    )

    assert mat2._MatlabDiscipline__inputs_size["x"] == 2
    assert mat2._MatlabDiscipline__inputs_size["y"] == 1
    assert mat2._MatlabDiscipline__outputs_size["z1"] == 2
    assert mat2._MatlabDiscipline__outputs_size["z2"] == 1
    assert mat2._MatlabDiscipline__is_size_known is True


def test_jac_output_names_error_wrong_name():
    """Test that jacobians output raise an error if names are wrong."""
    with pytest.raises(ValueError) as excp:
        MatlabDiscipline(
            MATLAB_FILES_DIR_PATH / "dummy_test_jac_wrong.m",
            is_jac_returned_by_func=True,
        )
    assert (
        str(excp.value) == "Jacobian terms ['jac_dy_dx'] are not found "
        "in the list of conventional names. "
        "It is reminded that jacobian terms' name "
        "should be such as 'jac_dout_din'"
    )


def test_jac_output_names_error_missing_term():
    """Test that jacobians output raise an error if a term is missing."""
    with pytest.raises(
        ValueError,
        match=re.escape(
            "The number of jacobian outputs "
            "does not correspond to what it "
            "should be. Make sure that all "
            "outputs have a jacobian matrix "
            "with respect to inputs."
        ),
    ):
        MatlabDiscipline(
            MATLAB_FILES_DIR_PATH / "dummy_test_multidim_jac_wrong.m",
            is_jac_returned_by_func=True,
        )


def test_jac_output_names():
    """Test that jacobians output name are detected when returning by the main
    function."""
    mat = MatlabDiscipline(
        MATLAB_SIMPLE_FUNC_MULTIDIM_JAC, is_jac_returned_by_func=True
    )

    assert mat._MatlabDiscipline__jac_output_names == [
        "jac_dz1_dx",
        "jac_dz1_dy",
        "jac_dz2_dx",
        "jac_dz2_dy",
    ]


def test_jac_output_indices():
    """Test that jacobians output have the right indices."""
    mat = MatlabDiscipline(
        MATLAB_SIMPLE_FUNC_MULTIDIM_JAC, is_jac_returned_by_func=True
    )

    assert mat._MatlabDiscipline__jac_output_indices == [2, 3, 4, 5]


def test_init_default_data():
    """Test that data are correctly initialized."""
    mat = MatlabDiscipline(
        MATLAB_COMPLEX_FUNC,
        matlab_data_path=MATLAB_FILES_DIR_PATH / "dummy_complex_fct_database.mat",
    )
    assert array(mat.default_input_data["a"]) == pytest.approx(
        array([[[1, 1], [1, 1]], [[1, 1], [1, 1]]])
    )
    assert array(mat.default_input_data["b"]) == pytest.approx(
        array([[[1, 1], [1, 1]], [[1, 1], [1, 1]]])
    )
    assert mat.default_input_data["c"] == pytest.approx(2)
    assert array(mat.default_input_data["d"]) == pytest.approx(array([1, 2]))
    assert mat.default_input_data["e"] == pytest.approx(1)
    assert mat.default_input_data["f"] == pytest.approx(1)


def test_search_file_error_not_found():
    """Test that an error is raised if file is not found."""
    with pytest.raises(
        IOError,
        match=re.escape("No file: dummy_test.m, found in directory: non_existing."),
    ):
        MatlabDiscipline("dummy_test.m", root_search_path="non_existing")


def test_search_file_error_two_files_found():
    """Test that an error is raised if two files are found."""
    with pytest.raises(IOError) as excp:
        MatlabDiscipline("dummy_test.m", root_search_path=MATLAB_FILES_DIR_PATH)
    assert (
        str(excp.value)
        == "At least two files dummy_test.m were "
        "in directory {}\n File one: {};"
        "\n File two: {}.".format(
            MATLAB_FILES_DIR_PATH,
            MATLAB_SIMPLE_FUNC,
            MATLAB_FILES_DIR_PATH / "matlab_files_bis_test" / "dummy_test.m",
        )
    )


def test_search_file():
    """Test that file is found."""
    mat = MatlabDiscipline(
        "dummy_test_multidim.m", root_search_path=MATLAB_FILES_DIR_PATH
    )
    assert mat._MatlabDiscipline__inputs == ["x", "y"]


def test_check_existing_function():
    """Test an existing user-made function."""
    mat = MatlabDiscipline(MATLAB_SIMPLE_FUNC)
    assert mat.function_name == "dummy_test"


def test_check_function_builtin():
    """Test a built-in function."""
    mat = MatlabDiscipline("cos", input_names=["x"], output_names=["y"])
    assert mat.function_name == "cos"


def test_run_builtin():
    """Test that built-in matlab function is correctly called and returned right
    values."""
    mat = MatlabDiscipline("cos", input_names=["x"], output_names=["out"])
    mat.execute({"x": array([0])})
    assert mat.io.data["out"] == pytest.approx(1)


@pytest.mark.parametrize("cleaning_interval", [0, 1])
def test_run_user(cleaning_interval: int):
    """Test that user matlab function is correctly called and returned right values."""
    mat = MatlabDiscipline(MATLAB_SIMPLE_FUNC, cleaning_interval=cleaning_interval)
    mat.execute({"x": array([2])})
    assert mat.io.data["y"] == pytest.approx(4)


def test_run_user_new_names():
    """Test that user matlab function is correctly called and returned right values when
    new names are prescribed for inputs and outputs."""
    mat = MatlabDiscipline(
        MATLAB_SIMPLE_FUNC, input_names=["in1"], output_names=["out"]
    )
    mat.execute({"in1": array([3])})
    assert mat.io.data["out"] == pytest.approx(9)


def test_run_user_multidim():
    """Test that user matlab function is correctly called and returned right values."""
    mat = MatlabDiscipline(
        MATLAB_SIMPLE_FUNC_MULTIDIM, matlab_data_path=FCT_MULTIDIM_DATASET
    )
    mat.execute({"x": array([1, 2]), "y": array([3])})
    assert array(mat.io.data["z1"]) == pytest.approx(array([1, 5]))
    assert mat.io.data["z2"] == pytest.approx(11)


def test_run_user_multidim_no_extension_data():
    """Test that an input matlab data file can be prescribed without extension."""
    mat = MatlabDiscipline(
        "dummy_test_multidim.m",
        matlab_data_path="dummy_file_multidim_fct",
        root_search_path=MATLAB_FILES_DIR_PATH,
    )
    mat.execute({"x": array([1, 2]), "y": array([3])})
    assert array(mat.io.data["z1"]) == pytest.approx(array([1, 5]))
    assert mat.io.data["z2"] == pytest.approx(11)


def test_run_user_multidim_jac():
    """Test that user matlab function is correctly called and returned right values when
    jacobian is defined."""
    mat = MatlabDiscipline(
        MATLAB_SIMPLE_FUNC_MULTIDIM_JAC,
        matlab_data_path=FCT_MULTIDIM_DATASET,
        is_jac_returned_by_func=True,
    )
    mat.execute({"x": array([1, 2]), "y": array([3])})
    assert array(mat.jac["z1"]["x"]) == pytest.approx(array([[2, 3], [0, 4]]))
    assert array(mat.jac["z1"]["y"]) == pytest.approx(array([[0], [54]]))
    assert array(mat.jac["z2"]["x"]) == pytest.approx(array([[4, 0]]))
    assert array(mat.jac["z2"]["y"]) == pytest.approx(array([[6]]))
    assert len(mat.io.data) == 4


def test_run_user_multidim_jac_wrong_size():
    """Test that user matlab function is correctly called and returned right values when
    jacobian is defined."""
    mat = MatlabDiscipline(
        MATLAB_FILES_DIR_PATH / "dummy_test_multidim_jac_wrong_size.m",
        matlab_data_path=FCT_MULTIDIM_DATASET,
        is_jac_returned_by_func=True,
    )
    with pytest.raises(ValueError) as excp:
        mat.execute({"x": array([1, 2]), "y": array([3])})

    assert str(excp.value) == (
        "Jacobian term 'jac_dz1_dx' has the wrong size "
        "(1, 4) whereas it should be (2, 2)."
    )


def test_save_data(tmp_wd):
    """Test that discipline data are correctly exported into a matlab file."""
    mat = MatlabDiscipline(MATLAB_SIMPLE_FUNC)
    mat.execute({"x": array([2])})
    output_file = "output_file.mat"
    mat.save_data_to_matlab(output_file)
    written_data = load_matlab_file(output_file)
    assert array(written_data["x"]) == pytest.approx(2)
    assert array(written_data["y"]) == pytest.approx(4)


def test_serialize(tmp_path):
    """Test that MatlabDiscipline can be serialized."""
    mat = MatlabDiscipline(MATLAB_SIMPLE_FUNC)

    file_name = "mat_disc.pk"
    with open(tmp_path / file_name, "wb") as f:
        pickle.dump(mat, f)

    # Clean lru_cache so a different engine is built
    get_matlab_engine.cache_clear()

    with open(tmp_path / file_name, "rb") as f:
        new_disc = pickle.load(f)

    out = new_disc.execute({"x": array([2])})
    assert out["y"] == pytest.approx(4)


@pytest.mark.slow
def test_parallel():
    """Test multiprocessing with matlab discipline.

    We check that the outputs are correctly computed from different process ID.
    """
    mat = MatlabDiscipline(MATLAB_PARALLEL_FUNC)

    ds = DesignSpace()
    ds.add_variable("x", lower_bound=-10, upper_bound=10)

    scenario = DOEScenario([mat], "y", ds, formulation_name="DisciplinaryOpt")
    scenario.add_observable("pid")

    n_samples = 10
    scenario.execute(algo_name="DiagonalDOE", n_samples=n_samples, n_processes=2)
    outputs, _ = scenario.formulation.optimization_problem.database.get_history(
        function_names=["pid", "y"]
    )

    # split outputs in two separate arrays depending on PID
    outputs = array(outputs)
    pid_1 = outputs[0, 0]
    out_1 = compress(outputs[:, 0] == pid_1, outputs, axis=0)
    out_2 = compress(outputs[:, 0] != pid_1, outputs, axis=0)

    assert out_1.shape[0] != n_samples
    assert out_2.shape[0] == n_samples - out_1.shape[0]


@pytest.mark.slow
@pytest.mark.parametrize("enable_discipline_statistics", [True, False])
def test_use_of_configure(
    enable_discipline_statistics: bool, enable_function_statistics: bool
) -> None:
    """Test that the use of ``gemseo.configure()`` does not change the behaviour.

    Issues may happen by using the cleaning interval option
    since it needs the access of statistics.

    Inspired from the test: ``test_parallel``.
    """
    configure(
        enable_discipline_statistics=enable_discipline_statistics,
        enable_function_statistics=enable_function_statistics,
    )

    mat = MatlabDiscipline(MATLAB_PARALLEL_FUNC, cleaning_interval=2)

    ds = DesignSpace()
    ds.add_variable("x", lower_bound=-10, upper_bound=10)

    scenario = DOEScenario([mat], "y", ds, formulation_name="DisciplinaryOpt")
    scenario.add_observable("pid")

    n_samples = 4
    scenario.execute(algo_name="DiagonalDOE", n_samples=n_samples, n_processes=2)
    outputs, _ = scenario.formulation.optimization_problem.database.get_history(
        function_names=["pid", "y"]
    )

    # split outputs in two separate arrays depending on PID
    outputs = array(outputs)
    pid_1 = outputs[0, 0]
    out_1 = compress(outputs[:, 0] == pid_1, outputs, axis=0)
    out_2 = compress(outputs[:, 0] != pid_1, outputs, axis=0)

    assert out_1.shape[0] != n_samples
    assert out_2.shape[0] == n_samples - out_1.shape[0]
