%module feistel
%{
    #include <Python.h>
    #include "feistel.h"
    #include "../c_keccak/keccak.h"
%}

extern unsigned char *encrypt_(unsigned char *, unsigned char *, unsigned char *, int);
extern unsigned char *decrypt_(unsigned char *, unsigned char *, unsigned char *, int);
