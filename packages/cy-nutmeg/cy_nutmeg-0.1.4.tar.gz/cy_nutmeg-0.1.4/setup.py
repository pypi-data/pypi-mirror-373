from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize
import numpy as np
import os


with open("README.md", 'r') as f:
    long_description = f.read()

setup(
    name="cy-nutmeg",
    version="0.1.4",
    description="A Cython-optimized implementation of the NUTMEG algorithm",
    author="Jonathan Ivey",
    author_email="jonathan8ivey@gmail.com",
    url="https://github.com/jonathanivey/NUTMEG",
    packages=find_packages(),
    ext_modules=cythonize(
        Extension(
            "nutmeg.nutmeg_cython",
            ["nutmeg_cython.pyx"],
            include_dirs=[np.get_include()],
            extra_compile_args=["-O3"],  # Optimize for speed
        ),
        compiler_directives={
            'language_level': "3",
            'boundscheck': False,
            'wraparound': False,
            'initializedcheck': False,
            'nonecheck': False,
        }
    ),
    install_requires=[
        "numpy>=1.19.0",
        "pandas>=1.0.0",
        "scipy>=1.5.0",
        "attr>=0.3.1",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
) 