from ntruencrypt import *
from parameters import k as K_PARAMS

params = K_PARAMS[80]

m = "".join([chr(randint(97, 122)) for n in range(1 << 5)])
priv, pub = keygen(params)
e = encrypt(pub, params, m)
c = decrypt(priv, params, e)

print "Pass" if m == c else "Fail"
