def inv(a, p):
    def gcd(a, b):
        if a == 0:
            return b, 0, 1
        else:
            g, y, x = gcd(b % a, a)
            return g, x - (b // a) * y, y
    g, x, y = gcd(a % p, p)
    if g != 1:
        raise Exception("No inverse exists for %s %% %s" % (a, p))
    else:
        return x % p


class polynomial:

    def __init__(self, coefficients):
        self.c = coefficients

    def __str__(self):
        string1 = ""
        string2 = ""
        for n in range(len(self)):
            x = self[n]
            if not x:
                continue
            string1 += " " * (len(str(x)) + 1) + str(n) + "  "
            string2 += str(x) + "x" + " " * len(str(n)) + "+ "
            if n == 0:
                string1 = string1.replace("0", "")
                string2 = string2.replace("x", "")
            if n == 1:
                string1 = string1.replace("1", " ")
        return string1[:-2] + "\n" + string2[:-2]

    def zero(n):
        return polynomial([0 for x in range(n)])

    def copy(self):
        return polynomial([x for x in self.c])

    def __len__(self):
        return len(self.c)

    def __getitem__(self, index):
        return self.c[index]

    def __setitem__(self, index, value):
        self.c[index] = value

    def __delitem__(self, index):
        del self[index]

    def __rshift__(self, n):
        return polynomial(self.c[n:] + self.c[:n])

    def __lshift__(self, n):
        return polynomial(self.c[-n:] + self.c[:-n])

    # TODO : Check gt function actually works
    def __gt__(self, other):
        if self.deg() != other.deg:
            return self.deg() > other.deg()
        else:
            return self.highest() > other.highest()

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
        new_c = [c % other for c in self.c]
        return polynomial(new_c)

    def centerlift(self, p):
        for n in range(len(self)):
            if self[n] > p / 2.:
                self[n] -= p

    # TODO : Implement eea algorithm
    def inverse(self, p):
        def eea(a, b, p):
            pass

    def deg(self):
        for i in range(1, len(self)):
            if self[-i] != 0:
                return len(self) - i
        return 0

    def highest(self):
        self[self.deg()]
