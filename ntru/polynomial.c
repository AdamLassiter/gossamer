#include "polynomial.h"


polynomial *new_polynomial(int len) {
	polynomial *p = (polynomial*) malloc(sizeof(polynomial));
	p->len = len;
	p->coeffs = (int*) malloc(len * sizeof(int));
	memset(p->coeffs, 0, p->len * sizeof(int));
	return p;
}


void free_polynomial(polynomial *p) {
	free(p->coeffs);
	free(p);
}


polynomial *from_PyTuple(PyObject *pyTuple) {
	int tupleSize = PyTuple_Size(pyTuple);
	polynomial *ret = new_polynomial(tupleSize);
	for (int i = 0; i < tupleSize; i ++) {
	   PyObject *tupleItem = PyTuple_GetItem(pyTuple, i);
	   if (PyInt_Check(tupleItem)) {
	      ret->coeffs[i] = PyInt_AsLong(tupleItem);
	   } else {
	      printf("Error: tuple contains a non-int value");
	      exit(1);
	   }
	}
	return ret;
}


PyObject *to_PyTuple(polynomial *poly) {
	PyObject *ret = PyTuple_New(poly->len);
	for (int i = 0; i < poly->len; i ++) {
		PyTuple_SetItem(ret, i, PyInt_FromLong(poly->coeffs[i]));
	}
	free_polynomial(poly);
	return ret;
}


void prettyprint(polynomial p) {
	for (int i = 0; i < p.len; i ++) {
		printf("%d ", p.coeffs[i]);
	}
	printf("\n");
}


void c_rshift(polynomial p, int n, polynomial *o) {
	void reverse(int arr[], int start, int end) {
		if (start >= end)
	    	return;
		int temp = arr[start];
		arr[start] = arr[end];
		arr[end] = temp;
		reverse(arr, start+1, end-1);
	}
	if (o->coeffs != p.coeffs) {
		memcpy(o->coeffs, p.coeffs, p.len * sizeof(int));
	}
	reverse(o->coeffs, 0, o->len - 1);
	reverse(o->coeffs, 0, n - 1);
	reverse(o->coeffs, n, o->len - 1);
}
PyObject *rshift(PyObject *P, int n) {
	polynomial *p = from_PyTuple(P);
	c_rshift(*p, n, p);
	return to_PyTuple(p);
}


void c_lshift(polynomial p, int n, polynomial *o) {
	c_rshift(p, mod(-n, p.len), o);
}
PyObject *lshift(PyObject *P, int n) {
	polynomial *p = from_PyTuple(P);
	c_lshift(*p, n, p);
	return to_PyTuple(p);
}


int c_degree(polynomial p) {
	if (p.len == 0) {
		return 0;
	} else if (p.coeffs[order(p)] == 0) {
		p.len --;
		return c_degree(p);
	} else {
		return order(p);
	}
}
int degree(PyObject *P) {
	return c_degree(*from_PyTuple(P));
}


void c_centerlift(polynomial p, int n, polynomial *o) {
	for (int i = 0; i < p.len; i ++) {
		o->coeffs[i] = p.coeffs[i] > (float)(n / 2.) ? p.coeffs[i] - n : p.coeffs[i];
	}
}
PyObject *centerlift(PyObject *P, int n) {
	polynomial *p = from_PyTuple(P);
	c_centerlift(*p, n, p);
	return to_PyTuple(p);
}


void c_s_add(polynomial p, int x, polynomial *o) {
	if (o->coeffs != p.coeffs) {
		memcpy(o->coeffs, p.coeffs, p.len * sizeof(int));
	}
	o->coeffs[0] += x;
}
PyObject *s_add(PyObject *P, int x) {
	polynomial *p = from_PyTuple(P);
	c_s_add(*p, x, p);
	return to_PyTuple(p);
}


void c_s_mul(polynomial p, int x, polynomial *o) {
	for (int i = 0; i < p.len; i ++) {
		o->coeffs[i] = p.coeffs[i] * x;
	}
}
PyObject *s_mul(PyObject *P, int x) {
	polynomial *p = from_PyTuple(P);
	c_s_mul(*p, x, p);
	return to_PyTuple(p);
}


void c_s_mod(polynomial p, int x, polynomial *o) {
	for (int i = 0; i < p.len; i ++) {
		o->coeffs[i] = mod(p.coeffs[i], x);
	}
}
PyObject *s_mod(PyObject *P, int x) {
	polynomial *p = from_PyTuple(P);
	c_s_mod(*p, x, p);
	return to_PyTuple(p);
}


void c_v_add(polynomial p, polynomial q, polynomial *o) {
	for (int i = 0; i < p.len; i ++) {
		o->coeffs[i] = p.coeffs[i] + q.coeffs[i];
	}
}
PyObject *v_add(PyObject *P, PyObject *Q) {
	polynomial *p = from_PyTuple(P),
	           *q = from_PyTuple(Q),
			   *r = new_polynomial(p->len);
	c_v_add(*p, *q, r);
	free_polynomial(p); free_polynomial(q);
	return to_PyTuple(r);
}


void c_v_sub(polynomial p, polynomial q, polynomial *o) {
	for (int i = 0; i < p.len; i ++) {
		o->coeffs[i] = p.coeffs[i] - q.coeffs[i];
	}
}
PyObject *v_sub(PyObject *P, PyObject *Q) {
	polynomial *p = from_PyTuple(P),
	           *q = from_PyTuple(Q),
			   *r = new_polynomial(p->len);
	c_v_sub(*p, *q, r);
	free_polynomial(p); free_polynomial(q);
	return to_PyTuple(r);
}


void c_v_mul(polynomial p, polynomial q, polynomial *o) {
	memset(o->coeffs, 0, o->len * sizeof(int));
	for (int i = 0; i < p.len; i ++) {
		for (int j = 0; j < q.len; j ++) {
			o->coeffs[(i+j) % p.len] += p.coeffs[i] * q.coeffs[j];
		}
	}
}
PyObject *v_mul(PyObject *P, PyObject *Q) {
	polynomial *p = from_PyTuple(P),
	           *q = from_PyTuple(Q),
			   *r = new_polynomial(p->len);
	c_v_mul(*p, *q, r);
	free_polynomial(p); free_polynomial(q);
	return to_PyTuple(r);
}


int inv(int a, int p) {
	int b0 = p, t, q;
	int x0 = 0, x1 = 1;
	if (p == 1) return 1;
	a = mod(a, p);
	while (a > 1) {
		q = a / p;
		t = p, p = a % p, a = t;
		t = x0, x0 = x1 - q * x0, x1 = t;
	}
	if (x1 < 0) x1 += b0;
	return x1;
}


int is_zero(polynomial F) {
	if (F.len > 0) {
		F.len --;
		F.coeffs += sizeof(int);
		return (F.coeffs[-1] == 0) && is_zero(F);
	} else {
		return true;
	}
}


void swap(polynomial *a, polynomial *b) {
    polynomial temp = *a;
    *a = *b;
    *b = temp;
}


void c_inverse_modp(polynomial F, int p, polynomial *o) {
	int N = F.len, k = N, u;
	polynomial *b = new_polynomial(N + 1),
	           *c = new_polynomial(N + 1),
			   *f = new_polynomial(N + 1),
			   *g = new_polynomial(N + 1),
			   *t1 = new_polynomial(N + 1),
			   *t2 = new_polynomial(N + 1);
	b->coeffs[0] = 1;
	memcpy(f->coeffs, F.coeffs, N * sizeof(int));
	g->coeffs[0] = -1; g->coeffs[g->len - 1] = 1;

	while (true) {
		while (c_degree(*f) != 0 && f->coeffs[0] == 0) {
			c_lshift(*f, 1, f);
			c_rshift(*c, 1, c);
			k ++;
		}

		if (c_degree(*f) == 0) {
			break;
		}

		if (c_degree(*f) < c_degree(*g)) {
			swap(f, g);
			swap(b, c);
		}

		u = f->coeffs[0] * inv(g->coeffs[0], p);
		c_s_mul(*g, u, t1); c_v_sub(*f, *t1, t2); c_s_mod(*t2, p, f);
		c_s_mul(*c, u, t1); c_v_sub(*b, *t1, t2); c_s_mod(*t2, p, b);
	}

	if (f->coeffs[0] != 0) {
		b->len --;
		c_s_mul(*b, inv(f->coeffs[0], p), o);
		c_lshift(*o, k % N, o);
		free_polynomial(b); free_polynomial(c);
		free_polynomial(f); free_polynomial(g);
		free_polynomial(t1); free_polynomial(t2);
	} else {
		memset(o->coeffs, 0, o->len * sizeof(int));
	}
	return;
}
PyObject *inverse_modp(PyObject *P, int n) {
	polynomial *p = from_PyTuple(P);
	c_inverse_modp(*p, n, p);
	if (is_zero(*p)) {
		Py_INCREF(Py_None);
		return Py_None;
	} else {
		return to_PyTuple(p);
	}
}


// WARNING - DOES NOT WORK
// FIXME Incorrectly inverts F id:13
void c_inverse_modpn(polynomial F, int pn, polynomial *o) {
	int *factorise_pn(int pn) {
		static int ret[2] = {2, 0};
		while (pn % ret[0] != 0) {
			ret[0] ++;
		}
		while (pn > 1) {
			pn /= ret[0];
			ret[1] ++;
		}
		return ret;
	}

	int pow(int x, int n) {
		return n > 1 ? x * pow(x, n - 1) : x;
	}

	int *pr = factorise_pn(pn);
	int p = pr[0], r = pr[1];
	c_inverse_modp(F, p, o);
	if (!is_zero(*o)) {
		polynomial *t1 = new_polynomial(F.len),
				   *t2 = new_polynomial(F.len),
				   *t3 = new_polynomial(F.len);
		int n = 2;
		while (r > 0) {
			c_v_mul(F, *o, t1);
			c_s_add(*t1, -2, t2);
			c_s_mul(*t2, -1, t2);
			c_v_mul(*t2, *o, t3);
			c_s_mod(*t3, pow(p, n), o);
			r /= 2;
			n *= 2;
		}
		c_s_mod(*o, pn, o);
		free_polynomial(t1); free_polynomial(t2); free_polynomial(t3);
	}
}
PyObject *inverse_modpn(PyObject *P, int n) {
	polynomial *p = from_PyTuple(P);
	c_inverse_modpn(*p, n, p);
	if (is_zero(*p)) {
		Py_INCREF(Py_None);
		return Py_None;
	} else {
		return to_PyTuple(p);
	}
}


int main(void) {
	polynomial *f = new_polynomial(11),
	           *g = new_polynomial(11),
			   *fg = new_polynomial(11);

    int fc[11] = {-1, 1, 1, 0, -1, 0, 1, 0, 0, 1, -1};
	memcpy(f->coeffs, fc, 11*sizeof(int));
	c_inverse_modp(*f, 3, g);
	c_v_mul(*f, *g, fg); c_s_mod(*fg, 3, fg);
	prettyprint(*f); prettyprint(*g); prettyprint(*fg);

	free_polynomial(f); free_polynomial(g); free_polynomial(fg);
}
