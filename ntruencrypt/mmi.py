from ring_polynomials import polynomial

def inverse_modpn(f, pn):
    p, n = factorize(pn)
    g = inverse_modp(f, p)
    if g is None:
        return None
    q = p
    while q < pn:
        q **= 2
        g *= 2-f*g
        g %= q
    return g
        

def inverse_modp(f, p):
    N = len(f)
    zero = lambda: polynomial([0 for n in range(N+1)])
    k = 0
    b, c, g = zero() + 1, zero(), zero()
    f = polynomial(f.c + [0])
    g[N], g[0] = 1, -1
    while True:
        while f[0] == 0 and f.deg() > 0:
            f >>= 1
            c <<= 1
            k += 1
        if f.deg() == 0:
            if mod_inv(f[0], p) == 0:
                return None
            ret = polynomial((mod_inv(f[0], p) * b)[:-1])
            return ret << (N-k) % N
        if f.deg() < g.deg():
            f, g = g, f
            b, c = c, b
        u = f[0] * mod_inv(g[0], p)
        f = (f - u * g) % p
        b = (b - u * c) % p


def mod_inv(a, p):
    def gcd(a, b):
        if a == 0:
            return b, 0, 1
        else:
            g, y, x = gcd(b % a, a)
            return g, x - (b // a) * y, y
    g, x, y = gcd(a % p, p)
    if g != 1:
        return 0
    else:
        return x % p


def factorize(n):
    from math import log
    i = 2
    while n % i:
        i += 1
    return i, int(log(n, i))
