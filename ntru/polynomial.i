%module polynomial
%{
    #include <Python.h>
    #include "polynomial.h"
%}

extern PyObject *rshift(PyObject*, int);
extern PyObject *lshift(PyObject*, int);

extern int degree(PyObject*);
extern PyObject *centerlift(PyObject*, int);

extern PyObject *s_mul(PyObject*, int);
extern PyObject *s_add(PyObject*, int);
extern PyObject *s_mod(PyObject*, int);

extern PyObject *v_add(PyObject*, PyObject*);
extern PyObject *v_sub(PyObject*, PyObject*);
extern PyObject *v_mul(PyObject*, PyObject*);

extern PyObject *inverse_modp(PyObject*, int);
extern PyObject *inverse_modpn(PyObject*, int);
