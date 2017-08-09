%module feistel
%{
    #include <Python.h>
    #include "feistel.h"
%}

extern PyObject *f_encrypt(PyObject *, PyObject *, PyObject *, int);
extern PyObject *f_decrypt(PyObject *, PyObject *, PyObject *, int);
