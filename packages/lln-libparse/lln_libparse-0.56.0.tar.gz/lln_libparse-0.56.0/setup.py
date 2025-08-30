#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path
from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

__file_dir__ = Path(__file__).absolute().parent
__version__ = subprocess.check_output(
    [sys.executable, __file_dir__ / "libparse" / "__version__.py"],
    encoding="utf8",
).strip()

ext = Pybind11Extension(
    "_libparse",
    [
        "libparse/wrapper.cpp",
        "yosys/passes/techmap/libparse.cc",
    ],
    include_dirs=["yosys/passes/techmap", "yosys"],
    define_macros=[("FILTERLIB", "1"), ("_YOSYS_", "1")],
)

setup(
    name="lln-libparse",
    packages=["libparse"],
    version=__version__,
    description="Python wrapper around Yosys' libparse module",
    long_description=open(__file_dir__ / "Readme.md").read(),
    long_description_content_type="text/markdown",
    author="Mohamed Gaber",
    author_email="me@donn.website",
    install_requires=["wheel"],
    python_requires=">=3.8",
    ext_modules=[ext],
    cmdclass={"build_ext": build_ext},
)
