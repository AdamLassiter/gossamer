from distutils.core import setup, Extension

polynomialModule = Extension('_polynomial',
                             sources=['polynomial.c'])

setup(name='polynomial',
      version='0.1',
      ext_modules=[polynomialModule],
      py_modules=['polynomial'])
