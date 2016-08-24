#include <Python.h>
#define order(p) (p.len - 1)
#define mod(a, b) ((b + (a % b)) % b)
#define true 1


typedef struct polynomial {
	int len;
	int  *coeffs;
} polynomial;


void inverse_modp(polynomial, int, polynomial*);
void inverse_modpn(polynomial, int, polynomial*);
