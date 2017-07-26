#! /usr/bin/python3

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


def bytes2base(bytes, base, N=0):
    """
    Converts a string to lists of ints, length N, in a given base
    """
    unpadded_list = base_convert(bytes, 256, base)
    return split(unpadded_list, N) if N else [unpadded_list]


def base2bytes(lists, base):
    """
    Converts lists of ints in a given base to a string
    """
    return bytes(base_convert(join(lists), base, 256))


class NTRUPolynomial(tuple):
    import c_ntruencrypt.polynomial as cLib

    @classmethod
    def new(cls, *args):
        """
        Shorthand to create new NTRUPolynomial instances
        """
        return cls(*args)

    def __new__(cls, coeffs):
        return super().__new__(cls, tuple(coeffs))

    def __rshift__(self, n):
        return self << -n

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return self + other * -1

    def __rsub__(self, other):
        return other + self * -1

    def is_zero(self):
        return all(x == 0 for x in self)

    def __lshift__(self, n):
        return self.new(self.cLib.lshift(self, n))

    def __add__(self, other):
        if isinstance(other, NTRUPolynomial):
            return self.new(self.cLib.v_add(self, other))
        else:
            return self.new(self.cLib.s_add(self, other))

    def __mul__(self, other):
        if isinstance(other, NTRUPolynomial):
            return self.new(self.cLib.v_mul(self, other))
        else:
            return self.new(self.cLib.s_mul(self, other))

    def __mod__(self, other):
        return self.new(self.cLib.s_mod(self, other))

    def centerlift(self, n):
        return self.new(self.cLib.centerlift(self, n))

    def degree(self):
        return self.cLib.degree(self)

    def inverse_modp(self, p):
        return self.new(self.cLib.inverse_modp(self, p))

    def inverse_modpn(self, pn):
        return self.new(self.cLib.inverse_modpn(self, pn))


class NTRUCipher(object):

    def __init__(self, params, keypair=None):
        self.key = keypair if keypair else self.keygen(params)
        self.params = params

    def __repr__(self):
        return '<NTRUCipher with f=%s, h=%s, params=%s>' % \
            (self.key['priv'], self.key['pub'], self.params)

    @staticmethod
    def __random_poly(params):
        # In need of improvement to meet spec, see docs/ntru/ntru_params.pdf
        k = [0 for n in range(params['N'])]
        d1, d2 = params['d'], params['d'] - 1
        for d, i in ((d1, 1), (d2, -1)):
            while d:
                r = randint(0, params['N'] - 1)
                if not k[r]:
                    k[r] = i
                    d -= 1
        return NTRUPolynomial(k)

    @staticmethod
    def keygen(params):
        """
        Generates a new valid, random public/private keypair
        """

        while True:
            f = NTRUCipher.__random_poly(params) * params['p'] + 1
            fq = f.inverse_modpn(params['q'])
            if fq is not None:
                break
        g = NTRUCipher.__random_poly(params)
        h = (fq * g * params['p']) % params['q']
        return {'priv': f, 'pub': h}

    def __encrypt_poly(self, poly):
        poly = poly.centerlift(self.params['p'])
        r = self.__random_poly(self.params)
        e = r * self.key['pub'] + poly
        e %= self.params['q']
        return e.centerlift(self.params['q']) % self.params['p']

    def encrypt(self, text):
        """
        Encrypt a given string using the current public key and parameters
        """
        polys = [self.__encrypt_poly(NTRUPolynomial(x))
                 for x in str2base(bytes(text, 'utf8'), self.params['p'], self.params['N'])]
        return base2str(polys, self.params['q']).decode('raw_unicode_escape')

    def decrypt_poly(self, poly):
        a = (self.key['priv'] * poly) % self.params['q']
        a = a.centerlift(self.params['q'])
        b = a % self.params['p']
        return b

    def decrypt(self, text):
        """
        Decrypt a given string using the current private key and parameters
        """
        polys = [self.decrypt_poly(NTRUPolynomial(x))
                 for x in str2base(bytes(text, 'raw_unicode_escape'), self.params['q'], self.params['N'])]
        return base2bytes(polys, self.params['p']).decode('utf8')

    def pubkey(self):
        return base2str([self.key['pub'] % self.params['p']] + [[1]],
                        self.params['p'])

    def privkey(self):
        return base2str([self.key['priv'] % self.params['q']] + [[1]],
                        self.params['q'])

    def set_key(self, pub="", priv=""):
        if pub:
            self.key['pub'] = NTRUPolynomial(str2base(pub, self.params['p']))
        if priv:
            self.key['priv'] = NTRUPolynomial(str2base(pub, self.params['q']))

    @staticmethod
    def preset(N, d, Hw, p, q):
        """
        Returns a factory function for the given parameters:
        N  - Size of polynomial ring
        d  - Number of 1s used in key generation
        Hw - Maximum Hamming-Weight of the plaintext polynomial
        p  - Prime modulus for polynomial ring
        q  - Prime-power modulus for polynomial ring
        """
        # TODO NTRU preset should check against Hw
        def create(keypair=None):
            layout = ['N', 'd', 'Hw', 'p', 'q']
            c = NTRUCipher(dict(zip(layout, (N, d, Hw, p, q))), keypair)
            return c
        return create


# NTRUEncrypt parameter presets
NTRUEncrypt80 = NTRUCipher.preset(251, 8, 72, 3, 3**8)
NTRUEncrypt112 = NTRUCipher.preset(347, 11, 132, 3, 3**9)
NTRUEncrypt128 = NTRUCipher.preset(397, 12, 156, 3, 3**10)
NTRUEncrypt160 = NTRUCipher.preset(491, 15, 210, 3, 3**10)
NTRUEncrypt192 = NTRUCipher.preset(587, 17, 306, 3, 3**10)
NTRUEncrypt256 = NTRUCipher.preset(787, 22, 462, 3, 3**11)
# HACK: Avoid powers of 2 for ntru q-vals
