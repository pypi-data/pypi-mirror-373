# Repository: https://gitlab.com/quantify-os/quantify
# Licensed according to the LICENSE file on the main branch
"""Utilities used to maintain deprecation and reverse-compatibility of the code."""

import functools
import inspect
import os
import warnings
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def _find_stack_level() -> int:
    """
    Find the first place in the stack that is not inside quantify-core
    (tests notwithstanding).
    (adopted from pandas.util._exceptions.find_stack_level).
    """
    import quantify  # noqa: PLC0415

    pkg_dir = os.path.dirname(quantify.__file__)
    test_dir = os.path.join(pkg_dir, "tests")

    frame = inspect.currentframe()
    n = 0
    while frame:
        fname = inspect.getfile(frame)
        if fname.startswith(pkg_dir) and not fname.startswith(test_dir):
            frame = frame.f_back
            n += 1
        else:
            break
    return n


def deprecated(
    drop_version: str, message_or_alias: str | Callable[P, R]
) -> Callable[[Callable[P, R] | type], Callable[P, R] | type]:
    """
    A decorator for deprecating classes and methods.

    Parameters
    ----------
    drop_version
        Version when the deprecated function/class will be removed.
    message_or_alias
        Either an explanatory message or a new replacement callable.

    """

    def deprecator(func_or_class: Callable[P, R] | type) -> Callable[P, R] | type:
        old_module = inspect.getmodule(func_or_class)
        if old_module is None:
            raise RuntimeError("Could not determine module of the deprecated object.")

        package = old_module.__name__.split(".", 1)[0].replace("_", "-")
        maybe_brackets = "" if isinstance(func_or_class, type) else "()"

        if callable(message_or_alias):
            new_module = inspect.getmodule(message_or_alias)
            if new_module is None:
                raise RuntimeError("Could not determine module of the moved object.")
            instruction = (
                f"Use {new_module.__name__}.{message_or_alias.__qualname__}"
                f"{maybe_brackets} instead."
            )
        else:
            instruction = message_or_alias

        message = (
            f"{'Class' if isinstance(func_or_class, type) else 'Function'} "
            f"{old_module.__name__}.{func_or_class.__qualname__}{maybe_brackets} is "
            f"deprecated and will be removed in {package}-{drop_version}. {instruction}"
        )

        if isinstance(func_or_class, type):
            cls = (
                type(
                    func_or_class.__name__,
                    message_or_alias.__bases__,
                    dict(message_or_alias.__dict__),
                )
                if isinstance(message_or_alias, type)
                else func_or_class
            )

            orig_init = cls.__init__  # type: ignore

            @functools.wraps(orig_init)
            def _wrapped_init(
                self,  # noqa: ANN001
                *args: object,
                **kwargs: object,
            ) -> None:
                warnings.warn(message, FutureWarning, stacklevel=_find_stack_level())
                orig_init(self, *args, **kwargs)

            cls.__init__ = _wrapped_init  # type: ignore
            return cls

        func = message_or_alias if callable(message_or_alias) else func_or_class

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            warnings.warn(message, FutureWarning, stacklevel=_find_stack_level())
            return func(*args, **kwargs)

        return wrapper

    return deprecator
