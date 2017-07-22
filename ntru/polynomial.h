#include <Python.h>
#define order(p) (p.len - 1)
#define mod(a, b) ((b + (a % b)) % b)
#define true 1


typedef struct {
	int len;
	int  *coeffs;
} Polynomial;


PyObject *rshift(PyObject*, int);
PyObject *lshift(PyObject*, int);

int degree(PyObject*);
PyObject *centerlift(PyObject*, int);

PyObject *s_mul(PyObject*, int);
PyObject *s_add(PyObject*, int);
PyObject *s_mod(PyObject*, int);

PyObject *v_add(PyObject*, PyObject*);
PyObject *v_sub(PyObject*, PyObject*);
PyObject *v_mul(PyObject*, PyObject*);

PyObject *inverse_modp(PyObject*, int);
PyObject *inverse_modpn(PyObject*, int);
