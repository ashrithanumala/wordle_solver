from setuptools import setup, Extension
from pybind11.setup_helpers import Pybind11Extension, build_ext

ext_modules = [
    Pybind11Extension(
        "wordle_env",
        ["wordle_env.cpp"],
        include_dirs=['.'],
    ),
]

setup(
    name="wordle_env",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)
# python3 setup.py build_ext --inplace