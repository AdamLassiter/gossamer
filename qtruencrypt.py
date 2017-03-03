#!/usr/bin/python3

from random import randint
from math import log
from debug import debug


def base_convert(digits, fromBase, toBase):
    """
    Converts a list of ints, digits, from a given base to any other
    """
    n = 0
    for i in range(len(digits)):
        n += (digits[i] % fromBase) * (fromBase**i)
    if n == 0:
        return [0]
    newDigits = []
    while n:
        newDigits.append(int(n % toBase))
        n //= toBase
    return newDigits


def split(unpadded_list, N):
    """
    Splits a list into a series of N-length lists
    Pads the last list with terminator 0x01 and then 0x00 chars
    """
    terminated_list = unpadded_list + [1]
    padded_lists = []
    for n in range(0, len(terminated_list), N):
        padded_lists.append(terminated_list[n:n + N])
    padded_lists[-1].extend([0 for _ in range(N - len(padded_lists[-1]))])
    return padded_lists


def join(padded_lists):
    """
    Joins a series of lists, stripping trailing 0s from the output
    """
    unpadded_list = []
    for l in padded_lists:
        unpadded_list.extend(l)
    while unpadded_list[-1] == 0:
        del unpadded_list[-1]
    return unpadded_list[:-1]


def str2base(string, base, N=0):
    """
    Converts a string to lists of ints, length N, in a given base
    """
    unpadded_list = base_convert(list(bytearray(string)), 256, base)
    return split(unpadded_list, N) if N else [unpadded_list]


def base2str(lists, base):
    """
    Converts lists of ints in a given base to a string
    """
    return str(bytearray(base_convert(join(lists), base, 256)))


def mat2poly(matrix):
    res = map(Matrix.square, zip(*b))
    return RingPolynomial(res)


def poly2mat(polynomial):
    res = zip(*(reduce(lambda a, b: a + b, matrix) for matrix in polynomial))
    return Quaternion(matrix=Matrix.square(res))


class Matrix(list):

    @staticmethod
    def square(x):
        from math import sqrt
        n = int(sqrt(len(x)))
        return Matrix([x[i::x] for i in range(n)])

    def __add__(self, other):
        if type(self) is type(other):
            res = [map(sum, zip(self_row, other_row))
                   for self_row, other_row in zip(self, other)]
            return Matrix(res)

    def __neg__(self):
        res = [map(lambda x: -x, row) for row in self]
        return Matrix(res)

    def __mul__(self, other):
        if type(self) is type(other):
            res = [[sum(x * y for x, y in zip(self_row, other_row))
                    for other_row in other.transpose()] for self_row in self]
        else:
            res = [[x * other for x in row] for row in self]
        return Matrix(res)

    def conjugate(self):
        res = map(lambda row: map(lambda x: x.conjugate()
                                  if hasattr(x, 'conjugate')
                                  else x, row),
                  self)
        return Matrix(res)

    def transpose(self):
        res = zip(*self)
        return Matrix(res)

    def conjugate_transpose(self):
        return self.conjugate().transpose()

    def __abs__(self):
        def det(x):
            def minor(x, i, j):
                y = x[:]
                del(y[i - 1])
                y = zip(*y)
                del(y[j - 1])
                return zip(*y)
            if len(x) == 1:
                return x[0][0]
            return sum([(-1) ** i * x[i][0] * det(minor(x, i + 1, 1))
                        for i in range(len(x))])
        return det(self)


class Quaternion(Matrix):

    def __init__(self, r=0, i=0, j=0, k=0, matrix=None):
        if matrix is not None:
            assert isinstance(matrix, Matrix)
            super().__init__(matrix)
        else:
            super().__init__([[r - i * 1j, -j - k * 1j],
                              [j - k * 1j,  r + i * 1j]])

    def __eq__(self, other):
        if type(self) is type(other):
            return super().__eq__(self, other)
        else if isinstance(other, complex):
            return self == Quaternion(other.real, other.imag)
        else:
            return self == Quaternion(other)

    def r(self):
        return self[0][0].real

    def i(self):
        return self[0][0].imag

    def j(self):
        return -self[0][1].real

    def k(self):
        return -self[0][1].imag

    def __str__(self):
        return '%d + %di + %dj + %dk' % (self.r(), self.i(),
                                         self.j(), self.k())


class RingPolynomial(list):

    @classmethod
    def new(cls, *args):
        """
        Shorthand to create new RingPolynomial instances
        """
        return cls(*args)

    def __init__(self, *args):
        super().__init__(*args)

    def __lshift__(self, n):
        return self.new(self[n:] + self[:n])

    def __rshift__(self, n):
        return self << -n

    def __add__(self, other):
        if type(self) is type(other):
            return self.new(map(lambda x, y: x + y, self, other))
        else:
            return self + self.new([other] + [0 for x in self[:-1]])

    def __sub__(self, other):
        return self + (-other)

    def __neg__(self):
        return self.new(map(lambda x: -x, self))

    def __mul__(self, other):
        if type(self) is type(other):
            return self.new(sum((self[i] * other) >> i
                                for i in range(len(self))))
        else:
            return self.new(map(lambda x: x * other, self))

    def __mod__(self, other):
        return self.new(map(lambda x: x % other, self))

    def is_zero(self):
        return all(x == 0 for x in self)

    def centerlift(self, n):
        # TODO: Convert from NTRU to QTRU
        # return self.new(map(lambda x: x - n if x > n / 2. else x, self))
        pass

    def degree(self):
        if self.is_zero():
            return 0
        elif self[-1] == 0:
            return self.new(self[:-1]).degree()
        else:
            return len(self) - 1

    def inverse_modp(self, p):
        # TODO: Convert from NTRU to QTRU
        """
        Finds a polynomial F' in the same ring as F such that F*F' = 1 mod p
        Returns None if no such polynomial exists
        """
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
        c = self.new([0] * (N + 1))
        b = c + 1
        f = self.new(self[:] + (0,))
        g = (c + 1 << 1) - 1
        while True:
            while f[0] == 0 and not f.is_zero():
                f <<= 1
                c >>= 1
                k += 1
            if f.degree() == 0:
                inv_f = inv(f[0], p)
                if inv_f:
                    return self.new((b * inv_f)[:-1]) << k % N
                else:
                    return None
            if f.degree() < g.degree():
                f, g, b, c = g, f, c, b
            u = f[0] * inv(g[0], p)
            f = (f - g * u) % p
            b = (b - c * u) % p

    def inverse_modpn(self, pn):
        # TODO: Convert from NTRU to QTRU
        """
        Finds a polynomial F' in the same ring as F such that F*F' = 1 mod p^n
        Returns None if no such polynomial exists
        """
        def factorise_pn(pn):
            p = 2
            n = 0
            while pn % p:
                p += 1
            while pn > 1:
                pn /= p
                n += 1
            return p, n

        p, r = factorise_pn(pn)
        g = self.inverse_modp(p)
        if g is not None:
            n = 2
            while r > 0:
                g *= 2 - self * g
                g %= p ** n
                r /= 2
                n *= 2
        return g % pn if g else None


class QTRUCipher(object):

    def __init__(self, params, keypair=None):
        self.key = keypair if keypair else self.keygen(params)
        self.params = params

    def __repr__(self):
        return '<QTRUCipher with f=%s, h=%s, params=%s>' % \
            (self.key['priv'], self.key['pub'], self.params)

    @staticmethod
    def random_poly(params):
        pass

    @staticmethod
    def keygen(params):
        """
        Generates a new valid, random public/private keypair
        """

        while True:
            f = QTRUCipher.random_poly(params) * params['p'] + 1
            fq = f.inverse_modpn(params['q'])
            if fq is not None:
                break
        g = QTRUCipher.random_poly(params)
        h = (fq * g * params['p']) % params['q']
        return {'priv': f, 'pub': h}

    def encrypt(self, text):
        """
        Encrypt a given string using the current public key and parameters
        """
        def encrypt_p(poly):
            poly = poly.centerlift(self.params['p'])
            r = self.random_poly(self.params)
            e = r * self.key['pub'] + poly
            return e % self.params['q']

        polys = [RingPolynomial(x)
                 for x in str2base(text, self.params['p'], self.params['N'])]
        cipherpolys = map(encrypt_p, polys)
        ciphertext = base2str(cipherpolys, self.params['q'])
        return ciphertext

    def decrypt(self, text):
        """
        Decrypt a given string using the current private key and parameters
        """
        def decrypt_p(poly):
            a = (self.key['priv'] * poly) % self.params['q']
            a = a.centerlift(self.params['q'])
            b = a % self.params['p']
            b = b.centerlift(self.params['p'])
            return b

        polys = [RingPolynomial(x)
                 for x in str2base(text, self.params['q'], self.params['N'])]
        plainpolys = map(decrypt_p, polys)
        plaintext = base2str(plainpolys, self.params['p'])
        return plaintext

    def pubkey(self):
        return base2str([self.key['pub'] % self.params['p']] + [[1]],
                        self.params['p'])

    def privkey(self):
        return base2str([self.key['priv'] % self.params['q']] + [[1]],
                        self.params['q'])

    def set_key(self, pub='', priv=''):
        if pub:
            self.key['pub'] = RingPolynomial(str2base(pub, self.params['p']))
        if priv:
            self.key['priv'] = RingPolynomial(str2base(pub, self.params['q']))

    @staticmethod
    def preset(N, d, Hw, p, q):
        pass


# QTRUEncrypt parameter presets
pass
