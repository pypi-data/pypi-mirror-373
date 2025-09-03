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
# Copyright (c) 2018 IRT-AESE.
# All rights reserved.
# Contributors:
#    INITIAL AUTHORS - API and implementation and/or documentation
#        :author: François Gallard: initial Scilab version
#        :author: Arthur Piat: conversion Scilab to Matlab and complementary features
#        :author: Nicolas Roussouly: GEMSEO integration
"""Definition of the Matlab discipline.

Overview
--------

This module contains the :class:`.MatlabDiscipline`
which enables to automatically create a wrapper of any Matlab function.
This class can be used in order to interface any Matlab code
and to use it inside a MDO process.
"""

from __future__ import annotations

import logging
import os
import re
from multiprocessing import Value
from os.path import exists
from os.path import join
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar
from typing import Final

import matlab.engine
import numpy as np
from gemseo.core.discipline.discipline import Discipline
from gemseo.core.parallel_execution.callable_parallel_execution import (
    CallableParallelExecution,
)
from gemseo.utils.portable_path import to_os_specific

from gemseo_matlab.engine import MatlabEngine
from gemseo_matlab.engine import get_matlab_engine
from gemseo_matlab.matlab_data_processor import MatlabDataProcessor
from gemseo_matlab.matlab_data_processor import convert_array_from_matlab
from gemseo_matlab.matlab_data_processor import double2array
from gemseo_matlab.matlab_data_processor import load_matlab_file
from gemseo_matlab.matlab_data_processor import save_matlab_file
from gemseo_matlab.matlab_parser import MatlabParser

if TYPE_CHECKING:
    from collections.abc import Mapping
    from collections.abc import MutableMapping
    from collections.abc import Sequence
    from multiprocessing.sharedctypes import Synchronized

    from gemseo.typing import StrKeyMapping

LOGGER = logging.getLogger(__name__)


class MatlabDiscipline(Discipline):
    """Base wrapper for matlab discipline.

    Generates a discipline of given matlab function and wrap it to be executed with
    GEMSEO. Can be used on encrypted, MATLAB build-in and user made function.

    Examples:
        >>> # build the discipline from the MATLAB function "function.m"
        >>> disc = MatlabDiscipline("function.m")
        >>> # Execute the discipline
        >>> disc.execute({"x": array([2.0]), "y": array([1.0])})
        >>>
        >>> # build discipline with initial data from MATLAB file
        >>> disc = MatlabDiscipline("function.m", matlab_data_file="data.mat")
        >>> # execute discipline from default values
        >>> disc.execute()
        >>>
        >>> # build discipline from MATLAB file located in matlab_files directory
        >>> disc = MatlabDiscipline("function.m", root_search_path="matlab_files")
        >>>
        >>> # build discipline with jacobian returned by the matlab function
        >>> disc = MatlabDiscipline("function.m", is_jac_returned_by_func=True)
        >>> disc.execute({"x": array([2.0]), "y": array([1.0])})
        >>> # print jacboian values
        >>> print(disc.jac)

    Note:
        If ``is_jac_returned_by_func`` is True, jacobian matrices must be returned
        by the matlab function itself. In such case, function outputs must contain
        standard output as well as new outputs for jacobian terms. These new
        outputs must follow naming convention described in function
        :meth:`.MatlabDiscipline._get_jac_name`. They can be returned
        in any order.
    """

    JAC_PREFIX: ClassVar[str] = "jac_"

    _ATTR_NOT_TO_SERIALIZE = Discipline._ATTR_NOT_TO_SERIALIZE.union([
        "_MatlabDiscipline__engine",
        "__n_executions",
    ])

    __TMP_ATTR_FOR_SERIALIZED_ENGINE_NAME: Final[str] = "matlab_engine_name"

    __TMP_ATTR_FOR_SERIALIZED_PATHS: Final[str] = "matlab_paths"

    __n_executions: Synchronized[int]
    """The number of calls to the execution method."""

    def __init__(
        self,
        matlab_function_path: str | Path,
        input_names: Sequence[str] = (),
        output_names: Sequence[str] = (),
        add_subfold_path: bool = False,
        root_search_path: str | Path = "",
        matlab_engine_name: str = "matlab",
        matlab_data_path: str | Path = "",
        name: str = "",
        cleaning_interval: int = 0,
        check_opt_data: bool = True,
        is_jac_returned_by_func: bool = False,
    ) -> None:
        """
        Args:
            matlab_function_path: The path of the Matlab file or Name of the function.
            input_names: The input variables.
            output_names: The output variables.
            add_subfold_path: Whether to add all sub-folder to matlab engine path.
            root_search_path: The root directory to launch the research of matlab file.
            matlab_engine_name: The name of the matlab engine used for this discipline.
            matlab_data_path: The .mat path containing the default values of data.
            cleaning_interval: The iteration interval at which matlab workspace is
                cleaned.
            check_opt_data: Whether to check input and output data of
                discipline.
            is_jac_returned_by_func: Wether the jacobian matrices should be returned
                of matlab function with standard outputs,
                the conventional name 'jac_dout_din' is used as jacobian
                term of any output 'out' with respect to input 'in'.
        """  # noqa: D205, D212, D415
        super().__init__(name=name)
        # Force multiprocessing the spwan method
        CallableParallelExecution.MULTI_PROCESSING_START_METHOD = (
            CallableParallelExecution.MultiProcessingStartMethod.SPAWN
        )
        self.__fct_name = None
        self._init_shared_memory_attrs_before()

        matlab_function_path = str(matlab_function_path)
        if not input_names or not output_names:
            parser = MatlabParser()

            if root_search_path:
                path = self.__search_file(matlab_function_path, root_search_path)
                parser.parse(path)
                if matlab_data_path and not exists(str(matlab_data_path)):  # noqa: PTH110
                    matlab_data_path = self.__search_file(
                        str(matlab_data_path), root_search_path, ".mat"
                    )
            else:
                parser.parse(matlab_function_path)

            input_data = parser.inputs
            output_data = parser.outputs
            function_path = (parser.directory / parser.function_name).with_suffix(".m")
        else:
            function_path = matlab_function_path

        if input_names:
            input_data = input_names
        if output_names:
            output_data = output_names

        self.__engine = get_matlab_engine(matlab_engine_name)
        self.__inputs = input_data
        self.__outputs = output_data
        # init size with -1 -> means that size is currently unknown
        self.__is_size_known = False
        self.__inputs_size = dict.fromkeys(self.__inputs, -1)
        self.__outputs_size = dict.fromkeys(self.__outputs, -1)

        # self.outputs can be filtered here

        self.__jac_output_names = []
        self.__jac_output_indices = []
        self.__is_jac_returned_by_func = is_jac_returned_by_func
        if self.__is_jac_returned_by_func:
            self.__filter_jacobian_in_outputs()
            self.__reorder_and_check_jacobian_consistency()

        self.__check_function(function_path, add_subfold_path)
        self.__check_opt_data = check_opt_data
        self.cleaning_interval = cleaning_interval
        self.__init_default_data(matlab_data_path)
        self.io.data_processor = MatlabDataProcessor()

    def _init_shared_memory_attrs_before(self) -> None:
        self.__n_executions = Value("i", 0)

    def __increment_n_executions(self) -> None:
        """Increment the number of executions by 1."""
        with self.__n_executions.get_lock():
            self.__n_executions.value += 1

    def __setstate__(
        self,
        state: Mapping[str, Any],
    ) -> None:
        engine_name = state.pop(self.__TMP_ATTR_FOR_SERIALIZED_ENGINE_NAME)
        paths = state.pop(self.__TMP_ATTR_FOR_SERIALIZED_PATHS)
        super().__setstate__(state)
        self.__engine = get_matlab_engine(engine_name)
        # We need to retrieve the path so the engine can find all needed matlab files
        for path in paths:
            self.__engine.add_path(Path(path))

    def __getstate__(self) -> dict[str, Any]:
        state = super().__getstate__()

        state[self.__TMP_ATTR_FOR_SERIALIZED_ENGINE_NAME] = self.__engine.engine_name

        # We need to cast the type of path depending on the OS when the serialization
        # is used through different platform
        state[self.__TMP_ATTR_FOR_SERIALIZED_PATHS] = [
            to_os_specific(Path(path)) for path in self.__engine.paths
        ]

        if not self.__engine.is_closed:
            self.__engine.close_session()
        return state

    @property
    def engine(self) -> MatlabEngine:
        """The matlab engine of the discipline.

        The engine is associated to the ``matlab_engine_name`` provided at the instance
        construction.
        """
        return self.__engine

    @property
    def function_name(self) -> str:
        """Return the name of the function."""
        return self.__fct_name

    @staticmethod
    def __search_file(
        file_name: str | Path,
        root_dir: str | Path,
        extension: str = ".m",
    ) -> str:
        """Locate recursively a file in the given root directory.

        Args:
            file_name: The name of the file to be located.
            root_dir: The root directory to launch the research.
            extension: The extension of the file in case not given by user.

        Returns:
            The path of the given file.

        Raises:
            IOError:
                * If two files are found in same directory;
                * If no file is found.
        """
        found_file = False
        re_matfile = re.compile(r"\S+\.\S*")
        file_name = str(file_name)
        grps = re_matfile.search(file_name)
        if grps is None:
            file_name += extension

        file_path = ""
        for subdir, _, files in os.walk(str(root_dir)):
            for file_loc in files:
                if file_loc == file_name:
                    if found_file:
                        msg = (
                            f"At least two files {file_name} "
                            f"were in directory {root_dir}"
                            f"\n File one: {file_path};"
                            f"\n File two: {Path(subdir) / file_loc}."
                        )  # noqa: PTH118
                        raise OSError(msg)
                    found_file = True
                    file_path = join(subdir, file_loc)  # noqa: PTH118
                    dir_name = subdir

        if not found_file:
            msg = f"No file: {file_name}, found in directory: {root_dir}."
            raise OSError(msg)

        LOGGER.info("File: %s found in directory: %s.", file_name, dir_name)
        return file_path

    def __check_function(
        self,
        matlab_function_path: str | Path,
        add_subfold_path: bool,
    ) -> None:
        """Check the availability of the prescribed MATLAB function.

        The function manages encrypted, build-in and user made function and
        unify their use.

        Args:
            matlab_function_path: A name for the matlab function to be wrapped.
            add_subfold_path: If true, add all sub-folders of the function to
                matlab search path.

        Raises:
            NameError: If the function (or file) does not exist.
        """
        path = Path(matlab_function_path)
        if path.exists():
            # Test if the file exists in the system
            self.__engine.add_path(path.parent, add_subfolder=add_subfold_path)
            self.__fct_name = path.stem
        elif self.__engine.exist(matlab_function_path)[0]:
            # If file does not exist, try to find an existing build-in function in
            # engine
            self.__fct_name = matlab_function_path
        else:
            # If no file and build-in function exist, raise error
            msg = f'No existing file or function "{matlab_function_path}".'
            raise NameError(msg)

    def __init_default_data(
        self,
        matlab_data_file: str,
    ) -> None:
        """Initialize default data of the discipline.

        Args:
            matlab_data_file: The path to the .mat containing default values of data
        """
        if matlab_data_file:
            saved_values = convert_array_from_matlab(
                load_matlab_file(str(matlab_data_file).replace(".mat", ""))
            )

        # Here, we temporary init inputs data with an array of
        # size 1 but that could not be the right size...
        # The right size can be known from either matlab_data_file or evaluating
        # the matlab function
        input_data = dict.fromkeys(self.__inputs, np.array([0.1]))
        # same remark as above about the size
        output_data = dict.fromkeys(self.__outputs, np.array([0.1]))

        if not self.auto_detect_grammar_files and matlab_data_file:
            input_data = self.__update_data(input_data.copy(), saved_values)

        if not self.auto_detect_grammar_files and matlab_data_file:
            output_data = self.__update_data(output_data.copy(), saved_values)

        self.input_grammar.update_from_data(input_data)
        self.output_grammar.update_from_data(output_data)

        # If none input matlab data is prescribed, we cannot know
        # the size of inputs and outputs. Thus, we must evaluate
        # the function in order to know the sizes
        if matlab_data_file:
            self.__is_size_known = True
            for input_name, input_value in input_data.items():
                self.__inputs_size[input_name] = len(input_value)

            for output_name, output_value in output_data.items():
                self.__outputs_size[output_name] = len(output_value)

        self.default_input_data = input_data.copy()

    def __filter_jacobian_in_outputs(self) -> None:
        """Filter jacobians in outputs names.

        This function is applied when _is_jac_returned_by_func is True. In such case,
        the function extracts the jacobian component from the list of output names
        returned by the matlab function. It thus fills _jac_output_names attributes as
        well as _jac_output_indices which corresponds to indices of jacobian component
        in the list of outputs returned by the matlab function.

        After applying this function, _outputs attribute no longer contains jacobian
        output names but only standard outputs.

        In order to filter jacobian component, this function just checks that jacobian
        names are prefixed by 'jac_'.
        """
        output_names = list(self.__outputs)

        # select jacobian output and remove them from self.outputs
        for i, out_name in enumerate(self.__outputs):
            if out_name[0:4] == self.JAC_PREFIX:
                self.__jac_output_names.append(out_name)
                self.__jac_output_indices.append(i)
                output_names.remove(out_name)

        # here self.outputs only contains output responses (no jacobian)
        self.__outputs = output_names

    def __reorder_and_check_jacobian_consistency(self) -> None:
        """This function checks jacobian output consistency.

        This function is used when _is_jac_returned_by_func is True.

        The function is called after calling jacobian filtering
        :meth:`.MatlabDiscipline._filter_jacobian_in_outputs`. It enables to:
        * check that all outputs have a jacobian matrix with respect to all inputs;
        * reorder the list of jacobian names (and indices) following the order
          from iterating over outputs then inputs lists;

        In order to check that all jacobian components exist, the function
        uses the conventional naming described in
        :meth:`.MatlabDiscipline._get_jac_name`.

        Raises:
            ValueError:
                * If the number of jacobian outputs is wrong;
                * If a specific jacobian output has the wrong name.
        """
        conventional_jac_names = self.__get_conventional_jac_names()
        new_indices = [-1] * len(conventional_jac_names)

        if len(conventional_jac_names) != len(self.__jac_output_names):
            msg = (
                "The number of jacobian outputs does "
                "not correspond to what it should be. "
                "Make sure that all outputs have a jacobian "
                "matrix with respect to inputs."
            )
            raise ValueError(msg)

        not_found = []
        for i, name in enumerate(conventional_jac_names):
            try:
                idx = self.__jac_output_names.index(name)
            except ValueError:  # noqa: PERF203
                not_found.append(name)
            else:
                new_indices[i] = self.__jac_output_indices[idx]

        if not_found:
            msg = (
                f"Jacobian terms {not_found} are not found in the "
                "list of conventional names. It is reminded that "
                "jacobian terms' name should be "
                "such as 'jac_dout_din'"
            )
            raise ValueError(msg)

        self.__jac_output_names = conventional_jac_names
        self.__jac_output_indices = new_indices

    def __get_conventional_jac_names(self) -> list[str]:
        """Return the list of jacobian names following the conventional naming.

        The conventional naming is described in :meth:`.MatlabDiscipline._get_jac_name`.
        """
        return [
            self.__get_jac_name(out_var, in_var)
            for out_var in self.__outputs
            for in_var in self.__inputs
        ]

    def __get_jac_name(
        self,
        out_var: str,
        in_var: str,
    ) -> str:
        """Return the name of jacobian given input and ouput variables.

        The conventional naming of jacobian component is the following:
        if outputs have any names ``out_1``, ``out_2``...
        and inputs are ``in_1``, ``in_2``... Therefore, names of jacobian
        components returned
        by the matlab function must be: ``jac_dout_1_din_1``,
        ``jac_dout_1_din_2``,
        ``jac_dout_2_din_1``, ``jac_dout_2_din_2``... which means
        that the names must be prefixed by ``jac_``, and followed by
        ``doutput`` and ``dinput`` seperated by ``_``.

        Args:
            out_var: The output variable name.
            in_var: The input variable name.

        Returns:
            The jacobian matrix name of output with respect to input.
        """
        return str(f"{self.JAC_PREFIX}d{out_var}_d{in_var}")

    def check_input_data(  # noqa: D102
        self,
        input_data: Mapping[str, np.ndarray],
        raise_exception: bool = True,
    ) -> None:
        if self.__check_opt_data:
            super().check_input_data(input_data, raise_exception=raise_exception)

    def check_output_data(self, raise_exception: bool = True) -> None:  # noqa: D102
        if self.__check_opt_data:
            super().check_output_data(raise_exception=raise_exception)

    def _run(self, input_data: StrKeyMapping) -> StrKeyMapping | None:
        """Run the Matlab discipline.

        If jacobian values are returned by the matlab function, they are filtered and
        used in order to fill :attr:`.MatlabDiscipline.jac`.

        Raises:
            ValueError:
                * If the execution of the matlab function fails.
                * If the size of the jacobian output matrix is wrong.
        """
        self.__increment_n_executions()
        list_of_values = [input_data.get(k) for k in self.__inputs if k in input_data]

        try:
            out_vals = self.__engine.execute_function(
                self.__fct_name,
                *list_of_values,
                nargout=len(self.__outputs) + len(self.__jac_output_names),
            )

        except matlab.engine.MatlabExecutionError:
            LOGGER.exception("Discipline: %s execution failed", self.name)
            raise

        # filter output values if jacobian is returned

        if self.__is_jac_returned_by_func:
            out_vals = np.array(out_vals, dtype=object)
            jac_vals = [out_vals[idx] for idx in self.__jac_output_indices]
            out_vals = np.delete(out_vals, self.__jac_output_indices)
            # --> now out_vals only contains output responses (no jacobian)

        if (
            self.cleaning_interval != 0
            and self.__n_executions.value % self.cleaning_interval == 0
        ):
            self.__engine.execute_function("clear", "all", nargout=0)
            LOGGER.debug(
                "MATLAB cache cleaned: Discipline called %s times",
                self.__n_executions.value,
            )

        out_names = self.__outputs

        output_data = {}
        if len(out_names) == 1:
            output_data[out_names[0]] = double2array(out_vals)
        else:
            for out_n, out_v in zip(out_names, out_vals):
                output_data[out_n] = double2array(out_v)

        if not self.__is_size_known:
            for i, var in enumerate(self.__inputs):
                self.__inputs_size[var] = len(list_of_values[i])
            for var in self.__outputs:
                self.__outputs_size[var] = len(output_data[var])
            self.__is_size_known = True

        if self.__is_jac_returned_by_func:
            self.__store_jacobian(jac_vals, output_data)

        return output_data

    def __store_jacobian(
        self, jac_vals: list[float], output_data: StrKeyMapping
    ) -> None:
        """Store the jacobian.

        Args:
            jac_vals: The values of the jacobian.
            output_data: The data computed by the matlab function.
        """
        # Those data will be processed by the data_processor and overwritten after _run,
        # here they are necessary for Initializing the jacobian.
        self.io.data.update(output_data)

        self._init_jacobian()

        cpt = 0
        for out_name in self.__outputs:
            self.jac[out_name] = {}
            for in_name in self.__inputs:
                self.jac[out_name][in_name] = np.atleast_2d(jac_vals[cpt])

                if self.jac[out_name][in_name].shape != (
                    self.__outputs_size[out_name],
                    self.__inputs_size[in_name],
                ):
                    msg = (
                        "Jacobian term 'jac_d{}_d{}' "
                        "has the wrong size {} whereas it should "
                        "be {}.".format(
                            out_name,
                            in_name,
                            self.jac[out_name][in_name].shape,
                            (
                                self.__outputs_size[out_name],
                                self.__inputs_size[in_name],
                            ),
                        )
                    )
                    raise ValueError(msg)

                cpt += 1

        self._has_jacobian = True

    @staticmethod
    def __update_data(
        data: MutableMapping[str, Any],
        other_data: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        """Update the values of a data mapping without adding new data names.

        Args:
            data: The data to be updated.
            other_data: The data to update ``data``.

        Returns:
            The updated data.
        """
        for key, value in other_data.items():
            if key in data:
                data[key] = value

        return data

    def save_data_to_matlab(self, file_path: str | Path) -> None:
        """Save local data to matlab .mat format.

        Args:
            file_path: The path where to save the file.
        """
        file_path = Path(file_path)
        save_matlab_file(self.io.data, file_path=file_path)
        msg = (
            f"Local data of discipline {self.name} exported to "
            f"{file_path.name}.mat successfully."
        )
        LOGGER.info(msg)
