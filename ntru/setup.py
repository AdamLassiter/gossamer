#! /usr/bin/python3

from distutils.core import setup, Extension

polynomial_module = Extension('_polynomial',
                              sources=['polynomial_wrap.c', 'polynomial.c'])

setup(name='polynomial',
      version='0.1',
      ext_modules=[polynomial_module],
      py_modules=['polynomial'])
