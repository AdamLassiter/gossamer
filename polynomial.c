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
	for (int i = 0; i < p.len; i++) {
		printf("%d ", p.coeffs[i]);
	}
	printf("\n");
}

void lshift(polynomial p, int n, polynomial *o) {
	void lshift_once_inplace(polynomial p) {
		int tmp = p.coeffs[0];
		for (int i = 0; i < p.len - 1; i++) {
			p.coeffs[i] = p.coeffs[i + 1];
		}
		p.coeffs[p.len - 1] = tmp;
	}
	memcpy(p.coeffs, o->coeffs, p.len * sizeof(int));
	for (int i = 0; i < n; i++) {
		lshift_once_inplace(*o);
	}
}

void rshift(polynomial p, int n, polynomial *o) {
	void rshift_once_inplace(polynomial p) {
		int tmp = p.coeffs[p.len - 1];
		for (int i = p.len - 1; i > 0; i--) {
			p.coeffs[i] = p.coeffs[i - 1];
		}
		p.coeffs[0] = tmp;
	}
	memcpy(p.coeffs, o->coeffs, p.len * sizeof(int));
	for (int i = 0; i < n; i++) {
		rshift_once_inplace(*o);
	}

}

int degree(polynomial p) {
	if (p.coeffs[order(p)] == 0) {
		p.len--;
		return degree(p);
	} else {
		return order(p);
	}
}

void centerlift(polynomial p, int n, polynomial *o) {
	for (int i = 0; i < p.len; i++) {
		o->coeffs[i] = p.coeffs[i] > (float)(n / 2.) ? p.coeffs[i] - n : p.coeffs[i];
	}
}

void s_add(polynomial p, int x, polynomial *o) {
	for (int i = 0; i < p.len; i++) {
		o->coeffs[i] = p.coeffs[i];
	}
	o->coeffs[0] += x;
}

void s_mul(polynomial p, int x, polynomial *o) {
	for (int i = 0; i < p.len; i++) {
		o->coeffs[i] = p.coeffs[i] * x;
	}
}

void s_mod(polynomial p, int x, polynomial *o) {
	for (int i = 0; i < p.len; i++) {
		o->coeffs[i] = mod(p.coeffs[i], x);
	}
}

void neg(polynomial p, polynomial *o) {
	s_mul(p, -1, o);
}

void v_add(polynomial p, polynomial q, polynomial *o) {
	for (int i = 0; i < p.len; i++) {
		o->coeffs[i] = p.coeffs[i] + q.coeffs[i];
	}
}

void v_sub(polynomial p, polynomial q, polynomial *o) {
	for (int i = 0; i < p.len; i++) {
		o->coeffs[i] = p.coeffs[i] - q.coeffs[i];
	}
}

void v_mul(polynomial p, polynomial q, polynomial *o) {
	for (int i = 0; i < p.len; i++) {
		for (int j = 0; j < q.len; j++) {
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
			k++;
		}
		if (degree(*f) == 0) {
			b->len--;
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
