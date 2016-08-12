from random import randint
from math import log


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
    Splits a list into a series of N-length lists, padding the last with 0s
    """
    padded_lists = []
    for n in range(0, len(unpadded_list), N):
        padded_lists.append(unpadded_list[n:n + N])
    padded_lists[-1].extend([0 for n in range(N - len(padded_lists[-1]))])
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
    return unpadded_list


def str2base(string, base, N):
    """
    Converts a string to a list of ints in a given base
    """
    return split(base_convert(list(bytearray(string)), 256, base), N)


def base2str(lists, base):
    """
    Converts a list of ints in a given base to a string
    """
    # FIXME: Will strip trailing null-characters
    return str(bytearray(base_convert(join(lists), base, 256)))


class NTRUPolynomial(tuple):

    @staticmethod
    def new(*args):
        """
        Shorthand to create new NTRUPolynomial instances
        """
        return NTRUPolynomial(*args)

    def __init__(self, coeffs):
        super(NTRUPolynomial, self).__init__(coeffs)

    def __lshift__(self, n):
        return self.new(self[n:] + self[:n])

    def __rshift__(self, n):
        return self << -n

    def __add__(self, other):
        if isinstance(other, NTRUPolynomial):
            return self.new(map(lambda x, y: x + y, self, other))
        else:
            return self + self.new([other] + [0 for x in self[:-1]])

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return self + other * -1

    def __rsub__(self, other):
        return other + self * -1

    def __mul__(self, other):
        if isinstance(other, NTRUPolynomial):
            return self.new(sum((other * self[i]) >> i for i in range(len(self))))
        else:
            return self.new(map(lambda x: other * x, self))

    def __mod__(self, other):
        return self.new(map(lambda x: x % other, self))

    def centerlift(self, p):
        return self.new(map(lambda x: x - p if x > p / 2. else x, self))

    def is_zero(self):
        return all(x == 0 for x in self)

    def degree(self):
        if self.is_zero():
            return 0
        elif self[-1] == 0:
            return self.new(self[:-1]).degree()
        else:
            return len(self) - 1

    def inverse_modp(self, p):
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

        p, n = factorise_pn(pn)
        g = self.inverse_modp(p)
        pn = p ** n
        if g is not None:
            while p < pn:
                p **= 2
                g *= 2 - self * g
                g %= p
        return g


class NTRUCipher(object):

    def __init__(self, params, keypair=None):
        self.key = keypair if keypair else self.keygen(params)
        self.params = params

    def __repr__(self):
        return '<NTRUCipher with f=%s, h=%s, params=%s>' % (self.key['priv'], self.key['pub'])

    @staticmethod
    def random_poly(params):
        # In need of improvement to meet spec, see docs/ntru/ntru_params.pdf
        k = [0 for n in range(params['N'])]
        d1, d2 = params['d'], params['d'] - 1
        while d1:
            r = randint(0, params['N'] - 1)
            k[r] = 1
            d1 -= 1
        while d2:
            r = randint(0, params['N'] - 1)
            if not k[r]:
                k[r] = -1
                d2 -= 1
        return NTRUPolynomial(k)

    @staticmethod
    def keygen(params):
        """
        Generates a new valid, random public/private keypair
        """

        while True:
            f = NTRUCipher.random_poly(params) * params['p'] + 1
            fq = f.inverse_modpn(params['q'])
            if fq is not None:
                break
        g = NTRUCipher.random_poly(params)
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
        polys = [NTRUPolynomial(x) for x in str2base(
            text, self.params['p'], self.params['N'])]
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
        polys = [NTRUPolynomial(x) for x in str2base(
            text, self.params['q'], self.params['N'])]
        plainpolys = map(decrypt_p, polys)
        plaintext = base2str(plainpolys, self.params['p'])
        return plaintext

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
        # FIXME: Obsolete since Sept. 2015, see ./params.pdf
        # TODO: Should actually use Hw
        def create(keypair=None):
            layout = ['N', 'd', 'Hw', 'p', 'q']
            c = NTRUCipher(dict(zip(layout, (N, d, Hw, p, q))), keypair)
            return c
        return create

# NTRUEncrypt parameter presets
NTRUEncrypt80 = NTRUCipher.preset(251, 8, 72, 3, 256)
NTRUEncrypt112 = NTRUCipher.preset(347, 11, 132, 3, 512)
NTRUEncrypt128 = NTRUCipher.preset(397, 12, 156, 3, 1024)
NTRUEncrypt160 = NTRUCipher.preset(491, 15, 210, 3, 1024)
NTRUEncrypt192 = NTRUCipher.preset(587, 17, 306, 3, 1024)
NTRUEncrypt256 = NTRUCipher.preset(787, 22, 462, 3, 2048)

if __name__ == '__main__':
    import tests
    tests.test_ntru()