import os
import shutil
from Cython.Build import cythonize
from setuptools import Extension

def build(setup_kwargs):
    extensions = [
        Extension(
            "*",
            ["pyfedic_cython/*.pyx"],
            extra_compile_args=['-fopenmp'],
            extra_link_args=['-fopenmp'],
            libraries=["m"],
        ),
    ]

    ext_modules = cythonize(
        extensions,
        #annotate=True,
    )

    setup_kwargs.update({
        'ext_modules': ext_modules,
    })
