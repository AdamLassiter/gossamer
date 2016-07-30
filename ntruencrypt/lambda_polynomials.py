def prettyprint(p):
    top = "".join([" " * (len(str(p[n])) + 1) +
                   ("" if n == 1 else str(n)) +
                   "  " if p[n] else "" for n in range(len(p))])

    btm = "".join([str(p[n]) + "x" +
                   ("" if n == 1 else " " * len(str(n))) +
                   "+ " if p[n] else "" for n in range(len(p))])

    return "\n".join([top[:-2], btm[:-2]])

lshift = lambda p, n: p[n:] + p[:n]
rshift = lambda p, n: lshift(p, -n)

hi_term = lambda p: p[-1] if p[-1] else hi_term(p[:-1])
order = lambda p: len(p) - 1
degree = lambda p: degree(p[:-1]) if p[-1] == 0 else order(p)
cntrlft = lambda p, n: map(lambda x: x - n if x > n / 2. else x, p)

sadd = lambda p, y: map(lambda x, y: x + y, p, [y] + [0] * order(p))
smul = lambda p, y: map(lambda x: x * y, p)
smod = lambda p, y: map(lambda x: x % y, p)
neg = lambda p: smul(p, -1)

vadd = lambda p, q: map(lambda x, y: x + y, p, q)
vsub = lambda p, q: vadd(p, neg(q))
rmap = lambda f, p: p[:1] + rmap(f, map(f, p[1:])) if p[1:] else p
vmul = lambda p, q: reduce(vadd, rmap(lambda r: rshift(r, 1),
                                      map(lambda y: smul(p, y), q)))

gcd = lambda a, b: (
    lambda g, x, y: [g, y - (b // a) * x, x])(*gcd(b % a, a)) if a else [b, 0, 1]
inv = lambda a, p: (lambda g, x, y: x % p if g == 1 else 0)(*gcd(a % p, p))


def inv_modp(F, p):
    k = 0
    N = len(F)
    c = [0] * (N + 1)
    b = sadd(c, 1)
    f = F + [0]
    g = sadd(lshift(sadd(c, 1), 1), -1)
    while True:
        while degree(f) and not f[0]:
            f, c = lshift(f, 1), rshift(c, 1)
            k += 1
        if not degree(f):
            return lshift(smul(b, inv(f[0], p))[:-1], k % N) if inv(f[0], p) else None
        if degree(f) < degree(g):
            f, g, b, c = g, f, c, b
        u = f[0] * inv(g[0], p)
        f = smod(vsub(f, smul(g, u)), p)
        b = smod(vsub(b, smul(c, u)), p)


def inv_modpn(F, p, n):
    g = inv_modp(F, p)
    pn = p ** n
    if g:
        while p < pn:
            p **= 2
            g = smod(vmul(g, sadd(neg(vmul(F, g)), 2)), p)
    return g

if __name__ == "__main__":
    f = [-1, 1, 1, 0, -1, 0, 1, 0, 0, 1, -1]
    print "Pass" if smod(vmul(f, inv_modp(f, 3)), 3) == [1] + [0 for x in f[1:]] else "Fail"
