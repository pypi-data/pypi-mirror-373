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

import numpy as np
import pytest

# skip if matlab API is not found.
pytest.importorskip("matlab")

from gemseo import create_discipline  # noqa: E402
from gemseo import create_scenario  # noqa: E402
from gemseo.algos.design_space import DesignSpace  # noqa: E402

from .matlab_files import MATLAB_FILES_DIR_PATH  # noqa: E402


def build_matlab_disciplines():
    """Build all matlab discipline for Sellar problem.

    Jacobian matrices are returned by matlab functions.
    """
    matlab_data = MATLAB_FILES_DIR_PATH / "sellar_data.mat"

    sellar1 = create_discipline(
        "MatlabDiscipline",
        matlab_function_path="Sellar1.m",
        matlab_data_path=matlab_data,
        name="sellar_1",
        root_search_path=MATLAB_FILES_DIR_PATH,
        is_jac_returned_by_func=True,
    )

    sellar2 = create_discipline(
        "MatlabDiscipline",
        matlab_function_path="Sellar2.m",
        matlab_data_path=matlab_data,
        root_search_path=MATLAB_FILES_DIR_PATH,
        name="sellar_2",
        is_jac_returned_by_func=True,
    )

    sellar_system = create_discipline(
        "MatlabDiscipline",
        matlab_function_path="SellarSystem.m",
        matlab_data_path=matlab_data,
        root_search_path=MATLAB_FILES_DIR_PATH,
        name="sellar_system",
        is_jac_returned_by_func=True,
    )

    return [sellar1, sellar2, sellar_system]


def build_matlab_scenario():
    """Build the Sellar scenario for matlab tests."""
    design_space = DesignSpace()
    design_space.add_variable("x", lower_bound=0.0, upper_bound=10.0, value=np.ones(1))
    design_space.add_variable(
        "z",
        2,
        lower_bound=(-10, 0.0),
        upper_bound=(10.0, 10.0),
        value=np.array([4.0, 3.0]),
    )
    design_space.add_variable(
        "y_1", lower_bound=-100.0, upper_bound=100.0, value=np.ones(1)
    )
    design_space.add_variable(
        "y_2", lower_bound=-100.0, upper_bound=100.0, value=np.ones(1)
    )

    disciplines = build_matlab_disciplines()
    scenario = create_scenario(
        disciplines,
        formulation_name="IDF",
        objective_name="obj",
        design_space=design_space,
    )

    scenario.add_constraint("c_1", "ineq")
    scenario.add_constraint("c_2", "ineq")

    return scenario


def test_matlab_jacobians_sellar1():
    """Check that jacobian matrices returned by matlab functions are correct with
    respect to finite difference computation for Sellar1."""
    sellar1, sellar2, sellar_system = build_matlab_disciplines()

    threshold = 1e-7
    step = 1e-7

    assert sellar1.check_jacobian(step=step, threshold=threshold)
    assert sellar2.check_jacobian(step=step, threshold=threshold)
    assert sellar_system.check_jacobian(step=step, threshold=threshold)


def test_matlab_optim_results():
    """Test obtained optimal values when solving sellar problem with matlab discipline.

    Jacobians are computed.
    """
    scenario = build_matlab_scenario()
    scenario.execute(algo_name="SLSQP", max_iter=20)

    # ref values are taken from the doc "Sellar Problem"

    optim_res = scenario.optimization_result
    assert optim_res.f_opt == pytest.approx(3.18339, rel=0.001)

    x_opt = scenario.design_space.get_current_value(as_dict=True)
    assert x_opt["x"] == pytest.approx(0.0, abs=0.0001)
    assert x_opt["z"][0] == pytest.approx(1.9776, abs=0.0001)
    assert x_opt["z"][1] == pytest.approx(0.0, abs=0.0001)
    assert x_opt["y_1"] == pytest.approx(3.16, abs=0.0001)
    assert x_opt["y_2"] == pytest.approx(3.75528, abs=0.0001)
