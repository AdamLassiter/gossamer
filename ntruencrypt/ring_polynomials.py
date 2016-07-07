class ring_polynomial:

    def __init__(self, coefficients=[], degree=0):
        if degree and coefficients and len(coefficients) - 1 > degree:
            raise ValueError("Degree too low for given coefficients.")
        self.coeffs = [0 for n in range(degree + 1)]
        if coefficients:
            self.coeffs[:len(coefficients)] = coefficients

    def __str__(self):
        top_line = ""
        bottom_line = ""
        for n in range(len(self)):
            x = self[n]
            if not x:
                continue
            top_line += " " * (len(str(x)) + 1) + str(n) + "  "
            bottom_line += str(x) + "x" + " " * len(str(n)) + "+ "
            if n == 0:
                top_line = top_line.replace("0", "")
                bottom_line = bottom_line.replace("x", "")
            if n == 1:
                top_line = top_line.replace("1", " ")
        return top_line[:-2] + "\n" + bottom_line[:-2]

    def zero(n):
        return polynomial([0 for x in range(n)])

    def copy(self):
        return polynomial([x for x in self.coeffs])

    def __len__(self):
        return len(self.coeffs)

    def __getitem__(self, index):
        return self.coeffs[index]

    def __setitem__(self, index, value):
        self.coeffs[index] = value

    def __delitem__(self, index):
        del self[index]

    def __rshift__(self, n):
        return polynomial(self.coeffs[n:] + self.coeffs[:n])

    def __lshift__(self, n):
        return polynomial(self.coeffs[-n:] + self.coeffs[:-n])

    # TODO : Check gt function actually works
    def __gt__(self, other):
        if self.deg() != other.deg:
            return self.deg() > other.deg()
        else:
            return self.most_significant() > other.most_significant()

    def __lt__(self, other):
        return other > self

    def __neg__(self):
        new_c = [-self[n] for n in range(len(self))]
        return polynomial(new_c)

    def __add__(self, other):
        if isinstance(other, polynomial):
            assert len(self) == len(other)
            new_c = [self[n] + other[n] for n in range(len(self))]
            return polynomial(new_c)
        else:
            new_c = [self[0] + other] + [self[n] for n in range(1, len(self))]
            return polynomial(new_c)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return (-self) + other

    def __mul__(self, other):
        if isinstance(other, polynomial):
            assert len(self) == len(other)
            new_c = [0 for n in range(len(self))]
            for i in range(len(self)):
                for j in range(len(self)):
                    new_c[(i + j) % len(self)] += self[i] * other[j]
            return polynomial(new_c)
        else:
            new_c = [self[n] * other for n in range(len(self))]
            return polynomial(new_c)

    def __rmul__(self, other):
        return self * other

    def __mod__(self, other):
        new_c = [c % other for c in self.coeffs]
        return polynomial(new_c)

    def centerlift(self, p):
        for n in range(len(self)):
            if self[n] > p / 2.:
                self[n] -= p

    def deg(self):
        for i in range(1, len(self)):
            if self[-i] != 0:
                return len(self) - i
        return 0

    def most_significant(self):
        self[self.deg()]

    def inverse_modp(self, p):
        # Find b s.t. ab = 1 mod p
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

        N = len(self.coeffs)
        k = 0
        zero = lambda: polynomial(degree=N)
        b, c, g = zero() + 1, zero(), zero()
        f = polynomial(coefficients=self.coeffs, degree=N)
        g[N], g[0] = 1, -1
        while True:
            while f[0] == 0 and f.deg() > 0:
                f >>= 1
                c <<= 1
                k += 1
            if f.deg() == 0:
                if mod_inv(f[0], p) == 0:
                    return None
                ret = polynomial(coefficients=(mod_inv(f[0], p) * b)[:-1])
                return ret << (N - k) % N
            if f.deg() < g.deg():
                f, g = g, f
                b, c = c, b
            u = f[0] * mod_inv(g[0], p)
            f = (f - u * g) % p
            b = (b - u * c) % p

    def inverse_modpn(self, pn):
        # Factorize p^n for some p, n
        def factorize(n):
            from math import log
            i = 2
            while n % i:
                i += 1
            return i, int(log(n, i))

        p, n = factorize(pn)
        g = self.inverse_modp(p)
        if g is None:
            return None
        q = p
        while q < pn:
            q **= 2
            g *= 2 - self * g
            g %= q
        return g
