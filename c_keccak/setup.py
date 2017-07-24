#! /usr/bin/python3

from distutils.core import setup, Extension

keccak_module = Extension('_keccak',
                          sources=['keccak_wrap.c', 'keccak.c'])

setup(name='keccak',
      version='0.1',
      ext_modules=[keccak_module],
      py_modules=['keccak'])
