%module polynomial
%{
        #include "polynomial.h"
%}

extern void inverse_modp(polynomial, int, polynomial*);
extern void inverse_modpn(polynomial, int, polynomial*);
