#! /usr/bin/python3

from distutils.core import setup, Extension

keccak_module = Extension('_keccak',
                          sources=['keccak_wrap.c', 'keccak.c'],
                          extra_compile_args=['-O0'])

setup(name='keccak',
      version='0.1',
      ext_modules=[keccak_module],
      py_modules=['keccak'])
