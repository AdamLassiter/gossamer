from random import randint
from math import floor, ceil
from convert import str_to_base, base_to_str
from ring_polynomials import ring_polynomial as polynomial


def random_key(params):
    k = [0 for n in range(params["N"])]
    d1, d2 = params["d"], params["d"] - 1
    while d1:
        r = randint(0, params["N"] - 1)
        k[r] = 1
        d1 -= 1
    while d2:
        r = randint(0, params["N"] - 1)
        if not k[r]:
            k[r] = -1
            d2 -= 1
    return polynomial(k)


def keygen(params):
    while True:
        f = random_key(params) * params["p"] + 1
        try:
            fq = f.inverse_modpn(params["q"])
            break
        except Exception as e:
            print e
            pass
    g = random_key(params)
    h = (fq * g * params["p"]) % params["q"]
    return f, h


def encrypt(key, params, message):
    def encrypt_p(key, params, poly):
        poly.centerlift(params["p"])
        r = random_key(params)
        e = r * key + poly
        return e % params["q"]
    polys = [polynomial(x) for x in str_to_base(
        message, params["p"], params["N"])]
    cipherpolys = [encrypt_p(key, params, poly).coeffs for poly in polys]
    ciphertext = base_to_str(cipherpolys, params["q"])
    return ciphertext


def decrypt(key, params, ciphertext):
    def decrypt_p(key, params, poly):
        poly.centerlift(params["q"])
        a = (key * poly) % params["q"]
        a.centerlift(params["q"])
        b = a % params["p"]
        b.centerlift(params["p"])
        return b
    polys = [polynomial(x) for x in str_to_base(
        ciphertext, params["q"], params["N"])]
    plainpolys = [decrypt_p(key, params, poly).coeffs for poly in polys]
    plaintext = base_to_str(plainpolys, params["p"])
    return plaintext


if __name__ == "__main__":
    from parameters import k as K_PARAMS
    params = K_PARAMS[80]
    m = "".join([chr(randint(97, 122)) for n in range(1 << 5)])
    print "Using N=%(N)d, p=%(p)d, q=%(q)d" % params
    print "Message is %s" % ("'%s'" % m if len(m) < 1 << 7
                             else "long (%d)" % len(m))
    print "Generating keys..."
    priv, pub = keygen(params)
    print "Encrypting..."
    e = encrypt(pub, params, m)
    print "Decrypting..."
    c = decrypt(priv, params, e)
    print "Success!" if m == c else "Failure!"
    print m
    print c
