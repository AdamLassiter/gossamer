%module keccak
%{
    #include <Python.h>
    #include "keccak.h"
%}

extern void new_hash(PyObject *, unsigned int, unsigned int);

%apply char {unsigned char};
extern PyObject *squeeze(PyObject *);

extern void absorb(PyObject *, PyObject *);
