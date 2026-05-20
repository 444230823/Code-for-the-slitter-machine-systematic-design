from setuptools import setup
from Cython.Build import cythonize

setup(
    name='_utility',
    ext_modules=cythonize("_utility.pyx", annotate=True),  # annotate=True 会生成Html文件，可用来对照 Python 程序和 C 程序的重合情况
    zip_safe=False,
)

