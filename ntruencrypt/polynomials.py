class Polynomial(tuple):

    def __init__(self, coeffs):
        super(Polynomial, self).__init__(coeffs)

    def __lshift__(self, n):
        return Polynomial(self[n:] + self[:n])

    def __rshift__(self, n):
        return self << -n

    def __add__(self, other):
        def match_lengths(p, q):
            if len(p) < len(q):
                return match_lengths(q, p)[::-1]
            else:
                return p, Polynomial(q[:] + tuple(0 for i in range(len(p) - len(q))))

        if isinstance(other, Polynomial):
            self, other = match_lengths(self, other)
            return Polynomial(map(lambda x, y: x + y, self, other))
        else:
            return self + match_lengths(self, Polynomial([other]))[1]

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return self + other * -1

    def __rsub__(self, other):
        return other + self * -1

    def __mul__(self, other):
        if isinstance(other, Polynomial):
            return Polynomial(sum((other * self[i]) >> i for i in range(len(self))))
        else:
            return Polynomial(map(lambda x: other * x, self))

    def __mod__(self, other):
        return Polynomial(map(lambda x: x % other, self))

    def centerlift(self, p):
        return Polynomial(map(lambda x: x - p if x > p / 2. else x, self))

    def is_zero(self):
        return all(x == 0 for x in self)

    def degree(self):
        if self.is_zero():
            return 0
        elif self[-1] == 0:
            return Polynomial(self[:-1]).degree()
        else:
            return len(self) - 1

    def inverse_modp(self, p):
        def inv(a, p):
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

        k, N = 0, len(self)
        c = Polynomial([0] * (N + 1))
        b = c + 1
        f = Polynomial(self[:] + (0,))
        g = (c + 1 << 1) - 1
        while True:
            while f[0] == 0 and not f.is_zero():
                f <<= 1
                c >>= 1
                k += 1
            if f.degree() == 0:
                inv_f = inv(f[0], p)
                if inv_f:
                    return Polynomial((b * inv_f)[:-1]) << k % N
                else:
                    return None
            if f.degree() < g.degree():
                f, g, b, c = g, f, c, b
            u = f[0] * inv(g[0], p)
            f = (f - g * u) % p
            b = (b - c * u) % p

    def inverse_modpn(self, pn):
        p, n = factorise_pn(pn)
        g = self.inverse_modp(p)
        pn = p ** n
        if g is not None:
            while p < pn:
                p **= 2
                g *= 2 - self * g
                g %= p
        return g


def factorise_pn(pn):
    p = 2
    n = 0
    while pn % p:
        p += 1
    while pn > 1:
        pn /= p
        n += 1
    return p, n

if __name__ == "__main__":
    f = Polynomial([-1, 1, 1, 0, -1, 0, 1, 0, 0, 1, -1])
    if (f.inverse_modp(3) * f) % 3 == Polynomial((1,) + tuple(0 for n in f[1:])):
        print "Pass"
    else:
        print "Fail"
