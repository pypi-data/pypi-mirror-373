#!/usr/bin/env python
from setuptools import setup


def get_version_and_cmdclass(pkg_path):
    """Load version.py module without importing the whole package.

    Template code from miniver
    """
    import os
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("version", os.path.join(pkg_path, "_version.py"))
    module = module_from_spec(spec)  # type: ignore
    spec.loader.exec_module(module)  # type: ignore
    return module.__version__, module.get_cmdclass(pkg_path)


package = "quantify"
version, cmdclass = get_version_and_cmdclass(package)

setup(
    name=package,
    version=version,
    cmdclass=cmdclass,
)
