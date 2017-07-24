#! /usr/bin/python3

from distutils.core import setup, Extension

feistel_module = Extension('_feistel',
                           sources=['feistel_wrap.c', 'feistel.c'])

setup(name='feistel',
      version='0.1',
      ext_modules=[feistel_module],
      py_modules=['feistel'])
