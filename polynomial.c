#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#define order(p) p.len - 1
#define mod(a, b) ((b + (a % b)) % b)
#define true 1

typedef struct polynomial {
	int len;
	int *coeffs;
} polynomial;


void prettyprint(polynomial p) {
	for (int i = 0; i < p.len; i ++) {
		printf("%d ", p.coeffs[i]);
	}
	printf("\n");
}


void rshift(polynomial p, int n, polynomial *o) {
	void reverse(int arr[], int start, int end) {
		if (start >= end)
	    	return;
		int temp = arr[start];
		arr[start] = arr[end];
		arr[end] = temp;
		reverse(arr, start+1, end-1);
	}
	memcpy(o->coeffs, p.coeffs, p.len*sizeof(int));
	reverse(o->coeffs, 0, o->len - 1);
	reverse(o->coeffs, 0, n - 1);
	reverse(o->coeffs, n, o->len - 1);
}


void lshift(polynomial p, int n, polynomial *o) {
	rshift(p, p.len - n, o);
}


int degree(polynomial p) {
	if (p.coeffs[order(p)] == 0) {
		p.len --;
		return degree(p);
	} else {
		return order(p);
	}
}


void centerlift(polynomial p, int n, polynomial *o) {
	for (int i = 0; i < p.len; i ++) {
		o->coeffs[i] = p.coeffs[i] > (float)(n / 2.) ? p.coeffs[i] - n : p.coeffs[i];
	}
}


void s_add(polynomial p, int x, polynomial *o) {
	for (int i = 0; i < p.len; i ++) {
		o->coeffs[i] = p.coeffs[i];
	}
	o->coeffs[0] += x;
}


void s_mul(polynomial p, int x, polynomial *o) {
	for (int i = 0; i < p.len; i ++) {
		o->coeffs[i] = p.coeffs[i] * x;
	}
}


void s_mod(polynomial p, int x, polynomial *o) {
	for (int i = 0; i < p.len; i ++) {
		o->coeffs[i] = mod(p.coeffs[i], x);
	}
}


void neg(polynomial p, polynomial *o) {
	s_mul(p, -1, o);
}


void v_add(polynomial p, polynomial q, polynomial *o) {
	for (int i = 0; i < p.len; i ++) {
		o->coeffs[i] = p.coeffs[i] + q.coeffs[i];
	}
}


void v_sub(polynomial p, polynomial q, polynomial *o) {
	for (int i = 0; i < p.len; i ++) {
		o->coeffs[i] = p.coeffs[i] - q.coeffs[i];
	}
}


void v_mul(polynomial p, polynomial q, polynomial *o) {
	memset(o->coeffs, 0, o->len*sizeof(int));
	for (int i = 0; i < p.len; i ++) {
		for (int j = 0; j < q.len; j ++) {
			o->coeffs[(i+j) % p.len] += p.coeffs[i] * q.coeffs[j];
		}
	}
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


polynomial *new_polynomial(int len) {
	polynomial *p = malloc(sizeof(polynomial));
	p->len = len;
	p->coeffs = malloc(len * sizeof(int));
	return p;
}


void free_polynomial(polynomial *p) {
	free(p->coeffs);
	free(p);
}


void inverse_modp(polynomial F, int p, polynomial *o) {
	int k = 0, N = F.len;
	k = N; N = k;
	polynomial *b = new_polynomial(N + 1),
	           *c = new_polynomial(N + 1),
			   *f = new_polynomial(N + 1),
			   *g = new_polynomial(N + 1);
	b->coeffs[0] = 1;
	memcpy(f->coeffs, F.coeffs, N * sizeof(int));
	g->coeffs[0] = -1; g->coeffs[g->len - 1] = 1;

	while (true) {
		while (degree(*f) != 0 && f->coeffs[0] == 0) {
			lshift(*f, 1, f);
			rshift(*c, 1, c);
			k ++;
		}
		if (degree(*f) == 0) {
			b->len --;
			s_mul(*b, inv(f->coeffs[0], p), o);
			lshift(*o, k % N, o);
			free_polynomial(b); free_polynomial(c);
			free_polynomial(f); free_polynomial(g);
			return;
		}
		if (degree(*f) < degree(*g)) {
			polynomial *tmp;
			tmp = f;
			f = g;
			g = tmp;
			tmp = b;
			b = c;
			c = tmp;
		}
		int u = f->coeffs[0] * inv(g->coeffs[0], p);
		polynomial *t1 = new_polynomial(N + 1),
		           *t2 = new_polynomial(N + 1);
		s_mul(*g, u, t1); v_sub(*f, *t1, t2); s_mod(*t2, p, f);
		s_mul(*c, u, t1); v_sub(*b, *t1, t2); s_mod(*t2, p, b);
		free_polynomial(t1); free_polynomial(t2);
	}
}


void inverse_modpn(polynomial F, int pn, polynomial *o) {
	int factorise_pn(int pn) {
		int p = 2;
		while (pn % p != 0) {
			p ++;
		}
		return p;
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

	int p = factorise_pn(pn);
	inverse_modp(F, p, o);
	if (!is_zero(*o)) {
		polynomial *t1 = new_polynomial(F.len),
				   *t2 = new_polynomial(F.len),
				   *t3 = new_polynomial(F.len);
		while (p < pn) {
			p *= p;
			v_mul(F, *o, t1);
			s_add(*t1, -2, t2);
			v_mul(*t2, *o, t3);
			s_mod(*t3, p, o);
		}
		free_polynomial(t1); free_polynomial(t2); free_polynomial(t3);
	}
}


int main() {
	polynomial *f = new_polynomial(11),
	           *g = new_polynomial(11),
			   *fg = new_polynomial(11);

    static int fc[11] = {-1, 1, 1, 0, -1, 0, 1, 0, 0, 1, -1};
	f->coeffs = fc;
	inverse_modp(*f, 3, g);
	v_mul(*f, *g, fg); s_mod(*fg, 3, fg);
	prettyprint(*fg);
}

// #include <Python.h> //Don't need stdio, stdlib or string headers
// static PyObject* lcs(PyObject* self, PyObject *args) {
//     PyObject *py_tuple;
//     int len;
//     if (!PyArg_ParseTuple(args, "O", &py_tuple)) {
//       return NULL;
//     }
//     len = PyTuple_Size(py_tuple);
//     int *c_array = malloc(len * sizeof(int));
//     while (len --) {
//         c_array[len] = (int) PyInt_AsLong(PyTuple_GetItem(py_tuple, len));
//     }
// }
//
// result = PyList_New(p.len);
// for(int i = 0; i < p.len; i ++) {
//     PyList_SetItem(result, i, PyInt_FromLong(p.coeffs[i]));
// }
