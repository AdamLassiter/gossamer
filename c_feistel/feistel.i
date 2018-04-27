%module feistel
%{
    #include <Python.h>
    #include "feistel.h"
    #include "../c_keccak/keccak.h"
%}

extern char *encrypt_(char *, char *, char *, int);
extern char *decrypt_(char *, char *, char *, int);
