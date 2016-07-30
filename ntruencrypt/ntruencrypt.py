from random import randint
from math import floor, ceil
from convert import str_to_base, base_to_str
from polynomials import Polynomial


def random_key(params):
    # In need of improvement to meet spec, see ./params.pdf
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
    return Polynomial(k)


def keygen(params):
    while True:
        f = random_key(params) * params["p"] + 1
        fq = f.inverse_modpn(params["q"])
        if fq is not None:
            break
    g = random_key(params)
    h = (fq * g * params["p"]) % params["q"]
    return f, h


def encrypt(key, params, message):
    def encrypt_p(key, params, poly):
        poly = poly.centerlift(params["p"])
        r = random_key(params)
        e = r * key + poly
        return e % params["q"]
    polys = [Polynomial(x) for x in str_to_base(
        message, params["p"], params["N"])]
    cipherpolys = [encrypt_p(key, params, poly) for poly in polys]
    ciphertext = base_to_str(cipherpolys, params["q"])
    return ciphertext


def decrypt(key, params, ciphertext):
    def decrypt_p(key, params, poly):
        # poly = poly.centerlift(params["q"])
        a = (key * poly) % params["q"]
        a = a.centerlift(params["q"])
        b = a % params["p"]
        b = b.centerlift(params["p"])
        return b
    polys = [Polynomial(x) for x in str_to_base(
        ciphertext, params["q"], params["N"])]
    plainpolys = [decrypt_p(key, params, poly) for poly in polys]
    plaintext = base_to_str(plainpolys, params["p"])
    return plaintext


if __name__ == "__main__":
    from parameters import k as K_PARAMS
    params = K_PARAMS[80]
    m = "".join([chr(randint(97, 122)) for n in range(1 << 5)])
    priv, pub = keygen(params)
    e = encrypt(pub, params, m)
    c = decrypt(priv, params, e)
    print "Pass" if m == c else "Fail"
