%module keccak
%{
    #include <Python.h>
    #include "keccak.h"
%}

extern KeccakHash *new_hash(unsigned int, unsigned int);

%apply char * {unsigned char *};
%newobject squeeze;
extern unsigned char *squeeze(PyObject *, unsigned char);

extern void absorb(PyObject *, PyObject *);
