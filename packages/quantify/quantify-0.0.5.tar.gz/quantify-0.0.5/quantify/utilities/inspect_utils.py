# Repository: https://gitlab.com/quantify-os/quantify
# Licensed according to the LICENSE file on the main branch
"""Python inspect helper functions."""

import inspect
import sys
from types import FunctionType, ModuleType
from typing import Any, Callable, Union

from IPython.display import Code, DisplayHandle, display


def get_members_of_module(
    module: ModuleType, predicate: Callable[[Any], bool]
) -> list[tuple[str, Union[type, FunctionType]]]:
    """
    Returns all members of a module that match the predicate function.

    Parameters
    ----------
    module :
        The module to inspect.
    predicate :
        The predicate function.

    Returns
    -------
    :
        The list of matching members of a module.

    """
    module_name: str = module.__name__
    members = inspect.getmembers(
        sys.modules[module_name],
        lambda member: predicate(member) and member.__module__ == module_name,  # pylint: disable=cell-var-from-loop
    )
    return members


def get_classes(*modules: ModuleType) -> dict[str, type[Any]]:
    """
    Returns a dictionary of class types by class names found in the modules provided
    in the 'modules' parameter.

    .. seealso:: :ref:`howto-utilities-inspect`

    Parameters
    ----------
    modules
        Variable length of modules.

    Returns
    -------
    :
        A dictionary containing the class members of a module by name.

    """
    classes_list = []
    for module in modules:
        classes_list.extend(get_members_of_module(module, inspect.isclass))

    return dict(classes_list)


def get_functions(*modules: ModuleType) -> dict[str, Callable]:
    """
    Returns a dictionary of functions by function names found in the modules provided
    in the 'modules' parameter.

    .. seealso:: :ref:`howto-utilities-inspect`

    Parameters
    ----------
    modules
        Variable length of modules.

    Returns
    -------
    :
        A dictionary containing the function members of a module by name.

    """
    function_list = []
    for module in modules:
        function_list.extend(get_members_of_module(module, inspect.isfunction))

    return dict(function_list)


def display_source_code(
    obj: Any,  # noqa: ANN401
    exec_display: bool = True,
) -> Code | DisplayHandle | None:
    """Displays the source code of a python object in a IPython kernel.

    Parameters
    ----------
    obj
        The python object for which to display the code.
    exec_display
        If ``True`` executes :func:`IPython.display.display` instead of returning an
        :class:`IPython.display.Code` object.

    Returns
    -------
    :
        The source code if ``exec_display==False``.

    """
    source_code: str = inspect.getsource(obj)
    code = Code(source_code, language="python")

    if not exec_display:
        return code

    return display(code)  # returns None
