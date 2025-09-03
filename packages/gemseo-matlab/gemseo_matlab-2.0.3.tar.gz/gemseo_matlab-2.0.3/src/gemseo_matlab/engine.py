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
#
# Contributors:
#    INITIAL AUTHORS - API and implementation and/or documentation
#        :author: Francois Gallard
#        :author: Arthur Piat
#        :author: Nicolas Roussouly: GEMSEO integration
#
#    OTHER AUTHORS   - MACROSCOPIC CHANGES
"""Definition of the matlab engine singleton for workspace handling.

Overview
--------

This module contains the :class:`.MatlabEngine` class
which enables to build the Matlab workspace.
The Matlab workspace must be seen as the Matlab "area"
where Matlab functions are executed as well as Matlab variables live.
The engine is basically used when creating a :class:`.MatlabDiscipline` instance
and therefore is not directly handled by the user.
However, a :class:`.MatlabEngine` instance can be used
outside a :class:`.MatlabDiscipline`
in order to directly call Matlab functions
and/or accessing to some variables into the Matlab workspace.

Since :class:`.MatlabEngine` is private, it cannot be used directly from the module.
It is rather used through the function :func:`.get_matlab_engine`
which enables to create only one instance with respect to the ``workspace_name``
(i.e. the instance is unique if the workspace name is the same
when calling several times the function).
Following this, :class:`.MatlabEngine` acts like a singleton.
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import Final

import matlab.engine
from strenum import StrEnum

from gemseo_matlab.matlab_data_processor import double2array

if TYPE_CHECKING:
    from numpy import ndarray

LOGGER = logging.getLogger(__name__)


@lru_cache
def get_matlab_engine(
    workspace_name: str = "matlab",
) -> MatlabEngine:
    """Return a new matlab engine.

    LRU cache decorator enables to cache the instance
    if prescribed ``workspace_name`` is the same.
    Therefore, it acts like a singleton.
    This means that calling this function with the same
    ``workspace_name`` returns the same instance.

    Args:
        workspace_name: The name of matlab workspace.

    Returns:
        A Matlab engine instance.

    Examples:
        >>> eng1 = get_matlab_engine()
        >>> eng2 = get_matlab_engine()
        >>> # make sure that engines are the same
        >>> eng1 is eng2
    """
    return MatlabEngine(workspace_name)


class MatlabEngine:
    """Wrapper around the matlab execution engine.

    Since this class is private, an instance should be built through
    :func:`get_matlab_engine` function.
    Using that latter function acts like a singleton,
    i.e. the returned instance is unique if the workspace name is the same.

    Examples:
        >>> eng1 = get_matlab_engine()
        >>> # add new searching directory to workspace with sub-dir
        >>> eng1.add_path("dir_to_files", add_subfolder=True)
        >>>
        >>> # check if a function exists in workspace and returns the type
        >>> exist, type_func = eng1.exist("cos")
        >>> # execute the function
        >>> eng1.execute_function("cos", 0, nargout=1)
        >>>
        >>> # quit engine
        >>> eng1.close_session()
        >>> print(eng1.is_closed)
    """

    class ParallelType(StrEnum):
        """Types of Matlab parallel execution."""

        LOCAL = "local"
        CLOUD = "MATLAB Parallel Cloud"

    __matlab: MatlabEngine
    """The matlab engine."""

    __is_closed: bool
    """Whether the matlab engine session is closed."""

    __paths: list[str]
    """The search paths for the matlab files."""

    __toolboxes: set[str]
    """The names of the matlab toolboxes."""

    __is_parallel: bool
    """Whether the execution is parallel."""

    __EXIST_TO_TYPE_NAME: Final[tuple] = (
        "",
        "variable",
        "file",
        "MEX-file",
        "Simulink-file",
        "MATLAB-built-in-function",
        "P-code-file",
        "folder",
        "class",
    )

    def __init__(self, engine_name: str) -> None:
        """
        Args:
            engine_name: The name identifying the engine.
        """  # noqa: D205, D212, D415
        self.__engine_name = engine_name
        self.__is_closed = True
        self.__paths = []
        self.__toolboxes = set()
        self.__is_parallel = False

        self.start_engine()
        self.add_path(str(Path(__file__).parent))

    @property
    def engine_name(self) -> str:
        """The engine name."""
        return self.__engine_name

    @property
    def paths(self) -> list[str]:
        """Return the paths."""
        return self.__paths

    @property
    def is_parallel(self) -> bool:
        """Return True if parallel is active."""
        return self.__is_parallel

    @property
    def is_closed(self) -> bool:
        """Return True if the matlab engine is closed."""
        return self.__is_closed

    def start_engine(self) -> None:
        """Start the matlab engine."""
        LOGGER.info('Starting Matlab engine named "%s".', self.__engine_name)
        self.__matlab = matlab.engine.start_matlab()
        LOGGER.info('Matlab engine named "%s" started', self.__engine_name)

        for path in self.__paths:
            self.__matlab.addpath(path)
        self.__is_closed = False

    def exist(self, name: str | Path) -> tuple[bool, str]:
        """Check if the given matlab file exists.

        Args:
            name: The name to be checked if present in MATLAB path.

        Returns:
            A boolean that tells if ``name`` exist.
            A string that indicates the type of file where
            ``function_name`` is found.
        """
        out = int(self.execute_function("exist", str(name)))
        # 0 — given name does not exist.
        # 1 — name is a variable in the workspace.
        # 2 — name is a file with extension .m, .mlx, or .mlapp,
        #     or name is the name of a file with a non-registered file
        #     extension (.mat, .fig, .txt).
        # 3 — name is a MEX-file on your MATLAB search path.
        # 4 — name is a loaded Simulink® model or a Simulink model or
        #     library file on your MATLAB search path.
        # 5 — name is a built-in MATLAB function. This does not include classes.
        # 6 — name is a P-code file on your MATLAB search path.
        # 7 — name is a folder.
        # 8 — name is a class. (exist returns 0 for Java classes if
        #     you start MATLAB with the -nojvm option.)
        return out != 0, self.__EXIST_TO_TYPE_NAME[out]

    def close_session(self) -> None:
        """Close the matlab session."""
        self.__matlab.quit()
        self.__is_closed = True

    def add_toolbox(self, toolbox_name: str) -> None:
        """Add a toolbox to the engine.

        The toolbox added would be needed for the functions
        used in the current session. It should be checked that
        the license is compatible.
        The name given here can be found using "license('inuse')" in MATLAB.

        Args:
            toolbox_name: The name of the toolbox to be checked.
        """
        self.__toolboxes.add(toolbox_name)

    def remove_toolbox(self, toolbox_name: str) -> None:
        """Remove a toolbox from the engine.

        Args:
            toolbox_name: The name of the toolbox to be checked.
        """
        self.__toolboxes.remove(toolbox_name)

    def add_path(
        self,
        path: str | Path,
        add_subfolder: bool = False,
    ) -> None:
        """Add a path to the matlab engine search directories.

        Args:
            path: The path to the directory or file to be added to path.
            add_subfolder: Whether to add the sub-folders recursively.

        Raises:
            ValueError: If the given path cannot be added to Matlab.
        """
        path = str(path)
        if path not in self.__paths:
            if not self.exist(path):
                msg = (
                    f"The given path {path} is not found and cannot be added to matlab."
                )
                raise ValueError(msg)
            self.__paths.append(path)
            self.__matlab.addpath(path)

        if add_subfolder:
            str_paths = self.execute_function("genpath", path)
            # first path in list is the path already in list
            for sub_path in str_paths.split(os.pathsep)[1:]:
                self.add_path(sub_path)

    def execute_function(
        self,
        func_name: str,
        *args: float | str,
        **kwargs: float,
    ) -> Any:
        """Executes a Matlab function called "func_name".

        Args:
            func_name: The function name to call.
            *args: Any arguments that must be passed to the function.
            **kwargs: Any arguments that must be passed to the function.

        Raises:
            matlab.engine.MatlabExecutionError: If the matlab function execution fails.
        """
        if self.__is_closed:
            self.start_engine()

        method = getattr(self.__matlab, func_name)

        try:
            return method(*args, **kwargs)

        except matlab.engine.MatlabExecutionError:
            LOGGER.exception(
                "Failed to execute Matlab function %s with arguments %s and %s",
                func_name,
                str(args),
                str(kwargs),
            )
            raise

    def start_parallel_computing(
        self,
        n_parallel_workers: int,
        parallel_type: ParallelType = ParallelType.LOCAL,
    ) -> None:
        """Start the parallel pool of matlab for parallel computing.

        This feature only works if parallel toolbox is available.

        Args:
            n_parallel_workers: The number of "workers" to the parallel pool.
            parallel_type: The type of parallel execution.
        """
        exist, _ = self.exist("parpool")

        if exist is False:
            LOGGER.warning("Parallel computing not available in MATLAB")
            self.__is_parallel = False
            return

        LOGGER.info(
            "Starting parallel computing with %s workers on '%s' cluster.",
            n_parallel_workers,
            parallel_type,
        )

        try:
            self.execute_function(
                "parpool", parallel_type, float(n_parallel_workers), nargout=0
            )
        except matlab.engine.MatlabExecutionError:
            LOGGER.warning(
                "Parallel computing could not be started, proceeding without."
            )
            self.__is_parallel = False
        else:
            self.__is_parallel = True

            LOGGER.info("MATLAB parallel computing successfully started.")
            LOGGER.info(
                "Only MATLAB function and classes using some 'parfor' will be "
                "computed in parallel."
            )

    def end_parallel_computing(self) -> None:
        """End the parallel computing.

        Raises:
            matlab.engine.MatlabExecutionError: If the parallel option is not
                correctly deactivated.
        """
        if not self.__is_parallel:
            LOGGER.info("Try to end parallel computing whereas it is not activated.")
            return

        LOGGER.info("Closing MATLAB parallel pools.")

        try:
            self.execute_function("eval", "delete(gcp('nocreate'))", nargout=0)
        except matlab.engine.MatlabExecutionError:
            LOGGER.warning("Parallel computing could not be closed.")
            raise
        else:
            self.__is_parallel = False

    def get_toolboxes(self) -> set[str]:
        """Return all toolboxes to be checked before launching this engine.

        Returns:
            All toolboxes.
        """
        return self.__toolboxes

    def execute_script(self, script_name: str) -> None:
        """Execute a script in the current workspace.

        After executing the script, the workspace point to the path
        where the script is located.

        Args:
            script_name: The script name.
        """
        # get the script absolute path
        entire_path = self.execute_function("which", script_name, nargout=1)
        abspath, _, _ = self.execute_function("fileparts", entire_path, nargout=3)

        # move to the script path
        self.execute_function("cd", abspath, nargout=0)

        # execute the script
        self.execute_function("run", script_name, nargout=0)

    def get_variable(self, item: str) -> ndarray:
        """Get any variable in the workspace.

        Args:
            item: The variable name.

        Returns:
            The value of the variable.

        Raises:
            ValueError: If the item is unknown inside the workspace.
        """
        try:
            return double2array(self.__matlab.workspace[item])
        except matlab.engine.MatlabExecutionError:
            msg = (
                f"The variable {item} does not exist in the "
                f"current {self.__engine_name} workspace."
            )
            raise ValueError(msg) from None

    def __del__(self) -> None:
        self.close_session()
